import datetime

from NEMO.models import (
    Account,
    AreaAccessRecord,
    Consumable,
    ConsumableWithdraw,
    Customization,
    Project,
    Reservation,
    StaffCharge,
    TrainingSession,
    UsageEvent,
    User,
)
from django.test import TestCase
from django.utils import timezone
from django.utils.timezone import make_aware

from NEMO_billing.invoices.models import InvoiceConfiguration, ProjectBillingDetails
from NEMO_billing.invoices.processors import invoice_data_processor_class as data_processor
from NEMO_billing.models import CustomCharge
from NEMO_billing.rates.models import DailySchedule, Rate, RateTime, RateType
from NEMO_billing.tests.test_utilities import basic_data


class TestRateAmount(TestCase):
    def test_usage_event_rate(self):
        test_user, test_project, tool, area = basic_data()

        tz = timezone.get_current_timezone()
        tool_usage_type = RateType.objects.get(type=RateType.Type.TOOL_USAGE)
        rate = Rate.objects.create(type=tool_usage_type, tool=tool, amount=60)  # 60 per hour = $1 per minute
        usage_start = make_aware(datetime.datetime(year=2022, month=2, day=21, hour=17), tz)  # Mon Feb 21 2022 at 5PM
        usage_end = make_aware(datetime.datetime(year=2022, month=2, day=25, hour=3), tz)  # Fri Feb 25 2022 at 3AM
        diff_minutes = (usage_end - usage_start).total_seconds() / 60
        # Create tool usage
        UsageEvent.objects.create(
            user=test_user, operator=test_user, project=test_project, tool=tool, start=usage_start, end=usage_end
        )

        billing_start = make_aware(datetime.datetime(year=2022, month=2, day=1), tz)
        billing_end = make_aware(datetime.datetime(year=2022, month=2, day=28), tz)
        config = InvoiceConfiguration.first_or_default()
        billables = data_processor.get_billable_items(billing_start, billing_end, config)
        self.assertEqual(len(billables), 1)
        usage_billable = billables[0]
        self.assertEqual(usage_billable.rate, rate)
        self.assertEqual(usage_billable.rate_type, tool_usage_type)
        self.assertEqual(usage_billable.quantity, diff_minutes)
        self.assertEqual(usage_billable.user, test_user)
        self.assertEqual(usage_billable.project, test_project)
        self.assertEqual(usage_billable.amount, diff_minutes * 1.0)

        # test with timed rate
        rate_time = RateTime.objects.create(name="rate time")
        # Tuesday morning double rate for an hour
        DailySchedule.objects.create(
            rate_time=rate_time, start_time=datetime.time(0, 0, 0), end_time=datetime.time(1, 0, 0), weekday=1
        )
        rate_with_time = Rate.objects.create(type=tool_usage_type, tool=tool, time=rate_time, amount=120)

        billables = data_processor.get_billable_items(billing_start, billing_end, config)
        self.assertEqual(len(billables), 3)
        # Total amount should be diff minus 1 hour at $1/min + 1 hour at $2/min
        self.assertEqual(sum([billable.amount for billable in billables]), (diff_minutes - 60) * 1.0 + 60 * 2.0)

        # Test with flat rate
        rate_with_time.delete()
        rate.flat = True
        rate.save()
        billables = data_processor.get_billable_items(billing_start, billing_end, config)
        self.assertEqual(len(billables), 1)
        usage_billable = billables[0]
        self.assertEqual(usage_billable.rate, rate)
        self.assertEqual(usage_billable.tool, tool)
        self.assertEqual(usage_billable.rate_type, tool_usage_type)
        self.assertEqual(usage_billable.quantity, diff_minutes)
        self.assertEqual(usage_billable.user, test_user)
        self.assertEqual(usage_billable.project, test_project)
        self.assertEqual(usage_billable.amount, 60)

        # Test with daily rate
        rate.daily = True
        rate.daily_split_multi_day_charges = False
        rate.save()
        billables = data_processor.get_billable_items(billing_start, billing_end, config)
        self.assertEqual(len(billables), 1)
        usage_billable = billables[0]
        self.assertEqual(usage_billable.rate, rate)
        self.assertEqual(usage_billable.tool, tool)
        self.assertEqual(usage_billable.rate_type, tool_usage_type)
        self.assertEqual(usage_billable.quantity, diff_minutes)
        self.assertEqual(usage_billable.user, test_user)
        self.assertEqual(usage_billable.project, test_project)
        self.assertEqual(usage_billable.amount, 60)

        # Add a second charge, same end day, should be zero since it's daily rate
        usage_start = make_aware(datetime.datetime(year=2022, month=2, day=25, hour=5), tz)  # Fri Feb 25 2022 at 5AM
        usage_end = make_aware(datetime.datetime(year=2022, month=2, day=25, hour=13), tz)  # Fri Feb 25 2022 at 1PM
        diff_minutes_2 = (usage_end - usage_start).total_seconds() / 60
        tool_usage = UsageEvent.objects.create(
            user=test_user, operator=test_user, project=test_project, tool=tool, start=usage_start, end=usage_end
        )
        billables = data_processor.get_billable_items(billing_start, billing_end, config)
        self.assertEqual(len(billables), 2)
        usage_billable = billables[0]
        self.assertEqual(usage_billable.rate, rate)
        self.assertEqual(usage_billable.tool, tool)
        self.assertEqual(usage_billable.rate_type, tool_usage_type)
        self.assertEqual(usage_billable.quantity, diff_minutes)
        self.assertEqual(usage_billable.user, test_user)
        self.assertEqual(usage_billable.project, test_project)
        self.assertEqual(usage_billable.amount, 60)
        usage_billable = billables[1]
        self.assertEqual(usage_billable.rate, rate)
        self.assertEqual(usage_billable.tool, tool)
        self.assertEqual(usage_billable.rate_type, tool_usage_type)
        self.assertEqual(usage_billable.quantity, diff_minutes_2)
        self.assertEqual(usage_billable.user, test_user)
        self.assertEqual(usage_billable.project, test_project)
        self.assertEqual(usage_billable.amount, 0)

        # Set the second record on a separate project
        test_project_2 = Project.objects.create(name="Test Project 2", account=Account.objects.get(name="Test Account"))
        test_project_2.projectbillingdetails = ProjectBillingDetails.objects.create(project=test_project_2)
        tool_usage.project = test_project_2
        tool_usage.save()
        billables = data_processor.get_billable_items(billing_start, billing_end, config)
        self.assertEqual(len(billables), 2)
        usage_billable = billables[0]
        self.assertEqual(usage_billable.amount, 60)
        usage_billable = billables[1]
        self.assertEqual(usage_billable.amount, 60)

        # Make it by account, now the second charge should be 0
        Customization.objects.create(name="rates_daily_per_account", value="enabled")
        billables = data_processor.get_billable_items(billing_start, billing_end, config)
        self.assertEqual(len(billables), 2)
        usage_billable = billables[0]
        self.assertEqual(usage_billable.amount, 60)
        usage_billable = billables[1]
        self.assertEqual(usage_billable.amount, 0)

    def test_area_access_rate(self):
        test_user, test_project, tool, area = basic_data()

        tz = timezone.get_current_timezone()
        area_access_type = RateType.objects.get(type=RateType.Type.AREA_USAGE)
        rate = Rate.objects.create(type=area_access_type, area=area, amount=60)  # 60 per hour = $1 per minute
        usage_start = make_aware(datetime.datetime(year=2022, month=2, day=21, hour=17), tz)  # Mon Feb 21 2022 at 5PM
        usage_end = make_aware(datetime.datetime(year=2022, month=2, day=25, hour=3), tz)  # Fri Feb 25 2022 at 3AM
        diff_minutes = (usage_end - usage_start).total_seconds() / 60
        # Create area usage
        AreaAccessRecord.objects.create(
            customer=test_user, project=test_project, area=area, start=usage_start, end=usage_end
        )

        billing_start = make_aware(datetime.datetime(year=2022, month=2, day=1), tz)
        billing_end = make_aware(datetime.datetime(year=2022, month=2, day=28), tz)
        config = InvoiceConfiguration.first_or_default()
        billables = data_processor.get_billable_items(billing_start, billing_end, config)
        self.assertEqual(len(billables), 1)
        usage_billable = billables[0]
        self.assertEqual(usage_billable.rate, rate)
        self.assertEqual(usage_billable.rate_type, area_access_type)
        self.assertEqual(usage_billable.quantity, diff_minutes)
        self.assertEqual(usage_billable.user, test_user)
        self.assertEqual(usage_billable.project, test_project)
        self.assertEqual(usage_billable.amount, diff_minutes * 1.0)

        # test with timed rate
        rate_time = RateTime.objects.create(name="rate_1")
        # Tuesday morning double rate for 2 hours
        DailySchedule.objects.create(
            rate_time=rate_time, start_time=datetime.time(0, 0, 0), end_time=datetime.time(2, 0, 0), weekday=1
        )
        rate_with_time = Rate.objects.create(type=area_access_type, area=area, time=rate_time, amount=120)

        billables = data_processor.get_billable_items(billing_start, billing_end, config)
        self.assertEqual(len(billables), 3)
        # Total amount should be diff minus 2 hours at $1/min + 2 hours at $2/min
        self.assertEqual(sum([billable.amount for billable in billables]), (diff_minutes - 120) * 1.0 + 120 * 2.0)

        # Test with flat rate
        rate_with_time.delete()
        rate.flat = True
        rate.save()
        billables = data_processor.get_billable_items(billing_start, billing_end, config)
        self.assertEqual(len(billables), 1)
        usage_billable = billables[0]
        self.assertEqual(usage_billable.rate, rate)
        self.assertEqual(usage_billable.area, area)
        self.assertEqual(usage_billable.rate_type, area_access_type)
        self.assertEqual(usage_billable.quantity, diff_minutes)
        self.assertEqual(usage_billable.user, test_user)
        self.assertEqual(usage_billable.project, test_project)
        self.assertEqual(usage_billable.amount, 60)

        # Test with daily rate
        rate.daily = True
        rate.daily_split_multi_day_charges = False
        rate.save()
        billables = data_processor.get_billable_items(billing_start, billing_end, config)
        self.assertEqual(len(billables), 1)
        usage_billable = billables[0]
        self.assertEqual(usage_billable.rate, rate)
        self.assertEqual(usage_billable.area, area)
        self.assertEqual(usage_billable.rate_type, area_access_type)
        self.assertEqual(usage_billable.quantity, diff_minutes)
        self.assertEqual(usage_billable.user, test_user)
        self.assertEqual(usage_billable.project, test_project)
        self.assertEqual(usage_billable.amount, 60)

        # Add a second charge, same end day, should be zero since it's daily rate
        usage_start = make_aware(datetime.datetime(year=2022, month=2, day=25, hour=5), tz)  # Fri Feb 25 2022 at 5AM
        usage_end = make_aware(datetime.datetime(year=2022, month=2, day=25, hour=13), tz)  # Fri Feb 25 2022 at 1PM
        diff_minutes_2 = (usage_end - usage_start).total_seconds() / 60
        area_record = AreaAccessRecord.objects.create(
            customer=test_user, project=test_project, area=area, start=usage_start, end=usage_end
        )
        billables = data_processor.get_billable_items(billing_start, billing_end, config)
        self.assertEqual(len(billables), 2)
        usage_billable = billables[0]
        self.assertEqual(usage_billable.rate, rate)
        self.assertEqual(usage_billable.area, area)
        self.assertEqual(usage_billable.rate_type, area_access_type)
        self.assertEqual(usage_billable.quantity, diff_minutes)
        self.assertEqual(usage_billable.user, test_user)
        self.assertEqual(usage_billable.project, test_project)
        self.assertEqual(usage_billable.amount, 60)
        usage_billable = billables[1]
        self.assertEqual(usage_billable.rate, rate)
        self.assertEqual(usage_billable.area, area)
        self.assertEqual(usage_billable.rate_type, area_access_type)
        self.assertEqual(usage_billable.quantity, diff_minutes_2)
        self.assertEqual(usage_billable.user, test_user)
        self.assertEqual(usage_billable.project, test_project)
        self.assertEqual(usage_billable.amount, 0)

        # Set the second record on a separate project
        test_project_2 = Project.objects.create(name="Test Project 2", account=Account.objects.get(name="Test Account"))
        test_project_2.projectbillingdetails = ProjectBillingDetails.objects.create(project=test_project_2)
        area_record.project = test_project_2
        area_record.save()
        billables = data_processor.get_billable_items(billing_start, billing_end, config)
        self.assertEqual(len(billables), 2)
        usage_billable = billables[0]
        self.assertEqual(usage_billable.amount, 60)
        usage_billable = billables[1]
        self.assertEqual(usage_billable.amount, 60)

        # Make it by account, now the second charge should be 0
        daily_rate_cust = Customization.objects.create(name="rates_daily_per_account", value="enabled")
        billables = data_processor.get_billable_items(billing_start, billing_end, config)
        self.assertEqual(len(billables), 2)
        usage_billable = billables[0]
        self.assertEqual(usage_billable.amount, 60)
        usage_billable = billables[1]
        self.assertEqual(usage_billable.amount, 0)

        # reset to by project
        daily_rate_cust.value = ""
        daily_rate_cust.save()

        # Set the second record on a separate project, separate user
        area_record.customer = User.objects.create(
            username="test1", first_name="Test1", last_name="Test1", is_staff=False, badge_number=2
        )
        area_record.project = test_project_2
        area_record.save()
        billables = data_processor.get_billable_items(billing_start, billing_end, config)
        self.assertEqual(len(billables), 2)
        usage_billable = billables[0]
        self.assertEqual(usage_billable.amount, 60)
        usage_billable = billables[1]
        self.assertEqual(usage_billable.amount, 60)

        # Make it by account, second charge should still be 60 (different user)
        daily_rate_cust.value = "enabled"
        daily_rate_cust.save()
        billables = data_processor.get_billable_items(billing_start, billing_end, config)
        self.assertEqual(len(billables), 2)
        usage_billable = billables[0]
        self.assertEqual(usage_billable.amount, 60)
        usage_billable = billables[1]
        self.assertEqual(usage_billable.amount, 60)

    def test_staff_charge_rate(self):
        test_user, test_project, tool, area = basic_data()
        staff_member = User.objects.create(
            username="staff", first_name="Staff", last_name="Staff", is_staff=True, badge_number=2
        )

        tz = timezone.get_current_timezone()
        staff_charge_type = RateType.objects.get(type=RateType.Type.STAFF_CHARGE)
        rate = Rate.objects.create(type=staff_charge_type, amount=60)  # 60 per hour = $1 per minute
        staff_charge_start = make_aware(
            datetime.datetime(year=2022, month=2, day=21, hour=17), tz
        )  # Mon Feb 21 2022 at 5PM
        staff_charge_end = make_aware(
            datetime.datetime(year=2022, month=2, day=25, hour=3), tz
        )  # Fri Feb 25 2022 at 3AM
        diff_minutes = (staff_charge_end - staff_charge_start).total_seconds() / 60
        # Create staff charge
        StaffCharge.objects.create(
            staff_member=staff_member,
            customer=test_user,
            project=test_project,
            start=staff_charge_start,
            end=staff_charge_end,
        )

        billing_start = make_aware(datetime.datetime(year=2022, month=2, day=1), tz)
        billing_end = make_aware(datetime.datetime(year=2022, month=2, day=28), tz)
        config = InvoiceConfiguration.first_or_default()
        billables = data_processor.get_billable_items(billing_start, billing_end, config)
        self.assertEqual(len(billables), 1)
        staff_charge_billable = billables[0]
        self.assertEqual(staff_charge_billable.rate, rate)
        self.assertEqual(staff_charge_billable.rate_type, staff_charge_type)
        self.assertEqual(staff_charge_billable.quantity, diff_minutes)
        self.assertEqual(staff_charge_billable.user, test_user)
        self.assertEqual(staff_charge_billable.project, test_project)
        self.assertEqual(staff_charge_billable.amount, diff_minutes * 1.0)

        # test with timed rate
        rate_time = RateTime.objects.create(name="rate_1")
        # Tuesday morning double rate for 3 hours
        DailySchedule.objects.create(
            rate_time=rate_time, start_time=datetime.time(0, 0, 0), end_time=datetime.time(3, 0, 0), weekday=1
        )
        rate_with_time = Rate.objects.create(type=staff_charge_type, time=rate_time, amount=120)

        billables = data_processor.get_billable_items(billing_start, billing_end, config)
        self.assertEqual(len(billables), 3)
        # Total amount should be diff minus 3 hours at $1/min + 3 hours at $2/min
        self.assertEqual(sum([billable.amount for billable in billables]), (diff_minutes - 180) * 1.0 + 180 * 2.0)

        # Test with flat rate
        rate_with_time.delete()
        rate.flat = True
        rate.save()
        billables = data_processor.get_billable_items(billing_start, billing_end, config)
        self.assertEqual(len(billables), 1)
        staff_charge_billable = billables[0]
        self.assertEqual(staff_charge_billable.rate, rate)
        self.assertEqual(staff_charge_billable.rate_type, staff_charge_type)
        self.assertEqual(staff_charge_billable.quantity, diff_minutes)
        self.assertEqual(staff_charge_billable.user, test_user)
        self.assertEqual(staff_charge_billable.project, test_project)
        self.assertEqual(staff_charge_billable.amount, 60)

    def test_supply_rate(self):
        test_user, test_project, tool, area = basic_data()
        staff_member = User.objects.create(
            username="staff", first_name="Staff", last_name="Staff", is_staff=True, badge_number=2
        )
        supply = Consumable.objects.create(name="Supply", quantity=99, reminder_threshold=5)

        tz = timezone.get_current_timezone()
        consumable_type = RateType.objects.get(type=RateType.Type.CONSUMABLE)
        rate = Rate.objects.create(type=consumable_type, amount=60, consumable=supply)  # 60 per supply
        order_date = make_aware(datetime.datetime(year=2022, month=2, day=25, hour=3), tz)  # Fri Feb 25 2022 at 3AM
        # Create order
        ConsumableWithdraw.objects.create(
            merchant=staff_member,
            customer=test_user,
            project=test_project,
            consumable=supply,
            date=order_date,
            quantity=10,
        )

        billing_start = make_aware(datetime.datetime(year=2022, month=2, day=1), tz)
        billing_end = make_aware(datetime.datetime(year=2022, month=2, day=28), tz)
        config = InvoiceConfiguration.first_or_default()
        billables = data_processor.get_billable_items(billing_start, billing_end, config)
        self.assertEqual(len(billables), 1)
        supply_billable = billables[0]
        self.assertEqual(supply_billable.rate, rate)
        self.assertEqual(supply_billable.consumable, supply)
        self.assertEqual(supply_billable.rate_type, consumable_type)
        self.assertEqual(supply_billable.quantity, 10)
        self.assertEqual(supply_billable.user, test_user)
        self.assertEqual(supply_billable.project, test_project)
        self.assertEqual(supply_billable.amount, 10 * 60.0)

    def test_training_individual_rate(self):
        test_user, test_project, tool, area = basic_data()
        staff_member = User.objects.create(
            username="staff", first_name="Staff", last_name="Staff", is_staff=True, badge_number=2
        )

        tz = timezone.get_current_timezone()
        training_individual_type = RateType.objects.get(type=RateType.Type.TOOL_TRAINING_INDIVIDUAL)
        rate = Rate.objects.create(type=training_individual_type, amount=60, tool=tool)  # 60 per hour
        training_date = make_aware(datetime.datetime(year=2022, month=2, day=25, hour=3), tz)  # Fri Feb 25 2022 at 3AM
        # Create 90-min training session training
        TrainingSession.objects.create(
            type=TrainingSession.Type.INDIVIDUAL,
            trainer=staff_member,
            trainee=test_user,
            project=test_project,
            tool=tool,
            date=training_date,
            duration=90,
        )

        billing_start = make_aware(datetime.datetime(year=2022, month=2, day=1), tz)
        billing_end = make_aware(datetime.datetime(year=2022, month=2, day=28), tz)
        config = InvoiceConfiguration.first_or_default()
        billables = data_processor.get_billable_items(billing_start, billing_end, config)
        self.assertEqual(len(billables), 1)
        training_billable = billables[0]
        self.assertEqual(training_billable.rate, rate)
        self.assertEqual(training_billable.tool, tool)
        self.assertEqual(training_billable.rate_type, training_individual_type)
        self.assertEqual(training_billable.quantity, 90)
        self.assertEqual(training_billable.user, test_user)
        self.assertEqual(training_billable.project, test_project)
        self.assertEqual(training_billable.amount, 1.5 * 60.0)

    def test_training_group_rate(self):
        test_user, test_project, tool, area = basic_data()
        staff_member = User.objects.create(
            username="staff", first_name="Staff", last_name="Staff", is_staff=True, badge_number=2
        )

        tz = timezone.get_current_timezone()
        training_group_type = RateType.objects.get(type=RateType.Type.TOOL_TRAINING_GROUP)
        rate = Rate.objects.create(type=training_group_type, amount=30, tool=tool)  # 30 per hour
        training_date = make_aware(datetime.datetime(year=2022, month=2, day=25, hour=3), tz)  # Fri Feb 25 2022 at 3AM
        # Create 90 min training session training
        TrainingSession.objects.create(
            type=TrainingSession.Type.GROUP,
            trainer=staff_member,
            trainee=test_user,
            project=test_project,
            tool=tool,
            date=training_date,
            duration=120,
        )

        billing_start = make_aware(datetime.datetime(year=2022, month=2, day=1), tz)
        billing_end = make_aware(datetime.datetime(year=2022, month=2, day=28), tz)
        config = InvoiceConfiguration.first_or_default()
        billables = data_processor.get_billable_items(billing_start, billing_end, config)
        self.assertEqual(len(billables), 1)
        training_billable = billables[0]
        self.assertEqual(training_billable.rate, rate)
        self.assertEqual(training_billable.tool, tool)
        self.assertEqual(training_billable.rate_type, training_group_type)
        self.assertEqual(training_billable.quantity, 120)
        self.assertEqual(training_billable.user, test_user)
        self.assertEqual(training_billable.project, test_project)
        self.assertEqual(training_billable.amount, 2 * 30.0)

    def test_missed_reservation_tool(self):
        test_user, test_project, tool, area = basic_data()

        tz = timezone.get_current_timezone()
        tool_missed_type = RateType.objects.get(type=RateType.Type.TOOL_MISSED_RESERVATION)
        rate = Rate.objects.create(type=tool_missed_type, tool=tool, amount=60)  # 60 per hour = $1 per minute
        usage_start = make_aware(datetime.datetime(year=2022, month=2, day=21, hour=17), tz)  # Mon Feb 21 2022 at 5PM
        usage_end = make_aware(datetime.datetime(year=2022, month=2, day=25, hour=3), tz)  # Fri Feb 25 2022 at 3AM
        diff_minutes = (usage_end - usage_start).total_seconds() / 60
        # Create tool missed reservation
        Reservation.objects.create(
            user=test_user,
            creator=test_user,
            project=test_project,
            tool=tool,
            start=usage_start,
            end=usage_end,
            short_notice=False,
            missed=True,
        )

        billing_start = make_aware(datetime.datetime(year=2022, month=2, day=1), tz)
        billing_end = make_aware(datetime.datetime(year=2022, month=2, day=28), tz)
        config = InvoiceConfiguration.first_or_default()
        billables = data_processor.get_billable_items(billing_start, billing_end, config)
        self.assertEqual(len(billables), 1)
        missed_billable = billables[0]
        self.assertEqual(missed_billable.rate, rate)
        self.assertEqual(missed_billable.tool, tool)
        self.assertEqual(missed_billable.rate_type, tool_missed_type)
        self.assertEqual(missed_billable.quantity, diff_minutes)
        self.assertEqual(missed_billable.user, test_user)
        self.assertEqual(missed_billable.project, test_project)
        self.assertEqual(missed_billable.amount, diff_minutes * 1.0)

        # test with timed rate
        rate_time = RateTime.objects.create(name="rate_1")
        # Tuesday morning double rate for 1 hours
        DailySchedule.objects.create(
            rate_time=rate_time, start_time=datetime.time(0, 0, 0), end_time=datetime.time(1, 0, 0), weekday=1
        )
        rate_with_time = Rate.objects.create(type=tool_missed_type, tool=tool, time=rate_time, amount=120)

        billables = data_processor.get_billable_items(billing_start, billing_end, config)
        self.assertEqual(len(billables), 3)
        # Total amount should be diff minus 1 hour at $1/min + 1 hour at $2/min
        self.assertEqual(sum([billable.amount for billable in billables]), (diff_minutes - 60) * 1.0 + 60 * 2.0)

        # Test with flat rate
        rate_with_time.delete()
        rate.flat = True
        rate.save()
        billables = data_processor.get_billable_items(billing_start, billing_end, config)
        self.assertEqual(len(billables), 1)
        missed_billable = billables[0]
        self.assertEqual(missed_billable.rate, rate)
        self.assertEqual(missed_billable.tool, tool)
        self.assertEqual(missed_billable.rate_type, tool_missed_type)
        self.assertEqual(missed_billable.quantity, diff_minutes)
        self.assertEqual(missed_billable.user, test_user)
        self.assertEqual(missed_billable.project, test_project)
        self.assertEqual(missed_billable.amount, 60)

    def test_missed_reservation_area(self):
        test_user, test_project, tool, area = basic_data()

        tz = timezone.get_current_timezone()
        area_missed_type = RateType.objects.get(type=RateType.Type.AREA_MISSED_RESERVATION)
        rate = Rate.objects.create(type=area_missed_type, tool=tool, amount=60)  # 60 per hour = $1 per minute
        usage_start = make_aware(datetime.datetime(year=2022, month=2, day=21, hour=17), tz)  # Mon Feb 21 2022 at 5PM
        usage_end = make_aware(datetime.datetime(year=2022, month=2, day=25, hour=3), tz)  # Fri Feb 25 2022 at 3AM
        diff_minutes = (usage_end - usage_start).total_seconds() / 60
        # Create area missed reservation
        Reservation.objects.create(
            user=test_user,
            creator=test_user,
            project=test_project,
            area=area,
            start=usage_start,
            end=usage_end,
            short_notice=False,
            missed=True,
        )

        billing_start = make_aware(datetime.datetime(year=2022, month=2, day=1), tz)
        billing_end = make_aware(datetime.datetime(year=2022, month=2, day=28), tz)
        config = InvoiceConfiguration.first_or_default()
        billables = data_processor.get_billable_items(billing_start, billing_end, config)
        self.assertEqual(len(billables), 1)
        missed_billable = billables[0]
        self.assertEqual(missed_billable.rate, rate)
        self.assertEqual(missed_billable.area, area)
        self.assertEqual(missed_billable.rate_type, area_missed_type)
        self.assertEqual(missed_billable.quantity, diff_minutes)
        self.assertEqual(missed_billable.user, test_user)
        self.assertEqual(missed_billable.project, test_project)
        self.assertEqual(missed_billable.amount, diff_minutes * 1.0)

        # test with timed rate
        rate_time = RateTime.objects.create(name="rate time 1")
        # Tuesday morning double rate for 1 hours
        DailySchedule.objects.create(
            rate_time=rate_time, start_time=datetime.time(0, 0, 0), end_time=datetime.time(1, 0, 0), weekday=1
        )
        rate_with_time = Rate.objects.create(type=area_missed_type, area=area, time=rate_time, amount=120)

        billables = data_processor.get_billable_items(billing_start, billing_end, config)
        self.assertEqual(len(billables), 3)
        # Total amount should be diff minus 1 hour at $1/min + 1 hour at $2/min
        self.assertEqual(sum([billable.amount for billable in billables]), (diff_minutes - 60) * 1.0 + 60 * 2.0)

        # Test with flat rate
        rate_with_time.delete()
        rate.flat = True
        rate.save()
        billables = data_processor.get_billable_items(billing_start, billing_end, config)
        self.assertEqual(len(billables), 1)
        missed_billable = billables[0]
        self.assertEqual(missed_billable.rate, rate)
        self.assertEqual(missed_billable.area, area)
        self.assertEqual(missed_billable.rate_type, area_missed_type)
        self.assertEqual(missed_billable.quantity, diff_minutes)
        self.assertEqual(missed_billable.user, test_user)
        self.assertEqual(missed_billable.project, test_project)
        self.assertEqual(missed_billable.amount, 60)

    def test_custom_charge_amount(self):
        test_user, test_project, tool, area = basic_data()
        staff_member = User.objects.create(
            username="staff", first_name="Staff", last_name="Staff", is_staff=True, badge_number=2
        )

        tz = timezone.get_current_timezone()
        charge_date = make_aware(datetime.datetime(year=2022, month=2, day=25, hour=3), tz)  # Fri Feb 25 2022 at 3AM
        # Create charge
        CustomCharge.objects.create(
            name="charge", creator=staff_member, customer=test_user, project=test_project, date=charge_date, amount=142
        )

        billing_start = make_aware(datetime.datetime(year=2022, month=2, day=1), tz)
        billing_end = make_aware(datetime.datetime(year=2022, month=2, day=28), tz)
        config = InvoiceConfiguration.first_or_default()
        billables = data_processor.get_billable_items(billing_start, billing_end, config)
        self.assertEqual(len(billables), 1)
        supply_billable = billables[0]
        self.assertIsNone(supply_billable.rate)
        self.assertIsNone(supply_billable.rate_type)
        self.assertEqual(supply_billable.quantity, 1)
        self.assertEqual(supply_billable.user, test_user)
        self.assertEqual(supply_billable.project, test_project)
        self.assertEqual(supply_billable.amount, 142)

    def test_rate_flat_and_timed_mixed(self):
        test_user, test_project, tool, area = basic_data()

        tz = timezone.get_current_timezone()
        tool_usage_type = RateType.objects.get(type=RateType.Type.TOOL_USAGE)
        rate = Rate.objects.create(type=tool_usage_type, tool=tool, amount=60, flat=True)  # 60 flat
        usage_start = make_aware(datetime.datetime(year=2022, month=2, day=21, hour=17), tz)  # Mon Feb 21 2022 at 5PM
        usage_end = make_aware(datetime.datetime(year=2022, month=2, day=25, hour=3), tz)  # Fri Feb 25 2022 at 3AM
        # Create tool usage
        UsageEvent.objects.create(
            user=test_user, operator=test_user, project=test_project, tool=tool, start=usage_start, end=usage_end
        )

        billing_start = make_aware(datetime.datetime(year=2022, month=2, day=1), tz)
        billing_end = make_aware(datetime.datetime(year=2022, month=2, day=28), tz)
        config = InvoiceConfiguration.first_or_default()

        # add timed rate
        rate_time = RateTime.objects.create(name="rate time")
        # Tuesday morning double rate (non-flat) for an hour
        DailySchedule.objects.create(
            rate_time=rate_time, start_time=datetime.time(0, 0, 0), end_time=datetime.time(1, 0, 0), weekday=1
        )
        Rate.objects.create(type=tool_usage_type, tool=tool, time=rate_time, amount=120)

        billables = data_processor.get_billable_items(billing_start, billing_end, config)
        self.assertEqual(len(billables), 3)
        # Total amount should be 60 twice + 1 hour at $2/min
        self.assertEqual(sum([billable.amount for billable in billables]), 60 + 60 + 60 * 2.0)

    def test_rate_flat_and_timed_mixed_reverse(self):
        test_user, test_project, tool, area = basic_data()

        tz = timezone.get_current_timezone()
        tool_usage_type = RateType.objects.get(type=RateType.Type.TOOL_USAGE)
        Rate.objects.create(type=tool_usage_type, tool=tool, amount=60)  # 60 /hr
        usage_start = make_aware(datetime.datetime(year=2022, month=2, day=21, hour=17), tz)  # Mon Feb 21 2022 at 5PM
        usage_end = make_aware(datetime.datetime(year=2022, month=2, day=25, hour=3), tz)  # Fri Feb 25 2022 at 3AM
        diff_minutes = (usage_end - usage_start).total_seconds() / 60
        # Create tool usage
        UsageEvent.objects.create(
            user=test_user, operator=test_user, project=test_project, tool=tool, start=usage_start, end=usage_end
        )

        billing_start = make_aware(datetime.datetime(year=2022, month=2, day=1), tz)
        billing_end = make_aware(datetime.datetime(year=2022, month=2, day=28), tz)
        config = InvoiceConfiguration.first_or_default()

        # add timed rate
        rate_time = RateTime.objects.create(name="rate time")
        # Tuesday morning double rate (flat) for an hour
        DailySchedule.objects.create(
            rate_time=rate_time, start_time=datetime.time(0, 0, 0), end_time=datetime.time(1, 0, 0), weekday=1
        )
        Rate.objects.create(type=tool_usage_type, tool=tool, time=rate_time, flat=True, amount=120)

        billables = data_processor.get_billable_items(billing_start, billing_end, config)
        self.assertEqual(len(billables), 3)
        # Total amount should be total mins minus 1 hour at $1/min + 1 hour flat 120
        self.assertEqual(sum([billable.amount for billable in billables]), (diff_minutes - 60) * 1 + 120)
