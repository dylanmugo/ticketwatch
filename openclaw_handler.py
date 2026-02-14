#!/usr/bin/env python3
"""
OpenClaw Integration for TicketWatch
Routes WhatsApp messages from OpenClaw to TicketWatch handler
"""
import sys
import json
import logging
import argparse
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(Path.home() / "ticketwatch" / "logs" / "openclaw.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Import TicketWatch modules
sys.path.insert(0, str(Path.home() / "ticketwatch"))
from handler import handle_message, handle_watch_confirm


def parse_openclaw_args():
    """Parse command line arguments from OpenClaw."""
    parser = argparse.ArgumentParser(description="TicketWatch OpenClaw Handler")
    parser.add_argument("--user-id", required=True, help="User phone number or ID")
    parser.add_argument("--message", required=True, help="WhatsApp message text")
    parser.add_argument("--phone", default=None, help="User phone number")
    parser.add_argument("--action", default="message", help="Action type (message/confirm)")
    parser.add_argument("--event-id", default=None, help="Event ID for confirmation")
    parser.add_argument("--event-name", default=None, help="Event name")
    parser.add_argument("--venue", default=None, help="Venue name")
    parser.add_argument("--date", default=None, help="Event date")
    parser.add_argument("--max-price", type=float, default=None, help="Max price")
    parser.add_argument("--quantity", type=int, default=1, help="Quantity")
    parser.add_argument("--buy-url", default=None, help="Ticketmaster buy URL")
    
    return parser.parse_args()


def format_whatsapp_response(result):
    """Convert handler result to WhatsApp message."""
    if not isinstance(result, dict):
        return str(result)
    
    message = result.get("message", "")
    
    # If there's a follow_up, add it
    if result.get("follow_up"):
        message += f"\n\n{result['follow_up']}"
    
    return message


def handle_watch_confirmation(user_id, phone, args):
    """Handle watch confirmation (yes/no response)."""
    if args.message.lower() in ["yes", "y", "confirm"]:
        result = handle_watch_confirm(
            user_id=user_id,
            event_id=args.event_id,
            event_name=args.event_name,
            venue=args.venue,
            date_str=args.date,
            max_price=args.max_price,
            quantity=args.quantity,
            buy_url=args.buy_url
        )
        return result
    else:
        return {
            "message": "❌ Watch cancelled. No problem! Say 'search for [event]' anytime."
        }


def main():
    """Main entry point for OpenClaw integration."""
    args = parse_openclaw_args()
    
    user_id = args.user_id
    phone = args.phone or user_id
    message = args.message
    
    logger.info(f"Message from {user_id}: {message[:50]}")
    
    try:
        # Handle different action types
        if args.action == "confirm_watch":
            # User is confirming a watch creation
            result = handle_watch_confirmation(user_id, phone, args)
        else:
            # Standard message handling
            result = handle_message(user_id, phone, message)
        
        # Extract message for WhatsApp
        whatsapp_message = format_whatsapp_response(result)
        
        # Output JSON for OpenClaw to route back via WhatsApp
        output = {
            "status": "success",
            "user_id": user_id,
            "intent": result.get("intent", "unknown"),
            "message": whatsapp_message,
            "action": result.get("action"),  # May include "confirm" for watch creation
            "metadata": {k: v for k, v in result.items() if k not in ["message", "status", "intent"]}
        }
        
        print(json.dumps(output, indent=2))
        logger.info(f"Response: {result.get('intent', 'unknown')}")
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        error_output = {
            "status": "error",
            "message": "Sorry, something went wrong. Please try again.",
            "error": str(e)
        }
        print(json.dumps(error_output, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(main())
