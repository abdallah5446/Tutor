import praw
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class RedditScraper:
    def __init__(self):
        # Reddit API credentials from environment variables
        self.client_id = os.getenv('REDDIT_CLIENT_ID')
        self.client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        self.user_agent = os.getenv('REDDIT_USER_AGENT', 'tutoring_scraper/1.0')
        
        # Initialize Reddit instance
        self.reddit = None
        self._initialize_reddit()
        
        # Tutoring-related keywords for filtering posts
        self.tutoring_keywords = [
            'tutor', 'tutoring', 'help with', 'need help', 'math help', 
            'homework help', 'study help', 'academic help', 'test prep',
            'algebra', 'calculus', 'chemistry', 'physics', 'biology',
            'english', 'writing', 'essay', 'assignment', 'exam prep',
            'looking for tutor', 'seeking tutor', 'private tutor',
            'online tutor', 'in person tutor', 'academic support'
        ]
        
        # Target subreddits for tutoring posts
        self.target_subreddits = [
            'HomeworkHelp', 'tutor', 'GetStudying', 'StudentLoans',
            'college', 'university', 'AskAcademia', 'study',
            'learnmath', 'chemhelp', 'PhysicsStudents', 'EnglishLearning',
            'students', 'studying', 'tutoring', 'AskReddit',
            'findareddit', 'tipofmytongue', 'HelpMeFind',
            'math', 'chemistry', 'physics', 'biology', 'engineering'
        ]
    
    def _initialize_reddit(self):
        """Initialize Reddit API connection"""
        try:
            if self.client_id and self.client_secret:
                self.reddit = praw.Reddit(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    user_agent=self.user_agent
                )
                # Test the connection
                self.reddit.user.me()
                print("Reddit API connection established successfully")
            else:
                print("Reddit API credentials not found. Using sample data.")
                self.reddit = None
        except Exception as e:
            print(f"Failed to initialize Reddit API: {e}")
            self.reddit = None
    
    def scrape_tutoring_posts(self) -> List[Dict[str, Any]]:
        """Scrape Reddit for tutoring-related posts"""
        leads = []
        
        if not self.reddit:
            print("Reddit API not available, returning sample data")
            return self._get_sample_leads()
        
        try:
            for subreddit_name in self.target_subreddits:
                try:
                    subreddit = self.reddit.subreddit(subreddit_name)
                    
                    # Search for recent posts (last 7 days)
                    for post in subreddit.new(limit=25):
                        # Skip posts older than 7 days
                        post_age = datetime.now() - datetime.fromtimestamp(post.created_utc)
                        if post_age.days > 7:
                            continue
                        
                        # Check if post is tutoring-related
                        if self._is_tutoring_related(post.title + " " + post.selftext):
                            lead = self._extract_lead_info(post)
                            if lead:
                                leads.append(lead)
                    
                    # Also search for tutoring-specific terms
                    for search_term in ['tutor', 'tutoring', 'homework help']:
                        try:
                            for post in subreddit.search(search_term, time_filter='week', limit=10):
                                if self._is_tutoring_related(post.title + " " + post.selftext):
                                    lead = self._extract_lead_info(post)
                                    if lead and not self._is_duplicate_lead(lead, leads):
                                        leads.append(lead)
                        except Exception as e:
                            print(f"Error searching r/{subreddit_name} for '{search_term}': {e}")
                            continue
                        
                except Exception as e:
                    print(f"Error accessing r/{subreddit_name}: {e}")
                    continue
            
            print(f"Successfully scraped {len(leads)} leads from Reddit")
            return leads
            
        except Exception as e:
            print(f"Error during Reddit scraping: {e}")
            return self._get_sample_leads()
    
    def _is_tutoring_related(self, text: str) -> bool:
        """Check if text contains tutoring-related keywords"""
        text_lower = text.lower()
        
        # More specific tutoring patterns
        tutoring_patterns = [
            r'\btutor\b', r'\btutoring\b', r'\bneed help\b',
            r'\bhomework help\b', r'\bstudy help\b', r'\bacademic help\b',
            r'\btest prep\b', r'\bexam prep\b', r'\bprivate tutor\b',
            r'\bonline tutor\b', r'\blooking for tutor\b', r'\bseeking tutor\b',
            r'\bhelp with math\b', r'\bhelp with chemistry\b', r'\bhelp with physics\b',
            r'\bmath tutor\b', r'\bchemistry tutor\b', r'\bphysics tutor\b',
            r'\benglish tutor\b', r'\bwriting help\b', r'\bessay help\b'
        ]
        
        # Check for specific patterns
        for pattern in tutoring_patterns:
            if re.search(pattern, text_lower):
                return True
        
        # Fallback to keyword matching
        return any(keyword in text_lower for keyword in self.tutoring_keywords)
    
    def _extract_lead_info(self, post) -> Dict[str, Any]:
        """Extract relevant information from a Reddit post"""
        try:
            # Basic post information
            title = post.title
            description = post.selftext if post.selftext else "No description available"
            url = f"https://reddit.com{post.permalink}"
            
            # Clean description (remove excessive whitespace, limit length)
            description = re.sub(r'\s+', ' ', description).strip()
            if len(description) > 500:
                description = description[:497] + "..."
            
            # Extract subject
            subject = self._extract_subject(title + " " + description)
            
            # Extract budget/pricing
            budget = self._extract_budget(title + " " + description)
            
            # Extract location (look for city/state patterns)
            location = self._extract_location(title + " " + description)
            
            # Determine contact method
            contact = "DM on Reddit"
            
            # Convert UTC timestamp to ISO format
            posted_date = datetime.fromtimestamp(post.created_utc).isoformat()
            
            lead = {
                'title': title,
                'description': description,
                'url': url,
                'location': location,
                'subject': subject,
                'budget': budget,
                'contact': contact,
                'posted_date': posted_date,
                'subreddit': post.subreddit.display_name,
                'score': post.score,
                'num_comments': post.num_comments
            }
            
            return lead
            
        except Exception as e:
            print(f"Error extracting lead info from Reddit post: {e}")
            return None
    
    def _extract_subject(self, text: str) -> str:
        """Extract subject from post text using keyword matching"""
        subjects = {
            'Mathematics': [
                'math', 'algebra', 'calculus', 'geometry', 'statistics', 
                'trigonometry', 'precalculus', 'differential', 'integral',
                'linear algebra', 'discrete math', 'number theory'
            ],
            'Science': [
                'chemistry', 'physics', 'biology', 'science', 'organic chemistry',
                'inorganic chemistry', 'biochemistry', 'molecular biology',
                'thermodynamics', 'quantum', 'mechanics', 'electricity'
            ],
            'English': [
                'english', 'writing', 'essay', 'literature', 'grammar',
                'composition', 'rhetoric', 'creative writing', 'poetry'
            ],
            'Computer Science': [
                'programming', 'coding', 'computer science', 'python', 'java',
                'javascript', 'c++', 'web development', 'software', 'algorithms',
                'data structures', 'machine learning', 'artificial intelligence'
            ],
            'Languages': [
                'spanish', 'french', 'german', 'chinese', 'japanese', 'italian',
                'language', 'esl', 'foreign language', 'linguistics'
            ],
            'Test Preparation': [
                'sat', 'act', 'gre', 'gmat', 'lsat', 'mcat', 'test prep',
                'exam prep', 'standardized test', 'college prep'
            ],
            'Business': [
                'accounting', 'finance', 'economics', 'business', 'marketing',
                'management', 'statistics', 'microeconomics', 'macroeconomics'
            ]
        }
        
        text_lower = text.lower()
        
        # Find the best matching subject
        subject_scores = {}
        for subject, keywords in subjects.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                subject_scores[subject] = score
        
        if subject_scores:
            return max(subject_scores, key=subject_scores.get)
        
        return 'General Academic Support'
    
    def _extract_budget(self, text: str) -> str:
        """Extract budget information from text using regex patterns"""
        # Comprehensive budget patterns
        budget_patterns = [
            r'\$\d+(?:\.\d{1,2})?(?:\s*(?:per|/)\s*(?:hour|hr|h))',
            r'\$\d+(?:\.\d{1,2})?\s*(?:an?\s*)?(?:hour|hr|h)',
            r'\d+\s*dollars?\s*(?:per\s*)?(?:hour|hr|h)',
            r'\$\d+(?:\.\d{1,2})?\s*(?:per\s*session|/session)',
            r'\d+\$\s*(?:per\s*)?(?:hour|hr|h)',
            r'(?:pay|paying|budget|rate)\s*:?\s*\$?\d+',
            r'\$\d+(?:\.\d{1,2})?(?:\s*-\s*\$?\d+(?:\.\d{1,2})?)?'
        ]
        
        for pattern in budget_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group().strip()
        
        # Look for general budget indicators
        budget_keywords = ['negotiable', 'flexible rate', 'competitive rate', 'reasonable rate']
        text_lower = text.lower()
        for keyword in budget_keywords:
            if keyword in text_lower:
                return keyword.title()
        
        return 'Not specified'
    
    def _extract_location(self, text: str) -> str:
        """Extract location information from text"""
        # Common location patterns
        location_patterns = [
            # US States and major cities
            r'\b(?:New York|NYC|Los Angeles|LA|Chicago|Houston|Phoenix|Philadelphia|San Antonio|San Diego|Dallas|San Jose|Austin|Jacksonville|Fort Worth|Columbus|Charlotte|San Francisco|Indianapolis|Seattle|Denver|Washington DC|Boston|El Paso|Nashville|Detroit|Oklahoma City|Portland|Las Vegas|Memphis|Louisville|Baltimore|Milwaukee|Albuquerque|Tucson|Fresno|Sacramento|Kansas City|Mesa|Virginia Beach|Atlanta|Colorado Springs|Raleigh|Omaha|Miami|Oakland|Minneapolis|Tulsa|Cleveland|Wichita|Arlington|New Orleans|Bakersfield|Tampa|Honolulu|Aurora|Anaheim|Santa Ana|St. Louis|Riverside|Corpus Christi|Lexington|Pittsburgh|Anchorage|Stockton|Cincinnati|St. Paul|Toledo|Newark|Greensboro|Plano|Henderson|Lincoln|Buffalo|Jersey City|Chula Vista|Fort Wayne|Orlando|St. Petersburg|Chandler|Laredo|Norfolk|Durham|Madison|Lubbock|Irvine|Winston-Salem|Glendale|Garland|Hialeah|Reno|Chesapeake|Gilbert|Baton Rouge|Irving|Scottsdale|North Las Vegas|Fremont|Boise|Richmond|San Bernardino|Birmingham|Spokane|Rochester|Des Moines|Modesto|Fayetteville|Tacoma|Oxnard|Fontana|Columbus|Montgomery|Moreno Valley|Shreveport|Aurora|Yonkers|Akron|Huntington Beach|Little Rock|Augusta|Amarillo|Glendale|Mobile|Grand Rapids|Salt Lake City|Tallahassee|Huntsville|Grand Prairie|Knoxville|Worcester|Newport News|Brownsville|Overland Park|Santa Clarita|Providence|Garden Grove|Chattanooga|Oceanside|Jackson|Fort Lauderdale|Santa Rosa|Rancho Cucamonga|Port St. Lucie|Tempe|Ontario|Vancouver|Springfield|Lancaster|Eugene|Pembroke Pines|Salem|Cape Coral|Peoria|Sioux Falls|Springfield|Springfield|Elk Grove|Rockford|Palmdale|Corona|Salinas|Pomona|Paterson|Joliet|Kansas City|Torrance|Syracuse|Bridgeport|Hayward|Fort Collins|Escondido|Lakewood|Naperville|Dayton|Hollywood|Sunnyvale|Alexandria|Mesquite|Hampton|Pasadena|Orange|Savannah|Cary|Fullerton|Warren|McAllen|Columbia|Sterling Heights|New Haven|Miramar|Waco|Thousand Oaks|Cedar Rapids|Charleston|Visalia|Topeka|Elizabeth|Gainesville|Thornton|Roseville|Carrollton|Coral Springs|Stamford|Simi Valley|Concord|Hartford|Kent|Lafayette|Midland|Surprise|Denton|Victorville|Evansville|Santa Clara|Abilene|Athens|Vallejo|Allentown|Norman|Beaumont|Independence|Murfreesboro|Ann Arbor|Fargo|Wilmington|Provo|Gold Coast|Miami Gardens|McKinney|Pearland|Richardson|Antioch|Overland Park|West Valley City|West Covina|Inglewood|Carlsbad|Rochester|Westminster|Miami Beach|Clearwater|Lowell|Cambridge|West Palm Beach|Arvada|Boulder|Lansing|Pueblo|Fairfield|El Monte|Richmond|Clarksville|Burbank|Pompano Beach|North Charleston|West Jordan|Gresham|Broken Arrow|Sandy|Temecula|Santa Maria|Tyler|Lake Forest|Rialto|Albany|Berkeley|Green Bay|Sparks|High Point|Ventura|Bend|Pueblo|Everett|West Covina|Palm Bay|Round Rock|El Cajon|Downey|Jurupa Valley|Norwalk|Temecula|Costa Mesa|Sandy Springs|Dearborn|College Station)\b',
            
            # Canadian cities and provinces
            r'\b(?:Toronto|Montreal|Vancouver|Calgary|Edmonton|Ottawa|Mississauga|Winnipeg|Quebec City|Hamilton|Brampton|London|Markham|Gatineau|Vaughan|Kitchener|Laval|Halifax|Windsor|Oshawa|Victoria|Saskatoon|Regina|Richmond|Oakville|Burlington|Barrie|Greater Sudbury|Sherbrooke|Abbotsford|Coquitlam|St. Catharines|Guelph|Cambridge|Whitby|Kelowna|Thunder Bay|Terrebonne|Waterloo|Delta|Langley|Richmond Hill|Brantford|Saint-Jean-sur-Richelieu|Burnaby|Lethbridge|Nanaimo|Red Deer|Kamloops|Medicine Hat|St. John\'s|Moncton|Saguenay|Trois-Rivières|Peterborough|Belleville|Sarnia|Chilliwack|Airdrie|Ajax|Cornwall|Granby|St. Thomas|Prince George|Sault Ste. Marie|Pickering|Charlottetown|Fredericton|North Bay|Brandon|Rimouski|Welland|Niagara Falls|Shawinigan|Joliette|Dollard-des-Ormeaux|Beloeil|Sept-Îles|Repentigny|Saint-Jérôme|North Vancouver|Brossard|New Westminster|Saanich|Maple Ridge|Saint-Eustache|Caledon|St. Albert|Strathcona County|Halton Hills|Blainville|Mirabel|Wood Buffalo|King|Clarington|Oakville|ON|BC|AB|SK|MB|QC|NS|NB|PE|NL|YT|NT|NU)\b',
            
            # General location patterns
            r'\b(?:in|at|near|around|located in|from)\s+([A-Z][a-zA-Z\s]+(?:,\s*[A-Z]{2})?)\b',
            r'\b([A-Z][a-zA-Z\s]+,\s*[A-Z]{2,3})\b',  # City, State/Province
            r'\b([A-Z][a-zA-Z\s]+ area)\b',
            r'\b(online|remote|virtual)\b'
        ]
        
        for pattern in location_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                location = matches[0] if isinstance(matches[0], str) else matches[0][0] if matches[0] else ""
                if location and len(location.strip()) > 2:
                    return location.strip()
        
        return 'Location not specified'
    
    def _is_duplicate_lead(self, new_lead: Dict[str, Any], existing_leads: List[Dict[str, Any]]) -> bool:
        """Check if a lead is duplicate based on title and URL similarity"""
        for existing_lead in existing_leads:
            # Check URL exact match
            if new_lead.get('url') == existing_lead.get('url'):
                return True
            
            # Check title similarity (simple approach)
            new_title = new_lead.get('title', '').lower().strip()
            existing_title = existing_lead.get('title', '').lower().strip()
            
            if new_title and existing_title and new_title == existing_title:
                return True
        
        return False
    
    def _get_sample_leads(self) -> List[Dict[str, Any]]:
        """Fallback sample data when Reddit API is not available"""
        return [
            {
                'title': 'Need help with Calculus 2 - derivatives and integrals',
                'description': 'Struggling with my calculus course, need a tutor for derivatives and integration. Willing to pay $25/hour.',
                'url': 'https://reddit.com/r/HomeworkHelp/sample1',
                'location': 'Toronto, ON',
                'subject': 'Mathematics',
                'budget': '$25/hour',
                'contact': 'DM on Reddit',
                'posted_date': (datetime.now() - timedelta(hours=2)).isoformat(),
                'subreddit': 'HomeworkHelp',
                'score': 5,
                'num_comments': 3
            },
            {
                'title': 'Chemistry tutor needed for organic chemistry',
                'description': 'Second year university student looking for help with organic chemistry reactions and mechanisms.',
                'url': 'https://reddit.com/r/chemistry/sample2',
                'location': 'Vancouver, BC',
                'subject': 'Science',
                'budget': 'Negotiable',
                'contact': 'DM on Reddit',
                'posted_date': (datetime.now() - timedelta(hours=5)).isoformat(),
                'subreddit': 'chemistry',
                'score': 8,
                'num_comments': 2
            },
            {
                'title': 'High school physics help needed',
                'description': 'Grade 12 student struggling with kinematics and dynamics. Need help before final exam.',
                'url': 'https://reddit.com/r/physics/sample3',
                'location': 'Montreal, QC',
                'subject': 'Science',
                'budget': '$20/hour',
                'contact': 'DM on Reddit',
                'posted_date': (datetime.now() - timedelta(hours=8)).isoformat(),
                'subreddit': 'physics',
                'score': 12,
                'num_comments': 7
            },
            {
                'title': 'Essay writing help for English literature',
                'description': 'University student needs help with essay structure and analysis for Shakespeare course.',
                'url': 'https://reddit.com/r/english/sample4',
                'location': 'Calgary, AB',
                'subject': 'English',
                'budget': '$30/hour',
                'contact': 'DM on Reddit',
                'posted_date': (datetime.now() - timedelta(hours=12)).isoformat(),
                'subreddit': 'english',
                'score': 6,
                'num_comments': 4
            }
        ]