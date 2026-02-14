"""
TicketWatch Stripe Payment Integration
Handles premium tier subscriptions (€4.99/month)
"""
import os
import json
import logging
import hashlib
import hmac
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Stripe configuration
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "sk_test_placeholder")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "pk_test_placeholder")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_placeholder")

PREMIUM_PRICE_ID = os.getenv("STRIPE_PRICE_ID", "price_placeholder")
PREMIUM_PRICE_EUR = 4.99


def create_checkout_session(user_id, phone):
    """
    Create Stripe checkout session for premium upgrade.
    Returns checkout URL.
    """
    try:
        import stripe
        stripe.api_key = STRIPE_SECRET_KEY
        
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price": PREMIUM_PRICE_ID,
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url=f"https://ticketwatch.ie/success?session_id={{CHECKOUT_SESSION_ID}}&user={user_id}",
            cancel_url="https://ticketwatch.ie/cancelled",
            customer_email=None,  # Optional: user email if available
            metadata={
                "user_id": user_id,
                "phone": phone,
            }
        )
        
        logger.info(f"Checkout session created for {user_id}: {session.id}")
        return {
            "success": True,
            "url": session.url,
            "session_id": session.id
        }
    except ImportError:
        # Stripe not installed - return mock for testing
        logger.warning("Stripe library not installed, using mock")
        return {
            "success": True,
            "url": f"https://stripe.mock/checkout?user={user_id}",
            "session_id": "mock_session_123"
        }
    except Exception as e:
        logger.error(f"Error creating checkout session: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def handle_webhook(payload, signature):
    """
    Validate and handle Stripe webhook events.
    Events: customer.subscription.created, customer.subscription.deleted, etc.
    """
    try:
        # Verify webhook signature
        expected_sig = hmac.new(
            STRIPE_WEBHOOK_SECRET.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_sig):
            logger.warning("Invalid webhook signature")
            return {"success": False, "error": "Invalid signature"}
        
        # Parse event
        event = json.loads(payload)
        event_type = event.get("type")
        
        logger.info(f"Webhook event: {event_type}")
        
        # Handle subscription events
        if event_type == "customer.subscription.created":
            return handle_subscription_created(event)
        elif event_type == "customer.subscription.deleted":
            return handle_subscription_deleted(event)
        elif event_type == "charge.failed":
            return handle_charge_failed(event)
        else:
            logger.info(f"Unhandled event type: {event_type}")
            return {"success": True}
        
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        return {"success": False, "error": str(e)}


def handle_subscription_created(event):
    """Handle new subscription."""
    from database import get_db
    
    data = event.get("data", {}).get("object", {})
    customer_id = data.get("customer")
    subscription_id = data.get("id")
    user_id = data.get("metadata", {}).get("user_id")
    
    if not user_id:
        logger.warning(f"No user_id in subscription metadata")
        return {"success": False}
    
    # Update user tier to premium
    db = get_db()
    db.execute(
        """INSERT OR REPLACE INTO subscriptions 
           (user_id, tier, stripe_customer_id, stripe_subscription_id, started_at, expires_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (user_id, "premium", customer_id, subscription_id, datetime.now().isoformat(), None)
    )
    db.execute(
        "UPDATE users SET tier = ? WHERE user_id = ?",
        ("premium", user_id)
    )
    db.commit()
    
    logger.info(f"Subscription created: {user_id} -> premium")
    return {"success": True}


def handle_subscription_deleted(event):
    """Handle subscription cancellation."""
    from database import get_db
    
    data = event.get("data", {}).get("object", {})
    subscription_id = data.get("id")
    user_id = data.get("metadata", {}).get("user_id")
    
    if not user_id:
        logger.warning(f"No user_id in subscription metadata")
        return {"success": False}
    
    # Revert user tier to free
    db = get_db()
    db.execute(
        "UPDATE users SET tier = ? WHERE user_id = ?",
        ("free", user_id)
    )
    db.execute(
        "UPDATE subscriptions SET expires_at = ? WHERE stripe_subscription_id = ?",
        (datetime.now().isoformat(), subscription_id)
    )
    db.commit()
    
    logger.info(f"Subscription deleted: {user_id} -> free")
    return {"success": True}


def handle_charge_failed(event):
    """Handle failed payment."""
    data = event.get("data", {}).get("object", {})
    customer_id = data.get("customer")
    reason = data.get("failure_message")
    
    logger.error(f"Charge failed for customer {customer_id}: {reason}")
    
    # Could send alert email here
    return {"success": True}


def send_payment_link(user_id, phone):
    """
    Send WhatsApp message with payment link.
    """
    from alerts import send_whatsapp_via_openclaw
    
    result = create_checkout_session(user_id, phone)
    
    if not result.get("success"):
        return {
            "success": False,
            "message": "Payment setup failed. Please try again."
        }
    
    message = f"""💳 **Upgrade to Premium**

Unlimited watches for just €4.99/month!

🎫 Free tier: 1 active watch
⭐ Premium: Unlimited watches

👉 [Upgrade Now]({result['url']})

Questions? Reply to this chat."""
    
    alert_result = send_whatsapp_via_openclaw(user_id, message)
    
    return {
        "success": alert_result.get("success", True),
        "payment_link": result.get("url")
    }


def format_invoice_email(user_id, amount, subscription_id):
    """Format invoice email template."""
    return f"""
Subject: TicketWatch Premium Invoice

Dear TicketWatch User,

Thank you for upgrading to TicketWatch Premium!

---
Subscription: {subscription_id}
Amount: €{amount:.2f}
Billing Cycle: Monthly
Date: {datetime.now().strftime('%Y-%m-%d')}

Your Tier: PREMIUM ⭐
Benefits:
✓ Unlimited ticket watches
✓ Instant alerts
✓ Priority support

---

Questions? Reply to this email.

Best regards,
TicketWatch Team
"""


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test
    result = create_checkout_session("test_user", "+353858536569")
    print(json.dumps(result, indent=2))
