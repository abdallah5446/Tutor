# Tutoring Lead Finder

A modern web application that aggregates tutoring opportunities from Reddit, Kijiji, and Facebook Marketplace, presenting them in a clean, searchable interface.

![Tutoring Lead Finder](https://img.shields.io/badge/Python-3.8%2B-blue) ![Flask](https://img.shields.io/badge/Flask-3.0.0-green) ![JavaScript](https://img.shields.io/badge/JavaScript-ES6-yellow)

## Features

### 🔍 Multi-Platform Scraping
- **Reddit**: Searches tutoring-related subreddits for help requests and tutor posts
- **Kijiji**: Monitors tutoring services and lesson requests in Canada
- **Facebook Marketplace**: Tracks tutoring opportunities and academic help posts

### 💻 Modern Web Interface
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Real-time Search**: Instant filtering by keywords, source, and subject
- **Interactive Dashboard**: Live statistics and source breakdown
- **Modal Details**: Click any lead for comprehensive information

### 📊 Smart Features
- **Duplicate Detection**: Automatically filters out duplicate posts
- **Subject Classification**: AI-powered categorization of tutoring subjects
- **Budget Extraction**: Automatically identifies pricing information
- **Location Parsing**: Extracts and displays location data

## Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd tutoring-lead-finder
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Open your browser**
   Navigate to `http://localhost:5000`

## Usage

### Dashboard Overview
- **Total Leads**: Number of all scraped leads
- **Recent Leads**: Leads found in the last 24 hours
- **Last Updated**: Timestamp of the most recent scraping
- **Refresh Button**: Manually trigger a new scraping session

### Filtering & Search
- **Keyword Search**: Search across titles, descriptions, and subjects
- **Source Filter**: Filter by Reddit, Kijiji, or Facebook
- **Subject Filter**: Filter by subject area (Math, Science, English, etc.)
- **Clear Filters**: Reset all filters to view all leads

### Lead Information
Each lead displays:
- **Title**: Original post title
- **Source**: Platform where the lead was found
- **Subject**: Automatically categorized subject area
- **Budget**: Extracted pricing information
- **Description**: Post content summary
- **Location**: Geographic location if available
- **Posted Date**: When the original post was created

## Project Structure

```
tutoring-lead-finder/
├── app.py                 # Main Flask application
├── lead_manager.py        # Lead storage and management
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── data/
│   └── leads.json        # Stored leads (auto-created)
├── scrapers/
│   ├── __init__.py
│   ├── reddit_scraper.py    # Reddit scraping logic
│   ├── kijiji_scraper.py    # Kijiji scraping logic
│   └── facebook_scraper.py  # Facebook scraping logic
├── templates/
│   └── index.html        # Main HTML template
└── static/
    ├── css/
    │   └── style.css     # Application styling
    └── js/
        └── app.js        # Frontend JavaScript
```

## API Endpoints

### GET `/`
Serves the main application interface

### GET `/api/leads`
Returns all leads with optional filtering
- **Query Parameters:**
  - `source`: Filter by source (reddit, kijiji, facebook)
  - `keyword`: Search by keyword

### GET `/api/scrape`
Manually triggers scraping of all sources
- **Response:** Status message indicating scraping has started

### GET `/api/stats`
Returns application statistics
- **Response:** Total leads, recent leads, source breakdown, last updated

## Configuration

### Reddit API (Optional)
For production use with Reddit, set up API credentials:

1. Create a Reddit app at https://www.reddit.com/prefs/apps
2. Add credentials to environment variables:
   ```bash
   export REDDIT_CLIENT_ID="your_client_id"
   export REDDIT_CLIENT_SECRET="your_client_secret"
   export REDDIT_USER_AGENT="tutoring_scraper"
   ```

### Web Scraping Considerations
- The current implementation uses sample data for demonstration
- Real scraping requires careful handling of rate limits and terms of service
- Consider using official APIs where available
- Implement proper error handling and retry logic

## Technology Stack

### Backend
- **Flask**: Web framework for Python
- **Beautiful Soup**: HTML parsing for web scraping
- **Requests**: HTTP library for API calls
- **PRAW**: Reddit API wrapper (optional)
- **Selenium**: Browser automation for dynamic content

### Frontend
- **HTML5**: Modern semantic markup
- **CSS3**: Responsive design with Flexbox and Grid
- **JavaScript ES6**: Modern JavaScript with async/await
- **Font Awesome**: Icon library

## Development

### Adding New Sources
1. Create a new scraper class in the `scrapers/` directory
2. Implement the `scrape_tutoring_posts()` method
3. Add the scraper to `app.py`
4. Update the frontend filters if needed

### Customizing Subjects
Edit the subject classification logic in each scraper's `_determine_subject()` method.

### Styling Changes
Modify `static/css/style.css` for visual customizations. The design uses CSS custom properties for easy theming.

## Deployment

### Local Development
```bash
python app.py
```

### Production (using Gunicorn)
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Docker (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

## Legal Considerations

- **Terms of Service**: Ensure compliance with each platform's ToS
- **Rate Limiting**: Implement appropriate delays between requests
- **Data Privacy**: Handle personal information responsibly
- **Copyright**: Respect intellectual property rights

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions, issues, or feature requests, please open an issue on GitHub.

## Acknowledgments

- Reddit API for community data access
- Kijiji for classified listings
- Facebook for marketplace opportunities
- Open source community for tools and libraries