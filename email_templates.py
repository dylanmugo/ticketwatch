"""
TicketWatch Email Templates
For transactional emails (receipts, alerts, newsletters)
"""


def welcome_email(user_name, user_email):
    """Welcome new user."""
    return {
        "subject": "Welcome to TicketWatch! 🎫",
        "html": f"""
<html>
<body style="font-family: sans-serif; background: #f5f5f5; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; background: white; padding: 40px;">
        <h1 style="color: #8b5cf6;">Welcome to TicketWatch!</h1>
        
        <p>Hi {user_name},</p>
        
        <p>You're now set up to catch sold-out concert tickets in Ireland. Here's how to get started:</p>
        
        <ol>
            <li><strong>Message on WhatsApp:</strong> Say "What's on?" to see upcoming events</li>
            <li><strong>Create a watch:</strong> "Watch for [artist] under €80"</li>
            <li><strong>Confirm:</strong> Reply "yes" when we show you the event</li>
            <li><strong>Get alerts:</strong> We'll notify you instantly when tickets drop</li>
        </ol>
        
        <p style="background: #f0f0f0; padding: 20px; border-radius: 8px;">
            <strong>Your account:</strong><br/>
            Tier: Free (1 active watch)<br/>
            Upgrade to Premium (€4.99/mo) anytime for unlimited watches.
        </p>
        
        <p>
            <a href="https://wa.me/353858536569" style="background: #8b5cf6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block;">
                Start on WhatsApp
            </a>
        </p>
        
        <p style="color: #888; font-size: 0.9em; margin-top: 40px;">
            Questions? Reply to this email or message us on WhatsApp.
        </p>
    </div>
</body>
</html>
        """
    }


def ticket_alert_email(event_name, venue, price, buy_url):
    """Alert user when tickets are available."""
    return {
        "subject": f"🚨 {event_name} tickets available!",
        "html": f"""
<html>
<body style="font-family: sans-serif; background: #f5f5f5; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; background: white; padding: 40px;">
        <h1 style="color: #10b981;">🎫 TICKETS AVAILABLE!</h1>
        
        <div style="background: #f0f0f0; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h2 style="margin: 0 0 10px 0;">{event_name}</h2>
            <p style="margin: 5px 0;"><strong>Venue:</strong> {venue}</p>
            <p style="margin: 5px 0;"><strong>Price:</strong> €{price}</p>
        </div>
        
        <p style="color: #ef4444; font-size: 1.1em; font-weight: bold;">⚡ Act fast — these won't last!</p>
        
        <p>
            <a href="{buy_url}" style="background: #10b981; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block; font-size: 1.1em;">
                Buy Now on Ticketmaster
            </a>
        </p>
        
        <p style="color: #888; font-size: 0.9em; margin-top: 40px;">
            This alert was sent because you set a watch for this event.
        </p>
    </div>
</body>
</html>
        """
    }


def upgrade_confirmation_email(user_name, amount):
    """Confirm premium upgrade."""
    return {
        "subject": "Premium Upgrade Confirmed ⭐",
        "html": f"""
<html>
<body style="font-family: sans-serif; background: #f5f5f5; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; background: white; padding: 40px;">
        <h1 style="color: #8b5cf6;">Welcome to Premium ⭐</h1>
        
        <p>Hi {user_name},</p>
        
        <p>Your upgrade is confirmed. You now have:</p>
        
        <ul style="font-size: 1.1em; line-height: 1.8;">
            <li>✓ Unlimited watches</li>
            <li>✓ Unlimited searches</li>
            <li>✓ Instant alerts (same as free)</li>
            <li>✓ Priority support</li>
        </ul>
        
        <div style="background: #f0f0f0; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <p style="margin: 0;"><strong>Invoice</strong></p>
            <p style="margin: 10px 0 0 0; font-size: 0.9em;">Amount: €{amount:.2f}</p>
            <p style="margin: 5px 0; font-size: 0.9em;">Billing Cycle: Monthly</p>
        </div>
        
        <p>You can cancel anytime from your WhatsApp chat or reply to this email.</p>
        
        <p style="color: #888; font-size: 0.9em; margin-top: 40px;">
            Questions? Message us on WhatsApp.
        </p>
    </div>
</body>
</html>
        """
    }


def weekly_summary_email(user_name, watches_count, alerts_count):
    """Weekly activity summary."""
    return {
        "subject": "Your TicketWatch Weekly Summary",
        "html": f"""
<html>
<body style="font-family: sans-serif; background: #f5f5f5; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; background: white; padding: 40px;">
        <h1 style="color: #8b5cf6;">Your TicketWatch Weekly Summary</h1>
        
        <p>Hi {user_name},</p>
        
        <div style="background: #f0f0f0; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <p style="margin: 0; font-size: 1.2em;"><strong>This Week</strong></p>
            <p style="margin: 10px 0 0 0;">Active watches: <strong>{watches_count}</strong></p>
            <p style="margin: 5px 0;">Alerts sent: <strong>{alerts_count}</strong></p>
        </div>
        
        <p>Keep watching and you'll find that perfect gig! 🎵</p>
        
        <p style="color: #888; font-size: 0.9em; margin-top: 40px;">
            Stop receiving these emails: Reply to this message or disable in WhatsApp settings.
        </p>
    </div>
</body>
</html>
        """
    }


def affiliate_payment_email(affiliate_name, amount, period):
    """Affiliate commission payment notification."""
    return {
        "subject": f"TicketWatch Affiliate Payment: €{amount:.2f}",
        "html": f"""
<html>
<body style="font-family: sans-serif; background: #f5f5f5; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; background: white; padding: 40px;">
        <h1 style="color: #10b981;">💰 Payment Processed</h1>
        
        <p>Hi {affiliate_name},</p>
        
        <p>Your affiliate commission has been paid:</p>
        
        <div style="background: #f0f0f0; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <p style="margin: 0;"><strong>Amount:</strong> €{amount:.2f}</p>
            <p style="margin: 10px 0 0 0; font-size: 0.9em;"><strong>Period:</strong> {period}</p>
            <p style="margin: 10px 0 0 0; font-size: 0.9em;"><strong>Status:</strong> Transferred to your bank account</p>
        </div>
        
        <p>Thank you for promoting TicketWatch! Keep sharing and earn more. 🚀</p>
        
        <p style="color: #888; font-size: 0.9em; margin-top: 40px;">
            Questions about your payment? Reply to this email.
        </p>
    </div>
</body>
</html>
        """
    }


if __name__ == "__main__":
    import json
    
    # Test email generation
    welcome = welcome_email("Dylan", "dylan@example.com")
    print("Welcome Email:")
    print(f"Subject: {welcome['subject']}")
    print("HTML: " + welcome['html'][:100] + "...\n")
    
    alert = ticket_alert_email("Fred Again", "3Arena Dublin", "72", "https://ticketmaster.ie/...")
    print("Alert Email:")
    print(f"Subject: {alert['subject']}\n")
