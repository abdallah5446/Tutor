from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import os
import json
from datetime import datetime
import threading
import time
from scrapers.reddit_scraper import RedditScraper
from scrapers.kijiji_scraper import KijijiScraper
from scrapers.facebook_scraper import FacebookScraper
from lead_manager import LeadManager

app = Flask(__name__)
CORS(app)

# Initialize lead manager and scrapers
lead_manager = LeadManager()
reddit_scraper = RedditScraper()
kijiji_scraper = KijijiScraper()
facebook_scraper = FacebookScraper()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/leads')
def get_leads():
    """Get all leads with optional filtering"""
    source = request.args.get('source', '')
    keyword = request.args.get('keyword', '')
    
    leads = lead_manager.get_leads(source=source, keyword=keyword)
    return jsonify({
        'leads': leads,
        'total': len(leads),
        'last_updated': lead_manager.get_last_updated()
    })

@app.route('/api/scrape')
def trigger_scrape():
    """Manually trigger a scrape of all sources"""
    def scrape_all():
        try:
            # Reddit scraping
            reddit_leads = reddit_scraper.scrape_tutoring_posts()
            lead_manager.add_leads(reddit_leads, 'reddit')
            
            # Kijiji scraping
            kijiji_leads = kijiji_scraper.scrape_tutoring_posts()
            lead_manager.add_leads(kijiji_leads, 'kijiji')
            
            # Facebook Marketplace scraping
            fb_leads = facebook_scraper.scrape_tutoring_posts()
            lead_manager.add_leads(fb_leads, 'facebook')
            
            print(f"Scraping completed at {datetime.now()}")
        except Exception as e:
            print(f"Error during scraping: {e}")
    
    # Run scraping in background thread
    thread = threading.Thread(target=scrape_all)
    thread.daemon = True
    thread.start()
    
    return jsonify({'message': 'Scraping started', 'status': 'success'})

@app.route('/api/stats')
def get_stats():
    """Get statistics about leads"""
    stats = lead_manager.get_stats()
    return jsonify(stats)

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('data', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('scrapers', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)