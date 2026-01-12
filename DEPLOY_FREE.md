# Deploy SkyMind for FREE - Complete Guide

## Option 1: Render.com (Recommended for Free)

### Step 1: Prepare the Repository

1. **Initialize Git** (if not already):
```bash
cd travel-agent
git init
git add .
git commit -m "Initial commit - SkyMind v0.2.0"
```

2. **Push to GitHub**:
```bash
# Create a new repo on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/skymind.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy to Render

1. **Go to** [render.com](https://render.com) and sign up (free)

2. **Click "New +"** → **"Web Service"**

3. **Connect your GitHub repo**: `skymind`

4. **Configure:**
   - **Name**: `skymind`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: **Free**

5. **Add Environment Variables**:
   ```
   ENV=production
   CACHE_ENABLED=false
   DATABASE_URL=<will be auto-filled when you add database>
   ALLOWED_ORIGINS=*
   ```

6. **Click "Create Web Service"**

7. **Wait 5-10 minutes** for deployment

8. **Your site is live!** 🎉
   - URL: `https://skymind.onrender.com`
   - Docs: `https://skymind.onrender.com/docs`

### Step 3: Add Free PostgreSQL Database

1. **In Render dashboard** → **"New +"** → **"PostgreSQL"**

2. **Configure:**
   - **Name**: `skymind-db`
   - **Plan**: **Free**

3. **Click "Create Database"**

4. **Copy the "Internal Database URL"**

5. **Go back to your Web Service** → **Environment**

6. **Update** `DATABASE_URL` with the copied URL

7. **Save Changes** (triggers auto-redeploy)

---

## Option 2: Fly.io (Good Free Tier)

### Step 1: Install Fly CLI

```bash
# macOS
brew install flyctl

# Or use install script
curl -L https://fly.io/install.sh | sh
```

### Step 2: Login and Launch

```bash
cd travel-agent

# Login
fly auth login

# Initialize and deploy
fly launch

# Follow prompts:
# - App name: skymind
# - Region: Choose closest to you
# - Database: Yes (PostgreSQL)
# - Deploy now: Yes
```

### Step 3: Set Environment Variables

```bash
fly secrets set ENV=production
fly secrets set CACHE_ENABLED=false
fly secrets set ALLOWED_ORIGINS=*
```

**Your site:** `https://skymind.fly.dev`

---

## Option 3: Railway (Trial Credits)

Railway gives you $5 trial credit (enough for ~1 month free).

### Quick Deploy:

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Add database
railway add --database postgresql

# Deploy
railway up

# Set environment
railway variables set CACHE_ENABLED=false
railway variables set ENV=production
```

**Your site:** `https://skymind.up.railway.app`

---

## Free Tier Limitations & Solutions

### ❌ No Redis Cache (Free Tier)
**Solution**: Set `CACHE_ENABLED=false` in environment variables
- Still works great, just slightly slower (200-500ms instead of 10-50ms)

### ❌ Server Sleeps After 15 Min (Render)
**Solution**: 
- First request takes 30s to wake up
- Or use a free uptime monitor like [UptimeRobot](https://uptimerobot.com) to ping every 5 min

### ❌ Database Expires After 90 Days (Render Free)
**Solution**: 
- Upgrade to $7/month DB later
- Or create new free DB every 90 days (not ideal)

---

## Testing Your Live Site

Once deployed, test it:

```bash
# Replace with your actual URL
export SITE_URL="https://skymind.onrender.com"

# Health check
curl $SITE_URL/health

# Search flights
curl -X POST $SITE_URL/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "origins": ["JFK"],
    "destinations": ["LAX"],
    "departure_date": "2024-06-15T00:00:00",
    "priority": "balanced"
  }'
```

---

## Making it a Masterpiece (Free Enhancements)

### 1. **Add a Beautiful Frontend**
Create a simple HTML/CSS/JS frontend:
- Deploy on **Vercel** (free)
- Or **Netlify** (free)
- Or **GitHub Pages** (free)

### 2. **Custom Domain** (Optional)
- Buy domain: ~$12/year (Namecheap, Google Domains)
- Point to your Render URL
- Free SSL included!

### 3. **Connect Real Flight API**
- **Amadeus**: Free tier (2K searches/month)
- Phase 2 of your implementation

### 4. **Add Analytics**
- **Google Analytics**: Free
- Track user searches and popular routes

### 5. **Monitoring**
- **Sentry**: Free tier for error tracking
- **UptimeRobot**: Free uptime monitoring

---

## Cost Breakdown

### Completely Free Setup:
- **Backend**: Render (Free)
- **Database**: Render PostgreSQL (Free for 90 days)
- **Frontend**: Vercel/Netlify (Free)
- **SSL**: Included (Free)
- **Monitoring**: Sentry Free + UptimeRobot (Free)
- **Flight API**: Amadeus Free Tier (2K/month)

**Total: $0/month** 🎉

### Upgrade Later (when you have users):
- **Render Pro**: $7/month (persistent DB)
- **Or Railway**: $5-20/month (includes Redis)
- **Domain**: $12/year

---

## Recommended: Start with Render

**Why:**
1. Easiest setup (no CLI needed)
2. Free PostgreSQL
3. Auto-deploys from GitHub
4. Great for MVPs

**After you validate the product:**
- Migrate to Railway ($5-20/month) for Redis caching
- Or stay on Render and upgrade DB ($7/month)

---

## Next Steps

1. **Push code to GitHub**
2. **Deploy to Render** (takes 10 minutes)
3. **Test your live API**
4. **Build a simple frontend** (optional)
5. **Connect Amadeus API** (Phase 2)
6. **Share with users!**

🚀 **You'll have a live, working flight search engine for FREE!**
