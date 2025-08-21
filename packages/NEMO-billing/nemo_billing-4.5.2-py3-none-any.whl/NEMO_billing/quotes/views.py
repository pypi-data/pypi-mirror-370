from datetime import datetime
from logging import getLogger
from urllib.parse import urlencode

from NEMO.models import Area, Consumable, Project, Tool, User
from NEMO.utilities import render_email_template, send_mail
from NEMO.views.customization import get_media_file_contents
from NEMO.views.pagination import SortedPaginator
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods

from NEMO_billing.invoices.utilities import flatten
from NEMO_billing.quotes.exceptions import FailedToSendQuoteEmailException, QuoteGenerationException
from NEMO_billing.quotes.forms import CreateQuoteForm, EditQuoteForm, QuoteItemForm
from NEMO_billing.quotes.models import Quote, QuoteConfiguration, QuoteItem
from NEMO_billing.quotes.utilities import (
    QUOTE_EMAIL_CATEGORY,
    available_configurations_for_user_to_create,
    available_configurations_for_user_to_create_or_approve,
    can_access_quotes,
    can_create_quotes,
    create_approval_request_notification,
    delete_approval_request_notification,
    get_approval_request_notifications_per_configuration,
    meets_send_email_prerequisites,
)
from NEMO_billing.rates.models import Rate, RateType
from NEMO_billing.rates.utilities import RateHistory
from NEMO_billing.rates.views import get_rate_type_choices, get_rate_types

quotes_logger = getLogger(__name__)


@login_required
@user_passes_test(can_access_quotes)
@require_GET
def quote_list(request, selected_configuration_id=None):
    user = request.user
    quote_configurations = QuoteConfiguration.objects.all()
    configurations_info = []
    configurations_exist = quote_configurations.exists()
    page = []
    selected_configuration = None
    status_filter = request.GET.get("status")

    if configurations_exist:
        if not selected_configuration_id:
            user_configurations = available_configurations_for_user_to_create_or_approve(user)
            selected_configuration = user_configurations[0] if user_configurations else quote_configurations.first()
            if selected_configuration:
                return redirect("quotes", selected_configuration_id=selected_configuration.id)
        else:
            selected_configuration = get_object_or_404(QuoteConfiguration, pk=selected_configuration_id)

        # Filter quotes based on selected configuration and status filter and paginate results
        quotes = Quote.objects.all()
        if selected_configuration:
            quotes = quotes.filter(configuration=selected_configuration.id)
        if status_filter:
            quotes = quotes.filter(status=status_filter)
        page = SortedPaginator(quotes, request).get_current_page()

        # Fetch notifications for configurations
        notification_map = get_approval_request_notifications_per_configuration(user)
        for configuration in quote_configurations:
            configuration_info = {
                "id": configuration.id,
                "name": configuration.name,
                "notification_count": notification_map.get(configuration.id, 0),
            }
            configurations_info.append(configuration_info)

    return render(
        request,
        "quotes/quote_list.html",
        {
            "page": page,
            "quote_configurations": configurations_info,
            "configurations_exist": configurations_exist,
            "selected_configuration": selected_configuration,
            "quote_statuses": Quote.Status.Choices,
            "selected_status": status_filter,
            "user_can_create": selected_configuration.can_user_create(user) if selected_configuration else False,
        },
    )


@login_required
@user_passes_test(can_create_quotes)
@require_http_methods(["GET", "POST"])
def create_quote(request, selected_configuration_id=None):
    user = request.user
    available_configurations = available_configurations_for_user_to_create(user)
    selected_configuration = None

    if selected_configuration_id:
        selected_configuration = get_object_or_404(QuoteConfiguration, pk=selected_configuration_id)
        if selected_configuration not in available_configurations:
            messages.error(request, "You do not have permission to create quotes with the selected configuration.")
            return redirect("create_quote")

    form = CreateQuoteForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            try:
                # Check that the user has permission to create quotes with the selected configuration
                configuration = form.cleaned_data.get("configuration")
                if not configuration.can_user_create(user):
                    messages.error(
                        request, "You don't have permission to create quotes with the selected configuration."
                    )
                    return render(
                        request, "quotes/create_quote.html", {"form": form, "configurations": available_configurations}
                    )

                quote = form.save(commit=False)
                quote.creator = user
                quote.status = Quote.Status.DRAFT
                quote.save()

                messages.success(request, "Quote created successfully.")
                return redirect("quote", quote_id=quote.id)
            except QuoteConfiguration.DoesNotExist:
                messages.error(request, "Selected configuration does not exist.")

    return render(
        request,
        "quotes/create_quote.html",
        {
            "form": form,
            "configurations": available_configurations,
            "selected_configuration": selected_configuration,
            "user_can_create": selected_configuration.can_user_create(user),
        },
    )


@login_required
@user_passes_test(can_access_quotes)
@require_http_methods(["GET", "POST"])
def view_quote(request, quote_id):
    user = request.user
    rate_type_choice = request.GET.get("type")
    item_id = request.GET.get("id")
    quote_obj = get_object_or_404(Quote, id=quote_id)
    quote_items = quote_obj.quoteitem_set.all()
    form = EditQuoteForm(request.POST or None, instance=get_object_or_404(Quote, id=quote_id))
    permissions = quote_obj.permissions(user)
    submitted_users = None
    show_send_emails_button = meets_send_email_prerequisites(quote_obj) and permissions["can_send_emails"]
    active_quote_item_tab = "rate"

    if request.method == "POST":
        user_ids = form.data.getlist("users")
        submitted_users = User.objects.filter(id__in=user_ids)

        if not permissions["can_edit_metadata"]:
            messages.error(request, "Cannot edit quote.")
            return redirect("quote", quote_id=quote_id)

        if form.is_valid():
            quote_obj = form.save()
            # Re-render the quote file if it has been updated (the linked project might have changed)
            try:
                quote_obj.render_and_save()
            except QuoteGenerationException as e:
                messages.warning(request, f"Quote '{quote_obj.name}' updated successfully but failed to render file.")
                return redirect("quote", quote_id=quote_obj.id)

            messages.success(request, f"Quote '{quote_obj.name}' updated successfully!")
            return redirect("quote", quote_id=quote_obj.id)

    context = {
        "quote": quote_obj,
        "quote_items": quote_items,
        "submitted": quote_obj.status == Quote.Status.PENDING_APPROVAL,
        "published": quote_obj.status == Quote.Status.PUBLISHED,
        "draft": quote_obj.status == Quote.Status.DRAFT,
        "updated": quote_obj.updated_date != quote_obj.created_date,
        "users": User.objects.filter(is_active=True).exclude(id=user.id),
        "projects": Project.objects.all(),
        "form": form,
        "submitted_users": submitted_users,
        "active_quote_item_tab": active_quote_item_tab,
        "show_send_emails_button": show_send_emails_button,
    }
    rate_search_context = get_rate_search_context(rate_type_choice, item_id)
    context.update(rate_search_context)
    context.update(permissions)

    return render(request, "quotes/quote.html", context)


@login_required
@user_passes_test(can_create_quotes)
@require_http_methods(["POST"])
def add_quote_item(request, quote_id):
    quote_obj = get_object_or_404(Quote, id=quote_id)
    user = request.user
    rate_type_choice = request.POST.get("rate_type_choice")
    item_id = request.POST.get("rate_type_item_id")
    permissions = quote_obj.permissions(user)
    show_send_emails_button = meets_send_email_prerequisites(quote_obj) and permissions["can_send_emails"]
    form = EditQuoteForm(instance=get_object_or_404(Quote, id=quote_id))
    # quote_item_type is used to determine which form was submitted (rate or custom)
    active_form_type = request.POST.get("quote_item_type")

    if not permissions["can_edit"]:
        messages.error(request, "You do not have permission to add items to this quote.")
        return redirect("quote", quote_id=quote_id)

    rate_id = request.POST.get("rate")
    rate = None
    if rate_id:
        try:
            rate = Rate.non_deleted().get(id=rate_id)

        except Rate.DoesNotExist:
            messages.error(request, "Selected rate does not exist.")
            return redirect("quote", quote_id=quote_id)

    defaults = (
        {
            "description": rate.quote_display(),
            "amount": rate.amount,
            "minimum_charge": rate.minimum_charge,
            "rate_type": get_rate_type(rate),
        }
        if rate
        else {}
    )

    item_form = QuoteItemForm(merge_post_data_with_defaults(request.POST, defaults))

    if item_form.is_valid():
        quote_item = item_form.save(commit=False)
        quote_item.quote = quote_obj
        quote_item.save()
        messages.success(request, "Item added to quote successfully!")

        # Redirect to the quote page with the rate type and item id selected
        url = reverse("quote", kwargs={"quote_id": quote_id})
        if rate_type_choice or item_id:
            query_params = {}
            if rate_type_choice:
                query_params["type"] = rate_type_choice
            if item_id:
                query_params["id"] = item_id
            url += "?" + urlencode(query_params)
        return redirect(url)
    else:
        quote_items = quote_obj.quoteitem_set.all()
        empty_form = QuoteItemForm()
        context = {
            "quote": quote_obj,
            "quote_items": quote_items,
            "rate_item_form": item_form if active_form_type == "rate" else empty_form,
            "selected_rate": rate,
            "custom_item_form": item_form if active_form_type == "custom" else empty_form,
            "submitted": quote_obj.status == Quote.Status.PENDING_APPROVAL,
            "published": quote_obj.status == Quote.Status.PUBLISHED,
            "draft": quote_obj.status == Quote.Status.DRAFT,
            "updated": quote_obj.updated_date != quote_obj.created_date,
            "users": User.objects.filter(is_active=True).exclude(id=user.id),
            "projects": Project.objects.all(),
            "form": form,
            "active_quote_item_tab": active_form_type,
            "show_send_emails_button": show_send_emails_button,
        }
        rate_search_context = get_rate_search_context(rate_type_choice, item_id)
        context.update(rate_search_context)
        context.update(permissions)
        return render(request, "quotes/quote.html", context)


def get_rate_type(rate):
    if rate.is_hourly_rate():
        if rate.daily:
            return QuoteItem.AmountType.DAILY
        elif rate.flat:
            return QuoteItem.AmountType.FLAT
        else:
            return QuoteItem.AmountType.HOURLY
    else:
        return QuoteItem.AmountType.NOT_APPLICABLE


def merge_post_data_with_defaults(post, defaults):
    non_empty_post_data = {k: v for k, v in post.items() if v and v.strip() != ""}
    return {**defaults, **non_empty_post_data}


@login_required
@user_passes_test(can_create_quotes)
@require_http_methods(["POST"])
def delete_quote_item(request, item_id):
    quote_item = get_object_or_404(QuoteItem, id=item_id)
    permissions = quote_item.quote.permissions(request.user)
    if not permissions["can_edit"]:
        messages.error(request, "You do not have permission to delete items from this quote.")
        return redirect("quote", quote_id=quote_item.quote.id)

    quote_id = quote_item.quote.id
    quote_item.delete()
    messages.success(request, "Item removed from quote successfully!")
    return redirect("quote", quote_id=quote_id)


@login_required
@require_http_methods(["POST"])
def edit_quote_item(request, item_id):
    quote_item = get_object_or_404(QuoteItem, id=item_id)
    user = request.user
    permissions = quote_item.quote.permissions(user)

    if not permissions["can_edit"]:
        messages.error(request, "You do not have permission to edit items in this quote.")
        return redirect("quote", quote_id=quote_item.quote.id)

    # Update the quote item with form data
    item_form = QuoteItemForm(request.POST, instance=quote_item)

    if item_form.is_valid():
        item_form.save()
        messages.success(request, "Item updated successfully!")
        return redirect("quote", quote_id=quote_item.quote.id)
    else:
        quote_obj = quote_item.quote
        quote_items = quote_obj.quoteitem_set.all()
        form = EditQuoteForm(instance=quote_obj)
        show_send_emails_button = meets_send_email_prerequisites(quote_obj) and permissions["can_send_emails"]
        active_quote_item_tab = "rate"

        context = {
            "quote": quote_obj,
            "quote_items": quote_items,
            "submitted": quote_obj.status == Quote.Status.PENDING_APPROVAL,
            "published": quote_obj.status == Quote.Status.PUBLISHED,
            "draft": quote_obj.status == Quote.Status.DRAFT,
            "updated": quote_obj.updated_date != quote_obj.created_date,
            "users": User.objects.filter(is_active=True).exclude(id=user.id),
            "projects": Project.objects.all(),
            "form": form,
            "active_quote_item_tab": active_quote_item_tab,
            "show_send_emails_button": show_send_emails_button,
            "edit_item_form": item_form,
            "edit_item_id": item_id,
        }
        rate_search_context = get_rate_search_context(None, None)
        context.update(rate_search_context)
        context.update(permissions)

        return render(request, "quotes/quote.html", context)


@login_required
@user_passes_test(can_create_quotes)
@require_http_methods(["POST"])
def add_tax(request, quote_id):
    quote_obj = get_object_or_404(Quote, id=quote_id)
    user = request.user
    permissions = quote_obj.permissions(user)
    if not permissions["can_edit"]:
        messages.error(request, "You do not have permission to add tax to this quote.")
        return redirect("quote", quote_id=quote_id)

    if quote_obj.configuration.tax is None:
        messages.error(request, "This quote configuration does not have a tax.")
        return redirect("quote", quote_id=quote_id)

    quote_obj.add_tax = True
    quote_obj.save()
    messages.success(request, "Tax added to quote successfully!")
    return redirect("quote", quote_id=quote_id)


@login_required
@user_passes_test(can_create_quotes)
@require_http_methods(["POST"])
def remove_tax(request, quote_id):
    quote_obj = get_object_or_404(Quote, id=quote_id)
    user = request.user
    permissions = quote_obj.permissions(user)
    if not permissions["can_edit"]:
        messages.error(request, "You do not have permission to remove tax from this quote.")
        return redirect("quote", quote_id=quote_id)

    quote_obj.add_tax = False
    quote_obj.save()
    messages.success(request, "Tax removed from quote successfully!")
    return redirect("quote", quote_id=quote_id)


def get_rate_search_context(rate_type_choice, item_id):
    tool = get_object_or_404(Tool, pk=item_id) if item_id and rate_type_choice == RateType.Type.TOOL else None
    area = get_object_or_404(Area, pk=item_id) if item_id and rate_type_choice == RateType.Type.AREA else None
    consumable = (
        get_object_or_404(Consumable, pk=item_id) if item_id and rate_type_choice == RateType.Type.CONSUMABLE else None
    )
    tools = list(Tool.objects.all())
    tools.sort(key=lambda x: (x.category, x.name))
    rate_types = get_rate_types(rate_type_choice)
    rates = []
    search_selection = None

    if rate_type_choice:
        if rate_type_choice in [RateType.Type.TOOL, RateType.Type.AREA, RateType.Type.CONSUMABLE]:
            if tool or area or consumable:
                rates = Rate.non_deleted().filter(type__in=rate_types)
                if tool:
                    rates = rates.filter(tool=tool)
                    search_selection = tool.__str__()
                elif area:
                    rates = rates.filter(area=area)
                    search_selection = area.__str__()
                elif consumable:
                    rates = rates.filter(consumable=consumable)
                    search_selection = consumable.__str__()
        else:
            rates = Rate.non_deleted().filter(type__in=rate_types)
            search_selection = rate_types.first().__str__().lower()

    current_and_future_rates = flatten(RateHistory(rates, datetime.today().date()).current_and_future_rates().values())
    current_and_future_rates.sort(key=lambda r: (r.type_id, r.category_id))

    return {
        "rate_types": rate_types,
        "rate_type_choice": rate_type_choice,
        "item_id": item_id,
        "item": tool or area or consumable,
        "rate_type_choices": get_rate_type_choices(),
        "tools": tools,
        "areas": Area.objects.filter(area_children_set__isnull=True),
        "consumables": Consumable.objects.all().order_by("category", "name"),
        "rates": current_and_future_rates,
        "search_selection": search_selection,
        "found_count": len(current_and_future_rates),
    }


@login_required
@user_passes_test(can_access_quotes)
@require_http_methods(["POST"])
def send_quote(request, quote_id):
    quote_obj = get_object_or_404(Quote, id=quote_id)
    user = request.user
    permissions = quote_obj.permissions(user)

    if not permissions["can_send_emails"]:
        messages.error(request, "You do not have permission to send this quote.")
        return redirect("quote", quote_id=quote_id)

    try:
        send_quote_email(quote_obj)
        messages.success(request, "Quote sent successfully!")
        quote_obj.last_emails_sent_date = timezone.now()
        quote_obj.save()
    except FailedToSendQuoteEmailException:
        messages.error(request, "Failed to send quote email.")

    return redirect("quote", quote_id=quote_id)


@login_required
@user_passes_test(can_access_quotes)
@require_http_methods(["POST"])
def render_quote(request, quote_id):
    quote_obj = get_object_or_404(Quote, id=quote_id)
    user = request.user
    permissions = quote_obj.permissions(user)

    if not permissions["can_send_emails"]:
        messages.error(request, "You do not have permission to render this quote.")
        return redirect("quote", quote_id=quote_id)

    try:
        quote_obj.render_and_save()
        messages.success(request, "Quote rendered successfully!")
    except QuoteGenerationException as e:
        messages.error(request, "Failed to render quote file.")

    return redirect("quote", quote_id=quote_id)


@require_GET
def public_view_quote(request, quote_id):
    try:
        quote = Quote.objects.filter(id=quote_id).first()
        token = request.GET.get("token")
        if not token or not quote.file_access_token or token != quote.file_access_token or not quote.file:
            return HttpResponse("Invalid Link", content_type="text/plain")
        if quote.is_expired:
            return HttpResponse("Link Expired", content_type="text/plain")
        return FileResponse(quote.file, as_attachment=False, filename=quote.file.name.split("/")[-1])
    except Exception:
        quotes_logger.exception(f"Failed to serve quote file for quote {quote_id}")
        return HttpResponse("Invalid Link", content_type="text/plain")


@login_required
@user_passes_test(can_access_quotes)
@require_http_methods(["POST"])
def update_quote_status(request, quote_id):
    quote_obj = get_object_or_404(Quote, id=quote_id)
    user = request.user
    permissions = quote_obj.permissions(user)
    action = next(
        iter(
            [
                state
                for state in ["approve_quote", "publish_quote", "submit_quote", "deny_quote"]
                if state in request.POST
            ]
        )
    )

    if action:
        if action == "approve_quote":

            if not permissions["can_approve"]:
                messages.error(request, "User does not have permission to approve this quote.")
                return redirect("quote", quote_id=quote_id)

            if not quote_obj.is_pending_approval:
                messages.error(request, "Only quotes pending approval can be approved.")
                return redirect("quote", quote_id=quote_id)

            quote_obj.publish(user)
            send_status_update_email(quote_obj)
            delete_approval_request_notification(quote_obj)
            messages.success(request, "Quote published successfully!")

        elif action == "deny_quote":

            if not permissions["can_approve"]:
                messages.error(request, "User does not have permission to deny this quote.")

            if not quote_obj.is_pending_approval:
                messages.error(request, "Only quotes pending approval can be denied.")

            quote_obj.deny()
            send_status_update_email(quote_obj)
            delete_approval_request_notification(quote_obj)
            messages.success(request, "Quote denied successfully!")

        elif action == "submit_quote":

            if not permissions["can_edit"]:
                messages.error(request, "User does not have permission to submit this quote for approval.")

            if not quote_obj.is_draft:
                messages.error(request, "Only draft quotes can be submitted for approval.")

            if not permissions["requires_approval"]:
                messages.error(request, "This quote does not require approval.")

            quote_obj.submit_for_approval()
            send_approval_request_email(quote_obj)
            create_approval_request_notification(quote_obj)
            messages.success(request, "Quote submitted for review successfully!")

        elif action == "publish_quote":

            if not permissions["can_edit"]:
                messages.error(request, "User does not have permission to publish this quote.")

            if permissions["requires_approval"]:
                messages.error(request, "This quote requires approval before it can be published.")

            if not quote_obj.is_draft:
                messages.error(request, "Only draft quotes can be published.")

            quote_obj.publish(user)
            delete_approval_request_notification(quote_obj)
            messages.success(request, "Quote published successfully!")

    return redirect("quote", quote_id=quote_id)


def send_status_update_email(quote):
    try:
        subject = f"Quote Status Update: {quote.name} - {quote.get_status_display()}"
        quote_status_update_email_template = get_media_file_contents("quote_status_update_email.html")
        if quote_status_update_email_template:
            content = render_email_template(quote_status_update_email_template, {"quote": quote})
            quote.creator.email_user(
                subject=subject, message=content, from_email=None, email_category=QUOTE_EMAIL_CATEGORY
            )
    except Exception as e:
        quotes_logger.exception(f"Failed to send status update email for quote {quote.name} ({quote.id})", e)


def send_approval_request_email(quote):
    try:
        subject = f"Quote Approval Request: {quote.name}"
        quote_approval_request_email_template = get_media_file_contents("quote_approval_request_email.html")
        if quote_approval_request_email_template:
            content = render_email_template(quote_approval_request_email_template, {"quote": quote})
            recipients = quote.configuration.get_all_reviewers()
            for recipient in recipients:
                recipient.email_user(
                    subject=subject, message=content, from_email=None, email_category=QUOTE_EMAIL_CATEGORY
                )
    except Exception as e:
        quotes_logger.exception(f"Failed to send approval request email for quote {quote.name} ({quote.id})", e)


def send_quote_email(quote):
    subject = f"Quote: {quote.name}"
    quote_email_template = get_media_file_contents("quote_email.html")
    if quote_email_template and quote.file_access_token and quote.file:
        content = render_email_template(quote_email_template, {"quote": quote, "quote_url": quote.get_access_url()})
        recipients = quote.get_all_recipients()
        try:
            send_mail(
                subject=subject,
                content=content,
                from_email=quote.configuration.email_from,
                bcc=recipients,
                cc=quote.configuration.email_cc,
                email_category=QUOTE_EMAIL_CATEGORY,
                fail_silently=False,
            )
        except Exception:
            quotes_logger.exception(f"Failed to send quote email for quote {quote.name} ({quote.id}) to {recipients}")
            raise FailedToSendQuoteEmailException(quote)
