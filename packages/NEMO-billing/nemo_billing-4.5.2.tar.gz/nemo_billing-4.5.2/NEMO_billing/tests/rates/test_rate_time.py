import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from django.utils.timezone import make_aware

from NEMO_billing.rates.models import DailySchedule, RateTime


class RateTimeTestCase(TestCase):
    def test_duration(self):
        split = DailySchedule(start_time=datetime.time(20, 0, 0), end_time=datetime.time(4, 0, 0), weekday=0)
        non_split = DailySchedule(start_time=datetime.time(16, 0, 0), end_time=datetime.time(20, 0, 0), weekday=1)
        full_day = DailySchedule(weekday=1)
        full_day_time = DailySchedule(start_time=datetime.time(6, 0, 0), end_time=datetime.time(6, 0, 0), weekday=1)
        no_start_time = DailySchedule(end_time=datetime.time(6, 0, 0), weekday=1)
        no_end_time = DailySchedule(start_time=datetime.time(6, 0, 0), weekday=1)
        self.assertEqual(split.duration().total_seconds(), 8 * 3600)
        self.assertEqual(non_split.duration().total_seconds(), 4 * 3600)
        self.assertEqual(full_day.duration().total_seconds(), 24 * 3600)
        self.assertEqual(full_day_time.duration().total_seconds(), 24 * 3600)
        self.assertEqual(no_start_time.duration().total_seconds(), 6 * 3600)
        self.assertEqual(no_end_time.duration().total_seconds(), 18 * 3600)

    def test_split_time(self):
        # 4PM - 4PM => split
        d_1 = DailySchedule(weekday=0, start_time=datetime.time(16, 0, 0), end_time=datetime.time(16, 0, 0))
        self.assertTrue(d_1.is_time_range_split())
        # 4PM - 4AM => split
        d_2 = DailySchedule(weekday=0, start_time=datetime.time(16, 0, 0), end_time=datetime.time(4, 0, 0))
        self.assertTrue(d_2.is_time_range_split())
        # 12AM - 12AM => not split
        d_3 = DailySchedule(weekday=0)
        self.assertFalse(d_3.is_time_range_split())
        # 12AM - 4PM => not split
        d_4 = DailySchedule(weekday=0, end_time=datetime.time(16, 0, 0))
        self.assertFalse(d_4.is_time_range_split())
        # 4PM - 12AM => not split
        d_5 = DailySchedule(weekday=0, start_time=datetime.time(16, 0, 0))
        self.assertFalse(d_5.is_time_range_split())
        # 4AM - 4PM => not split
        d_6 = DailySchedule(weekday=0, start_time=datetime.time(4, 0, 0), end_time=datetime.time(16, 0, 0))
        self.assertFalse(d_6.is_time_range_split())

    def test_earliest_match(self):
        tz = timezone.get_current_timezone()
        start_time_1 = make_aware(datetime.datetime(year=2022, month=2, day=20, hour=17), tz)  # Sun Feb 20 2022 at 5PM
        end_time_1 = make_aware(datetime.datetime(year=2022, month=2, day=23, hour=17), tz)  # Wed Feb 23 2022 at 5PM
        rate_time_1 = RateTime.objects.create(name="rate time 1")
        DailySchedule.objects.create(
            rate_time=rate_time_1, start_time=datetime.time(16, 0, 0), end_time=datetime.time(20, 0, 0), weekday=0
        )
        DailySchedule.objects.create(
            rate_time=rate_time_1, start_time=datetime.time(20, 0, 0), end_time=datetime.time(0, 0, 0), weekday=0
        )
        start_result_1 = make_aware(datetime.datetime(year=2022, month=2, day=21, hour=16), tz)  # Mon Feb 21 at 4PM
        end_result_1 = make_aware(datetime.datetime(year=2022, month=2, day=21, hour=20), tz)  # Mon Feb 21 at 8PM
        first_start_1, first_end_1 = rate_time_1.earliest_match(start_time_1, end_time_1)
        self.assertEqual(first_start_1, start_result_1)
        self.assertEqual(first_end_1, end_result_1)

        start_time_2 = datetime.datetime(year=2022, month=2, day=22, hour=17)  # Tue Feb 22 2022 at 5PM
        end_time_2 = datetime.datetime(year=2022, month=2, day=23, hour=17)  # Wed Feb 23 2022 at 5PM
        # no match
        first_start_2, first_end_2 = rate_time_1.earliest_match(start_time_2, end_time_2)
        self.assertIsNone(first_start_2)
        self.assertIsNone(first_end_2)

        # Should work without timezone too (it will assume it's the local)
        start_time_3 = datetime.datetime(year=2022, month=2, day=22, hour=17)  # Tue Feb 22 2022 at 5PM
        end_time_3 = datetime.datetime(year=2022, month=2, day=28, hour=22)  # Mon Feb 28 2022 at 10PM
        start_result_3 = datetime.datetime(year=2022, month=2, day=28, hour=16)  # Mon Feb 28 at 4PM
        end_result_3 = datetime.datetime(year=2022, month=2, day=28, hour=20)  # Mon Feb 28 at 8PM
        first_start_3, first_end_3 = rate_time_1.earliest_match(start_time_3, end_time_3)
        self.assertEqual(first_start_3, start_result_3.replace(tzinfo=tz))
        self.assertEqual(first_end_3, end_result_3.replace(tzinfo=tz))

        start_time_4 = make_aware(datetime.datetime(year=2022, month=2, day=21, hour=17), tz)  # Mon Feb 21 2022 at 5PM
        end_time_4 = make_aware(datetime.datetime(year=2022, month=2, day=28, hour=22), tz)  # Mon Feb 28 2022 at 10PM
        start_result_4 = make_aware(datetime.datetime(year=2022, month=2, day=21, hour=17), tz)  # Mon Feb 21 at 5PM
        end_result_4 = make_aware(datetime.datetime(year=2022, month=2, day=21, hour=20), tz)  # Mon Feb 21 at 8PM
        first_start_4, first_end_4 = rate_time_1.earliest_match(start_time_4, end_time_4)
        self.assertEqual(first_start_4, start_result_4.replace(tzinfo=tz))
        self.assertEqual(first_end_4, end_result_4.replace(tzinfo=tz))

    def test_rate_times_split_previous_day(self):
        # Original: Monday 8PM-4AM (split time)
        rate_time = RateTime.objects.create(name="original split")
        DailySchedule.objects.create(
            rate_time=rate_time, start_time=datetime.time(20, 0, 0), end_time=datetime.time(4, 0, 0), weekday=0
        )
        # Sunday 11PM-9PM should overlap (previous day split, stops after start)
        rate_time_1 = RateTime.objects.create(name="previous split 1")
        # We cannot have split Sunday
        with self.assertRaises(ValidationError) as cm:
            DailySchedule(
                rate_time=rate_time_1, start_time=datetime.time(23, 0, 0), end_time=datetime.time(21, 0, 0), weekday=6
            ).full_clean()
        # We cannot have split Sunday
        with self.assertRaises(ValidationError) as cm:
            DailySchedule(
                rate_time=rate_time_1, start_time=datetime.time(23, 0, 0), end_time=datetime.time(23, 0, 0), weekday=6
            ).full_clean()
        # Create it in 2 steps
        DailySchedule.objects.create(
            rate_time=rate_time_1, start_time=datetime.time(23, 0, 0), end_time=datetime.time(0, 0, 0), weekday=6
        )
        DailySchedule.objects.create(
            rate_time=rate_time_1, start_time=datetime.time(0, 0, 0), end_time=datetime.time(21, 0, 0), weekday=0
        )
        self.assertTrue(rate_time.overlaps(rate_time_1))

        # Sunday 11PM-5PM should NOT overlap (previous day split, stops before start)
        rate_time_2 = RateTime.objects.create(name="previous split 2")
        DailySchedule.objects.create(
            rate_time=rate_time_2, start_time=datetime.time(23, 0, 0), end_time=datetime.time(0, 0, 0), weekday=6
        )
        DailySchedule.objects.create(
            rate_time=rate_time_2, start_time=datetime.time(0, 0, 0), end_time=datetime.time(17, 0, 0), weekday=0
        )
        self.assertFalse(rate_time.overlaps(rate_time_2))

        # Sunday 5PM-11PM should NOT overlap (previous day not split)
        rate_time_3 = RateTime.objects.create(name="previous not split 3")
        DailySchedule.objects.create(
            rate_time=rate_time_3, start_time=datetime.time(17, 0, 0), end_time=datetime.time(23, 0, 0), weekday=6
        )
        self.assertFalse(rate_time.overlaps(rate_time_3))

    def test_rate_times_split_same_day(self):
        # Original: Monday 8PM-4AM (split time)
        rate_time = RateTime.objects.create(name="original split")
        DailySchedule.objects.create(
            rate_time=rate_time, start_time=datetime.time(20, 0, 0), end_time=datetime.time(4, 0, 0), weekday=0
        )
        # Monday 10PM-11PM should overlap (not split, begins later than start)
        rate_time_1 = RateTime.objects.create(name="split 1")
        DailySchedule.objects.create(
            rate_time=rate_time_1, start_time=datetime.time(22, 0, 0), end_time=datetime.time(23, 0, 0), weekday=0
        )
        self.assertTrue(rate_time.overlaps(rate_time_1))
        # Monday 5PM-5AM should overlap (split, begins before start and stops after end)
        rate_time_2 = RateTime.objects.create(name="split 2")
        DailySchedule.objects.create(
            rate_time=rate_time_2, start_time=datetime.time(17, 0, 0), end_time=datetime.time(5, 0, 0), weekday=0
        )
        self.assertTrue(rate_time.overlaps(rate_time_2))
        # Monday 5PM-2AM should overlap (split, begins before start and stops before end)
        rate_time_3 = RateTime.objects.create(name="split 3")
        DailySchedule.objects.create(
            rate_time=rate_time_3, start_time=datetime.time(17, 0, 0), end_time=datetime.time(2, 0, 0), weekday=0
        )
        self.assertTrue(rate_time.overlaps(rate_time_3))
        # Monday 10PM-2AM should overlap (split, begins after start and stops before end)
        rate_time_4 = RateTime.objects.create(name="split 4")
        DailySchedule.objects.create(
            rate_time=rate_time_4, start_time=datetime.time(22, 0, 0), end_time=datetime.time(2, 0, 0), weekday=0
        )
        self.assertTrue(rate_time.overlaps(rate_time_4))
        # Monday 10PM-5AM should overlap (split begins after start and stops after end)
        rate_time_5 = RateTime.objects.create(name="split 5")
        DailySchedule.objects.create(
            rate_time=rate_time_5, start_time=datetime.time(22, 0, 0), end_time=datetime.time(5, 0, 0), weekday=0
        )
        self.assertTrue(rate_time.overlaps(rate_time_5))
        # Monday 1AM-3AM should NOT overlap (not split, begins before start and ends before start)
        rate_time_6 = RateTime.objects.create(name="same 1")
        DailySchedule.objects.create(
            rate_time=rate_time_6, start_time=datetime.time(1, 0, 0), end_time=datetime.time(3, 0, 0), weekday=0
        )
        self.assertFalse(rate_time.overlaps(rate_time_6))
        # Monday 1AM-5PM should NOT overlap (not split, begins before start and ends before start)
        rate_time_7 = RateTime.objects.create(name="same 2")
        DailySchedule.objects.create(
            rate_time=rate_time_7, start_time=datetime.time(1, 0, 0), end_time=datetime.time(5, 0, 0), weekday=0
        )
        self.assertFalse(rate_time.overlaps(rate_time_7))
        # Monday 4PM-5PM should NOT overlap (not split, begins before start and ends before start)
        rate_time_8 = RateTime.objects.create(name="same 3")
        DailySchedule.objects.create(
            rate_time=rate_time_8, start_time=datetime.time(16, 0, 0), end_time=datetime.time(17, 0, 0), weekday=0
        )
        self.assertFalse(rate_time.overlaps(rate_time_8))

    def test_rate_times_split_next_day(self):
        # Original: Monday 8PM-4AM (split time)
        rate_time = RateTime.objects.create(name="original split")
        DailySchedule.objects.create(
            rate_time=rate_time, start_time=datetime.time(20, 0, 0), end_time=datetime.time(4, 0, 0), weekday=0
        )
        # Tuesday 1-5AM should overlap (next day, begins before end)
        rate_time_1 = RateTime.objects.create(name="next 1")
        DailySchedule.objects.create(
            rate_time=rate_time_1, start_time=datetime.time(1, 0, 0), end_time=datetime.time(5, 0, 0), weekday=1
        )
        self.assertTrue(rate_time.overlaps(rate_time_1))
        # Tuesday 1-2AM should overlap (next day, begins & stops before end)
        rate_time_2 = RateTime.objects.create(name="next 2")
        DailySchedule.objects.create(
            rate_time=rate_time_2, start_time=datetime.time(1, 0, 0), end_time=datetime.time(2, 0, 0), weekday=1
        )
        self.assertTrue(rate_time.overlaps(rate_time_2))
        # Tuesday 5-8PM should NOT overlap (next day split, stops before start)
        rate_time_3 = RateTime.objects.create(name="next 3")
        DailySchedule.objects.create(
            rate_time=rate_time_3, start_time=datetime.time(17, 0, 0), end_time=datetime.time(20, 0, 0), weekday=1
        )
        self.assertFalse(rate_time.overlaps(rate_time_3))
        # Tuesday 11PM-5PM should NOT overlap (next day not split)
        rate_time_4 = RateTime.objects.create(name="next split")
        DailySchedule.objects.create(
            rate_time=rate_time_4, start_time=datetime.time(23, 0, 0), end_time=datetime.time(17, 0, 0), weekday=1
        )
        self.assertFalse(rate_time.overlaps(rate_time_4))

    def test_rate_times_previous_day(self):
        # Original: monday 4PM-8PM
        rate_time = RateTime.objects.create(name="original")
        DailySchedule.objects.create(
            rate_time=rate_time, start_time=datetime.time(16, 0, 0), end_time=datetime.time(20, 0, 0), weekday=0
        )
        # Sunday 11PM-9PM should overlap (previous day split, stops after start)
        rate_time_1 = RateTime.objects.create(name="previous split 1")
        DailySchedule.objects.create(
            rate_time=rate_time_1, start_time=datetime.time(23, 0, 0), end_time=datetime.time(0, 0, 0), weekday=6
        )
        DailySchedule.objects.create(
            rate_time=rate_time_1, start_time=datetime.time(0, 0, 0), end_time=datetime.time(21, 0, 0), weekday=0
        )
        self.assertTrue(rate_time.overlaps(rate_time_1))
        # Sunday 11PM-2PM should NOT overlap (previous day split, stops before start)
        rate_time_2 = RateTime.objects.create(name="previous split 2")
        DailySchedule.objects.create(
            rate_time=rate_time_2, start_time=datetime.time(23, 0, 0), end_time=datetime.time(0, 0, 0), weekday=6
        )
        DailySchedule.objects.create(
            rate_time=rate_time_2, start_time=datetime.time(0, 0, 0), end_time=datetime.time(14, 0, 0), weekday=0
        )
        self.assertFalse(rate_time.overlaps(rate_time_2))

    def test_rate_times_same_day(self):
        # Original: Monday 4PM-8PM
        rate_time = RateTime.objects.create(name="original")
        DailySchedule.objects.create(
            rate_time=rate_time, start_time=datetime.time(16, 0, 0), end_time=datetime.time(20, 0, 0), weekday=0
        )
        # Monday 6AM-2PM should NOT overlap (not split, stops before start)
        rate_time_1 = RateTime.objects.create(name="same 1")
        DailySchedule.objects.create(
            rate_time=rate_time_1, start_time=datetime.time(6, 0, 0), end_time=datetime.time(14, 0, 0), weekday=0
        )
        self.assertFalse(rate_time.overlaps(rate_time_1))
        # Monday 9PM-11PM should NOT overlap (not split, begins after end)
        rate_time_2 = RateTime.objects.create(name="same 2")
        DailySchedule.objects.create(
            rate_time=rate_time_2, start_time=datetime.time(21, 0, 0), end_time=datetime.time(23, 0, 0), weekday=0
        )
        self.assertFalse(rate_time.overlaps(rate_time_2))
        # Monday 6AM-11PM should overlap (not split, begins before start and stops after end)
        rate_time_3 = RateTime.objects.create(name="same 3")
        DailySchedule.objects.create(
            rate_time=rate_time_3, start_time=datetime.time(6, 0, 0), end_time=datetime.time(23, 0, 0), weekday=0
        )
        self.assertTrue(rate_time.overlaps(rate_time_3))
        # Monday 5PM-6PM should overlap (not split, begins after start and stops before end)
        rate_time_4 = RateTime.objects.create(name="same 4")
        DailySchedule.objects.create(
            rate_time=rate_time_4, start_time=datetime.time(17, 0, 0), end_time=datetime.time(18, 0, 0), weekday=0
        )
        self.assertTrue(rate_time.overlaps(rate_time_4))
        # Monday 6AM-6PM should overlap (not split, begins before start and stops before end)
        rate_time_5 = RateTime.objects.create(name="same 5")
        DailySchedule.objects.create(
            rate_time=rate_time_5, start_time=datetime.time(6, 0, 0), end_time=datetime.time(18, 0, 0), weekday=0
        )
        self.assertTrue(rate_time.overlaps(rate_time_5))
        # Monday 6PM-11PM should overlap (not split, begins before end and stops after end)
        rate_time_6 = RateTime.objects.create(name="same 6")
        DailySchedule.objects.create(
            rate_time=rate_time_6, start_time=datetime.time(6, 0, 0), end_time=datetime.time(23, 0, 0), weekday=0
        )
        self.assertTrue(rate_time.overlaps(rate_time_6))
        # Monday 2PM-2AM should overlap (split, begins before start and stops after end)
        rate_time_7 = RateTime.objects.create(name="split 1")
        DailySchedule.objects.create(
            rate_time=rate_time_7, start_time=datetime.time(18, 0, 0), end_time=datetime.time(2, 0, 0), weekday=0
        )
        self.assertTrue(rate_time.overlaps(rate_time_7))
        # Monday 6PM-2AM should overlap (split, begins before end and stops after end)
        rate_time_8 = RateTime.objects.create(name="split 2")
        DailySchedule.objects.create(
            rate_time=rate_time_8, start_time=datetime.time(14, 0, 0), end_time=datetime.time(2, 0, 0), weekday=0
        )
        self.assertTrue(rate_time.overlaps(rate_time_8))
        # Monday 11PM-2AM should NOT overlap (split, begins after end)
        rate_time_9 = RateTime.objects.create(name="split 3")
        DailySchedule.objects.create(
            rate_time=rate_time_9, start_time=datetime.time(23, 0, 0), end_time=datetime.time(2, 0, 0), weekday=0
        )
        self.assertFalse(rate_time.overlaps(rate_time_9))
        # Monday 11PM-7PM should NOT overlap (split, begins after end)
        rate_time_10 = RateTime.objects.create(name="split 4")
        DailySchedule.objects.create(
            rate_time=rate_time_10, start_time=datetime.time(23, 0, 0), end_time=datetime.time(19, 0, 0), weekday=0
        )
        self.assertFalse(rate_time.overlaps(rate_time_10))

    def test_rate_times_edge_cases(self):
        # Original: Monday 4PM-8PM
        rate_time = RateTime.objects.create(name="original")
        DailySchedule.objects.create(
            rate_time=rate_time, start_time=datetime.time(16, 0, 0), end_time=datetime.time(20, 0, 0), weekday=0
        )
        # Monday 4PM-8PM should overlap
        rate_time_1 = RateTime.objects.create(name="edge 1")
        DailySchedule.objects.create(
            rate_time=rate_time_1, start_time=datetime.time(16, 0, 0), end_time=datetime.time(20, 0, 0), weekday=0
        )
        self.assertTrue(rate_time.overlaps(rate_time_1))
        # Monday 6AM-4PM should NOT overlap
        rate_time_2 = RateTime.objects.create(name="edge 2")
        DailySchedule.objects.create(
            rate_time=rate_time_2, start_time=datetime.time(6, 0, 0), end_time=datetime.time(16, 0, 0), weekday=0
        )
        self.assertFalse(rate_time.overlaps(rate_time_2))
        # Monday 8PM-11PM should NOT overlap
        rate_time_3 = RateTime.objects.create(name="edge 3")
        DailySchedule.objects.create(
            rate_time=rate_time_3, start_time=datetime.time(20, 0, 0), end_time=datetime.time(23, 0, 0), weekday=0
        )
        self.assertFalse(rate_time.overlaps(rate_time_3))
        # Monday 8PM-2AM should NOT overlap
        rate_time_4 = RateTime.objects.create(name="edge 4")
        DailySchedule.objects.create(
            rate_time=rate_time_4, start_time=datetime.time(20, 0, 0), end_time=datetime.time(2, 0, 0), weekday=0
        )
        self.assertFalse(rate_time.overlaps(rate_time_4))
        # Monday 8PM-2AM should NOT overlap
        rate_time_5 = RateTime.objects.create(name="edge 5")
        DailySchedule.objects.create(
            rate_time=rate_time_5, start_time=datetime.time(20, 0, 0), end_time=datetime.time(2, 0, 0), weekday=0
        )
        self.assertFalse(rate_time.overlaps(rate_time_5))
        # Sunday 11PM-4PM should NOT overlap
        rate_time_6 = RateTime.objects.create(name="edge 6")
        DailySchedule.objects.create(
            rate_time=rate_time_6, start_time=datetime.time(23, 0, 0), end_time=datetime.time(0, 0, 0), weekday=6
        )
        DailySchedule.objects.create(
            rate_time=rate_time_6, start_time=datetime.time(0, 0, 0), end_time=datetime.time(16, 0, 0), weekday=0
        )
        self.assertFalse(rate_time.overlaps(rate_time_6))

    def test_rate_times_split_edge_cases(self):
        # Original: Monday 8PM-4AM (split time)
        rate_time = RateTime.objects.create(name="original split")
        DailySchedule.objects.create(
            rate_time=rate_time, start_time=datetime.time(20, 0, 0), end_time=datetime.time(4, 0, 0), weekday=0
        )
        # Monday 8PM-4AM should overlap
        rate_time_1 = RateTime.objects.create(name="split 1")
        DailySchedule.objects.create(
            rate_time=rate_time_1, start_time=datetime.time(20, 0, 0), end_time=datetime.time(4, 0, 0), weekday=0
        )
        self.assertTrue(rate_time.overlaps(rate_time_1))
