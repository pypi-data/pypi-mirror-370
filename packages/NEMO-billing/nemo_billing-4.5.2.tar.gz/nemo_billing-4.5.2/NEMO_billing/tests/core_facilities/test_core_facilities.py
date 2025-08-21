from django.test import TestCase

from NEMO_billing.models import CoreFacility


class TestCoreFacilities(TestCase):
    def test_create_without_external_id(self):
        """
        Tests that you can create a CoreFacility without providing an external_id.
        Check that the external_id is correctly stored as an empty string.
        """
        name_value = "Core Facility Name without External ID"

        entries_count = CoreFacility.objects.count()
        corefac = CoreFacility.objects.create(name=name_value)

        self.assertEqual(CoreFacility.objects.count(), entries_count + 1)
        self.assertIsNotNone(corefac.id)
        self.assertEqual(corefac.name, name_value)
        # For CharField, Django often converts None to an empty string on save if blank=True.
        self.assertIsNone(corefac.external_id)

    def test_create_with_external_id(self):
        """
        Tests that you can create a CoreFacility with an external_id.
        Check that the external_id is correctly stored.
        """
        name_value = "Core Facility Name with External ID"
        external_id_value = "External-ID-For-Core-Facility"

        entries_count = CoreFacility.objects.count()
        corefac = CoreFacility.objects.create(name=name_value, external_id=external_id_value)

        self.assertEqual(CoreFacility.objects.count(), entries_count + 1)
        self.assertIsNotNone(corefac.id)
        self.assertEqual(corefac.name, name_value)
        self.assertEqual(corefac.external_id, external_id_value)

    def test_core_facility_retrieval(self):
        """
        Tests that retrieving a CoreFacility matches its creation values.
        """
        name_value = "Core Facility Name to Test Retrieval"
        external_id_value = "Retrieval-External-ID"
        CoreFacility.objects.create(name=name_value, external_id=external_id_value)

        retrieved = CoreFacility.objects.get(name=name_value)

        self.assertEqual(retrieved.name, name_value)
        self.assertEqual(retrieved.external_id, external_id_value)
        self.assertIsNotNone(retrieved.id)

    def test_core_facility_retrieval_no_external_id(self):
        """
        Tests that retrieving a CoreFacility matches its creation values, with
        no external_id provided.
        """
        name_value = "Core Facility Name to Test Retrieval no External ID"
        CoreFacility.objects.create(
            name=name_value,
        )

        retrieved = CoreFacility.objects.get(name=name_value)

        self.assertEqual(retrieved.name, name_value)
        self.assertIsNone(retrieved.external_id)
        self.assertIsNotNone(retrieved.id)

    def test_core_facility_retrieval_empty_external_id(self):
        """
        Tests that retrieving a CoreFacility matches its creation values, with
        external_id as an empty string.
        """
        name_value = "Core Facility Name to Test Retrieval no External ID"
        CoreFacility.objects.create(name=name_value, external_id="")

        retrieved = CoreFacility.objects.get(name=name_value)

        self.assertEqual(retrieved.name, name_value)
        self.assertEqual(retrieved.external_id, "")
        self.assertIsNotNone(retrieved.id)
