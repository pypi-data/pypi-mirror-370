import datetime

from NEMO.models import Account, EmailLog, Project, User
from django.core.management import call_command
from django.test import TestCase

from NEMO_billing.customization import BillingCustomization
from NEMO_billing.invoices.models import ProjectBillingDetails


class RateTimeTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        BillingCustomization.set("billing_accounting_email_address", "accounting@test.com")
        BillingCustomization.set("billing_project_expiration_reminder_days", "3,2,1")
        cls.pi = User.objects.create(
            username="pi", first_name="Principal", last_name="Investigator", email="pi@test.com"
        )
        account = Account.objects.create(name="Test Account")
        cls.test_project = Project.objects.create(name="Test Project", account=account)
        cls.test_project_2 = Project.objects.create(name="Test Project 2", account=account)
        next_day = datetime.date.today() + datetime.timedelta(days=1)
        next_two_days = datetime.date.today() + datetime.timedelta(days=2)
        cls.test_project.projectbillingdetails = ProjectBillingDetails.objects.create(
            project=cls.test_project, expires_on=next_day
        )
        cls.test_project.projectbillingdetails = ProjectBillingDetails.objects.create(
            project=cls.test_project_2, expires_on=next_two_days
        )

    def test_project_expiration(self):
        self.assertFalse(EmailLog.objects.exists())
        call_command("deactivate_expired_projects")
        # No project PIs and no ccs, no emails
        self.assertFalse(EmailLog.objects.exists())
        # One project expiring
        self.pi.managed_projects.add(self.test_project)
        call_command("deactivate_expired_projects")
        self.assertEqual(EmailLog.objects.count(), 1)
        EmailLog.objects.all().delete()
        # Two projects expiring
        self.pi.managed_projects.add(self.test_project_2)
        call_command("deactivate_expired_projects")
        self.assertEqual(EmailLog.objects.count(), 1)
        self.assertTrue("Projects expiring" in EmailLog.objects.first().subject)
        self.assertEqual(EmailLog.objects.first().to, self.pi.email)
        EmailLog.objects.all().delete()
        # Set a cc email, it should send an email to it
        BillingCustomization.set("billing_project_expiration_reminder_cc", "cc@example.com")
        call_command("deactivate_expired_projects")
        self.assertTrue(EmailLog.objects.exists())
        self.assertTrue("cc@example.com" in EmailLog.objects.first().to)
        self.assertTrue(self.pi.email in EmailLog.objects.first().to)
