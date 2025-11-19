# Copyright (c) 2025, KlyONIX Tech Consulting Pvt Ltd and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today, add_days


class TestComplianceTracker(FrappeTestCase):
	def setUp(self):
		"""Set up test fixtures."""
		# Create a test compliance category
		if not frappe.db.exists("Compliance Category", "Test Compliance Category"):
			category = frappe.get_doc(
				{
					"doctype": "Compliance Category",
					"category_name": "Test Compliance Category",
					"description": "Category for testing",
					"is_active": 1,
				}
			)
			category.insert()

		# Clean up any existing test trackers
		frappe.db.delete("Compliance Tracker", {"document_name": ["like", "Test Compliance%"]})
		frappe.db.commit()

	def tearDown(self):
		"""Clean up after tests."""
		frappe.db.delete("Compliance Tracker", {"document_name": ["like", "Test Compliance%"]})
		frappe.db.delete("Compliance Category", {"category_name": "Test Compliance Category"})
		frappe.db.commit()

	def test_create_compliance_tracker(self):
		"""Test creating a basic compliance tracker."""
		tracker = frappe.get_doc(
			{
				"doctype": "Compliance Tracker",
				"document_name": "Test Compliance Document 1",
				"compliance_category": "Test Compliance Category",
				"type": "License",
				"issuer_supplier": "Test Supplier",
				"issue_date": today(),
				"expiry_date": add_days(today(), 365),
				"status": "Active",
			}
		)
		tracker.insert()

		self.assertEqual(tracker.document_name, "Test Compliance Document 1")
		self.assertEqual(tracker.compliance_category, "Test Compliance Category")
		self.assertEqual(tracker.status, "Active")

	def test_required_fields(self):
		"""Test that required fields are enforced."""
		# Missing document_name
		tracker = frappe.get_doc(
			{
				"doctype": "Compliance Tracker",
				"compliance_category": "Test Compliance Category",
				"issuer_supplier": "Test Supplier",
				"issue_date": today(),
				"expiry_date": add_days(today(), 365),
				"status": "Active",
			}
		)

		with self.assertRaises(frappe.exceptions.MandatoryError):
			tracker.insert()

	def test_reminder_fields(self):
		"""Test reminder functionality fields."""
		tracker = frappe.get_doc(
			{
				"doctype": "Compliance Tracker",
				"document_name": "Test Compliance Document Reminder",
				"compliance_category": "Test Compliance Category",
				"issuer_supplier": "Test Supplier",
				"issue_date": today(),
				"expiry_date": add_days(today(), 365),
				"status": "Active",
				"enable_reminder": 1,
				"remind_before_days": 30,
			}
		)
		tracker.insert()

		self.assertEqual(tracker.enable_reminder, 1)
		self.assertEqual(tracker.remind_before_days, 30)

	def test_status_options(self):
		"""Test that status field accepts valid options."""
		valid_statuses = ["Active", "Expiring Soon", "Expired", "Renewing"]

		for status in valid_statuses:
			tracker = frappe.get_doc(
				{
					"doctype": "Compliance Tracker",
					"document_name": f"Test Compliance Document {status}",
					"compliance_category": "Test Compliance Category",
					"issuer_supplier": "Test Supplier",
					"issue_date": today(),
					"expiry_date": add_days(today(), 365),
					"status": status,
				}
			)
			tracker.insert()
			self.assertEqual(tracker.status, status)

	def test_update_compliance_tracker(self):
		"""Test updating an existing compliance tracker."""
		tracker = frappe.get_doc(
			{
				"doctype": "Compliance Tracker",
				"document_name": "Test Compliance Document Update",
				"compliance_category": "Test Compliance Category",
				"issuer_supplier": "Test Supplier",
				"issue_date": today(),
				"expiry_date": add_days(today(), 365),
				"status": "Active",
			}
		)
		tracker.insert()

		# Update the tracker
		tracker.status = "Expiring Soon"
		tracker.description = "Updated description"
		tracker.save()

		# Verify updates
		updated_tracker = frappe.get_doc("Compliance Tracker", tracker.name)
		self.assertEqual(updated_tracker.status, "Expiring Soon")
		self.assertEqual(updated_tracker.description, "Updated description")

	def test_in_charge_user_link(self):
		"""Test that in_charge field links to User."""
		tracker = frappe.get_doc(
			{
				"doctype": "Compliance Tracker",
				"document_name": "Test Compliance Document User",
				"compliance_category": "Test Compliance Category",
				"issuer_supplier": "Test Supplier",
				"issue_date": today(),
				"expiry_date": add_days(today(), 365),
				"status": "Active",
				"in_charge": "Administrator",
			}
		)
		tracker.insert()

		self.assertEqual(tracker.in_charge, "Administrator")
