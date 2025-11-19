import frappe
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def already_sent_recently(customer, interval_days):
	threshold_date = datetime.today() - timedelta(days=interval_days)
	return frappe.db.exists(
		"Communication",
		{
			"reference_doctype": "Customer",
			"reference_name": customer,
			"communication_type": "Automated Message",
			"creation": [">", threshold_date.strftime("%Y-%m-%d")],
		},
	)


def log_communication(customer, subject):
	frappe.get_doc(
		{
			"doctype": "Communication",
			"communication_type": "Automated Message",
			"subject": subject,
			"reference_doctype": "Customer",
			"reference_name": customer,
			"content": subject,
			"sent_or_received": "Sent",
		}
	).insert(ignore_permissions=True)

def send_license_expiry_reminders():
	settings = frappe.get_single("Compliance Plus Settings")
	expiry_threshold = settings.expiry_threshold or 15
	set_interval = settings.set_interval or 15
	sender = settings.sender
	template_name = settings.email_template

	if not sender or not template_name:
		frappe.log_error("Sender or Email Template not configured.", "License Expiry Configuration Error")
		logger.error("Sender or Email Template not configured in Compliance Plus Settings")
		return

	try:
		template = frappe.get_doc("Email Template", template_name)
	except Exception as e:
		frappe.log_error("Invalid Email Template", frappe.get_traceback())
		logger.error(f"Failed to load Email Template '{template_name}': {str(e)}")
		return

	today = datetime.today().date()
	target_expiry_date = today + timedelta(days=expiry_threshold)

	customers = frappe.get_all(
		"Customer", filters={"disabled": 0}, fields=["name", "customer_name", "email_id"]
	)

	emails_sent = 0
	customers_skipped = 0

	for customer in customers:
		if not customer.email_id:
			logger.info(f"Skipped customer {customer.name}: No email ID")
			customers_skipped += 1
			continue

		if already_sent_recently(customer.name, set_interval):
			logger.info(f"Skipped customer {customer.name}: Email already sent recently")
			customers_skipped += 1
			continue

		dl_details = frappe.get_all(
			"Drug License Details",
			filters={"parent": customer.name, "expiry_date": ["between", [today, target_expiry_date]]},
			fields=["license_number", "expiry_date"],
		)

		fssai_details = frappe.get_all(
			"FSSAI Details",
			filters={"parent": customer.name, "expiry_date": ["between", [today, target_expiry_date]]},
			fields=["license_number", "expiry_date"],
		)

		if not dl_details and not fssai_details:
			logger.info(f"Skipped customer {customer.name}: No expiring licenses")
			customers_skipped += 1
			continue

		context = {
			"doc": {
				"customer_name": customer.customer_name,
				"company": frappe.defaults.get_global_default("company"),
				"fsl_dl_details": dl_details,
				"fsl_fssai_details": fssai_details,
			}
		}

		try:
			message = frappe.render_template(template.response, context)
		except Exception:
			frappe.log_error("Template Render Failed", frappe.get_traceback())
			logger.error(f"Failed to render template for customer {customer.name}")
			continue

		try:
			frappe.sendmail(
				recipients=[customer.email_id], sender=sender, subject=template.subject, message=message
			)
			log_communication(customer.name, template.subject)
			logger.info(f"Email queued for {customer.email_id}")
			emails_sent += 1
		except Exception:
			frappe.log_error("Email Send Failed", frappe.get_traceback())
			logger.error(f"Failed to send email to {customer.email_id}")

	logger.info(
		f"License expiry reminder cron completed: {emails_sent} emails sent, {customers_skipped} customers skipped"
	)
