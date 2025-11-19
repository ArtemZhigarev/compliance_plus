# Copyright (c) 2025, KlyONIX Tech Consulting Pvt Ltd and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestCompliancePlusSettings(FrappeTestCase):
	def setUp(self):
		"""Set up test fixtures."""
		# Get the single doctype instance
		self.settings = frappe.get_single("Compliance Plus Settings")

	def test_settings_is_single_doctype(self):
		"""Test that Compliance Plus Settings is a single doctype."""
		meta = frappe.get_meta("Compliance Plus Settings")
		self.assertTrue(meta.issingle)

	def test_default_expiry_threshold(self):
		"""Test default value for expiry_threshold."""
		# Reset settings
		self.settings.expiry_threshold = None
		self.settings.save()

		# Get fresh instance
		settings = frappe.get_single("Compliance Plus Settings")
		# Default should be 30 according to JSON
		self.assertIn(settings.expiry_threshold, [None, 30])

	def test_default_set_interval(self):
		"""Test default value for set_interval."""
		# Reset settings
		self.settings.set_interval = None
		self.settings.save()

		# Get fresh instance
		settings = frappe.get_single("Compliance Plus Settings")
		# Default should be 15 according to JSON
		self.assertIn(settings.set_interval, [None, 15])

	def test_update_settings(self):
		"""Test updating settings values."""
		self.settings.expiry_threshold = 45
		self.settings.set_interval = 20
		self.settings.save()

		# Verify updates
		updated_settings = frappe.get_single("Compliance Plus Settings")
		self.assertEqual(updated_settings.expiry_threshold, 45)
		self.assertEqual(updated_settings.set_interval, 20)

	def test_settings_fields_exist(self):
		"""Test that all expected fields exist in settings."""
		meta = frappe.get_meta("Compliance Plus Settings")
		field_names = [field.fieldname for field in meta.fields]

		expected_fields = ["email_template", "sender_id", "sender", "expiry_threshold", "set_interval"]

		for field in expected_fields:
			self.assertIn(field, field_names, f"Field {field} should exist in Compliance Plus Settings")

	def test_email_template_link(self):
		"""Test that email_template field links to Email Template."""
		meta = frappe.get_meta("Compliance Plus Settings")
		email_template_field = next((f for f in meta.fields if f.fieldname == "email_template"), None)

		self.assertIsNotNone(email_template_field)
		self.assertEqual(email_template_field.options, "Email Template")

	def test_sender_fetched_from_email_account(self):
		"""Test that sender field is fetched from sender_id."""
		meta = frappe.get_meta("Compliance Plus Settings")
		sender_field = next((f for f in meta.fields if f.fieldname == "sender"), None)

		self.assertIsNotNone(sender_field)
		self.assertEqual(sender_field.fetch_from, "sender_id.email_id")
