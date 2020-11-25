from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from checkout.webhook_handler import Stripe_WH_Handler

import stripe


@require_POST
@csrf_exempt
def webhook(request):
    """
    Listen for webhooks from Stripe
    (taken mostly from the Stripe docs)
    """
    # Setup
    wh_secret = settings.STRIPE_WH_SECRET
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Get the webhook data and verify its signature
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        # Try to construct a webhook event
        event = stripe.Webhook.construct_event(
            payload, sig_header, wh_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)
    except Exception as e:
        # Generic exception
        return HttpResponse(content=e, status=400)

    # Setup a webhook handler
    handler = Stripe_WH_Handler(request)

    # Map webhook events to handler functions
    event_map = {
        'payment_intent.succeeded': handler.handle_payment_intent_succeeded,
        'payment_intent.'
        'payment_failed': handler.handle_payment_intent_payment_failed,
    }

    # Get webhook type from Stripe
    event_type = event['type']

    # If a handler matches it or use generic one as default
    event_handler = event_map.get(event_type, handler.handle_event)

    # Call that event handler with the event
    response = event_handler(event)
    return response
