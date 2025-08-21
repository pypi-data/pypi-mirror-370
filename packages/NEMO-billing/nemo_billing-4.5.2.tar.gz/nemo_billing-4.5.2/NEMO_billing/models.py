from __future__ import annotations

import datetime
from typing import List, Optional

from NEMO.constants import CHAR_FIELD_MEDIUM_LENGTH, CHAR_FIELD_SMALL_LENGTH
from NEMO.exceptions import ProjectChargeException
from NEMO.mixins import BillableItemMixin
from NEMO.models import (
    Area,
    BaseCategory,
    BaseModel,
    Consumable,
    Project,
    SerializationByNameModel,
    StaffCharge,
    Tool,
    User,
    validate_waive_information,
)
from django.core.exceptions import ValidationError
from django.core.validators import validate_comma_separated_integer_list
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from NEMO_billing.invoices.models import BillableItemType, InvoiceConfiguration
from NEMO_billing.templatetags.billing_tags import cap_discount_installed


class CoreFacility(BaseModel):
    name = models.CharField(
        max_length=CHAR_FIELD_MEDIUM_LENGTH, unique=True, help_text="The name of this core facility."
    )
    external_id = models.CharField(
        max_length=CHAR_FIELD_MEDIUM_LENGTH,
        null=True,
        blank=True,
        help_text="An external ID to associate with this core facility.",
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Core facilities"


class CoreRelationship(BaseModel):
    core_facility = models.ForeignKey(CoreFacility, on_delete=models.CASCADE)
    tool = models.OneToOneField(Tool, related_name="core_rel", blank=True, null=True, on_delete=models.CASCADE)
    area = models.OneToOneField(Area, related_name="core_rel", blank=True, null=True, on_delete=models.CASCADE)
    staff_charge = models.OneToOneField(
        StaffCharge, related_name="core_rel", blank=True, null=True, on_delete=models.CASCADE
    )
    consumable = models.OneToOneField(
        Consumable, related_name="core_rel", blank=True, null=True, on_delete=models.CASCADE
    )

    def get_item(self):
        return self.area or self.tool or self.consumable or self.staff_charge

    def __str__(self):
        return f"{self.get_item()} - {self.core_facility}"


class CustomCharge(BaseModel, BillableItemMixin):
    name = models.CharField(max_length=CHAR_FIELD_MEDIUM_LENGTH, help_text="The name of this custom charge.")
    additional_details = models.CharField(
        max_length=CHAR_FIELD_MEDIUM_LENGTH, null=True, blank=True, help_text="Additional details for this charge."
    )
    customer = models.ForeignKey(
        User, related_name="custom_charge_customer", on_delete=models.CASCADE, help_text="The customer to charge."
    )
    creator = models.ForeignKey(
        User,
        related_name="custom_charge_creator",
        on_delete=models.CASCADE,
        help_text="The person who created this charge.",
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, help_text="The project to bill for this charge.")
    date = models.DateTimeField(help_text="The date of the custom charge.")
    amount = models.DecimalField(
        decimal_places=2, max_digits=8, help_text="The amount of the charge. Use a negative amount for adjustments."
    )
    core_facility = models.ForeignKey(CoreFacility, null=True, blank=True, on_delete=models.SET_NULL)
    cap_eligible = models.BooleanField(default=False, help_text="Check this box to make this charge count towards CAP")
    validated = models.BooleanField(default=False)
    validated_by = models.ForeignKey(
        User, null=True, blank=True, related_name="custom_charge_validated_set", on_delete=models.CASCADE
    )
    waived = models.BooleanField(default=False)
    waived_on = models.DateTimeField(null=True, blank=True)
    waived_by = models.ForeignKey(
        User, null=True, blank=True, related_name="custom_charge_waived_set", on_delete=models.CASCADE
    )

    def clean(self):
        errors = {}
        if self.amount == 0:
            errors["amount"] = _("Please enter a positive or negative amount")
        if self.project_id and self.customer_id:
            try:
                from NEMO.policy import policy_class as policy

                policy.check_billing_to_project(self.project, self.customer, self, self)
            except ProjectChargeException as e:
                errors["project"] = e.msg
        if cap_discount_installed():
            # If this custom charge is cap eligible, check that there is actually a matching CAP configuration
            if self.cap_eligible:
                if self.customer_id and self.project_id:
                    from NEMO_billing.cap_discount.models import CAPDiscountConfiguration

                    rate_category = self.project.projectbillingdetails.category
                    from NEMO_billing.invoices.models import BillableItemType

                    cap_filter = CAPDiscountConfiguration.objects.filter(
                        rate_category=rate_category,
                        charge_types__contains=BillableItemType.CUSTOM_CHARGE.value,
                    )
                    if self.core_facility:
                        cap_filter = cap_filter.filter(core_facilities__in=[self.core_facility])
                    else:
                        cap_filter = cap_filter.filter(core_facilities__isnull=True)
                    if not cap_filter.exists():
                        errors["cap_eligible"] = _(
                            f"No CAP configuration accepting Custom charges exists for this rate category ({rate_category})"
                        )
        errors.update(validate_waive_information(self))
        if errors:
            raise ValidationError(errors)

    # To match BillableItemMixin
    def get_customer(self) -> User:
        return self.customer

    def get_operator(self) -> Optional[User]:
        return self.creator

    def get_start(self) -> Optional[datetime.datetime]:
        return None

    def get_end(self) -> Optional[datetime.datetime]:
        return self.date

    def __str__(self):
        return self.name


# Create and add a shortcut function to get core_facility from Tool, Consumable, Area or Staff Charge
def get_core_facility(self):
    # Add an exception for tool children, whose core facility is the parent's core facility
    if isinstance(self, Tool) and self.is_child_tool():
        return self.parent_tool.core_facility
    if hasattr(self, "core_rel"):
        return self.core_rel.core_facility


class Department(BaseCategory):
    pass


class InstitutionType(BaseCategory):
    pass


class Institution(SerializationByNameModel):
    name = models.CharField(
        max_length=CHAR_FIELD_MEDIUM_LENGTH, unique=True, help_text="The unique name for this institution"
    )
    institution_type = models.ForeignKey(InstitutionType, null=True, blank=True, on_delete=models.SET_NULL)
    state = models.CharField(max_length=CHAR_FIELD_SMALL_LENGTH, null=True, blank=True)
    country = models.CharField(
        max_length=2,
        choices=[
            ("AF", "Afghanistan"),
            ("AL", "Albania"),
            ("DZ", "Algeria"),
            ("AD", "Andorra"),
            ("AO", "Angola"),
            ("AI", "Anguilla"),
            ("AQ", "Antarctica"),
            ("AG", "Antigua & Barbuda"),
            ("AR", "Argentina"),
            ("AM", "Armenia"),
            ("AW", "Aruba"),
            ("AU", "Australia"),
            ("AT", "Austria"),
            ("AZ", "Azerbaijan"),
            ("BS", "Bahamas"),
            ("BH", "Bahrain"),
            ("BD", "Bangladesh"),
            ("BB", "Barbados"),
            ("BY", "Belarus"),
            ("BE", "Belgium"),
            ("BZ", "Belize"),
            ("BJ", "Benin"),
            ("BM", "Bermuda"),
            ("BT", "Bhutan"),
            ("BO", "Bolivia"),
            ("BA", "Bosnia & Herzegovina"),
            ("BW", "Botswana"),
            ("BV", "Bouvet Island"),
            ("BR", "Brazil"),
            ("GB", "Britain (UK)"),
            ("IO", "British Indian Ocean Territory"),
            ("BN", "Brunei"),
            ("BG", "Bulgaria"),
            ("BF", "Burkina Faso"),
            ("BI", "Burundi"),
            ("KH", "Cambodia"),
            ("CM", "Cameroon"),
            ("CA", "Canada"),
            ("CV", "Cape Verde"),
            ("BQ", "Caribbean NL"),
            ("KY", "Cayman Islands"),
            ("CF", "Central African Rep."),
            ("TD", "Chad"),
            ("CL", "Chile"),
            ("CN", "China"),
            ("CX", "Christmas Island"),
            ("CC", "Cocos (Keeling) Islands"),
            ("CO", "Colombia"),
            ("KM", "Comoros"),
            ("CD", "Congo (Dem. Rep.)"),
            ("CG", "Congo (Rep.)"),
            ("CK", "Cook Islands"),
            ("CR", "Costa Rica"),
            ("HR", "Croatia"),
            ("CU", "Cuba"),
            ("CW", "Curaçao"),
            ("CY", "Cyprus"),
            ("CZ", "Czech Republic"),
            ("CI", "Côte d'Ivoire"),
            ("DK", "Denmark"),
            ("DJ", "Djibouti"),
            ("DM", "Dominica"),
            ("DO", "Dominican Republic"),
            ("TL", "East Timor"),
            ("EC", "Ecuador"),
            ("EG", "Egypt"),
            ("SV", "El Salvador"),
            ("GQ", "Equatorial Guinea"),
            ("ER", "Eritrea"),
            ("EE", "Estonia"),
            ("SZ", "Eswatini (Swaziland)"),
            ("ET", "Ethiopia"),
            ("FK", "Falkland Islands"),
            ("FO", "Faroe Islands"),
            ("FJ", "Fiji"),
            ("FI", "Finland"),
            ("FR", "France"),
            ("GF", "French Guiana"),
            ("PF", "French Polynesia"),
            ("TF", "French S. Terr."),
            ("GA", "Gabon"),
            ("GM", "Gambia"),
            ("GE", "Georgia"),
            ("DE", "Germany"),
            ("GH", "Ghana"),
            ("GI", "Gibraltar"),
            ("GR", "Greece"),
            ("GL", "Greenland"),
            ("GD", "Grenada"),
            ("GP", "Guadeloupe"),
            ("GU", "Guam"),
            ("GT", "Guatemala"),
            ("GG", "Guernsey"),
            ("GN", "Guinea"),
            ("GW", "Guinea-Bissau"),
            ("GY", "Guyana"),
            ("HT", "Haiti"),
            ("HM", "Heard Island & McDonald Islands"),
            ("HN", "Honduras"),
            ("HK", "Hong Kong"),
            ("HU", "Hungary"),
            ("IS", "Iceland"),
            ("IN", "India"),
            ("ID", "Indonesia"),
            ("IR", "Iran"),
            ("IQ", "Iraq"),
            ("IE", "Ireland"),
            ("IM", "Isle of Man"),
            ("IL", "Israel"),
            ("IT", "Italy"),
            ("JM", "Jamaica"),
            ("JP", "Japan"),
            ("JE", "Jersey"),
            ("JO", "Jordan"),
            ("KZ", "Kazakhstan"),
            ("KE", "Kenya"),
            ("KI", "Kiribati"),
            ("KP", "Korea (North)"),
            ("KR", "Korea (South)"),
            ("KW", "Kuwait"),
            ("KG", "Kyrgyzstan"),
            ("LA", "Laos"),
            ("LV", "Latvia"),
            ("LB", "Lebanon"),
            ("LS", "Lesotho"),
            ("LR", "Liberia"),
            ("LY", "Libya"),
            ("LI", "Liechtenstein"),
            ("LT", "Lithuania"),
            ("LU", "Luxembourg"),
            ("MO", "Macau"),
            ("MG", "Madagascar"),
            ("MW", "Malawi"),
            ("MY", "Malaysia"),
            ("MV", "Maldives"),
            ("ML", "Mali"),
            ("MT", "Malta"),
            ("MH", "Marshall Islands"),
            ("MQ", "Martinique"),
            ("MR", "Mauritania"),
            ("MU", "Mauritius"),
            ("YT", "Mayotte"),
            ("MX", "Mexico"),
            ("FM", "Micronesia"),
            ("MD", "Moldova"),
            ("MC", "Monaco"),
            ("MN", "Mongolia"),
            ("ME", "Montenegro"),
            ("MS", "Montserrat"),
            ("MA", "Morocco"),
            ("MZ", "Mozambique"),
            ("MM", "Myanmar (Burma)"),
            ("NA", "Namibia"),
            ("NR", "Nauru"),
            ("NP", "Nepal"),
            ("NL", "Netherlands"),
            ("NC", "New Caledonia"),
            ("NZ", "New Zealand"),
            ("NI", "Nicaragua"),
            ("NE", "Niger"),
            ("NG", "Nigeria"),
            ("NU", "Niue"),
            ("NF", "Norfolk Island"),
            ("MK", "North Macedonia"),
            ("MP", "Northern Mariana Islands"),
            ("NO", "Norway"),
            ("OM", "Oman"),
            ("PK", "Pakistan"),
            ("PW", "Palau"),
            ("PS", "Palestine"),
            ("PA", "Panama"),
            ("PG", "Papua New Guinea"),
            ("PY", "Paraguay"),
            ("PE", "Peru"),
            ("PH", "Philippines"),
            ("PN", "Pitcairn"),
            ("PL", "Poland"),
            ("PT", "Portugal"),
            ("PR", "Puerto Rico"),
            ("QA", "Qatar"),
            ("RO", "Romania"),
            ("RU", "Russia"),
            ("RW", "Rwanda"),
            ("RE", "Réunion"),
            ("AS", "Samoa (American)"),
            ("WS", "Samoa (western)"),
            ("SM", "San Marino"),
            ("ST", "Sao Tome & Principe"),
            ("SA", "Saudi Arabia"),
            ("SN", "Senegal"),
            ("RS", "Serbia"),
            ("SC", "Seychelles"),
            ("SL", "Sierra Leone"),
            ("SG", "Singapore"),
            ("SK", "Slovakia"),
            ("SI", "Slovenia"),
            ("SB", "Solomon Islands"),
            ("SO", "Somalia"),
            ("ZA", "South Africa"),
            ("GS", "South Georgia & the South Sandwich Islands"),
            ("SS", "South Sudan"),
            ("ES", "Spain"),
            ("LK", "Sri Lanka"),
            ("BL", "St Barthelemy"),
            ("SH", "St Helena"),
            ("KN", "St Kitts & Nevis"),
            ("LC", "St Lucia"),
            ("SX", "St Maarten (Dutch)"),
            ("MF", "St Martin (French)"),
            ("PM", "St Pierre & Miquelon"),
            ("VC", "St Vincent"),
            ("SD", "Sudan"),
            ("SR", "Suriname"),
            ("SJ", "Svalbard & Jan Mayen"),
            ("SE", "Sweden"),
            ("CH", "Switzerland"),
            ("SY", "Syria"),
            ("TW", "Taiwan"),
            ("TJ", "Tajikistan"),
            ("TZ", "Tanzania"),
            ("TH", "Thailand"),
            ("TG", "Togo"),
            ("TK", "Tokelau"),
            ("TO", "Tonga"),
            ("TT", "Trinidad & Tobago"),
            ("TN", "Tunisia"),
            ("TR", "Turkey"),
            ("TM", "Turkmenistan"),
            ("TC", "Turks & Caicos Is"),
            ("TV", "Tuvalu"),
            ("UM", "US minor outlying islands"),
            ("UG", "Uganda"),
            ("UA", "Ukraine"),
            ("AE", "United Arab Emirates"),
            ("US", "United States"),
            ("UY", "Uruguay"),
            ("UZ", "Uzbekistan"),
            ("VU", "Vanuatu"),
            ("VA", "Vatican City"),
            ("VE", "Venezuela"),
            ("VN", "Vietnam"),
            ("VG", "Virgin Islands (UK)"),
            ("VI", "Virgin Islands (US)"),
            ("WF", "Wallis & Futuna"),
            ("EH", "Western Sahara"),
            ("YE", "Yemen"),
            ("ZM", "Zambia"),
            ("ZW", "Zimbabwe"),
            ("AX", "Åland Islands"),
        ],
    )
    zip_code = models.CharField(max_length=12, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class ProjectBillingHardCap(BaseModel):
    enabled = models.BooleanField(default=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    configuration = models.ForeignKey(InvoiceConfiguration, null=True, blank=True, on_delete=models.CASCADE)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    amount = models.DecimalField(decimal_places=2, max_digits=14)
    charge_types = models.CharField(
        validators=[validate_comma_separated_integer_list],
        max_length=CHAR_FIELD_SMALL_LENGTH,
        help_text="List of charge types that will count towards this CAP",
    )

    @property
    def billable_charge_types(self) -> List[BillableItemType]:
        return [BillableItemType(int(value)) for value in self.charge_types.split(",") if value]

    def get_charge_types_display(self):
        return mark_safe(
            "<br>".join([charge_type.friendly_display_name() for charge_type in self.billable_charge_types])
        )

    def clean(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError(
                {
                    "start_date": _("Start date must be before end date"),
                }
            )
        if self.project_id:
            if not self.project.projectbillingdetails.no_tax and not self.configuration:
                raise ValidationError(
                    {
                        "configuration": _(
                            "Configuration is required for taxed projects. Select a configuration or make the project tax exempt"
                        )
                    }
                )

    class Meta:
        ordering = ["-start_date"]


setattr(Tool, "core_facility", property(get_core_facility))
setattr(Consumable, "core_facility", property(get_core_facility))
setattr(Area, "core_facility", property(get_core_facility))
setattr(StaffCharge, "core_facility", property(get_core_facility))
