# Reddit API Setup Guide

This guide will walk you through setting up Reddit API credentials to enable real tutoring lead scraping from Reddit.

## 🔑 Getting Reddit API Credentials

### Step 1: Create a Reddit Account
If you don't have one already, create a Reddit account at https://www.reddit.com/register

### Step 2: Create a Reddit App

1. **Navigate to Reddit Apps:**
   - Go to https://www.reddit.com/prefs/apps
   - You might need to log in if you haven't already

2. **Create New App:**
   - Scroll to the bottom of the page
   - Click "Create App" or "Create Another App"

3. **Fill Out App Information:**
   - **Name:** `Tutoring Lead Scraper` (or any name you prefer)
   - **App type:** Select `script`
   - **Description:** `Scrapes tutoring opportunities from Reddit` (optional)
   - **About URL:** Leave blank (optional)
   - **Redirect URI:** `http://localhost:8080` (required, but we won't use it)

4. **Create the App:**
   - Click "Create app"

### Step 3: Get Your Credentials

After creating the app, you'll see your app details:

- **Client ID:** This is the 14-character string under your app name (looks like: `abcd1234efgh56`)
- **Client Secret:** This is the longer string next to "secret" (looks like: `xyz789_AbCdEfGhIjKlMnOpQrStUv`)

## 🔧 Configure the Application

### Step 1: Create Environment File

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit the `.env` file:**
   ```bash
   nano .env
   # or use your preferred text editor
   ```

3. **Add your credentials:**
   ```env
   REDDIT_CLIENT_ID=your_14_character_client_id_here
   REDDIT_CLIENT_SECRET=your_27_character_client_secret_here
   REDDIT_USER_AGENT=tutoring_scraper/1.0
   ```

### Step 2: Restart the Application

```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Restart the Flask application
python app.py
```

## ✅ Verify It's Working

1. **Check Console Output:**
   Look for the message: `Reddit API connection established successfully`

2. **Test the Scraping:**
   - Open http://localhost:5000
   - Click the "Refresh Leads" button
   - You should see real Reddit posts being scraped

3. **Check Lead Quality:**
   - Real Reddit leads will have additional fields:
     - Subreddit badge (e.g., "r/HomeworkHelp")
     - Reddit score (upvotes)
     - Number of comments
     - More diverse and recent content

## 🎯 What the Scraper Does

The enhanced Reddit scraper will:

### **Search Multiple Subreddits:**
- r/HomeworkHelp - Students seeking academic help
- r/tutor - Dedicated tutoring community
- r/learnmath - Math learning community
- r/chemhelp - Chemistry help requests
- r/PhysicsStudents - Physics study support
- r/EnglishLearning - English language help
- r/college, r/university - General academic communities
- And many more...

### **Use Smart Filtering:**
- Pattern matching for tutoring keywords
- Filters out non-tutoring related posts
- Focuses on recent posts (last 7 days)
- Removes duplicates automatically

### **Extract Rich Information:**
- Post title and full description
- Automatic subject categorization
- Budget/pricing extraction using regex
- Location detection for US/Canadian cities
- Reddit-specific metadata (score, comments, subreddit)

### **Advanced Features:**
- Real-time post discovery
- Intelligent duplicate detection
- Comprehensive location parsing
- Multiple budget format recognition
- Subject classification with scoring

## 🚀 Expected Results

With Reddit API enabled, you should see:

- **10-50+ real leads** per scraping session (depending on current activity)
- **Diverse subjects:** Math, Science, English, Programming, Test Prep, etc.
- **Current posts:** Fresh content from the last week
- **Rich metadata:** Scores, comments, subreddit information
- **Better targeting:** Only posts actually related to tutoring

## 🛡️ Rate Limiting & Best Practices

The scraper includes built-in protections:

- **Respects Reddit's rate limits** (1 request per second)
- **Focuses on recent content** (last 7 days only)
- **Limited scope** (25 posts per subreddit)
- **Error handling** for private/quarantined subreddits
- **Graceful fallbacks** if API fails

## 🔍 Troubleshooting

### **"Reddit API credentials not found"**
- Check that `.env` file exists in the project root
- Verify credentials are correctly formatted (no quotes needed)
- Ensure no extra spaces in the credentials

### **"Failed to initialize Reddit API"**
- Verify your Reddit app is configured as a "script" type
- Check that client ID and secret are correct
- Try creating a new Reddit app

### **No leads found or empty results**
- This is normal if there are no recent tutoring posts
- Try running the scraper at different times of day
- The scraper focuses on recent posts (last 7 days)

### **API Rate Limiting**
- The scraper automatically handles rate limits
- If you see rate limit errors, wait a few minutes and try again

## 📈 Performance Expectations

**Typical Results Per Scraping Session:**
- **Peak times (evenings/weekends):** 20-50+ leads
- **Off-peak times:** 5-15 leads
- **Subject distribution:** Math (40%), Science (25%), English (15%), Other (20%)
- **Response time:** 30-60 seconds for full scrape

**Best Times to Scrape:**
- **Sunday-Thursday evenings** (6-10 PM EST)
- **During academic semesters** (Sep-May)
- **Before exam periods** (mid-terms, finals)

Ready to get real tutoring leads from Reddit! 🎓