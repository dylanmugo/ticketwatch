# TicketWatch Vercel Deployment Guide

**Status:** ✅ Ready to Deploy  
**Estimated Time:** 15 minutes  

---

## Quick Deploy (3 Steps)

### 1. Push to GitHub

```bash
cd /home/admin/ticketwatch
git remote add origin https://github.com/YOUR_USERNAME/ticketwatch.git
git push -u origin main
```

### 2. Connect to Vercel

- Go to https://vercel.com/new
- Select "Next.js"
- Import your GitHub repo
- Click "Deploy"

### 3. Set Domain

- Vercel dashboard → Settings → Domains
- Add `ticketwatch.ie` (if registered)
- Or use Vercel's free subdomain

**LIVE in < 5 minutes** ✅

---

## Manual Deploy (Alternative)

```bash
npm install -g vercel
cd /home/admin/ticketwatch/landing-page
vercel login
vercel deploy
```

---

## Environment Variables

No env vars needed for basic deploy. When adding Stripe:

```
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_xxxxx
STRIPE_SECRET_KEY=sk_live_xxxxx (backend only)
```

Set in Vercel Dashboard → Settings → Environment Variables

---

## File Structure

```
landing-page/
├── app/
│   ├── page.tsx          (homepage)
│   ├── layout.tsx        (root layout)
│   └── globals.css       (tailwind)
├── package.json
├── next.config.js
├── tailwind.config.ts
├── tsconfig.json
├── vercel.json
└── .vercelignore
```

---

## Verify Build Locally

```bash
cd /home/admin/ticketwatch/landing-page
npm install
npm run build
npm run start
```

Visit http://localhost:3000

---

## After Deployment

1. ✅ Test homepage loads
2. ✅ Check pricing section
3. ✅ Click WhatsApp button
4. ✅ Mobile responsive?
5. ✅ Social media links work

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "Module not found" | Run `npm install` |
| Build fails | Check node_modules, delete & reinstall |
| CSS not loading | Verify tailwind.config.ts |
| Image errors | Check public/ folder exists |

---

## Next Steps

1. Deploy landing page (today)
2. Connect Stripe (tomorrow)
3. Add checkout page (day 3)
4. Go live with payments (day 4)

---

**You're ready. Deploy now.** 🚀
