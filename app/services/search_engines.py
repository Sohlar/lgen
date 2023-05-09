import requests
import json
import re
from bs4 import BeautifulSoup
import phonenumbers
from email_validator import validate_email, EmailNotValidError
import time
from abc import ABC, abstractmethod

# Import API keys from config.py
from .config import GOOG_API_KEY, GOOGLE_CX, BING_API_KEY

class SearchEngine(ABC):
    
    @abstractmethod
    def search(self, query):
        pass

    def get_page_content(self, url, params):
        try:
            response = requests.get(url, params)
            if response.status_code == 200:
                return response.text
            else:
                print(f"Error: {response.status_code}")
                print(f"Reason: {response.reason}")
                return None
        except Exception as e:
            print(f"Error: {e}")
            return None

    def preprocess_text(self, content):
        content = content.replace('\n', ' ')
        content = re.sub(r'\s+', ' ', content)
        return content

    def find_email_addresses(self, content):
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        emails = email_pattern.findall(content)

        valid_emails = []

        for email in emails:
            try:
                validate_email(email)
                valid_emails.append(email)
            except EmailNotValidError:
                pass
        return valid_emails

    def find_phone_numbers(self, content, default_region='US', is_html=False):
        if is_html:
            soup = BeautifulSoup(content, 'html.parser')
            content = soup.get_text()

        content = self.preprocess_text(self=self, content=content)

        valid_numbers = []
        for match in phonenumbers.PhoneNumberMatcher(content, default_region):
            number = match.number
            if phonenumbers.is_valid_number(number):
                formatted_number = phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)
                valid_numbers.append(formatted_number)
        return valid_numbers

    def _find_contact_info(self, url, params):
        url_content = self.get_page_content(self=self, url=url, params=params)

        if url_content is None:
            return ({'email': None, 'phone': None, 'url': url})
        
        email = self.find_email_addresses(self=self, content=url_content)
        phone = self.find_phone_numbers(self=self, content=url_content, is_html=True)
        return ({'email': email, 'phone': phone, 'url': url})

class GoogleSearch(SearchEngine):

    def search(self, query, start_index=10, num_results=10):
        url_results = []
        for start_index in range(1, num_results,10):    
            base_url = 'https://www.googleapis.com/customsearch/v1'
            params = {
                'key': GOOG_API_KEY,
                'cx': GOOGLE_CX,
                'q': query,
                'start': start_index,
                'num': num_results
            }
            response = requests.get(base_url, params=params)
            data = response.json()
            url_results.extend(self._find_contact_info(self=self, url=item['link'], params=params) for item in data['items'])
        return url_results

class BingSearch(SearchEngine):

    def search(self, query, offset=10, num_urls=10):
        url_results = []
        for offset in range(0, num_urls, 10):
            base_url = 'https://api.bing.microsoft.com/v7.0/search'
            headers = {
                'Ocp-Apim-Subscription-Key': BING_API_KEY
            }
            params = {
                'q': query,
                'offset': offset,
                'count': num_urls
            }
            response = requests.get(base_url, headers=headers, params=params)
            data = response.json()
            #data['webPages']['value']['id']
            foo = data['webPages']

            url_results.extend(self._find_contact_info(self=self, url=item['url'], params=params) for item in foo['value'])
            time.sleep(1)
        return url_results
    
class EbaySearch(SearchEngine):

    def search(self, query):
        try:
            api = Finding(appid=EBAY_APP_ID, config_file=None)
            response = api.execute('findItemsAdvanced', {'keywords': query})

            url_results = []

            for item in response.reply.searchResult.item:
                if hasattr(item, 'viewItemURL'):
                    url_results.extend(self._find_contact_info(item.viewItemURL, {}))

            return url_results

        except ConnectionError as e:
            print(e)
            print(e.response.dict())
            return []

class MapsSearch(SearchEngine):

    def search(self, query, city):
        base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            "query": f"{query} in {city}",
            "key": GMAPS_API_KEY
        }

        response = requests.get(base_url, params=params)
        data = response.json()

        url_results = []
        for result in data["results"]:
            if "website" in result:
                url_results.extend(self._find_contact_info(result["website"], params))

        return url_results

