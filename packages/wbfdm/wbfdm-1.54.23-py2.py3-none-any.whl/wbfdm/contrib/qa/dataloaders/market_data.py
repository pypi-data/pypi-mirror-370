from contextlib import suppress
from datetime import date
from enum import Enum
from functools import reduce
from itertools import batched
from typing import TYPE_CHECKING, Iterator

import pypika as pk
from django.db import ProgrammingError, connections
from pypika import Case, Column, MSSQLQuery
from pypika import functions as fn
from pypika.enums import Order, SqlTypes
from pypika.terms import ValueWrapper
from wbcore.contrib.dataloader.dataloaders import Dataloader
from wbcore.contrib.dataloader.utils import dictfetchall

from wbfdm.contrib.qa.dataloaders.utils import create_table
from wbfdm.dataloaders.protocols import MarketDataProtocol
from wbfdm.dataloaders.types import MarketDataDict
from wbfdm.enums import Frequency, MarketData

if TYPE_CHECKING:
    pass


class DS2MarketData(Enum):
    OPEN = "Open_"
    CLOSE = "Close_"
    HIGH = "High"
    LOW = "Low"
    BID = "Bid"
    ASK = "Ask"
    VWAP = "VWAP"
    VOLUME = "Volume"
    MARKET_CAPITALIZATION = "MktCap"
    SHARES_OUTSTANDING = "NumShrs"


class DatastreamMarketDataDataloader(MarketDataProtocol, Dataloader):
    def market_data(
        self,
        values: list[MarketData] = [MarketData.CLOSE],
        from_date: date | None = None,
        to_date: date | None = None,
        exact_date: date | None = None,
        frequency: Frequency = Frequency.DAILY,
        target_currency: str | None = None,
        apply_fx_rate: bool = True,
        **kwargs,
    ) -> Iterator[MarketDataDict]:
        """Get market data for instruments.

        Args:
            queryset (QuerySet["Instrument"]): The queryset of instruments.
            values (list[MarketData]): List of values to include in the results.
            from_date (date | None): The starting date for filtering prices. Defaults to None.
            to_date (date | None): The ending date for filtering prices. Defaults to None.
            frequency (Frequency): The frequency of the requested data

        Returns:
            Iterator[MarketDataDict]: An iterator of dictionaries conforming to the DailyValuationDict.
        """

        lookup = {
            f"{k[0]},{k[1]}": v for k, v in self.entities.values_list("dl_parameters__market_data__parameters", "id")
        }

        # Define tables
        pricing = pk.Table("vw_DS2Pricing")

        mapping, create_mapping_table = create_table(
            "#ds2infoexchcode", Column("InfoCode", SqlTypes.INTEGER), Column("ExchIntCode", SqlTypes.INTEGER)
        )

        # Base query to get data we always need unconditionally
        query = (
            pk.MSSQLQuery.from_(pricing)
            .select(
                fn.Concat(pricing.InfoCode, ",", pricing.ExchIntCode).as_("external_identifier"),
                fn.Concat(
                    pricing.InfoCode, ",", pricing.ExchIntCode, "_", fn.Cast(pricing.MarketDate, SqlTypes.DATE)
                ).as_("id"),
                fn.Cast(pricing.MarketDate, SqlTypes.DATE).as_("valuation_date"),
                ValueWrapper("qa-ds2").as_("source"),
            )
            # We join on _codes, which removes all instruments not in _codes - implicit where
            .join(mapping)
            .on((pricing.InfoCode == mapping.InfoCode) & (pricing.ExchIntCode == mapping.ExchIntCode))
            .where(pricing.AdjType == 2)
            .orderby(pricing.MarketDate, order=Order.desc)
        )

        # if a target currency is required, we join on the fx tables and set the currency to the desired one
        # otherwise we just set the currency to whatever the currency is from the instrument
        fx_rate = None
        if target_currency:
            query = query.select(ValueWrapper(target_currency).as_("currency"))
            fx_code = pk.Table("DS2FxCode")
            fx_rate = pk.Table("DS2FxRate")
            query = (
                query.select(
                    (Case().when(pricing.Currency == target_currency, 1).else_(1 / fx_rate.midrate)).as_("fx_rate")
                )
                # Join FX code table matching currencies and ensuring SPOT rate type
                .left_join(fx_code)
                .on(
                    (fx_code.FromCurrCode == pricing.Currency)
                    & (fx_code.ToCurrCode == target_currency)
                    & (fx_code.RateTypeCode == "SPOT")
                )
                # Join FX rate table matching internal code and date
                .left_join(fx_rate)
                .on((fx_rate.ExRateIntCode == fx_code.ExRateIntCode) & (fx_rate.ExRateDate == pricing.MarketDate))
                # We filter out rows which do not have a proper fx rate (we exclude same currency conversions)
                .where((Case().when(pricing.Currency == target_currency, 1).else_(fx_rate.midrate).isnotnull()))
            )

        else:
            query = query.select(pricing.Currency.as_("currency"))

        # if market cap or shares outstanding are required we need to join with an additional table
        if MarketData.MARKET_CAPITALIZATION in values or MarketData.SHARES_OUTSTANDING in values:
            pricing_2 = pk.Table("vw_DS2Pricing", alias="pricing_2")
            num_shares = pk.Table("DS2NumShares")
            query = query.left_join(pricing_2).on(
                (pricing_2.InfoCode == pricing.InfoCode)
                & (pricing_2.ExchIntcode == pricing.ExchIntCode)
                & (pricing_2.MarketDate == pricing.MarketDate)
                & (pricing_2.AdjType == 0)
            )

            value = pricing_2.Close_
            if fx_rate and apply_fx_rate:
                value /= Case().when(pricing_2.Currency == target_currency, 1).else_(fx_rate.midrate)

            query = query.select(value.as_("undadjusted_close"))
            query = query.select(
                MSSQLQuery.from_(num_shares)
                .select(num_shares.NumShrs * 1_000)
                .where((pricing_2.InfoCode == num_shares.InfoCode) & (num_shares.EventDate <= pricing_2.MarketDate))
                .orderby(num_shares.EventDate, order=Order.desc)
                .limit(1)
                .as_("unadjusted_outstanding_shares")
            )

        for market_data in filter(
            lambda x: x not in (MarketData.SHARES_OUTSTANDING, MarketData.MARKET_CAPITALIZATION), values
        ):
            ds2_value = DS2MarketData[market_data.name].value
            value = getattr(pricing, ds2_value)
            if fx_rate and apply_fx_rate and market_data is not MarketData.SHARES_OUTSTANDING:
                value /= Case().when(pricing.Currency == target_currency, 1).else_(fx_rate.midrate)

            query = query.select(value.as_(market_data.value))

        # Add conditional where clauses
        if from_date:
            query = query.where(pricing.MarketDate >= from_date)

        if to_date:
            query = query.where(pricing.MarketDate <= to_date)

        if exact_date:
            query = query.where(pricing.MarketDate == exact_date)

        with connections["qa"].cursor() as cursor:
            with suppress(ProgrammingError):
                cursor.execute(create_mapping_table.get_sql())
                for batch in batched(
                    self.entities.values_list("dl_parameters__market_data__parameters", flat=True), 1000
                ):
                    sql = reduce(lambda x, y: x.insert(y), batch, MSSQLQuery.into(mapping)).get_sql()
                    cursor.execute(sql)

            # import sqlparse
            # print(sqlparse.format(query.get_sql(), reindent=True))

            cursor.execute(query.get_sql())

            for row in dictfetchall(cursor, MarketDataDict):
                row["instrument_id"] = lookup[row["external_identifier"]]

                if MarketData.MARKET_CAPITALIZATION in values:
                    row["market_capitalization"] = row["unadjusted_outstanding_shares"] * (
                        row["undadjusted_close"] or 0
                    )
                    del row["unadjusted_outstanding_shares"]
                    del row["undadjusted_close"]

                if MarketData.SHARES_OUTSTANDING in values:
                    row["outstanding_shares"] = (row["market_capitalization"] / row["close"]) if row["close"] else None
                row["fx_rate"] = row.get("fx_rate", 1.0)
                yield row

            cursor.execute(MSSQLQuery.drop_table(mapping).get_sql())
