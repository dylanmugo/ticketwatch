"""
TicketWatch Analytics & Metrics
Track user behavior, revenue, engagement
"""
import json
import logging
from datetime import datetime, timedelta
from database import get_db

logger = logging.getLogger(__name__)


def get_daily_metrics(days=30):
    """Get metrics for past N days."""
    db = get_db()
    
    metrics = []
    for i in range(days):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        
        users_created = db.execute(
            "SELECT COUNT(*) as cnt FROM users WHERE DATE(created_at) = ?",
            (date,)
        ).fetchone()['cnt']
        
        watches_created = db.execute(
            "SELECT COUNT(*) as cnt FROM watches WHERE DATE(created_at) = ?",
            (date,)
        ).fetchone()['cnt']
        
        alerts_sent = db.execute(
            "SELECT COUNT(*) as cnt FROM alerts_sent WHERE DATE(sent_at) = ?",
            (date,)
        ).fetchone()['cnt']
        
        metrics.append({
            "date": date,
            "users_created": users_created,
            "watches_created": watches_created,
            "alerts_sent": alerts_sent
        })
    
    return metrics


def get_cohort_analysis():
    """Analyze user cohorts by signup date."""
    db = get_db()
    
    cohorts = db.execute(
        """SELECT 
           DATE(created_at) as cohort_date,
           COUNT(*) as users,
           SUM(CASE WHEN tier='premium' THEN 1 ELSE 0 END) as premium_users
           FROM users
           GROUP BY DATE(created_at)
           ORDER BY cohort_date DESC"""
    ).fetchall()
    
    return [{
        "date": c['cohort_date'],
        "total": c['users'],
        "premium": c['premium_users'],
        "conversion": f"{(c['premium_users'] / c['users'] * 100):.1f}%" if c['users'] > 0 else "0%"
    } for c in cohorts]


def get_watch_metrics():
    """Analyze watch creation and conversion."""
    db = get_db()
    
    total_watches = db.execute("SELECT COUNT(*) as cnt FROM watches").fetchone()['cnt']
    active_watches = db.execute("SELECT COUNT(*) as cnt FROM watches WHERE status='active'").fetchone()['cnt']
    alerted_watches = db.execute("SELECT COUNT(*) as cnt FROM watches WHERE status='alerted'").fetchone()['cnt']
    cancelled_watches = db.execute("SELECT COUNT(*) as cnt FROM watches WHERE status='cancelled'").fetchone()['cnt']
    
    avg_max_price = db.execute("SELECT AVG(max_price) as avg_price FROM watches WHERE max_price IS NOT NULL").fetchone()['avg_price']
    
    return {
        "total": total_watches,
        "active": active_watches,
        "alerted": alerted_watches,
        "cancelled": cancelled_watches,
        "alert_rate": f"{(alerted_watches / max(total_watches, 1) * 100):.1f}%",
        "average_max_price": f"€{avg_max_price:.2f}" if avg_max_price else "N/A"
    }


def get_revenue_metrics():
    """Calculate revenue and projections."""
    db = get_db()
    
    premium_users = db.execute("SELECT COUNT(*) as cnt FROM users WHERE tier='premium'").fetchone()['cnt']
    total_users = db.execute("SELECT COUNT(*) as cnt FROM users").fetchone()['cnt']
    
    monthly_mrr = premium_users * 4.99
    annual_arr = monthly_mrr * 12
    
    # Estimate affiliate revenue (conservative: 0.5 per premium user)
    affiliate_revenue = premium_users * 0.5
    
    return {
        "premium_users": premium_users,
        "total_users": total_users,
        "conversion_rate": f"{(premium_users / max(total_users, 1) * 100):.1f}%",
        "monthly_mrr": f"€{monthly_mrr:.2f}",
        "annual_arr": f"€{annual_arr:.2f}",
        "monthly_affiliate": f"€{affiliate_revenue:.2f}",
        "total_monthly_revenue": f"€{(monthly_mrr + affiliate_revenue):.2f}"
    }


def export_analytics_csv():
    """Export analytics to CSV format."""
    metrics = get_daily_metrics(30)
    
    csv = "date,users_created,watches_created,alerts_sent\n"
    for m in metrics:
        csv += f"{m['date']},{m['users_created']},{m['watches_created']},{m['alerts_sent']}\n"
    
    return csv


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("=== Daily Metrics (Past 7 Days) ===")
    metrics = get_daily_metrics(7)
    for m in metrics[:7]:
        print(json.dumps(m))
    
    print("\n=== Cohort Analysis ===")
    cohorts = get_cohort_analysis()
    for c in cohorts:
        print(json.dumps(c))
    
    print("\n=== Watch Metrics ===")
    watches = get_watch_metrics()
    print(json.dumps(watches, indent=2))
    
    print("\n=== Revenue Metrics ===")
    revenue = get_revenue_metrics()
    print(json.dumps(revenue, indent=2))
