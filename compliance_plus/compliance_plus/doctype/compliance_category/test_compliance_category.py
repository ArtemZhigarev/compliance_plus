# Copyright (c) 2025, KlyONIX Tech Consulting Pvt Ltd and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestComplianceCategory(FrappeTestCase):
	def setUp(self):
		"""Set up test fixtures."""
		# Clean up any existing test categories
		frappe.db.delete("Compliance Category", {"category_name": ["like", "Test Category%"]})
		frappe.db.commit()

	def tearDown(self):
		"""Clean up after tests."""
		frappe.db.delete("Compliance Category", {"category_name": ["like", "Test Category%"]})
		frappe.db.commit()

	def test_create_compliance_category(self):
		"""Test creating a basic compliance category."""
		category = frappe.get_doc(
			{
				"doctype": "Compliance Category",
				"category_name": "Test Category 1",
				"description": "Test Description",
				"is_active": 1,
			}
		)
		category.insert()

		self.assertEqual(category.category_name, "Test Category 1")
		self.assertEqual(category.description, "Test Description")
		self.assertEqual(category.is_active, 1)

		# Verify it was saved to database
		saved_category = frappe.get_doc("Compliance Category", "Test Category 1")
		self.assertEqual(saved_category.category_name, "Test Category 1")

	def test_category_name_is_required(self):
		"""Test that category name is a required field."""
		category = frappe.get_doc(
			{"doctype": "Compliance Category", "description": "Test Description", "is_active": 1}
		)

		with self.assertRaises(frappe.exceptions.MandatoryError):
			category.insert()

	def test_category_name_is_unique(self):
		"""Test that category name must be unique."""
		# Create first category
		category1 = frappe.get_doc(
			{
				"doctype": "Compliance Category",
				"category_name": "Test Category Unique",
				"description": "First Category",
				"is_active": 1,
			}
		)
		category1.insert()

		# Try to create duplicate
		category2 = frappe.get_doc(
			{
				"doctype": "Compliance Category",
				"category_name": "Test Category Unique",
				"description": "Duplicate Category",
				"is_active": 1,
			}
		)

		with self.assertRaises(frappe.exceptions.DuplicateEntryError):
			category2.insert()

	def test_default_is_active_value(self):
		"""Test that is_active defaults to 0."""
		category = frappe.get_doc(
			{"doctype": "Compliance Category", "category_name": "Test Category Default", "description": "Test"}
		)
		category.insert()

		self.assertEqual(category.is_active, 0)

	def test_update_compliance_category(self):
		"""Test updating an existing compliance category."""
		category = frappe.get_doc(
			{
				"doctype": "Compliance Category",
				"category_name": "Test Category Update",
				"description": "Original Description",
				"is_active": 0,
			}
		)
		category.insert()

		# Update the category
		category.description = "Updated Description"
		category.is_active = 1
		category.save()

		# Verify updates
		updated_category = frappe.get_doc("Compliance Category", "Test Category Update")
		self.assertEqual(updated_category.description, "Updated Description")
		self.assertEqual(updated_category.is_active, 1)
