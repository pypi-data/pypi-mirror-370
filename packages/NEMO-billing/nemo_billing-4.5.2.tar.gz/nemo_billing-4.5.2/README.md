# NEMO billing

This billing plugin for NEMO includes core facilities and custom charges/adjustments.
It also includes sub-modules for adding rates and invoices.


# Installation

`pip install NEMO-billing`

# Add core billing plugin

in `settings.py` add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    '...',
    'NEMO_billing',  # Add before NEMO to have new navbar menu items show up
    'NEMO_billing.rates',
    'NEMO_billing.invoices',
    # 'NEMO_billing.cap_discount',  # Optional
    # 'NEMO_billing.prepayments',  # Optional
    # 'NEMO_billing.quotes',  # Optional
    '...',
    # 'NEMO_user_details',  # If using user details plugin
    '...',
    'NEMO',
    '...'
]
```

### NEMO Compatibility

NEMO & NEMO-CE >= 7.2.0 ----> NEMO-Billing >= 4.4.0

NEMO & NEMO-CE >= 7.0.0 ----> NEMO-Billing >= 4.0.0

NEMO & NEMO-CE >= 6.0.0 ----> NEMO-Billing >= 3.0.0

NEMO >= 5.5.3 NEMO-CE >= 2.4.4 ----> NEMO-Billing >= 2.9.4

NEMO >= 5.5.2 ----> NEMO-Billing >= 2.9.1

NEMO >= 5.5.0 ----> NEMO-Billing >= 2.9.0

NEMO >= 5.3.0 ----> NEMO-Billing >= 2.8.0

NEMO >= 4.7.0 ----> NEMO-Billing >= 2.7.0

NEMO >= 4.6.4 ----> NEMO-Billing >= 2.6.13

NEMO >= 4.6.0 ----> NEMO-Billing >= 2.5.8

NEMO >= 4.5.0 ----> NEMO-Billing >= 2.0.0

NEMO >= 4.3.0 ----> NEMO-Billing >= 1.23.0

NEMO >= 4.2.1 ----> NEMO-Billing >= 1.22.2

NEMO >= 4.2.0 ----> NEMO-Billing >= 1.22.1

NEMO >= 4.1.0 ----> NEMO-Billing >= 1.19.0

NEMO >= 4.0.0 ----> NEMO-Billing >= 1.18.0

NEMO >= 3.14.0 ----> NEMO-Billing >= 1.16.0

NEMO >= 3.13.0 ----> NEMO-Billing >= 1.13.0

NEMO 3.10.0 to 3.12.2 ----> NEMO-Billing 1.5.0 to 1.12.0 

### Usage

This plugin will add core facilities and custom charges which can be added through django admin.

Core Facility can be set on Custom Charges, Tools, Areas, Consumables and Staff Charges

There are 2 ways to set them up:
1. In Detailed Administration -> Core Facilities, you can select each tool, area, consumable or staff charge
2. In Detailed Administration -> NEMO on each individual custom charge, tool, area, consumable or staff charge

Core Facility can be accessed on a tool, area, consumable or staff charge using:
`tool.core_facility`, `area.core_facility`, `consumable.core_facility` or  `staff_charge.core_facility`

### Options
By default, a Core Facility is not required for each custom charge, tool, area, consumable or staff charge.

That can be changed by updating the following default settings in `settings.py`:

```python
TOOL_CORE_FACILITY_REQUIRED = False
AREA_CORE_FACILITY_REQUIRED = False
CONSUMABLE_CORE_FACILITY_REQUIRED = False
STAFF_CHARGE_CORE_FACILITY_REQUIRED = False
CUSTOM_CHARGE_CORE_FACILITY_REQUIRED = False
```

In the billing (user, project billing, billing API, invoices) tool usage and area access on behalf of a user (only during a remote project) are categorized as Staff Charges.

That can be changed by updating the following default settings in `settings.py`

```python
STAFF_TOOL_USAGE_AS_STAFF_CHARGE = True
STAFF_AREA_ACCESS_AS_STAFF_CHARGE = True
```


# Add Rates plugin

in `settings.py` add to `INSTALLED_APPS`:

    'NEMO_billing.rates',

### Rates module options
The following default properties can be changed in `settings.py`

```python
# The display rate currency is set to $ by default
RATE_CURRENCY = "CAD "
# Missed reservations rates will have the "flat" checkbox checked by default
DEFAULT_MISSED_RESERVATION_FLAT = True
# The rate list URL can be customized
RATE_LIST_URL = "fee_schedule"
```


# Add Invoices plugin

in `settings.py` add to `INSTALLED_APPS`:

    'NEMO_billing.invoices',

### Invoices module options
The following default properties can be changed in `settings.py`:

```python
# Date formats
INVOICE_DATETIME_FORMAT = "%m/%d/%Y %H:%M:%S"
INVOICE_DATE_FORMAT = "%B %d, %Y"
# Invoice email prefix
INVOICE_EMAIL_SUBJECT_PREFIX = "[NEMO Billing] "
# Whether to validate that all billable items belong to a core facility before generating invoice
INVOICE_ALL_ITEMS_MUST_BE_IN_FACILITY = False 
```


# Add CAP discount plugin

in `settings.py` add to `INSTALLED_APPS`:

    'NEMO_billing.cap_discount',

CAP Discount settings are available in Customization -> Billing CAP


# Add Project prepayments/funds plugin

in `settings.py` add to `INSTALLED_APPS`:

    'NEMO_billing.prepayments',


### Email templates
To change email templates, either go to Invoices customization settings in NEMO and upload new files, or directly create a file in NEMO's media folder with the same name.<br>
The following templates can be set:

* `email_send_invoice_subject.txt`
* `email_send_invoice_message.html`
* `email_send_invoice_reminder_subject.txt`
* `email_send_invoice_reminder_message.html`
* `billing_project_expiration_reminder_email_subject.txt`
* `billing_project_expiration_reminder_email_message.html`

### Timed services/cron jobs
To send reminder emails, set a cron job daily with one of the 2 options:

1. send an authenticated http request to `<nemo_url>/invoices/send_invoice_payment_reminder`
2. run command `django-admin send_invoice_payment_reminder` or `python manage.py send_invoice_payment_reminder`

Similarly, to automatically deactivate expired projects and send expiration reminders, set a cron job daily with one of the 2 options:

1. send an authenticated http request to `<nemo_url>/projects/deactivate_expired_projects`
2. run command `django-admin deactivate_expired_projects` or `python manage.py deactivate_expired_projects`


# Add Quotes plugin

in `settings.py` add to `INSTALLED_APPS`:

    'NEMO_billing.quotes',


### Email templates
To add email templates, either go to Quotes customization settings in NEMO and upload new files, or directly create a file in NEMO's media folder with the same name.<br>
The following templates are available in the [resources folder](https://gitlab.com/nemo-community/atlantis-labs/nemo-billing/-/blob/master/resources/emails):

* `quote_email.html`
* `quote_approval_request_email.html`
* `quote_status_update_email.html`


### Dashboard icon
You can add a dashboard icon in `Detailed administration -> Landing page choices`:
- Icon: [quotes.png](https://gitlab.com/nemo-community/atlantis-labs/nemo-billing/-/blob/master/resources/icons/quotes.png)
- URL: `/quotes` 

### URL
- make sure `<nemo_url>/public_quote/*` URL is public in your webserver (nginx, apache, etc.)

# Post Installation

run:

`python manage.py migrate`
