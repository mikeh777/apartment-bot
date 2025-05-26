import random
#from twilio.rest import Client
from utils import in_area, check_for_record, store_in_db
import settings
import sys
import requests
from bs4 import BeautifulSoup

def build_craigslist_url(min_bedrooms, max_bedrooms, min_price, max_price, distance):
    url = (
        f"https://sfbay.craigslist.org/search/san-francisco-ca/apa"
        f"?isTrusted=true&lat=37.7982&lon=-122.4359"
        f"&max_bedrooms={max_bedrooms}&max_price={max_price}"
        f"&min_bedrooms={min_bedrooms}&min_price={min_price}"
        f"&search_distance={distance}"
    )
    return url

# Optional: rotate among a list of good user agents
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
]

def get_craigslist_listings(url):
    session = requests.Session()
    session.headers.update({
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    })

    try:
        response = session.get(url, timeout=10)
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return []

    if response.status_code != 200 or "specialCurtainMessages" in response.text:
        print("Blocked or invalid response from Craigslist")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    container = soup.find('div', class_='cl-search-results-container')
    if not container:
        print("Listings container not found.")
        return []

    listings = []

    for tag in container.find_all('li', recursive=False):
        if 'nearby-separator' in tag.get('class', []):
            break

        title_tag = tag.find('a', class_='cl-app-anchor cl-search-anchor text-only posting-title')
        price_tag = tag.find('span', class_='price')
        bedrooms_tag = tag.find('span', class_='post-bedrooms')

        title = title_tag.text.strip() if title_tag else "No title"
        link = title_tag['href'] if title_tag else "No link"
        price = price_tag.text.strip() if price_tag else "No price"
        num_bedrooms = bedrooms_tag.text.strip() if bedrooms_tag else "No bedrooms"

        listings.append({
            'title': title,
            'price': price,
            'num_bedrooms': num_bedrooms,
            'link': link
        })

    return listings
def scrape_for_apartments():
    # Build URL's to scrape

    craiglist_url = build_craigslist_url(settings.MIN_NUM_BEDROOMS,
                                         settings.MAX_NUM_BEDROOMS,
                                         settings.MIN_PRICE,
                                         settings.MAX_PRICE,
                                         settings.DISTANCE_FROM_LOCATION)
    #trulia_url = build_trulia_url()
    # Get results from respective websites

    cl_results = get_craigslist_listings(craiglist_url)
    #tr_results = scrape_trulia(settings.)
    #adding a counter to limit the amount of results that can be sent at one time
    counter = 0
    print(len(cl_results))
    results_processed = 0
    for result in cl_results:
        print(result)

        # if check_for_record(result):
        #     continue
        # else:
        #     counter += 1
        #     geotag = result["geotag"]
        #     #set blank area
        #     area = ""
        #     for a, coords in settings.AREAS.items():
        #         print(result);
        #         if geotag is not None and in_area(geotag, coords):
        #             area = a
        #     #couldn't find from Geotag, string search the listing
        #     if area == "":
        #         # print settings.NEIGHBORHOODS
        #         for hood in settings.NEIGHBORHOODS:
        #             if result["where"] is not None and hood in result["where"].lower():
        #                 area = hood
        #     if area != '' and counter < 10:
        #         store_in_db(result)
        #         client = Client(settings.ACCOUNT_SID, settings.AUTH_TOKEN)
        #         text = "{} per month in {}.\n {}".format(result['price'], result['where'], result["url"])
        #         message = client.messages.create(body=text, from = settings.TWILIO_PHONE_NUMBER, to = settings.TARGET_PHONE_NUMBER)