from django.forms import ModelForm

from NEMO_billing.quotes.models import Quote, QuoteItem


class CreateQuoteForm(ModelForm):
    class Meta:
        model = Quote
        fields = ["name", "configuration"]


class EditQuoteForm(ModelForm):
    class Meta:
        model = Quote
        fields = ["name", "project", "users", "emails"]


class QuoteItemForm(ModelForm):
    class Meta:
        model = QuoteItem
        exclude = ["quote"]
