from collections import defaultdict
from datetime import timedelta

from NEMO.models import Notification, User
from NEMO.utilities import get_model_instance
from NEMO.views.customization import get_media_file_contents
from NEMO.views.notifications import delete_notification
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from NEMO_billing.quotes.apps import NEMOQuotesConfig
from NEMO_billing.quotes.models import Quote, QuoteConfiguration

QUOTE_REVIEW_NOTIFICATION = "quote_review"
QUOTE_EMAIL_CATEGORY = NEMOQuotesConfig.plugin_id + 1


def available_configurations_for_user_to_create_or_approve(user):
    return [
        quote_configuration
        for quote_configuration in QuoteConfiguration.objects.all()
        if quote_configuration.can_user_create(user) or quote_configuration.can_user_approve(user)
    ]


def available_configurations_for_user_to_create(user):
    return [
        quote_configuration
        for quote_configuration in QuoteConfiguration.objects.all()
        if quote_configuration.can_user_create(user)
    ]


def can_access_quotes(user: User) -> bool:
    """
    A user can access quotes features if they are superuser or if they have permissions to create or approve quotes.
    """
    return user.is_active and (user.is_superuser or bool(available_configurations_for_user_to_create_or_approve(user)))


def can_create_quotes(user: User) -> bool:
    """
    A user can create quotes if they have permissions to create quotes in at least one configuration.
    """
    return bool(available_configurations_for_user_to_create(user))


def meets_send_email_prerequisites(quote: Quote) -> bool:
    quote_email_template = get_media_file_contents("quote_email.html")
    return bool(quote_email_template and quote.file and quote.file_access_token and bool(quote.get_all_recipients()))


def create_approval_request_notification(quote: Quote):
    expiration = timezone.now() + timedelta(days=30)
    user_to_notify = quote.configuration.get_all_reviewers()
    for user in user_to_notify:
        Notification.objects.update_or_create(
            user=user,
            notification_type=QUOTE_REVIEW_NOTIFICATION,
            content_type=ContentType.objects.get_for_model(quote),
            object_id=quote.id,
            defaults={"expiration": expiration},
        )


def delete_approval_request_notification(quote: Quote):
    delete_notification(QUOTE_REVIEW_NOTIFICATION, quote.id)


def get_approval_request_notifications_per_configuration(user: User):
    notifications = defaultdict(int)
    for notification in Notification.objects.filter(notification_type=QUOTE_REVIEW_NOTIFICATION, user=user):
        quote = get_model_instance(notification.content_type, notification.object_id)
        notifications[quote.configuration.id] += 1
    return notifications
