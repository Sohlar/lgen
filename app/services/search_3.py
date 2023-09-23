import requests

import re

from bs4 import BeautifulSoup
import phonenumbers
from email_validator import validate_email, EmailNotValidError
from app.services.logger import logger


# Import API keys from config.py

from .config import GOOG_API_KEY, GOOGLE_CX


class GoogleSearch:
    def search(self, query, start_index=10, num_urls=9):
        logger.debug("Starting Google Search")
        for start in range(start_index, start_index + num_urls, 10):
            base_url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": GOOG_API_KEY,
                "cx": GOOGLE_CX,
                "q": query,
                "start": start,
                "num": 10,
            }
            logger.debug(f"Parameters set: {params}")

            headers = {
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1",
                "Accept-Encoding": "gzip",
            }
            logger.debug(f"Headers set: {headers}")
            response = requests.get(url=base_url, params=params, headers=headers)
            logger.debug("Request sent")
            data = response.json()
            logger.debug("Response received and parsed")
            if "items" in data:
                for item in data["items"]:
                    logger.debug(f"Processing item: {item}")
                    yield self._find_contact_info(url=item["link"])
                    item.clear()  # Clear each item after yielding
                    logger.debug("Item processed and cleared")
                del data["items"]
                logger.debug("All items processed")
            else:
                logger.error("No Items in the Response")
                print("No Items in the Response")

    def get_page_content(self, url):
        try:
            response = requests.get(url)
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
        content = content.replace("\n", " ")
        content = re.sub(r"\s+", " ", content)
        return content

    def find_email_addresses(self, content):
        email_pattern = re.compile(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        )
        emails = email_pattern.findall(content)

        valid_emails = [email for email in emails if self.is_valid_email(email)]
        return valid_emails

    def is_valid_email(self, email):
        try:
            validate_email(email)
            return True
        except EmailNotValidError:
            return False

    def find_phone_numbers(self, content, default_region="US", is_html=False):
        if is_html:
            soup = BeautifulSoup(content, "html.parser")
            content = soup.get_text()

        content = self.preprocess_text(content=content)

        valid_numbers = [
            self.format_number(match.number)
            for match in phonenumbers.PhoneNumberMatcher(content, default_region)
            if phonenumbers.is_valid_number(match.number)
        ]
        return valid_numbers

    def format_number(self, number):
        return phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)

    def _find_contact_info(self, url):
        url_content = self.get_page_content(url=url)

        if url_content is None:
            return {"email": None, "phone": None, "url": url}

        email = self.find_email_addresses(content=url_content)
        phone = self.find_phone_numbers(content=url_content, is_html=True)
        return {"email": email, "phone": phone, "url": url}


""" if __name__ == "__main__":
    gs = GoogleSearch()
    results = gs.search('orange farms in california')

    print(results) """
