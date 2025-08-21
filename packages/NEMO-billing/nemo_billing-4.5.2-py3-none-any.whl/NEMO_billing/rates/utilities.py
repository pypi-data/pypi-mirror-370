import datetime
from collections import defaultdict
from typing import Dict, Iterable, List, Optional

from NEMO_billing.exceptions import BillingException
from NEMO_billing.invoices.utilities import flatten
from NEMO_billing.rates.models import Rate, RateTime


class RateHistory:

    def __init__(self, rates: Iterable[Rate], as_of_date: datetime.date = None):
        self.as_of_date = as_of_date or datetime.date.today()
        self.rate_list = rates
        self.master_rates: Dict[Optional[RateTime], List[Rate]] = defaultdict(list)
        for rate in rates:
            self.master_rates[rate.time].append(rate)
        for rate_time, rate_list in self.master_rates.items():
            self.master_rates[rate_time] = sorted(
                rate_list, key=lambda r: r.effective_date or datetime.datetime.min.date()  # Use a fallback for None
            )

    def current_rates(self, as_of_date: datetime.date = None) -> Dict[Optional[RateTime], List[Rate]]:
        # Returns the current rates dictionary by time and sorted by ascending effective date
        # There can only be one current rate for each rate_time/type combination
        d = as_of_date or self.as_of_date
        current_rates_unique_dict = defaultdict(lambda: defaultdict())
        for rate_time, rate_list in self.master_rates.items():
            for individual_rate in rate_list:
                if individual_rate.effective_date is None or individual_rate.effective_date <= d:
                    current_rates_unique_dict[rate_time][individual_rate.natural_identifier()] = individual_rate
        current_rates_dict = defaultdict(list)
        for rate_time, rate_dict in current_rates_unique_dict.items():
            current_rates_dict[rate_time].extend(rate_dict.values())
        return current_rates_dict

    def current_rate(self, as_of_date: datetime.date = None) -> Dict[Optional[RateTime], Rate]:
        # Returns the current rate dictionary by time for only one type/category per rate_time
        # It won't work if the master_rates dict has more than one type/category per rate_time
        d = as_of_date or self.as_of_date
        current_rate_dict: Dict[Optional[RateTime], Rate] = {}
        # This only works because the master_rates dictionary is sorted by effective date (we only keep the most recent)
        # check that all rates only have one type/category/item, otherwise throw an error
        for rate_time, rate_list in self.master_rates.items():
            for individual_rate in rate_list:
                if individual_rate.effective_date is None or individual_rate.effective_date <= d:
                    if rate_time in current_rate_dict:
                        previous_rate_id = current_rate_dict[rate_time].natural_identifier()
                        new_rate_id = individual_rate.natural_identifier()
                        if previous_rate_id != new_rate_id:
                            raise BillingException(
                                f"The rates have multiple identifiers: {previous_rate_id} and {new_rate_id} and we cannot determine which one is current"
                            )
                    current_rate_dict[rate_time] = individual_rate
        return current_rate_dict

    def current_and_future_rates(self, as_of_date: datetime.date = None) -> Dict[Optional[RateTime], List[Rate]]:
        current_and_future_rates_dict = defaultdict(list)
        for rate_time, rate_list in self.current_rates(as_of_date).items():
            current_and_future_rates_dict[rate_time].extend(rate_list)
        for rate_time, rate_list in self.future_rates(as_of_date).items():
            current_and_future_rates_dict[rate_time].extend(rate_list)
        return current_and_future_rates_dict

    def future_rates(self, as_of_date: datetime.date = None) -> Dict[Optional[RateTime], List[Rate]]:
        # Returns the future rates dictionary by time and sorted by ascending effective date
        d = as_of_date or self.as_of_date
        future_rates_dict = defaultdict(list)
        for rate_time, rate_list in self.master_rates.items():
            for individual_rate in rate_list:
                if individual_rate.effective_date is not None and individual_rate.effective_date > d:
                    future_rates_dict[rate_time].append(individual_rate)
        return future_rates_dict

    def past_rates(self, as_of_date: datetime.date = None) -> Dict[Optional[RateTime], List[Rate]]:
        # Returns the past rates dictionary by time and sorted by descending effective date
        d = as_of_date or self.as_of_date
        current_rates = flatten(self.current_rates(as_of_date).values())
        past_rates_dict = defaultdict(list)
        for rate_time, rate_list in self.master_rates.items():
            for individual_rate in rate_list:
                if individual_rate not in current_rates and (
                    individual_rate.effective_date is None or individual_rate.effective_date <= d
                ):
                    past_rates_dict[rate_time].append(individual_rate)
        return past_rates_dict

    def all_rates(self) -> List[Rate]:
        return flatten(self.master_rates.values())


def get_rate_history(
    rate_type_id,
    rates: List[Rate] = None,
    category_id=None,
    tool_id=None,
    area_id=None,
    consumable_id=None,
    as_of_date: datetime.date = None,
) -> RateHistory:
    # if we are not given a list of rates, we get them from the database and filter directly
    if rates is None:
        matching_rates = Rate.non_deleted().filter(
            type_id=rate_type_id,
            category_id=category_id,
            tool_id=tool_id,
            area_id=area_id,
            consumable=consumable_id,
        )
    # otherwise we filter the given rates programmatically
    else:
        matching_rates = []
        for rate in rates:
            if rate.type_id == rate_type_id:
                category_match = not category_id or rate.category_id == category_id
                tool_match = not tool_id or rate.tool_id == tool_id
                area_match = not area_id or rate.area_id == area_id
                consumable_match = not consumable_id or rate.consumable_id == consumable_id
                if category_match and tool_match and area_match and consumable_match:
                    matching_rates.append(rate)

    return RateHistory(matching_rates, as_of_date)
