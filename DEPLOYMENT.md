# TicketWatch Deployment Guide

Everything is ready to deploy on your RockPro64. Follow these steps to go live.

---

## 🚀 Deployment Steps (5 minutes)

### Step 1: OpenClaw Integration

Your existing OpenClaw instance needs to route WhatsApp messages to TicketWatch.

**Option A: Manual Integration (Simplest)**

Create a custom message handler in OpenClaw that calls:

```bash
python3 /home/admin/ticketwatch/openclaw_handler.py \
  --user-id "$CALLER" \
  --message "$MESSAGE"
```

This returns JSON with the WhatsApp response.

**Option B: Use as OpenClaw Skill**

The SKILL.md file in `/home/admin/.openclaw/workspace/skills/ticketwatch/` teaches OpenClaw how to handle ticket watch requests.

### Step 2: Deploy Cron Job

**Option A: System Crontab (If available)**

```bash
crontab -e
```

Add this line:

```
*/5 * * * * cd /home/admin/ticketwatch && python3 watcher.py >> logs/watcher.log 2>&1
```

Save and exit. Verify:

```bash
crontab -l | grep ticketwatch
```

**Option B: systemd Timer (Recommended for ARM64)**

If cron isn't available, use systemd timers (better for RockPro64):

```bash
# Copy service files to systemd
sudo cp /home/admin/ticketwatch/ticketwatch-watcher.service /etc/systemd/system/
sudo cp /home/admin/ticketwatch/ticketwatch-watcher.timer /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable the timer
sudo systemctl enable ticketwatch-watcher.timer

# Start the timer
sudo systemctl start ticketwatch-watcher.timer

# Verify it's running
sudo systemctl status ticketwatch-watcher.timer
```

Check logs:

```bash
journalctl -u ticketwatch-watcher.timer -f
journalctl -u ticketwatch-watcher.service -f
```

### Step 3: Verify Everything Works

**Test the handler:**

```bash
cd /home/admin/ticketwatch

# Test search
python3 openclaw_handler.py \
  --user-id "test" \
  --message "What concerts are on in Dublin?"

# Test watch creation
python3 openclaw_handler.py \
  --user-id "test" \
  --message "Watch for Fred Again under €80"
```

Both should return JSON without errors.

**Test the watcher:**

```bash
python3 watcher.py
```

Should check database and output JSON.

### Step 4: Go Live

Send a real WhatsApp message from your phone (or a test phone):

```
"What's on?"
```

You should get back a list of Irish events.

Then try:

```
"Watch for Bicep under €50"
```

You should get a confirmation prompt.

---

## 📊 Monitoring

### Check if watcher is running

**With cron:**

```bash
grep CRON /var/log/syslog | grep ticketwatch | tail -5
```

**With systemd:**

```bash
sudo journalctl -u ticketwatch-watcher.service -n 20
```

### Check logs

```bash
tail -f /home/admin/ticketwatch/logs/watcher-$(date +%Y-%m-%d).log
tail -f /home/admin/ticketwatch/logs/openclaw.log
```

### Check database

```bash
sqlite3 /home/admin/ticketwatch/data/ticketwatch.db

# See watches
SELECT user_id, event_name, max_price, status FROM watches;

# See alerts sent
SELECT event_name, current_price, sent_at FROM alerts_sent ORDER BY sent_at DESC LIMIT 5;

# See users
SELECT * FROM users;
```

---

## 🔧 Troubleshooting

### Watcher isn't running

**Check it exists:**

```bash
ls -la /home/admin/ticketwatch/watcher.py
```

**Run manually to debug:**

```bash
cd /home/admin/ticketwatch
python3 watcher.py
```

If errors, fix them in the code.

**If using cron:**

```bash
# Check crontab
crontab -l | grep ticketwatch

# Force run manually
*/5 * * * * cd /home/admin/ticketwatch && python3 watcher.py
```

**If using systemd:**

```bash
sudo systemctl status ticketwatch-watcher.timer
sudo systemctl status ticketwatch-watcher.service
```

### OpenClaw handler returning errors

```bash
python3 /home/admin/ticketwatch/openclaw_handler.py \
  --user-id "test" \
  --message "test message"
```

Check `/home/admin/ticketwatch/logs/openclaw.log` for details.

### No alerts being sent

1. **Check database has watches:**

```bash
sqlite3 /home/admin/ticketwatch/data/ticketwatch.db \
  "SELECT * FROM watches WHERE status='active';"
```

If empty, watches aren't being created.

2. **Check watcher is running:**

```bash
ps aux | grep watcher
```

3. **Check logs:**

```bash
tail -f /home/admin/ticketwatch/logs/watcher-$(date +%Y-%m-%d).log
```

4. **Test watcher manually:**

```bash
cd /home/admin/ticketwatch
python3 watcher.py
```

---

## 📱 Testing Checklist

Before going live, test these:

- [ ] Handler works: `python3 openclaw_handler.py --user-id "test" --message "test"`
- [ ] Search works: "What concerts are on?"
- [ ] Watch creation works: "Watch for [artist] under €[price]"
- [ ] Watch confirmation works: Send "yes" after watch prompt
- [ ] List works: "My watches"
- [ ] Cancel works: "Cancel [artist]"
- [ ] Status works: "Any updates?"
- [ ] Watcher runs: `python3 watcher.py`
- [ ] Logs are created: `ls logs/`
- [ ] Database persists: `sqlite3 data/ticketwatch.db "SELECT COUNT(*) FROM watches;"`
- [ ] Real Ticketmaster API is working

---

## 🚦 Auto-Start on Boot

To make TicketWatch auto-start when RockPro64 reboots:

**With systemd timer (already enabled above):**

```bash
sudo systemctl is-enabled ticketwatch-watcher.timer
# Output should be: enabled
```

**With cron:**

Cron runs automatically on boot, no extra config needed.

---

## 🎯 Production Checklist

Before going live publicly:

- [ ] API key is set (not hardcoded in public repo)
- [ ] Ticketmaster API is working
- [ ] Watcher runs every 5 minutes
- [ ] Alerts send within 1 minute of match
- [ ] Database backups scheduled
- [ ] Error notifications set up
- [ ] WhatsApp rate limiting configured
- [ ] Usage monitoring in place
- [ ] Rollback plan documented

---

## 📈 Next Steps (Week 2)

1. **Monitor for 3 days** — Check logs, verify alerts work
2. **Add Stripe** — Payment integration for premium tier
3. **Build landing page** — Next.js + Vercel
4. **Affiliate program** — Ticketmaster commission setup
5. **Marketing** — Social posts, Reddit, Irish music groups

---

## 🆘 Support

For issues:

1. Check logs: `/home/admin/ticketwatch/logs/`
2. Test manually: `python3 openclaw_handler.py --user-id "test" --message "test"`
3. Check database: `sqlite3 data/ticketwatch.db ".schema"`
4. Review code: `vim handler.py`, `vim watcher.py`

---

**Ready to ship.** 🚀

**Questions?** Check README.md, SKILL.md, or QUICKSTART.md.
