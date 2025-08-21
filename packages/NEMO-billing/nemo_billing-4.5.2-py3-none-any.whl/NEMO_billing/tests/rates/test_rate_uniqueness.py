import datetime

from NEMO.models import Consumable, Tool
from django.core.exceptions import ValidationError
from django.test import TestCase

from NEMO_billing.rates.models import DailySchedule, Rate, RateCategory, RateTime, RateType


class RateTestCase(TestCase):
    def test_rate_no_category_no_items(self):
        # Tool missed reservation is a good example of a rate not category or item specific
        tool_missed_resa = RateType.objects.get(type="TOOL_MISSED_RESERVATION")
        self.assertFalse(tool_missed_resa.category_specific)
        self.assertFalse(tool_missed_resa.item_specific)
        Rate.objects.create(type=tool_missed_resa, amount="10.00")
        # Try creating another one (should fail)
        with self.assertRaises(ValidationError) as cm:
            Rate(type=tool_missed_resa, amount="20.00").full_clean()
            self.assertIn("__all__", cm.exception.error_dict)

        # Create another one with an effective date
        effective_date = datetime.date(2023, 1, 1)
        effective_date_2 = datetime.date(2024, 1, 1)
        Rate.objects.create(type=tool_missed_resa, amount="10.00", effective_date=effective_date)
        Rate.objects.create(type=tool_missed_resa, amount="10.00", effective_date=effective_date_2)

        # Try creating another one with the same effective date (should fail)
        with self.assertRaises(ValidationError) as cm:
            Rate(type=tool_missed_resa, amount="20.00", effective_date=effective_date).full_clean()
            self.assertIn("__all__", cm.exception.error_dict)

    def test_rate_no_category_items(self):
        # Consumable is a good example of a rate not category specific but item specific
        gold = Consumable.objects.create(name="Gold", quantity=10, reminder_email="test@test.com", reminder_threshold=5)
        platinum = Consumable.objects.create(
            name="Platinum", quantity=10, reminder_email="test@test.com", reminder_threshold=5
        )
        consumable_type = RateType.objects.get(type="CONSUMABLE")
        self.assertFalse(consumable_type.category_specific)
        self.assertTrue(consumable_type.item_specific)
        Rate.objects.create(type=consumable_type, consumable=gold, amount="10.00")
        # Try creating another one (should fail)
        with self.assertRaises(ValidationError) as cm:
            Rate(type=consumable_type, consumable=gold, flat=True, amount="20.00").full_clean()
        self.assertIn("__all__", cm.exception.error_dict)
        # Try creating another one with another item (should pass)
        Rate(type=consumable_type, consumable=platinum, flat=True, amount="20.00").full_clean()

        # Create another one with an effective date
        effective_date = datetime.date(2023, 1, 1)
        effective_date_2 = datetime.date(2024, 1, 1)
        Rate.objects.create(type=consumable_type, consumable=gold, amount="10.00", effective_date=effective_date)
        Rate.objects.create(type=consumable_type, consumable=gold, amount="10.00", effective_date=effective_date_2)

        # Try creating another one with the same effective date (should fail)
        with self.assertRaises(ValidationError) as cm:
            Rate(type=consumable_type, consumable=gold, amount="20.00", effective_date=effective_date).full_clean()
            self.assertIn("__all__", cm.exception.error_dict)

    def test_rate_category_no_items(self):
        # Staff charge is a good example of a rate category specific but not item specific
        industry = RateCategory.objects.create(name="Industry")
        academia = RateCategory.objects.create(name="Academia")
        staff_charge_type = RateType.objects.get(type="STAFF_CHARGE")
        self.assertTrue(staff_charge_type.category_specific)
        self.assertFalse(staff_charge_type.item_specific)
        Rate.objects.create(type=staff_charge_type, category=industry, amount="10.00")
        # Try creating another one (should fail)
        with self.assertRaises(ValidationError) as cm:
            Rate(type=staff_charge_type, category=industry, amount="20.00").full_clean()
        self.assertIn("__all__", cm.exception.error_dict)
        # Try creating another one with another category (should pass)
        Rate(type=staff_charge_type, category=academia, amount="20.00").full_clean()

        # Create another one with an effective date
        effective_date = datetime.date(2023, 1, 1)
        effective_date_2 = datetime.date(2024, 1, 1)
        Rate.objects.create(type=staff_charge_type, category=industry, amount="10.00", effective_date=effective_date)
        Rate.objects.create(type=staff_charge_type, category=industry, amount="10.00", effective_date=effective_date_2)

        # Try creating another one with the same effective date (should fail)
        with self.assertRaises(ValidationError) as cm:
            Rate(type=staff_charge_type, category=industry, amount="20.00", effective_date=effective_date).full_clean()
            self.assertIn("__all__", cm.exception.error_dict)

    def test_rate_category_items(self):
        # Tool usage is a good example of a rate category specific and item specific
        tool1 = Tool.objects.create(name="tool_1")
        tool2 = Tool.objects.create(name="tool_2")
        industry = RateCategory.objects.create(name="Industry")
        academia = RateCategory.objects.create(name="Academia")
        tool_usage_type = RateType.objects.get(type="TOOL_USAGE")
        self.assertTrue(tool_usage_type.category_specific)
        self.assertTrue(tool_usage_type.item_specific)
        Rate.objects.create(type=tool_usage_type, tool=tool1, category=industry, amount="10.00")
        # Try creating another one (should fail)
        with self.assertRaises(ValidationError) as cm:
            Rate(type=tool_usage_type, tool=tool1, category=industry, amount="20.00").full_clean()
        self.assertIn("__all__", cm.exception.error_dict)
        # Try creating another one with another category (should pass)
        Rate(type=tool_usage_type, tool=tool1, category=academia, amount="20.00").full_clean()
        # Try creating another one with another item (should pass)
        Rate(type=tool_usage_type, tool=tool2, category=industry, amount="30.00").full_clean()

        # Create another one with an effective date
        effective_date = datetime.date(2023, 1, 1)
        effective_date_2 = datetime.date(2024, 1, 1)
        Rate.objects.create(
            type=tool_usage_type, tool=tool1, category=industry, amount="10.00", effective_date=effective_date
        )
        Rate.objects.create(
            type=tool_usage_type, tool=tool1, category=industry, amount="10.00", effective_date=effective_date_2
        )

        # Try creating another one with the same effective date (should fail)
        with self.assertRaises(ValidationError) as cm:
            Rate(
                type=tool_usage_type, tool=tool1, category=industry, amount="20.00", effective_date=effective_date
            ).full_clean()
            self.assertIn("__all__", cm.exception.error_dict)

    def test_rate_time_overlap(self):
        # Tool usage is a good example of a rate category specific and item specific
        tool1 = Tool.objects.create(name="tool_1")
        tool_usage_type = RateType.objects.get(type="TOOL_USAGE")
        self.assertTrue(tool_usage_type.item_specific)
        # Create base rate
        Rate.objects.create(type=tool_usage_type, tool=tool1, amount="10.00")

        # Create first rate time
        rate_time_1 = RateTime.objects.create(name="Mon 10AM - 10PM")
        DailySchedule.objects.create(
            rate_time=rate_time_1, start_time=datetime.time(10, 0, 0), end_time=datetime.time(22, 0, 0), weekday=0
        )
        # Create overlapping time
        rate_time_2 = RateTime.objects.create(name="Mon 8PM - 10AM")
        daily_schedule_2 = DailySchedule.objects.create(
            rate_time=rate_time_2, start_time=datetime.time(20, 0, 0), end_time=datetime.time(10, 0, 0), weekday=0
        )

        rate_1 = Rate(type=tool_usage_type, tool=tool1, amount="10.00", time=rate_time_1)
        self.assertIsNone(rate_1.full_clean())
        rate_1.save()

        # Try creating another one (should fail)
        with self.assertRaises(ValidationError) as cm:
            Rate(type=tool_usage_type, tool=tool1, amount="20.00", time=rate_time_2).full_clean()

        # Create another one that doesn't overlap (start at 11PM)
        daily_schedule_2.start_time = datetime.time(23, 0, 0)
        self.assertIsNone(daily_schedule_2.full_clean())
        daily_schedule_2.save()
        rate_2 = Rate(type=tool_usage_type, tool=tool1, amount="20.00", time=rate_time_2)
        self.assertIsNone(rate_2.full_clean())
        rate_2.save()
        self.assertIsNone(rate_2.full_clean())

        # Changing the rate time later should trigger validation error if it will make rates overlap
        daily_schedule_2.start_time = datetime.time(20, 0, 0)
        with self.assertRaises(ValidationError) as cm:
            daily_schedule_2.full_clean()
