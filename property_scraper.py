import os
import time
import random
import csv
import json
import requests
from typing import Dict, List, Optional
from datetime import datetime

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import random
import time
from typing import Optional, Dict, List, Any
from bs4 import BeautifulSoup
import os

# Configuration
BASE_URL = "https://www.property.co.zw"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# Property types and their corresponding slugs on the website
PROPERTY_TYPES = {
    'townhouse': 'townhouses',
    'apartment': 'flats-apartments',
    'house': 'houses'
}

# Suburbs in Harare by region
HARARE_SUBURBS = {
    'north': ['Borrowdale', 'Borrowdale Brooke', 'Chisipite', 'Glen Lorne', 
              'Gunhill', 'Hellenic', 'Highlands', 'Holiday Inn', 'Houghton Park',
              'Mt Pleasant', 'Newlands', 'Pomona', 'Umwinsidale'],
    'south': ['Ardbennie', 'Arundel', 'Arundel Village', 'Belvedere', 
              'Eastlea', 'Greendale', 'Greencroft', 'Hatfield', 'Mabvuku',
              'Rugare', 'Southerton', 'St Martins', 'Sunnyvale', 'Tynwald', 'Waterfalls'],
    'east': ['Alexandra Park', 'Ashbrittle', 'Avonlea', 'Avondale', 
             'Belgravia', 'Belvedere', 'Bluff Hill', 'Borrowdale', 'Borrowdale Brooke',
             'Chisipite', 'Colne Valley', 'Eastlea', 'Eastview', 'Glen Lorne',
             'Glenwood', 'Greendale', 'Groombridge', 'Hillside', 'Hillside Dales',
             'Hillside East', 'Hillside North', 'Hillside West', 'Houghton Park',
             'Lorraine', 'Lorraine Ridge', 'Mabelreign', 'Malborough', 'Marlborough',
             'Marlborough East', 'Marlborough West', 'Marlborough South', 'Meyrick Park',
             'Mount Pleasant', 'Mount Pleasant Heights', 'New Marlborough', 'Newlands',
             'Northwood', 'Pomona', 'Ridgeview', 'Rolf Valley', 'Rolf Valley South',
             'Rolf Valley North', 'Rolf Valley East', 'Rolf Valley West', 'Rolf Valley Heights',
             'Rolf Valley Gardens', 'Rolf Valley View', 'Rolf Valley Villas', 'Rolf Valley Estates',
             'Rolf Valley Mansions', 'Rolf Valley Palms', 'Rolf Valley Heights', 'Rolf Valley View',
             'Rolf Valley Gardens', 'Rolf Valley Villas', 'Rolf Valley Estates', 'Rolf Valley Mansions',
             'Rolf Valley Palms', 'Rolf Valley Heights', 'Rolf Valley View', 'Rolf Valley Gardens',
             'Rolf Valley Villas', 'Rolf Valley Estates', 'Rolf Valley Mansions', 'Rolf Valley Palms'],
    'west': ['Adylinn', 'Ambly', 'Arundel', 'Ashdown Park', 'Ashbrittle', 'Avondale', 
             'Avondale West', 'Avonlea', 'Belgravia', 'Belvedere', 'Borrowdale',
             'Borrowdale Brooke', 'Borrowdale West', 'Chisipite', 'Colne Valley',
             'Eastlea', 'Eastview', 'Glen Lorne', 'Glenwood', 'Greendale',
             'Groombridge', 'Hillside', 'Hillside Dales', 'Hillside East',
             'Hillside North', 'Hillside West', 'Houghton Park', 'Lorraine',
             'Lorraine Ridge', 'Mabelreign', 'Malborough', 'Marlborough',
             'Marlborough East', 'Marlborough West', 'Marlborough South',
             'Meyrick Park', 'Mount Pleasant', 'Mount Pleasant Heights',
             'New Marlborough', 'Newlands', 'Northwood', 'Pomona', 'Ridgeview',
             'Rolf Valley', 'Rolf Valley South', 'Rolf Valley North',
             'Rolf Valley East', 'Rolf Valley West', 'Rolf Valley Heights',
             'Rolf Valley Gardens', 'Rolf Valley View', 'Rolf Valley Villas',
             'Rolf Valley Estates', 'Rolf Valley Mansions', 'Rolf Valley Palms']
}

# Base search URL
SEARCH_URL = "https://www.property.co.zw/property-for-sale/?search=true&page={page}&keywords={suburb}"

class PropertyScraper:
    def __init__(self, headless: bool = False, proxy: str = None):
        self.ua = UserAgent()
        self.data = []
        self.visited_urls = set()
        self.proxy = proxy
        self.driver = self._init_driver(headless)
        self.cookies_accepted = False
        
    def _init_driver(self, headless: bool = False):
        """Initialize and return a Chrome WebDriver with mobile emulation and proxy."""
        chrome_options = Options()
        
        # Add proxy if provided
        if self.proxy:
            chrome_options.add_argument(f'--proxy-server={self.proxy}')
        
        # Rotate through multiple mobile devices
        mobile_devices = [
            {
                "deviceMetrics": { "width": 375, "height": 812, "pixelRatio": 3.0 },
                "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
            },
            {
                "deviceMetrics": { "width": 414, "height": 896, "pixelRatio": 3.0 },
                "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
            },
            {
                "deviceMetrics": { "width": 360, "height": 800, "pixelRatio": 3.0 },
                "userAgent": "Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
            }
        ]
        
        # Randomly select a mobile device profile
        import random
        mobile_emulation = random.choice(mobile_devices)
        chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
        
        # Set a random viewport size
        viewport_width = random.randint(360, 414)
        viewport_height = random.randint(600, 900)
        chrome_options.add_argument(f'--window-size={viewport_width},{viewport_height}')
        
        # Basic options
        if headless:
            chrome_options.add_argument('--headless=new')
        
        # Anti-detection options
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Disable automation flags
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('--disable-browser-side-navigation')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--disable-features=IsolateOrigins,site-per-process')
        chrome_options.add_argument('--disable-site-isolation-trials')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--disable-xss-auditor')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--disable-popup-blocking')
        chrome_options.add_argument('--disable-default-apps')
        chrome_options.add_argument('--mute-audio')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-setuid-sandbox')
        chrome_options.add_argument('--disable-webgl')
        chrome_options.add_argument('--disable-threaded-animation')
        chrome_options.add_argument('--disable-threaded-scrolling')
        chrome_options.add_argument('--disable-in-process-stack-traces')
        chrome_options.add_argument('--disable-logging')
        chrome_options.add_argument('--log-level=3')
        chrome_options.add_argument('--output=/dev/null')
        
        # Note: Removed argument shuffling as chrome_options.arguments is read-only
        
        # Disable images for faster loading
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "permissions.default.stylesheet": 2,
            "permissions.default.image": 2,
            "javascript.enabled": True,
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # Additional arguments to mimic a real user
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--disable-features=IsolateOrigins,site-per-process')
        chrome_options.add_argument('--disable-site-isolation-trials')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--disable-xss-auditor')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--disable-popup-blocking')
        chrome_options.add_argument('--disable-default-apps')
        chrome_options.add_argument('--mute-audio')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-setuid-sandbox')
        chrome_options.add_argument('--disable-webgl')
        chrome_options.add_argument('--disable-threaded-animation')
        chrome_options.add_argument('--disable-threaded-scrolling')
        chrome_options.add_argument('--disable-in-process-stack-traces')
        chrome_options.add_argument('--disable-logging')
        chrome_options.add_argument('--log-level=3')
        chrome_options.add_argument('--output=/dev/null')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Set page load timeout
        driver.set_page_load_timeout(30)
        return driver
    
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry logic."""
        session = requests.Session()
        retry = Retry(
            total=5,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504, 429],
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session
    
    def _simulate_human_behavior(self):
        """Simulate human-like mouse movements and scrolling."""
        try:
            # Random mouse movements
            width = random.randint(100, 1000)
            height = random.randint(100, 700)
            self.driver.execute_script(f"window.scrollTo({width}, {height});")
            
            # Random mouse movement pattern
            actions = webdriver.ActionChains(self.driver)
            for _ in range(random.randint(2, 5)):
                x_offset = random.randint(-100, 100)
                y_offset = random.randint(-50, 50)
                actions.move_by_offset(x_offset, y_offset)
                actions.perform()
                time.sleep(random.uniform(0.1, 0.5))
                
        except Exception as e:
            print(f"Warning in human behavior simulation: {str(e)}")
    
    def _random_scroll(self):
        """Simulate human-like scrolling behavior."""
        try:
            # Scroll in random patterns
            scroll_pause_time = random.uniform(0.5, 1.5)
            scroll_amount = random.randint(300, 1000)
            
            # Scroll down
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            time.sleep(scroll_pause_time)
            
            # Sometimes scroll back up a bit
            if random.random() > 0.7:  # 30% chance to scroll up
                self.driver.execute_script("window.scrollBy(0, -200);")
                time.sleep(scroll_pause_time)
                
        except Exception as e:
            print(f"Warning in random scroll: {str(e)}")
    
    def _get_random_delay(self) -> float:
        """Return a random delay between requests to avoid detection."""
        return random.uniform(3, 8)  # Increased delay range
    
    def _accept_cookies(self) -> bool:
        """Try to accept cookies if a cookie banner is present."""
        if self.cookies_accepted:
            return True
            
        try:
            # Common cookie accept button selectors
            cookie_selectors = [
                "button#onetrust-accept-btn-handler",
                "button.cc-btn.cc-dismiss",
                "button[class*='cookie']",
                "button[class*='accept']",
                "button[class*='agree']",
                "button[class*='dismiss']",
                "button[class*='consent']",
                "button[class*='banner']",
                "button[onclick*='cookie']",
                "button[onclick*='accept']",
            ]
            
            for selector in cookie_selectors:
                try:
                    button = WebDriverWait(self.driver, 2).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    button.click()
                    self.cookies_accepted = True
                    print("Accepted cookies")
                    time.sleep(1)
                    return True
                except:
                    continue
        except Exception as e:
            print(f"Error handling cookies: {str(e)}")
        
        return False

    def _solve_captcha(self) -> bool:
        """Handle CAPTCHA if detected."""
        print("CAPTCHA detected. Please solve it manually in the browser...")
        input("Press Enter after solving the CAPTCHA to continue...")
        return True

    def _get_headers(self) -> dict:
        """Return headers with a random user agent."""
        headers = HEADERS.copy()
        headers['User-Agent'] = self.ua.random
        return headers
    
    def _get_page(self, url: str, max_retries: int = 2) -> Optional[BeautifulSoup]:
        """Fetch a page using Selenium with mobile emulation and CAPTCHA handling."""
        for attempt in range(max_retries):
            try:
                # Random delay with increasing backoff
                delay = random.uniform(5, 12) + (attempt * 3)
                print(f"Waiting {delay:.1f} seconds before request...")
                time.sleep(delay)
                
                print(f"Fetching {url} (attempt {attempt + 1}/{max_retries})...")
                
                # Randomize timeouts
                timeout = random.randint(15, 30)
                self.driver.set_page_load_timeout(timeout)
                
                # Add random referer
        
                # Add random headers
                self.driver.execute_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """)
                
                # Use execute_async_script to load the page with custom headers
                script = """
                const [url] = arguments;
                return new Promise((resolve, reject) => {
                    const xhr = new XMLHttpRequest();
                    xhr.open('GET', url, true);
                    xhr.setRequestHeader('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8');
                    xhr.setRequestHeader('Accept-Language', 'en-US,en;q=0.5');
                    xhr.setRequestHeader('Connection', 'keep-alive');
                    xhr.setRequestHeader('Upgrade-Insecure-Requests', '1');
                    xhr.onload = function() {
                        if (this.status >= 200 && this.status < 300) {
                            document.open();
                            document.write(this.responseText);
                            document.close();
                            resolve(true);
                        } else {
                            reject(new Error(`HTTP ${this.status}`));
                        }
                    };
                    xhr.onerror = () => reject(new Error('Network Error'));
                    xhr.send();
                });
                """
                
                # Try both methods - direct get and XHR
                try:
                    self.driver.execute_async_script(script, url)
                except:
                    # Fallback to regular get if XHR fails
                    self.driver.get(url)
                
                # Wait for content to load with longer timeout
                try:
                    WebDriverWait(self.driver, 15).until(
                        lambda d: d.execute_script('return document.readyState') == 'complete'
                    )
                except:
                    print("Page load timed out, but continuing...")
                
                # Handle cookies if not already accepted
                self._accept_cookies()
                
                # Check if we got a CAPTCHA or access denied
                page_source = self.driver.page_source.lower()
                if 'captcha' in page_source or 'access denied' in page_source:
                    if not self._solve_captcha():
                        print("CAPTCHA not solved. Trying again...")
                        continue
                    # If CAPTCHA was solved, reload the page
                    self.driver.get(url)
                    WebDriverWait(self.driver, 15).until(
                        lambda d: d.execute_script('return document.readyState') == 'complete'
                    )
                    
                return BeautifulSoup(self.driver.page_source, 'html.parser')
                
            except Exception as e:
                print(f"Error loading page: {str(e)}")
                if attempt == max_retries - 1:
                    print("Max retries reached. Giving up.")
                    return None
                time.sleep(2 ** attempt)  # Exponential backoff
    
    def extract_property_data(self, property_url: str) -> Optional[Dict]:
        """Extract property data from a property detail page."""
        print(f"Extracting data from: {property_url}")
        soup = self._get_page(property_url)
        if not soup:
            return None
            
        # Initialize property data with default values
        property_data = {
            'property_id': '',
            'location_suburb': '',
            'property_type': '',
            'stand_size_sqm': '',
            'building_size_sqm': '',
            'bedrooms': '',
            'bathrooms': '',
            'sale_price_usd': '',
            'rental_income_usd_monthly (est)': '',
            'has_solar': 0,
            'has_water_recycling': 0,
            'has_smart_locks': 0,
            'has_smart_thermostats': 0,
            'has_integrated_security': 0,
            'has_ev_charging': 0,
        }
        
        # Extract data from the property page
        # Note: These selectors need to be updated based on the actual page structure
        try:
            # Extract property ID from URL
            property_data['property_id'] = property_url.split('/')[-1]
            
            # Extract property title
            title = soup.find('h1', class_='title')
            if title:
                property_data['location_suburb'] = title.get_text(strip=True)
                
            # Extract property type
            property_type = soup.find('div', class_='property-type')
            if property_type:
                property_data['property_type'] = property_type.get_text(strip=True)
                
            # Extract price
            price_elem = soup.find('div', class_='price')
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                # Clean price text and convert to number
                price = ''.join(filter(lambda x: x.isdigit() or x in '.,', price_text))
                # Remove thousand separators and convert to float
                price = float(price.replace(',', '').replace('.', '', price.count('.')-1))
                property_data['sale_price_usd'] = price
                
            # Extract property details
            details = soup.find_all('div', class_='property-features')
            for detail in details:
                label = detail.find('span', class_='name')
                value = detail.find('span', class_='value')
                if label and value:
                    label_text = label.get_text(strip=True).lower()
                    value_text = value.get_text(strip=True)
                    
                    if 'bed' in label_text:
                        property_data['bedrooms'] = int(''.join(filter(str.isdigit, value_text)) or 0)
                    elif 'bath' in label_text:
                        property_data['bathrooms'] = int(''.join(filter(str.isdigit, value_text)) or 0)
                    elif 'stand' in label_text and 'size' in label_text:
                        # Extract just the number from '500 m²' -> 500
                        size = ''.join(filter(lambda x: x.isdigit() or x == '.', value_text))
                        property_data['stand_size_sqm'] = float(size) if size else 0
                    elif 'size' in label_text or 'area' in label_text:
                        size = ''.join(filter(lambda x: x.isdigit() or x == '.', value_text))
                        property_data['building_size_sqm'] = float(size) if size else 0
            
            # Check for amenities/features
            features_section = soup.find('div', class_='features')
            if features_section:
                features = features_section.find_all('li')
                for feature in features:
                    feature_text = feature.get_text(strip=True).lower()
                    if 'solar' in feature_text:
                        property_data['has_solar'] = 1
                    elif 'water' in feature_text and ('recycling' in feature_text or 'harvesting' in feature_text):
                        property_data['has_water_recycling'] = 1
                    elif 'smart lock' in feature_text or 'smartlock' in feature_text:
                        property_data['has_smart_locks'] = 1
                    elif 'thermostat' in feature_text:
                        property_data['has_has_smart_thermostats'] = 1
                    elif 'security' in feature_text or 'alarm' in feature_text or 'cctv' in feature_text:
                        property_data['has_integrated_security'] = 1
                    elif 'charging' in feature_text and ('ev' in feature_text or 'electric' in feature_text):
                        property_data['has_ev_charging'] = 1
            
            return property_data
            
        except Exception as e:
            print(f"Error extracting data from {property_url}: {e}")
            return None
    
    def scrape_region(self, region_name: str, property_type: str, max_pages: int = 2):
        """Scrape properties of a specific type in a region."""
        print(f"\n=== Scraping {property_type}s in {region_name} ===")
        
        # Get all suburbs for this region
        suburbs = HARARE_SUBURBS.get(region_name.lower(), [])
        if not suburbs:
            print(f"No suburbs found for region: {region_name}")
            return
            
        for suburb in suburbs:
            print(f"\nSearching for {property_type}s in {suburb}...")
            page = 1
            processed_urls = set()  # Track processed URLs to avoid duplicates
            
            while page <= max_pages:
                # Construct the search URL with the correct structure
                search_url = SEARCH_URL.format(
                    page=page,
                    suburb=suburb.replace(' ', '+')
                )
                
                # Add property type to search
                search_url += f"&property_type={property_type}"
                
                print(f"Scraping page {page} of {property_type}s in {suburb}...")
                print(f"URL: {search_url}")
                
                soup = self._get_page(search_url)
                if not soup:
                    print(f"Failed to fetch page {page}")
                    break
                
                # Debug: Save the page content for inspection
                with open(f'debug_page_{page}.html', 'w', encoding='utf-8') as f:
                    f.write(str(soup))
                
                # Find property links on the search results page
                property_links = []
                
                # Try multiple possible selectors for property listings
                listing_selectors = [
                    'div.property-listing',
                    'div.property-item',
                    'div.property-card',
                    'div.listing-item',
                    'div.property',
                    'article.property',
                    'div.item',
                    'div.listing',
                    'div.result-item'
                ]
                
                listings = []
                for selector in listing_selectors:
                    listings = soup.select(selector)
                    if listings:
                        print(f"Found {len(listings)} listings with selector: {selector}")
                        break
                        
                if not listings:
                    print("No property listings found on the page.")
                    break
            
            for listing in listings:
                link = listing.find('a', href=True)
                if link and '/for-sale/' in link['href']:
                    full_url = link['href'] if link['href'].startswith('http') else f"{BASE_URL}{link['href']}"
                    property_links.append(full_url)
                    
            if not property_links:
                print(f"No property links found on page {page}")
                break
            
            # If no more properties found, break the loop
            if not property_links:
                print(f"No more properties found on page {page}")
                break
            
            # Scrape each property page
            for link in property_links:
                if not link.startswith('http'):
                    link = f"{BASE_URL}{link}"
                property_data = self.extract_property_data(link)
                if property_data:
                    self.data.append(property_data)
            
            page += 1
    
    def save_to_csv(self, filename: str = 'scraped_properties.csv'):
        """Save scraped data to a CSV file."""
        if not self.data:
            print("No data to save.")
            return
            
        # Define the fieldnames based on the template
        fieldnames = [
            'property_id', 'location_suburb', 'property_type', 'stand_size_sqm', 
            'building_size_sqm', 'bedrooms', 'bathrooms', 'sale_price_usd', 
            'rental_income_usd_monthly (est)', 'has_solar', 'has_water_recycling', 
            'has_smart_locks', 'has_smart_thermostats', 'has_integrated_security', 
            'has_ev_charging'
        ]
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.data)
            print(f"Successfully saved {len(self.data)} properties to {filename}")
        except Exception as e:
            print(f"Error saving to CSV: {e}")

def get_free_proxies() -> list:
    """Get a list of free proxies (for demonstration purposes).
    In production, consider using a paid proxy service."""
    # This is a basic example - in practice, you'd want to use a reliable proxy service
    return [
        None,  # First try without proxy
        'http://proxy1.example.com:8080',
        'http://proxy2.example.com:8080'
    ]

def test_scraper():
    """Test the scraper with a single page."""
    print("\n=== Starting Mobile Scraper Test ===")
    print("This will open a Chrome window with mobile emulation.")
    print("Please do not interact with the browser window.\n")
    
    # Get a list of proxies to try
    proxies = get_free_proxies()
    scraper = None
    
    # Try each proxy until one works
    for proxy in proxies:
        try:
            print(f"\nTrying with proxy: {proxy if proxy else 'No proxy'}")
            scraper = PropertyScraper(headless=False, proxy=proxy)
            break  # If we get here, initialization was successful
        except Exception as e:
            print(f"Failed with proxy {proxy}: {str(e)}")
            if scraper and hasattr(scraper, 'driver'):
                try:
                    scraper.driver.quit()
                except:
                    pass
    
    if not scraper:
        print("Failed to initialize with any proxy. Trying without proxy...")
        scraper = PropertyScraper(headless=False)
    
    try:
        # Test with the main listings page
        test_url = "https://www.property.co.zw/property-for-sale/"
        print(f"Testing with URL: {test_url}")
        
        # Get the page
        soup = scraper._get_page(test_url, max_retries=3)
        
        if soup:
            # Save the page source for debugging
            with open('test_page.html', 'w', encoding='utf-8') as f:
                f.write(soup.prettify())
            print("Page saved to test_page.html for inspection")
            
            # Try to extract some data
            print("\nPage title:", soup.title.string if soup.title else "No title found")
            # Save the page for inspection
            with open('test_page.html', 'w', encoding='utf-8') as f:
                f.write(str(soup))
            print("\nSuccessfully saved test page to test_page.html")
            
            # Try to extract property links for analysis
            links = soup.find_all('a', href=True)
            property_links = [link['href'] for link in links if '/for-sale/' in link['href']]
            
            # Clean and deduplicate links
            property_links = list(set(property_links))
            
            print(f"\nFound {len(property_links)} unique property links:")
            for i, link in enumerate(property_links[:10], 1):
                print(f"{i}. {link}")
            
            if len(property_links) > 10:
                print(f"... and {len(property_links) - 10} more")
            
            # If we found property links, try to scrape the first one
            if property_links:
                first_property = property_links[0]
                if not first_property.startswith('http'):
                    first_property = f"{BASE_URL}{first_property}"
                
                print(f"\nAttempting to scrape first property: {first_property}")
                property_data = scraper.extract_property_data(first_property)
                
                if property_data:
                    print("\nSuccessfully scraped property data:")
                    for key, value in property_data.items():
                        print(f"{key}: {value}")
                    
                    # Save the scraped data
                    output_file = 'scraped_properties.csv'
                    scraper.data = [property_data]  # Add to data list
                    scraper.save_to_csv(output_file)
                    print(f"\nData saved to {output_file}")
    
    except Exception as e:
        print(f"\nAn error occurred during testing: {str(e)}")
    
    finally:
        # Always close the browser when done
        if hasattr(scraper, 'driver'):
            scraper.driver.quit()
            print("\nBrowser closed.")

def main():
    print("Starting property scraper...")
    print("This script will test the scraper with a single page first.")
    
    # Run the test function
    try:
        test_scraper()
        print("\nTest complete. You can now check the output files and modify the script for full scraping.")
    except Exception as e:
        print(f"\nError during testing: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        if 'scraper' in locals() and hasattr(scraper, 'driver'):
            try:
                scraper.driver.quit()
            except:
                pass

if __name__ == "__main__":
    main()
