from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Dict, Set

from NEMO.decorators import accounting_or_user_office_or_manager_required
from NEMO.forms import ProjectForm
from NEMO.models import Account, ActivityHistory, MembershipHistory, Project, ProjectDocuments, User
from NEMO.utilities import render_combine_responses
from NEMO.views.accounts_and_projects import select_accounts_and_projects
from NEMO.views.customization import ProjectsAccountsCustomization
from django.contrib.auth.decorators import login_required, permission_required
from django.forms import models
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_http_methods

from NEMO_billing.customization import BillingCustomization
from NEMO_billing.invoices.models import ProjectBillingDetails
from NEMO_billing.invoices.utilities import render_and_send_email
from NEMO_billing.rates.models import RateCategory


class ProjectDetailsForm(models.ModelForm):
    class Meta:
        model = ProjectBillingDetails
        exclude = ["project"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["staff_host"].queryset = User.objects.filter(is_active=True, is_staff=True)


@accounting_or_user_office_or_manager_required
@require_http_methods(["GET", "POST"])
def edit_project(request, project_id=None):
    try:
        project = Project.objects.get(id=project_id)
    except (Project.DoesNotExist, ValueError):
        project = None
    try:
        project_details = project.projectbillingdetails
    except (ProjectBillingDetails.DoesNotExist, AttributeError):
        project_details = ProjectBillingDetails(project=project)
    form = ProjectForm(request.POST or None, instance=project)
    details_form = ProjectDetailsForm(request.POST or None, instance=project_details)
    dictionary = {
        "user_list": User.objects.filter(is_active=True),
        "rate_categories": RateCategory.objects.all(),
        "allow_document_upload": ProjectsAccountsCustomization.get_bool("project_allow_document_upload"),
        "form": form,
        "form_details": details_form,
    }
    if request.method == "GET":
        return render(request, "invoices/project/edit_project.html", dictionary)
    elif request.method == "POST":
        if not form.is_valid() or not details_form.is_valid():
            if request.FILES.getlist("project_documents") or request.POST.get("remove_documents"):
                form.add_error(field=None, error="Project document changes were lost, please resubmit them.")
            return render(request, "invoices/project/edit_project.html", dictionary)
        else:
            project = form.save()
            details_form.instance.project = project
            details_form.save()
            active_changed = form.initial.get("active", None) != project.active
            account_changed = form.initial.get("account", None) != project.account.id
            if not project_id or account_changed:
                if project_id and account_changed:
                    removed_account_history = MembershipHistory()
                    removed_account_history.authorizer = request.user
                    removed_account_history.action = MembershipHistory.Action.REMOVED
                    removed_account_history.child_content_object = project
                    removed_account_history.parent_content_object = Account.objects.get(id=form.initial["account"])
                    removed_account_history.save()
                account_history = MembershipHistory()
                account_history.authorizer = request.user
                account_history.action = MembershipHistory.Action.ADDED
                account_history.child_content_object = project
                account_history.parent_content_object = project.account
                account_history.save()
            if not project_id or active_changed:
                project_history = ActivityHistory()
                project_history.authorizer = request.user
                project_history.action = project.active
                project_history.content_object = project
                project_history.save()

            # Handle file uploads
            for f in request.FILES.getlist("project_documents"):
                ProjectDocuments.objects.create(document=f, project=project)
            ProjectDocuments.objects.filter(id__in=request.POST.getlist("remove_documents")).delete()

            return redirect("project", project.id)


@accounting_or_user_office_or_manager_required
@require_http_methods(["GET", "POST"])
def custom_project_view(request, kind=None, identifier=None):
    original_response = select_accounts_and_projects(request, kind=kind, identifier=identifier)
    projects = []
    if kind == "project":
        projects = Project.objects.filter(id=identifier)
    elif kind == "account":
        projects = Project.objects.filter(account_id=identifier)
    return render_combine_responses(
        request,
        original_response,
        "invoices/project/view_project_additional_info.html",
        {"projects": projects, "rate_categories": RateCategory.objects.exists()},
    )


@login_required
@require_GET
@permission_required("NEMO.trigger_timed_services", raise_exception=True)
def deactivate_expired_projects(request):
    return do_deactivate_expired_projects()


def do_deactivate_expired_projects():
    for project in Project.objects.filter(active=True, projectbillingdetails__expires_on__lt=datetime.now()):
        project.active = False
        project.save()
    send_project_expiration_reminders()
    return HttpResponse()


def send_project_expiration_reminders():
    accounting_email = BillingCustomization.get("billing_accounting_email_address")
    expiration_reminder_days = BillingCustomization.get("billing_project_expiration_reminder_days")
    if expiration_reminder_days:
        project_expiration_reminder_cc = BillingCustomization.get("billing_project_expiration_reminder_cc")
        email_projects: Dict[str, Set[Project]] = defaultdict(set)
        ccs = [e for e in project_expiration_reminder_cc.split(",") if e]
        for remaining_days in [int(days) for days in expiration_reminder_days.split(",")]:
            expiration_date = date.today() + timedelta(days=remaining_days)
            for project in Project.objects.filter(active=True, projectbillingdetails__expires_on=expiration_date):
                send_to = project.projectbillingdetails.email_to()
                for email_pi in send_to:
                    email_projects[email_pi].add(project)
        for pi_email, projects in email_projects.items():
            sorted_projects = sorted(projects, key=lambda x: x.projectbillingdetails.expires_on)
            render_and_send_email(
                "invoices/email/billing_project_expiration_reminder_email",
                {"projects": sorted_projects, "today": datetime.today().date()},
                to=[pi_email],
                from_email=accounting_email,
                cc=ccs,
            )
