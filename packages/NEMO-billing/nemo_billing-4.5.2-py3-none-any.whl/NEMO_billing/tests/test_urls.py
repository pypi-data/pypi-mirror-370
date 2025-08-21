from django.test import TestCase
from django.urls import reverse

from NEMO_billing.models import CoreFacility
from NEMO_billing.tests.test_utilities import basic_data


class TestURLs(TestCase):
    def test_staff_charge(self):
        user, project, tool, area = basic_data()
        CoreFacility.objects.create(name="Test")
        self.client.force_login(user)
        response = self.client.get(reverse("staff_charges"), follow=True)
        self.assertEqual(response.status_code, 200)
        # it's redirect to login
        self.assertEqual(response.request["PATH_INFO"], "/")
        # Make user staff
        user.is_staff = True
        user.save()
        response = self.client.get(reverse("staff_charges"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.request["PATH_INFO"], "/")
        self.assertContains(response, "core facility")

    def test_api(self):
        user, project, tool, area = basic_data()
        self.client.force_login(user)
        response = self.client.get(reverse("billingdata-list"), follow=True)
        # Forbidden
        self.assertEqual(response.status_code, 403)
        # Make user admin
        user.is_superuser = True
        user.save()
        response = self.client.get(reverse("billingdata-list") + "?start=01/01/2020&end=01/01/2099", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.request["PATH_INFO"], "/")
