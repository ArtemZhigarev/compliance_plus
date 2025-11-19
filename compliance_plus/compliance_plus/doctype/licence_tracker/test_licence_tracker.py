# Copyright (c) 2025, KlyONIX Tech Consulting Pvt Ltd and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today, add_days


class TestLicenceTracker(FrappeTestCase):
	def setUp(self):
		"""Set up test fixtures."""
		# Clean up any existing test licences
		frappe.db.delete("Licence Tracker", {"document_name": ["like", "Test Licence%"]})
		frappe.db.commit()

	def tearDown(self):
		"""Clean up after tests."""
		frappe.db.delete("Licence Tracker", {"document_name": ["like", "Test Licence%"]})
		frappe.db.commit()

	def test_create_licence_tracker(self):
		"""Test creating a basic licence tracker."""
		licence = frappe.get_doc(
			{
				"doctype": "Licence Tracker",
				"document_name": "Test Licence Document 1",
				"type": "Business License",
				"issuer_supplier": "Government Authority",
				"issue_date": today(),
				"expiry_date": add_days(today(), 365),
				"status": "Active",
			}
		)
		licence.insert()

		self.assertEqual(licence.document_name, "Test Licence Document 1")
		self.assertEqual(licence.type, "Business License")
		self.assertEqual(licence.status, "Active")

	def test_required_fields(self):
		"""Test that required fields are enforced."""
		# Missing document_name
		licence = frappe.get_doc(
			{
				"doctype": "Licence Tracker",
				"issuer_supplier": "Government Authority",
				"issue_date": today(),
				"expiry_date": add_days(today(), 365),
				"status": "Active",
			}
		)

		with self.assertRaises(frappe.exceptions.MandatoryError):
			licence.insert()

	def test_status_options(self):
		"""Test that status field accepts valid options."""
		valid_statuses = ["Active", "Expiring Soon", "Expired", "Renewing"]

		for status in valid_statuses:
			licence = frappe.get_doc(
				{
					"doctype": "Licence Tracker",
					"document_name": f"Test Licence {status}",
					"issuer_supplier": "Test Authority",
					"issue_date": today(),
					"expiry_date": add_days(today(), 365),
					"status": status,
				}
			)
			licence.insert()
			self.assertEqual(licence.status, status)

	def test_reminder_functionality(self):
		"""Test reminder fields."""
		licence = frappe.get_doc(
			{
				"doctype": "Licence Tracker",
				"document_name": "Test Licence Reminder",
				"issuer_supplier": "Test Authority",
				"issue_date": today(),
				"expiry_date": add_days(today(), 90),
				"status": "Active",
				"enable_reminder": 1,
				"remind_before_days": 15,
			}
		)
		licence.insert()

		self.assertEqual(licence.enable_reminder, 1)
		self.assertEqual(licence.remind_before_days, 15)

	def test_update_licence_tracker(self):
		"""Test updating an existing licence tracker."""
		licence = frappe.get_doc(
			{
				"doctype": "Licence Tracker",
				"document_name": "Test Licence Update",
				"issuer_supplier": "Test Authority",
				"issue_date": today(),
				"expiry_date": add_days(today(), 30),
				"status": "Active",
			}
		)
		licence.insert()

		# Update status to expiring soon
		licence.status = "Expiring Soon"
		licence.description = "Renewal in progress"
		licence.save()

		# Verify updates
		updated_licence = frappe.get_doc("Licence Tracker", licence.name)
		self.assertEqual(updated_licence.status, "Expiring Soon")
		self.assertEqual(updated_licence.description, "Renewal in progress")

	def test_naming_series(self):
		"""Test that naming series is applied correctly."""
		licence = frappe.get_doc(
			{
				"doctype": "Licence Tracker",
				"document_name": "Test Licence Series",
				"issuer_supplier": "Test Authority",
				"issue_date": today(),
				"expiry_date": add_days(today(), 365),
				"status": "Active",
			}
		)
		licence.insert()

		# Name should follow LIT-.YYYY.-.#### pattern
		self.assertTrue(licence.name.startswith("LIT-"))
