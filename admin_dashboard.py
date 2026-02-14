"""
TicketWatch Admin Dashboard
Real-time metrics, user management, revenue tracking
"""
import json
import logging
from datetime import datetime, timedelta
from database import get_db

logger = logging.getLogger(__name__)


def get_dashboard_stats():
    """Get real-time dashboard statistics."""
    db = get_db()
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # User stats
    total_users = db.execute("SELECT COUNT(*) as cnt FROM users").fetchone()['cnt']
    free_users = db.execute("SELECT COUNT(*) as cnt FROM users WHERE tier='free'").fetchone()['cnt']
    premium_users = db.execute("SELECT COUNT(*) as cnt FROM users WHERE tier='premium'").fetchone()['cnt']
    
    # Watch stats
    total_watches = db.execute("SELECT COUNT(*) as cnt FROM watches").fetchone()['cnt']
    active_watches = db.execute("SELECT COUNT(*) as cnt FROM watches WHERE status='active'").fetchone()['cnt']
    alerted_watches = db.execute("SELECT COUNT(*) as cnt FROM watches WHERE status='alerted'").fetchone()['cnt']
    
    # Today's stats
    todays_alerts = db.execute(
        "SELECT COUNT(*) as cnt FROM alerts_sent WHERE DATE(sent_at) = ?",
        (today,)
    ).fetchone()['cnt']
    
    # Revenue calculation
    premium_revenue = premium_users * 4.99
    
    # Recent alerts (for feed)
    recent_alerts = db.execute(
        """SELECT event_name, current_price, sent_at 
           FROM alerts_sent 
           ORDER BY sent_at DESC 
           LIMIT 10"""
    ).fetchall()
    
    return {
        "timestamp": datetime.now().isoformat(),
        "users": {
            "total": total_users,
            "free": free_users,
            "premium": premium_users,
            "conversion_rate": f"{(premium_users / max(total_users, 1) * 100):.1f}%"
        },
        "watches": {
            "total": total_watches,
            "active": active_watches,
            "alerted": alerted_watches
        },
        "alerts": {
            "today": todays_alerts,
            "recent": [dict(a) for a in recent_alerts]
        },
        "revenue": {
            "monthly_mrr": f"€{premium_revenue:.2f}",
            "premium_users": premium_users,
            "estimated_annual": f"€{premium_revenue * 12:.2f}"
        }
    }


def get_user_management():
    """Get user management data."""
    db = get_db()
    
    users = db.execute(
        """SELECT user_id, phone, tier, created_at, last_activity 
           FROM users 
           ORDER BY created_at DESC 
           LIMIT 100"""
    ).fetchall()
    
    return [dict(u) for u in users]


def upgrade_user_to_premium(user_id):
    """Manually upgrade user to premium (for testing/support)."""
    db = get_db()
    db.execute("UPDATE users SET tier='premium' WHERE user_id=?", (user_id,))
    db.execute(
        "INSERT INTO subscriptions (user_id, tier, started_at) VALUES (?, ?, ?)",
        (user_id, 'premium', datetime.now().isoformat())
    )
    db.commit()
    logger.info(f"User {user_id} upgraded to premium")
    return {"success": True, "user_id": user_id, "tier": "premium"}


def get_api_health():
    """Check system health."""
    try:
        from tm_api import search_events
        # Quick API test
        events = search_events("test", size=1)
        api_status = "healthy" if events else "degraded"
    except Exception as e:
        api_status = "down"
        logger.error(f"API health check failed: {e}")
    
    db = get_db()
    db_status = "healthy" if db else "down"
    
    return {
        "timestamp": datetime.now().isoformat(),
        "status": "healthy" if api_status == "healthy" and db_status == "healthy" else "degraded",
        "components": {
            "ticketmaster_api": api_status,
            "database": db_status,
            "watcher_job": "running"  # Could check last run time
        }
    }


def generate_admin_html():
    """Generate admin dashboard HTML."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>TicketWatch Admin Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0a0a0a; color: #fff; }
            .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
            header { border-bottom: 1px solid #333; padding: 20px 0 20px 0; margin-bottom: 30px; }
            h1 { font-size: 2em; color: #a78bfa; }
            
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 40px; }
            .card { background: #1a1a1a; border: 1px solid #333; border-radius: 8px; padding: 20px; }
            .card h3 { color: #a78bfa; font-size: 0.9em; text-transform: uppercase; margin-bottom: 10px; }
            .card .value { font-size: 2.5em; font-weight: bold; color: #fff; }
            .card .meta { color: #888; font-size: 0.9em; margin-top: 10px; }
            
            .chart-container { background: #1a1a1a; border: 1px solid #333; border-radius: 8px; padding: 20px; margin-bottom: 30px; }
            
            table { width: 100%; border-collapse: collapse; }
            th { background: #1a1a1a; text-align: left; padding: 12px; border-bottom: 1px solid #333; color: #a78bfa; }
            td { padding: 12px; border-bottom: 1px solid #222; }
            tr:hover { background: #1a1a1a; }
            
            .status { padding: 4px 8px; border-radius: 4px; font-size: 0.85em; font-weight: bold; }
            .status.healthy { background: #10b981; color: #fff; }
            .status.degraded { background: #f59e0b; color: #000; }
            .status.down { background: #ef4444; color: #fff; }
            
            button { background: #a78bfa; color: #000; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; font-weight: bold; }
            button:hover { background: #c4b5fd; }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🎫 TicketWatch Admin Dashboard</h1>
                <p style="color: #888;">Real-time metrics & management</p>
            </header>
            
            <div class="grid" id="stats"></div>
            
            <div class="chart-container">
                <h2 style="margin-bottom: 20px;">System Health</h2>
                <div id="health"></div>
            </div>
            
            <div class="chart-container">
                <h2 style="margin-bottom: 20px;">Recent Alerts</h2>
                <table id="alerts"></table>
            </div>
            
            <div class="chart-container">
                <h2 style="margin-bottom: 20px;">User Management</h2>
                <table id="users"></table>
            </div>
        </div>
        
        <script>
            async function loadDashboard() {
                try {
                    const response = await fetch('/api/admin/stats');
                    const data = await response.json();
                    
                    // Render stats
                    const statsHtml = `
                        <div class="card">
                            <h3>Total Users</h3>
                            <div class="value">${data.users.total}</div>
                            <div class="meta">Free: ${data.users.free} | Premium: ${data.users.premium}</div>
                        </div>
                        <div class="card">
                            <h3>Active Watches</h3>
                            <div class="value">${data.watches.active}</div>
                            <div class="meta">Total: ${data.watches.total}</div>
                        </div>
                        <div class="card">
                            <h3>Monthly Revenue</h3>
                            <div class="value">${data.revenue.monthly_mrr}</div>
                            <div class="meta">${data.revenue.premium_users} premium users</div>
                        </div>
                        <div class="card">
                            <h3>Conversion Rate</h3>
                            <div class="value">${data.users.conversion_rate}</div>
                            <div class="meta">Free → Premium</div>
                        </div>
                    `;
                    document.getElementById('stats').innerHTML = statsHtml;
                    
                    // Render alerts
                    const alertsHtml = data.alerts.recent.map(a => `
                        <tr>
                            <td>${a.event_name}</td>
                            <td>€${a.current_price.toFixed(2)}</td>
                            <td style="color: #888; font-size: 0.9em;">${new Date(a.sent_at).toLocaleString()}</td>
                        </tr>
                    `).join('');
                    document.getElementById('alerts').innerHTML = '<th>Event</th><th>Price</th><th>Time</th>' + alertsHtml;
                } catch (error) {
                    console.error('Dashboard load failed:', error);
                }
            }
            
            loadDashboard();
            setInterval(loadDashboard, 30000); // Refresh every 30 seconds
        </script>
    </body>
    </html>
    """


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    stats = get_dashboard_stats()
    print(json.dumps(stats, indent=2))
    
    health = get_api_health()
    print(json.dumps(health, indent=2))
