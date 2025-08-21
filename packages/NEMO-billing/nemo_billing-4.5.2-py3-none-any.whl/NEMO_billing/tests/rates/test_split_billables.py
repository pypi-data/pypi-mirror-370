import datetime
from typing import Dict, List

from NEMO_billing.invoices.models import InvoiceConfiguration

try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo

from NEMO.models import AreaAccessRecord, UsageEvent
from django.test import TestCase
from django.utils import timezone
from django.utils.timezone import make_aware

from NEMO_billing.invoices.exceptions import NoRateSetException
from NEMO_billing.invoices.processors import BillableItem, break_up_and_add, find_rates, split_records_by_day
from NEMO_billing.rates.models import DailySchedule, Rate, RateTime, RateType
from NEMO_billing.tests.test_utilities import basic_data


class TestRateTimeSplitBillables(TestCase):
    def setUp(self):
        self.config = InvoiceConfiguration.first_or_default()

    def test_split_billable_items(self):
        test_user, test_project, tool, area = basic_data()
        tz = timezone.get_current_timezone()
        rate_time = RateTime.objects.create(name="rate time")
        # Rate time MON-TUE 4PM-8PM
        DailySchedule.objects.create(
            rate_time=rate_time, start_time=datetime.time(16, 0, 0), end_time=datetime.time(20, 0, 0), weekday=0
        )
        DailySchedule.objects.create(
            rate_time=rate_time, start_time=datetime.time(16, 0, 0), end_time=datetime.time(20, 0, 0), weekday=1
        )
        tool_usage_type = RateType.objects.get(type="TOOL_USAGE")
        rate_with_time = Rate.objects.create(type=tool_usage_type, tool=tool, time=rate_time, amount=10)
        start = make_aware(datetime.datetime(year=2022, month=2, day=21, hour=17), tz)  # Mon Feb 21 2022 at 5PM
        end = make_aware(datetime.datetime(year=2022, month=2, day=25, hour=3), tz)  # Fri Feb 25 2022 at 3AM
        billable = BillableItem(
            UsageEvent(tool=tool, start=start, user=test_user, operator=test_user, end=end, project=test_project),
            test_project,
        )
        billables: List[BillableItem] = []
        # Should fail because we don't have a base rate set
        with self.assertRaises(NoRateSetException):
            find_rates(
                billable.rate_type,
                billable.project,
                self.config,
                billable.tool,
                billable.area,
                billable.consumable,
            )
        base_rate = Rate.objects.create(type=tool_usage_type, tool=tool, amount=5)
        # Now should work after we reinit the config which contains all rates
        self.config.init_rate_help()
        rates = find_rates(
            billable.rate_type, billable.project, self.config, billable.tool, billable.area, billable.consumable
        )
        break_up_and_add(billables, rates, billable.start, billable.end, billable)
        # We should have 4 chunks
        self.assertEqual(len(billables), 4)
        first = billables[0]
        second = billables[1]
        third = billables[2]
        last = billables[3]
        # First chunk: start until Monday, Feb 21 at 8PM
        self.assertEqual(first.start, start)
        self.assertEqual(first.end, make_aware(datetime.datetime(year=2022, month=2, day=21, hour=20), tz))
        self.assertEqual(first.rate, rate_with_time)
        self.assertEqual(first.project, test_project)
        # Second chunk: start Monday, Feb 21 at 8PM until Tuesday, Feb 22 4PM, base rate
        self.assertEqual(second.start, make_aware(datetime.datetime(year=2022, month=2, day=21, hour=20), tz))
        self.assertEqual(second.end, make_aware(datetime.datetime(year=2022, month=2, day=22, hour=16), tz))
        self.assertEqual(second.rate, base_rate)
        self.assertEqual(second.project, test_project)
        # Third chunk: start Tuesday, Feb 22 at 4PM until Tuesday, Feb 22 8PM
        self.assertEqual(third.start, make_aware(datetime.datetime(year=2022, month=2, day=22, hour=16), tz))
        self.assertEqual(third.end, make_aware(datetime.datetime(year=2022, month=2, day=22, hour=20), tz))
        self.assertEqual(third.rate, rate_with_time)
        self.assertEqual(third.project, test_project)
        # Last chunk: start Tuesday, Feb 22 at 8PM until end
        self.assertEqual(last.start, make_aware(datetime.datetime(year=2022, month=2, day=22, hour=20), tz))
        self.assertEqual(last.end, end)
        self.assertEqual(last.rate, base_rate)
        self.assertEqual(last.project, test_project)

    def test_split_billable_items_no_times(self):
        test_user, test_project, tool, area = basic_data()
        tz = timezone.get_current_timezone()
        rate_time = RateTime.objects.create(name="rate time")
        # Rate time MON-WED full days
        DailySchedule.objects.create(rate_time=rate_time, weekday=0)
        DailySchedule.objects.create(rate_time=rate_time, weekday=2)
        tool_usage_type = RateType.objects.get(type="TOOL_USAGE")
        rate_with_time = Rate.objects.create(type=tool_usage_type, tool=tool, time=rate_time, amount=10)
        start = make_aware(datetime.datetime(year=2022, month=2, day=21, hour=17), tz)  # Mon Feb 21 2022 at 5PM
        end = make_aware(datetime.datetime(year=2022, month=2, day=25, hour=3), tz)  # Fri Feb 25 2022 at 3AM
        billable = BillableItem(
            UsageEvent(tool=tool, start=start, user=test_user, operator=test_user, end=end, project=test_project),
            test_project,
        )
        billables: List[BillableItem] = []
        # Should fail because we don't have a base rate set
        with self.assertRaises(NoRateSetException):
            find_rates(
                billable.rate_type,
                billable.project,
                self.config,
                billable.tool,
                billable.area,
                billable.consumable,
            )
        base_rate = Rate.objects.create(type=tool_usage_type, tool=tool, amount=5)
        # Now should work after we reinit the config which contains all rates
        self.config.init_rate_help()
        rates = find_rates(
            billable.rate_type, billable.project, self.config, billable.tool, billable.area, billable.consumable
        )
        break_up_and_add(billables, rates, billable.start, billable.end, billable)
        # We should have 4 chunks
        self.assertEqual(len(billables), 4)
        first = billables[0]
        second = billables[1]
        third = billables[2]
        last = billables[3]
        # First chunk: start until Tuesday, Feb 22 at 0:00
        self.assertEqual(first.start, start)
        self.assertEqual(first.end, make_aware(datetime.datetime(year=2022, month=2, day=22, hour=0), tz))
        self.assertEqual(first.rate, rate_with_time)
        self.assertEqual(first.project, test_project)
        # Second chunk: start Tuesday, Feb 22 at 0:00 until Wednesday, Feb 23 0:00, base rate
        self.assertEqual(second.start, make_aware(datetime.datetime(year=2022, month=2, day=22, hour=0), tz))
        self.assertEqual(second.end, make_aware(datetime.datetime(year=2022, month=2, day=23, hour=0), tz))
        self.assertEqual(second.rate, base_rate)
        self.assertEqual(second.project, test_project)
        # Third chunk: start Wednesday, Feb 23 at 0:00 until Thursday, Feb 24 0:00
        self.assertEqual(third.start, make_aware(datetime.datetime(year=2022, month=2, day=23, hour=0), tz))
        self.assertEqual(third.end, make_aware(datetime.datetime(year=2022, month=2, day=24, hour=0), tz))
        self.assertEqual(third.rate, rate_with_time)
        self.assertEqual(third.project, test_project)
        # Last chunk: start Tuesday, Feb 22 at 8PM until end
        self.assertEqual(last.start, make_aware(datetime.datetime(year=2022, month=2, day=24, hour=0), tz))
        self.assertEqual(last.end, end)
        self.assertEqual(last.rate, base_rate)
        self.assertEqual(last.project, test_project)

    def test_split_billable_items_split_rate_time(self):
        test_user, test_project, tool, area = basic_data()
        tz = timezone.get_current_timezone()
        # Rate time MON-TUE 8PM-10AM
        rate_time = RateTime.objects.create(name="rate time")
        DailySchedule.objects.create(
            rate_time=rate_time, start_time=datetime.time(20, 0, 0), end_time=datetime.time(10, 0, 0), weekday=0
        )
        DailySchedule.objects.create(
            rate_time=rate_time, start_time=datetime.time(20, 0, 0), end_time=datetime.time(10, 0, 0), weekday=1
        )
        tool_usage_type = RateType.objects.get(type="TOOL_USAGE")
        rate_with_time = Rate.objects.create(type=tool_usage_type, tool=tool, time=rate_time, amount=10)
        start = make_aware(datetime.datetime(year=2022, month=2, day=22, hour=4), tz)  # Tue Feb 22 2022 at 4AM
        end = make_aware(datetime.datetime(year=2022, month=2, day=25, hour=3), tz)  # Fri Feb 25 2022 at 3AM
        billable = BillableItem(
            UsageEvent(tool=tool, start=start, user=test_user, operator=test_user, end=end, project=test_project),
            test_project,
        )
        billables: List[BillableItem] = []
        base_rate = Rate.objects.create(type=tool_usage_type, tool=tool, amount=5)
        rates = find_rates(
            billable.rate_type, billable.project, self.config, billable.tool, billable.area, billable.consumable
        )
        break_up_and_add(billables, rates, billable.start, billable.end, billable)
        # We should have 4 chunks
        self.assertEqual(len(billables), 4)
        first = billables[0]
        second = billables[1]
        third = billables[2]
        last = billables[3]
        # First chunk: start until TUE, Feb 22 at 10AM
        self.assertEqual(first.start, start)
        self.assertEqual(first.end, make_aware(datetime.datetime(year=2022, month=2, day=22, hour=10), tz))
        self.assertEqual(first.rate, rate_with_time)
        self.assertEqual(first.project, test_project)
        # Second chunk: start TUE, Feb 22 at 10AM until TUE, Feb 22 8PM, base rate
        self.assertEqual(second.start, make_aware(datetime.datetime(year=2022, month=2, day=22, hour=10), tz))
        self.assertEqual(second.end, make_aware(datetime.datetime(year=2022, month=2, day=22, hour=20), tz))
        self.assertEqual(second.rate, base_rate)
        self.assertEqual(second.project, test_project)
        # Third chunk: start TUE, Feb 22 at 8PM until WED, Feb 23 10AM
        self.assertEqual(third.start, make_aware(datetime.datetime(year=2022, month=2, day=22, hour=20), tz))
        self.assertEqual(third.end, make_aware(datetime.datetime(year=2022, month=2, day=23, hour=10), tz))
        self.assertEqual(third.rate, rate_with_time)
        self.assertEqual(third.project, test_project)
        # Last chunk: start WED, Feb 23 at 10AM until end
        self.assertEqual(last.start, make_aware(datetime.datetime(year=2022, month=2, day=23, hour=10), tz))
        self.assertEqual(last.end, end)
        self.assertEqual(last.rate, base_rate)
        self.assertEqual(last.project, test_project)

    def test_split_billable_items_split_rate_time_end(self):
        test_user, test_project, tool, area = basic_data()
        tz = timezone.get_current_timezone()
        # Rate time TUE 8PM-10AM
        rate_time = RateTime.objects.create(name="rate time")
        DailySchedule.objects.create(
            rate_time=rate_time, start_time=datetime.time(20, 0, 0), end_time=datetime.time(10, 0, 0), weekday=1
        )
        tool_usage_type = RateType.objects.get(type="TOOL_USAGE")
        rate_with_time = Rate.objects.create(type=tool_usage_type, tool=tool, time=rate_time, amount=10)
        start = make_aware(datetime.datetime(year=2022, month=2, day=22, hour=4), tz)  # TUE Feb 22 2022 at 4AM
        end = make_aware(datetime.datetime(year=2022, month=2, day=22, hour=21), tz)  # TUE Feb 22 2022 at 9PM
        billable = BillableItem(
            UsageEvent(tool=tool, start=start, user=test_user, operator=test_user, end=end, project=test_project),
            test_project,
        )
        billables: List[BillableItem] = []
        base_rate = Rate.objects.create(type=tool_usage_type, tool=tool, amount=5)
        rates = find_rates(
            billable.rate_type, billable.project, self.config, billable.tool, billable.area, billable.consumable
        )
        break_up_and_add(billables, rates, billable.start, billable.end, billable)
        # We should have 2 chunks
        self.assertEqual(len(billables), 2)
        first = billables[0]
        last = billables[1]
        # First chunk: start until TUE, Feb 22 at 8PM
        self.assertEqual(first.start, start)
        self.assertEqual(first.end, make_aware(datetime.datetime(year=2022, month=2, day=22, hour=20), tz))
        self.assertEqual(first.rate, base_rate)
        self.assertEqual(first.project, test_project)
        # Last chunk: start TUE, Feb 22 at 8PM until end
        self.assertEqual(last.start, make_aware(datetime.datetime(year=2022, month=2, day=22, hour=20), tz))
        self.assertEqual(last.end, end)
        self.assertEqual(last.rate, rate_with_time)
        self.assertEqual(last.project, test_project)

    def test_split_billable_items_no_overlap(self):
        test_user, test_project, tool, area = basic_data()
        tz = timezone.get_current_timezone()
        # Rate time MON 8PM-10AM
        rate_time = RateTime.objects.create(name="rate time")
        DailySchedule.objects.create(
            rate_time=rate_time, start_time=datetime.time(20, 0, 0), end_time=datetime.time(10, 0, 0), weekday=0
        )
        tool_usage_type = RateType.objects.get(type="TOOL_USAGE")
        rate_with_time = Rate.objects.create(type=tool_usage_type, tool=tool, time=rate_time, amount=10)
        start = make_aware(datetime.datetime(year=2022, month=2, day=22, hour=13), tz)  # Tue Feb 22 2022 at 1PM
        end = make_aware(datetime.datetime(year=2022, month=2, day=22, hour=15), tz)  # Tue Feb 22 2022 at 3PM
        billable = BillableItem(
            UsageEvent(tool=tool, start=start, user=test_user, operator=test_user, end=end, project=test_project),
            test_project,
        )
        billables: List[BillableItem] = []
        base_rate = Rate.objects.create(type=tool_usage_type, tool=tool, amount=5)
        rates = find_rates(
            billable.rate_type, billable.project, self.config, billable.tool, billable.area, billable.consumable
        )
        break_up_and_add(billables, rates, billable.start, billable.end, billable)
        # We should have 1 chunk
        self.assertEqual(len(billables), 1)
        first = billables[0]
        # First and only chunk: start until end
        self.assertEqual(first.start, start)
        self.assertEqual(first.end, end)
        self.assertEqual(first.rate, base_rate)
        self.assertEqual(first.project, test_project)

    def test_split_billable_items_dst_forward(self):
        test_user, test_project, tool, area = basic_data()
        # Test with DST (EST = March 13 2AM -> 3AM)
        tz = zoneinfo.ZoneInfo("America/New_York")
        # Rate time SAT 8PM-2AM
        rate_time = RateTime.objects.create(name="rate time")
        DailySchedule.objects.create(
            rate_time=rate_time, start_time=datetime.time(20, 0, 0), end_time=datetime.time(2, 0, 0), weekday=5
        )
        tool_usage_type = RateType.objects.get(type="TOOL_USAGE")
        rate_with_time = Rate.objects.create(type=tool_usage_type, tool=tool, time=rate_time, amount=10)
        start = make_aware(datetime.datetime(year=2022, month=3, day=13, hour=1), tz)  # Sun Mar 13 2022 at 1AM
        end = make_aware(datetime.datetime(year=2022, month=3, day=13, hour=3), tz)  # Sun Mar 13 2022 at 3AM
        billable = BillableItem(
            UsageEvent(tool=tool, start=start, user=test_user, operator=test_user, end=end, project=test_project),
            test_project,
        )
        billables: List[BillableItem] = []
        base_rate = Rate.objects.create(type=tool_usage_type, tool=tool, amount=5)
        rates = find_rates(
            billable.rate_type, billable.project, self.config, billable.tool, billable.area, billable.consumable
        )
        break_up_and_add(billables, rates, billable.start, billable.end, billable)
        # We should have 1 chunk
        self.assertEqual(len(billables), 1)
        first = billables[0]
        # First chunk: start until end, but it should be 1 hours, not 2
        self.assertEqual(first.start, start)
        self.assertEqual(first.end, end)
        self.assertEqual(first.rate, rate_with_time)
        self.assertEqual(first.project, test_project)
        self.assertNotEqual(first.quantity, 2 * 60.0)
        self.assertEqual(first.quantity, 1 * 60.0)

    def test_split_billable_items_dst_backwards(self):
        test_user, test_project, tool, area = basic_data()
        # Test with DST (EST = NOV 6 2AM -> 1AM)
        tz = zoneinfo.ZoneInfo("America/New_York")
        # Rate time SAT 8PM-2AM
        rate_time = RateTime.objects.create(name="rate time")
        DailySchedule.objects.create(
            rate_time=rate_time, start_time=datetime.time(20, 0, 0), end_time=datetime.time(2, 0, 0), weekday=5
        )
        tool_usage_type = RateType.objects.get(type="TOOL_USAGE")
        rate_with_time = Rate.objects.create(type=tool_usage_type, tool=tool, time=rate_time, amount=10)
        start = make_aware(datetime.datetime(year=2022, month=11, day=6, hour=0), tz)  # Sun NOV 6 2022 at 12AM
        end = make_aware(datetime.datetime(year=2022, month=11, day=6, hour=2), tz)  # Sun NOV 6 2022 at 2AM (new 2AM)
        billable = BillableItem(
            UsageEvent(tool=tool, start=start, user=test_user, operator=test_user, end=end, project=test_project),
            test_project,
        )
        billables: List[BillableItem] = []
        base_rate = Rate.objects.create(type=tool_usage_type, tool=tool, amount=5)
        rates = find_rates(
            billable.rate_type, billable.project, self.config, billable.tool, billable.area, billable.consumable
        )
        break_up_and_add(billables, rates, billable.start, billable.end, billable)
        # We should have 2 chunks
        self.assertEqual(len(billables), 2)
        first = billables[0]
        last = billables[1]
        # First chunk: start until 2AM old (1AM new), but it should be 2 hours, not 1
        self.assertEqual(first.start, start)
        self.assertEqual(
            first.end, make_aware(datetime.datetime(year=2022, month=11, day=6, hour=6), datetime.timezone.utc)
        )
        self.assertEqual(first.rate, rate_with_time)
        self.assertEqual(first.project, test_project)
        self.assertEqual(first.quantity, 2 * 60.0)
        self.assertNotEqual(first.quantity, 1 * 60.0)
        # Last chunk: from 2AM old (1AM new) until end but it should be 1 hour, not 0
        # Both chunk will not have the rate time, second part will have the regular rate
        self.assertEqual(
            last.start, make_aware(datetime.datetime(year=2022, month=11, day=6, hour=6), datetime.timezone.utc)
        )
        self.assertEqual(last.end, end)
        self.assertEqual(last.rate, base_rate)
        self.assertEqual(last.project, test_project)
        self.assertEqual(last.quantity, 1 * 60.0)
        self.assertNotEqual(last.quantity, 0 * 60.0)

        start_2 = make_aware(datetime.datetime(year=2022, month=11, day=6, hour=0), tz)  # Sun NOV 6 2022 at 12AM
        end_2 = make_aware(datetime.datetime(year=2022, month=11, day=6, hour=4), tz)  # Sun NOV 6 2022 at 4AM (new 4AM)
        billable_2 = BillableItem(
            UsageEvent(tool=tool, start=start_2, user=test_user, operator=test_user, end=end_2, project=test_project),
            test_project,
        )
        billables_2: List[BillableItem] = []
        break_up_and_add(billables_2, rates, billable_2.start, billable_2.end, billable_2)
        # We should have only 2 chunks again (second part is using base rate)
        self.assertEqual(len(billables_2), 2)
        last_one = billables_2[1]
        # First chunk same as before
        # Last chunk: 1AM until 4AM
        self.assertEqual(
            last_one.start, make_aware(datetime.datetime(year=2022, month=11, day=6, hour=6), datetime.timezone.utc)
        )
        self.assertEqual(last_one.end, end_2)
        self.assertEqual(last_one.rate, base_rate)
        self.assertEqual(last_one.project, test_project)
        self.assertEqual(last_one.quantity, 3 * 60.0)

    def test_split_billable_items_complete_overlap(self):
        test_user, test_project, tool, area = basic_data()
        tz = timezone.get_current_timezone()
        # Rate time MON 8PM-10AM
        rate_time = RateTime.objects.create(name="rate time")
        DailySchedule.objects.create(
            rate_time=rate_time, start_time=datetime.time(20, 0, 0), end_time=datetime.time(10, 0, 0), weekday=0
        )
        tool_usage_type = RateType.objects.get(type="TOOL_USAGE")
        rate_with_time = Rate.objects.create(type=tool_usage_type, tool=tool, time=rate_time, amount=10)
        start = make_aware(datetime.datetime(year=2022, month=2, day=22, hour=4), tz)  # Tue Feb 22 2022 at 4AM
        end = make_aware(datetime.datetime(year=2022, month=2, day=22, hour=5), tz)  # Tue Feb 22 2022 at 5AM
        billable = BillableItem(
            UsageEvent(tool=tool, start=start, user=test_user, operator=test_user, end=end, project=test_project),
            test_project,
        )
        billables: List[BillableItem] = []
        base_rate = Rate.objects.create(type=tool_usage_type, tool=tool, amount=5)
        rates = find_rates(
            billable.rate_type, billable.project, self.config, billable.tool, billable.area, billable.consumable
        )
        break_up_and_add(billables, rates, billable.start, billable.end, billable)
        # We should have 1 chunk
        self.assertEqual(len(billables), 1)
        first = billables[0]
        # First and only chunk: start until TUE, Feb 22 at 5AM
        self.assertEqual(first.start, start)
        self.assertEqual(first.end, make_aware(datetime.datetime(year=2022, month=2, day=22, hour=5), tz))
        self.assertEqual(first.rate, rate_with_time)
        self.assertEqual(first.project, test_project)

    def test_split_billable_items_max_time_in_between(self):
        test_user, test_project, tool, area = basic_data()
        tz = timezone.get_current_timezone()
        # Rate time MON 8PM-10AM
        rate_time = RateTime.objects.create(name="rate time")
        DailySchedule.objects.create(
            rate_time=rate_time, start_time=datetime.time(20, 0, 0), end_time=datetime.time(10, 0, 0), weekday=0
        )
        tool_usage_type = RateType.objects.get(type="TOOL_USAGE")
        rate_with_time = Rate.objects.create(type=tool_usage_type, tool=tool, time=rate_time, amount=10)
        start = make_aware(datetime.datetime(year=2022, month=2, day=22, hour=11), tz)  # TUE Feb 22 2022 at 11AM
        end = make_aware(datetime.datetime(year=2022, month=3, day=1, hour=16), tz)  # TUE Mar 1 2022 at 4PM
        billable = BillableItem(
            UsageEvent(tool=tool, start=start, user=test_user, operator=test_user, end=end, project=test_project),
            test_project,
        )
        billables: List[BillableItem] = []
        base_rate = Rate.objects.create(type=tool_usage_type, tool=tool, amount=5)
        rates = find_rates(
            billable.rate_type, billable.project, self.config, billable.tool, billable.area, billable.consumable
        )
        break_up_and_add(billables, rates, billable.start, billable.end, billable)
        # We should have 3 chunks
        self.assertEqual(len(billables), 3)
        first = billables[0]
        second = billables[1]
        last = billables[2]
        # First chunk: start until MON, Feb 28 at 8PM
        self.assertEqual(first.start, start)
        self.assertEqual(first.end, make_aware(datetime.datetime(year=2022, month=2, day=28, hour=20), tz))
        self.assertEqual(first.rate, base_rate)
        self.assertEqual(first.project, test_project)
        # Second chunk: MON, Feb 28 at 8PM to TUE, Feb 29 at 10AM
        self.assertEqual(second.start, make_aware(datetime.datetime(year=2022, month=2, day=28, hour=20), tz))
        self.assertEqual(second.end, make_aware(datetime.datetime(year=2022, month=3, day=1, hour=10), tz))
        self.assertEqual(second.rate, rate_with_time)
        self.assertEqual(second.project, test_project)
        # last chunk: TUE, Feb 29 at 10AM until end
        self.assertEqual(last.start, make_aware(datetime.datetime(year=2022, month=3, day=1, hour=10), tz))
        self.assertEqual(last.end, end)
        self.assertEqual(last.rate, base_rate)
        self.assertEqual(last.project, test_project)

    def test_split_billable_items_multiple_rate_times(self):
        test_user, test_project, tool, area = basic_data()
        tz = timezone.get_current_timezone()
        tool_usage_type = RateType.objects.get(type="TOOL_USAGE")
        # Rate time MON 8PM-10AM
        rate_time = RateTime.objects.create(name="rate time")
        DailySchedule.objects.create(
            rate_time=rate_time, start_time=datetime.time(20, 0, 0), end_time=datetime.time(10, 0, 0), weekday=0
        )
        rate_with_time = Rate.objects.create(type=tool_usage_type, tool=tool, time=rate_time, amount=10)
        # Rate time WED 10PM-11PM
        rate_time_2 = RateTime.objects.create(name="rate time 2")
        DailySchedule.objects.create(
            rate_time=rate_time_2, start_time=datetime.time(22, 0, 0), end_time=datetime.time(23, 0, 0), weekday=2
        )
        rate_with_time_2 = Rate.objects.create(type=tool_usage_type, tool=tool, time=rate_time_2, amount=25)
        start = make_aware(datetime.datetime(year=2022, month=2, day=22, hour=11), tz)  # TUE Feb 22 2022 at 11AM
        end = make_aware(datetime.datetime(year=2022, month=3, day=1, hour=16), tz)  # TUE Mar 1 2022 at 4PM
        billable = BillableItem(
            UsageEvent(tool=tool, start=start, user=test_user, operator=test_user, end=end, project=test_project),
            test_project,
        )
        billables: List[BillableItem] = []
        base_rate = Rate.objects.create(type=tool_usage_type, tool=tool, amount=5)
        rates = find_rates(
            billable.rate_type, billable.project, self.config, billable.tool, billable.area, billable.consumable
        )
        break_up_and_add(billables, rates, billable.start, billable.end, billable)
        # We should have 5 chunks
        self.assertEqual(len(billables), 5)
        first = billables[0]
        second = billables[1]
        third = billables[2]
        fourth = billables[3]
        last = billables[4]
        # First chunk: start until WED, Feb 23 at 10PM
        self.assertEqual(first.start, start)
        self.assertEqual(first.end, make_aware(datetime.datetime(year=2022, month=2, day=23, hour=22), tz))
        self.assertEqual(first.rate, base_rate)
        self.assertEqual(first.project, test_project)
        # Second chunk:  WED, Feb 23 at 10PM until WED, Feb 23 at 11PM
        self.assertEqual(second.start, make_aware(datetime.datetime(year=2022, month=2, day=23, hour=22), tz))
        self.assertEqual(second.end, make_aware(datetime.datetime(year=2022, month=2, day=23, hour=23), tz))
        self.assertEqual(second.rate, rate_with_time_2)
        self.assertEqual(second.project, test_project)
        # Third chunk: WED, Feb 23 at 11PM until MON, Feb 28 at 8PM
        self.assertEqual(third.start, make_aware(datetime.datetime(year=2022, month=2, day=23, hour=23), tz))
        self.assertEqual(third.end, make_aware(datetime.datetime(year=2022, month=2, day=28, hour=20), tz))
        self.assertEqual(third.rate, base_rate)
        self.assertEqual(third.project, test_project)
        # Fourth chunk: MON, Feb 28 at 8PM to TUE, Feb 29 at 10AM
        self.assertEqual(fourth.start, make_aware(datetime.datetime(year=2022, month=2, day=28, hour=20), tz))
        self.assertEqual(fourth.end, make_aware(datetime.datetime(year=2022, month=3, day=1, hour=10), tz))
        self.assertEqual(fourth.rate, rate_with_time)
        self.assertEqual(fourth.project, test_project)
        # last chunk: TUE, Feb 29 at 10AM until end
        self.assertEqual(last.start, make_aware(datetime.datetime(year=2022, month=3, day=1, hour=10), tz))
        self.assertEqual(last.end, end)
        self.assertEqual(last.rate, base_rate)
        self.assertEqual(last.project, test_project)

    def test_split_area_access_records(self):
        test_user, test_project, tool, area = basic_data()
        now = make_aware(datetime.datetime.now())
        record = AreaAccessRecord.objects.create(
            customer=test_user,
            project=test_project,
            area=area,
            start=now - datetime.timedelta(minutes=1),
            end=now,
        )
        # Should be unchanged
        self.assertEqual([record], split_records_by_day(record))
        # Now let's add one overnight
        record = AreaAccessRecord.objects.create(
            customer=test_user,
            project=test_project,
            area=area,
            start=now - datetime.timedelta(hours=23, minutes=59),
            end=now,
        )
        new_records = split_records_by_day(record)
        midnight_today = now.astimezone().replace(hour=0, minute=0, second=0, microsecond=0)
        self.assertEqual(2, len(new_records))
        self.assertEqual(new_records[0].area, record.area)
        self.assertEqual(new_records[0].customer, record.customer)
        self.assertEqual(new_records[0].project, record.project)
        self.assertEqual(new_records[0].start, record.start)
        self.assertEqual(new_records[0].end, midnight_today)
        self.assertEqual(new_records[1].area, record.area)
        self.assertEqual(new_records[1].customer, record.customer)
        self.assertEqual(new_records[1].project, record.project)
        self.assertEqual(new_records[1].start, midnight_today)
        self.assertEqual(new_records[1].end, record.end)
        # Have it span across more than one day
        record_start = now - datetime.timedelta(days=7)
        record = AreaAccessRecord.objects.create(
            customer=test_user,
            project=test_project,
            area=area,
            start=record_start,
            end=now,
        )
        # request them now, should have 8
        new_records = split_records_by_day(record)
        self.assertEqual(8, len(new_records))
        self.assertEqual(new_records[0].start, record.start)
        self.assertEqual(new_records[7].end, record.end)


def get_area_dict(area_access_record) -> Dict:
    return {key: value for key, value in area_access_record.__dict__.items() if key != "_state"}
