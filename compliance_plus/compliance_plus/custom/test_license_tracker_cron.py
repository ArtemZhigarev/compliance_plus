# Copyright (c) 2025, KlyONIX Tech Consulting Pvt Ltd and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today, add_days
from compliance_plus.compliance_plus.custom.license_tracker_cron import (
	already_sent_recently,
	log_communication,
	send_license_expiry_reminders,
)
from unittest.mock import patch


class TestLicenseTrackerCron(FrappeTestCase):
	def setUp(self):
		"""Set up test fixtures."""
		# Clean up test data
		frappe.db.delete("Communication", {"reference_name": ["like", "Test Customer%"]})
		frappe.db.commit()

	def tearDown(self):
		"""Clean up after tests."""
		frappe.db.delete("Communication", {"reference_name": ["like", "Test Customer%"]})
		frappe.db.commit()

	def test_already_sent_recently_no_communication(self):
		"""Test already_sent_recently when no communication exists."""
		result = already_sent_recently("Test Customer New", 15)
		self.assertFalse(result)

	def test_already_sent_recently_old_communication(self):
		"""Test already_sent_recently with old communication."""
		# Create a communication from 20 days ago
		old_comm = frappe.get_doc(
			{
				"doctype": "Communication",
				"communication_type": "Automated Message",
				"subject": "Old Test Message",
				"reference_doctype": "Customer",
				"reference_name": "Test Customer Old",
				"content": "Old test content",
				"sent_or_received": "Sent",
			}
		)
		old_comm.insert()
		# Manually set creation date to 20 days ago
		frappe.db.set_value("Communication", old_comm.name, "creation", add_days(today(), -20))

		result = already_sent_recently("Test Customer Old", 15)
		self.assertFalse(result)

	def test_log_communication(self):
		"""Test logging a communication."""
		log_communication("Test Customer Log", "Test Subject")

		# Verify communication was created
		comm_exists = frappe.db.exists(
			"Communication",
			{"reference_doctype": "Customer", "reference_name": "Test Customer Log", "subject": "Test Subject"},
		)
		self.assertTrue(comm_exists)

	@patch("compliance_plus.compliance_plus.custom.license_tracker_cron.frappe.sendmail")
	def test_send_license_expiry_reminders_no_settings(self, mock_sendmail):
		"""Test send_license_expiry_reminders when settings are not configured."""
		# Create settings without email template or sender
		settings = frappe.get_single("Compliance Plus Settings")
		settings.email_template = None
		settings.sender = None
		settings.save()

		# Should return early without error
		send_license_expiry_reminders()

		# Verify no email was sent
		mock_sendmail.assert_not_called()

	def test_already_sent_recently_with_recent_communication(self):
		"""Test already_sent_recently with recent communication."""
		# Create a recent communication
		recent_comm = frappe.get_doc(
			{
				"doctype": "Communication",
				"communication_type": "Automated Message",
				"subject": "Recent Test Message",
				"reference_doctype": "Customer",
				"reference_name": "Test Customer Recent",
				"content": "Recent test content",
				"sent_or_received": "Sent",
			}
		)
		recent_comm.insert()

		result = already_sent_recently("Test Customer Recent", 15)
		self.assertTrue(result)

	def test_log_communication_fields(self):
		"""Test that log_communication creates correct fields."""
		log_communication("Test Customer Fields", "Test Subject Fields")

		comm = frappe.get_last_doc(
			"Communication",
			filters={
				"reference_doctype": "Customer",
				"reference_name": "Test Customer Fields",
			},
		)

		self.assertEqual(comm.communication_type, "Automated Message")
		self.assertEqual(comm.subject, "Test Subject Fields")
		self.assertEqual(comm.reference_doctype, "Customer")
		self.assertEqual(comm.reference_name, "Test Customer Fields")
		self.assertEqual(comm.sent_or_received, "Sent")
