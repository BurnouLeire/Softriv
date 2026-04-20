# services/quote_service.py

from apps.sales.models import Quote, QuoteGroup, Items
from django.db import transaction
def create_quote_with_items(data, user):
    with transaction.atomic():
        quote = Quote.objects.create(...)

        group = QuoteGroup.objects.create(
            quote=quote,
            name="GENERAL"
        )

        for item_data in data['items']:
            Items.objects.create(group=group, **item_data)

    return quote