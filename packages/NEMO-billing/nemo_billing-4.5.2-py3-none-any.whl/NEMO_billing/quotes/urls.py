from django.urls import path

from NEMO_billing.quotes import views


urlpatterns = [
    path("create_quote/", views.create_quote, name="create_quote"),
    path("create_quote/<int:selected_configuration_id>", views.create_quote, name="create_quote"),
    path("quote/<int:quote_id>/", views.view_quote, name="quote"),
    path("quote/<int:quote_id>/update_status/", views.update_quote_status, name="update_quote_status"),
    path("quote/<int:quote_id>/add_item/", views.add_quote_item, name="add_quote_item"),
    path("quote/<int:quote_id>/send_emails/", views.send_quote, name="quote_send_emails"),
    path("quote/<int:quote_id>/render/", views.render_quote, name="quote_render"),
    path("quote/<int:quote_id>/add_tax/", views.add_tax, name="quote_add_tax"),
    path("quote/<int:quote_id>/remove_tax/", views.remove_tax, name="quote_remove_tax"),
    path("quotes/", views.quote_list, name="quotes"),
    path("quotes/<int:selected_configuration_id>", views.quote_list, name="quotes"),
    path("quote_item/<int:item_id>/delete/", views.delete_quote_item, name="delete_quote_item"),
    path("quote_item/<int:item_id>/edit/", views.edit_quote_item, name="edit_quote_item"),
    path("public_quote/<int:quote_id>/", views.public_view_quote, name="public_quote_view"),
]
