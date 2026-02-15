"""
Stripe Payment Integration for TrueValue AI
=============================================
Handles checkout sessions, webhooks, customer portal, and subscription management.

Env vars required:
  STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET
  STRIPE_PRICE_BASIC, STRIPE_PRICE_PRO, STRIPE_PRICE_ENTERPRISE
"""

import os
import logging
from typing import Optional

import stripe

from database import update_user_tier, log_subscription_event, get_user

logger = logging.getLogger("payments")

# Configure Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

# Price IDs for each tier (set in Stripe Dashboard)
PRICE_IDS = {
    "basic": os.getenv("STRIPE_PRICE_BASIC", ""),
    "pro": os.getenv("STRIPE_PRICE_PRO", ""),
    "enterprise": os.getenv("STRIPE_PRICE_ENTERPRISE", ""),
}

# Reverse lookup: price_id -> tier
PRICE_TO_TIER = {v: k for k, v in PRICE_IDS.items() if v}

# Tier pricing in AED for reference
TIER_PRICING_AED = {
    "basic": 99,
    "pro": 299,
    "enterprise": 999,
}


def is_stripe_configured() -> bool:
    """Check if Stripe is properly configured."""
    return bool(stripe.api_key and stripe.api_key.startswith("sk_"))


async def create_checkout_session(
    user_id: int,
    tier: str,
    username: Optional[str] = None,
    success_url: str = "https://t.me/TrueValueAIBot?start=payment_success",
    cancel_url: str = "https://t.me/TrueValueAIBot?start=payment_cancel",
) -> Optional[str]:
    """
    Create a Stripe Checkout session and return the URL.
    Returns None if Stripe is not configured or tier is invalid.
    """
    if not is_stripe_configured():
        logger.warning("Stripe not configured — cannot create checkout session")
        return None

    price_id = PRICE_IDS.get(tier)
    if not price_id:
        logger.error("No Stripe price ID configured for tier: %s", tier)
        return None

    try:
        # Check if user already has a Stripe customer
        user = await get_user(user_id)
        customer_id = user.get("stripe_customer_id") if user else None

        session_params = {
            "mode": "subscription",
            "payment_method_types": ["card"],
            "line_items": [{"price": price_id, "quantity": 1}],
            "success_url": success_url,
            "cancel_url": cancel_url,
            "metadata": {
                "user_id": str(user_id),
                "tier": tier,
                "username": username or "",
            },
        }

        if customer_id:
            session_params["customer"] = customer_id
        else:
            session_params["customer_creation"] = "always"

        session = stripe.checkout.Session.create(**session_params)
        logger.info("Created checkout session for user %s, tier %s", user_id, tier)
        return session.url

    except stripe.StripeError as exc:
        logger.error("Stripe checkout error: %s", exc)
        return None


async def handle_webhook_event(payload: bytes, sig_header: str) -> dict:
    """
    Process a Stripe webhook event.
    Returns a dict with event processing result.
    """
    if not WEBHOOK_SECRET:
        return {"error": "Webhook secret not configured"}

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, WEBHOOK_SECRET)
    except stripe.SignatureVerificationError:
        logger.warning("Invalid Stripe webhook signature")
        return {"error": "Invalid signature"}
    except ValueError:
        logger.warning("Invalid Stripe webhook payload")
        return {"error": "Invalid payload"}

    event_type = event["type"]
    data = event["data"]["object"]

    logger.info("Processing Stripe event: %s", event_type)

    if event_type == "checkout.session.completed":
        return await _handle_checkout_completed(data, event["id"])

    elif event_type == "customer.subscription.updated":
        return await _handle_subscription_updated(data, event["id"])

    elif event_type == "customer.subscription.deleted":
        return await _handle_subscription_deleted(data, event["id"])

    elif event_type == "invoice.payment_failed":
        return await _handle_payment_failed(data, event["id"])

    else:
        logger.debug("Unhandled Stripe event type: %s", event_type)
        return {"status": "ignored", "event_type": event_type}


async def _handle_checkout_completed(session: dict, event_id: str) -> dict:
    """Handle successful checkout — upgrade user tier."""
    metadata = session.get("metadata", {})
    user_id = int(metadata.get("user_id", 0))
    tier = metadata.get("tier", "basic")
    customer_id = session.get("customer")
    subscription_id = session.get("subscription")

    if not user_id:
        return {"error": "No user_id in session metadata"}

    # Get current tier for logging
    user = await get_user(user_id)
    from_tier = user.get("tier", "free") if user else "free"

    # Update user in database
    await update_user_tier(
        user_id=user_id,
        tier=tier,
        stripe_customer_id=customer_id,
        stripe_subscription_id=subscription_id,
    )

    # Log subscription event
    amount_aed = TIER_PRICING_AED.get(tier, 0)
    await log_subscription_event(
        user_id=user_id,
        event_type="checkout_completed",
        from_tier=from_tier,
        to_tier=tier,
        stripe_event_id=event_id,
        amount_aed=amount_aed,
    )

    logger.info("User %s upgraded from %s to %s", user_id, from_tier, tier)
    return {"status": "upgraded", "user_id": user_id, "tier": tier}


async def _handle_subscription_updated(subscription: dict, event_id: str) -> dict:
    """Handle subscription change (upgrade/downgrade)."""
    customer_id = subscription.get("customer")
    subscription_id = subscription.get("id")
    price_id = subscription.get("items", {}).get("data", [{}])[0].get("price", {}).get("id", "")
    new_tier = PRICE_TO_TIER.get(price_id, "basic")

    # Find user by Stripe customer ID
    # For now, use metadata if available
    metadata = subscription.get("metadata", {})
    user_id = int(metadata.get("user_id", 0))

    if not user_id:
        logger.warning("Cannot find user for subscription update: %s", subscription_id)
        return {"status": "user_not_found"}

    user = await get_user(user_id)
    from_tier = user.get("tier", "free") if user else "free"

    await update_user_tier(user_id=user_id, tier=new_tier)
    await log_subscription_event(
        user_id=user_id,
        event_type="subscription_updated",
        from_tier=from_tier,
        to_tier=new_tier,
        stripe_event_id=event_id,
    )

    return {"status": "updated", "user_id": user_id, "new_tier": new_tier}


async def _handle_subscription_deleted(subscription: dict, event_id: str) -> dict:
    """Handle subscription cancellation — downgrade to free."""
    metadata = subscription.get("metadata", {})
    user_id = int(metadata.get("user_id", 0))

    if not user_id:
        return {"status": "user_not_found"}

    user = await get_user(user_id)
    from_tier = user.get("tier", "free") if user else "free"

    await update_user_tier(user_id=user_id, tier="free", stripe_subscription_id=None)
    await log_subscription_event(
        user_id=user_id,
        event_type="subscription_cancelled",
        from_tier=from_tier,
        to_tier="free",
        stripe_event_id=event_id,
    )

    logger.info("User %s subscription cancelled, downgraded to free", user_id)
    return {"status": "cancelled", "user_id": user_id}


async def _handle_payment_failed(invoice: dict, event_id: str) -> dict:
    """Handle failed payment — log but don't immediately downgrade."""
    customer_id = invoice.get("customer")
    subscription_id = invoice.get("subscription")

    metadata = invoice.get("metadata", {})
    user_id = int(metadata.get("user_id", 0))

    if user_id:
        await log_subscription_event(
            user_id=user_id,
            event_type="payment_failed",
            stripe_event_id=event_id,
        )

    logger.warning("Payment failed for customer %s, subscription %s", customer_id, subscription_id)
    return {"status": "payment_failed", "customer_id": customer_id}


async def create_customer_portal_session(
    stripe_customer_id: str,
    return_url: str = "https://t.me/TrueValueAIBot",
) -> Optional[str]:
    """Create a Stripe Customer Portal session for self-service management."""
    if not is_stripe_configured() or not stripe_customer_id:
        return None

    try:
        session = stripe.billing_portal.Session.create(
            customer=stripe_customer_id,
            return_url=return_url,
        )
        return session.url
    except stripe.StripeError as exc:
        logger.error("Stripe portal error: %s", exc)
        return None


async def cancel_subscription(stripe_subscription_id: str) -> bool:
    """Cancel a Stripe subscription."""
    if not is_stripe_configured() or not stripe_subscription_id:
        return False

    try:
        stripe.Subscription.cancel(stripe_subscription_id)
        return True
    except stripe.StripeError as exc:
        logger.error("Stripe cancellation error: %s", exc)
        return False
