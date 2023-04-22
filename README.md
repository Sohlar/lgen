# Web Scraper App 🌐
A web scraping application built using Flask, BeautifulSoup, and other useful libraries. This app allows users to scrape contact information from different websites with the help of various search engines.

## Features 🔎
Scrape contact information (emails and phone numbers) from websites
Supports multiple search engines: Google, Bing, eBay, and Google Maps
Easily configurable and extensible
Efficient scraping using multithreading
Export results to CSV files
Installation 🛠️

Clone the repository:
```console
git clone https://github.com/yourusername/web-scraper-app.git
```
Create a virtual environment and activate it:
```console
python -m venv venv

source venv/bin/activate  # For Linux and macOS
venv\Scripts\activate  # For Windows
```
Install the required dependencies:
```console
pip install -r requirements.txt
```
Configure environment variables:
Create a .env file in the root directory of the project and set the required API keys:

```makefile
GOOG_API_KEY=your_google_api_key
GOOG_CX_KEY=your_google_cx_key
BING_API_KEY=your_bing_api_key
EBAY_API_KEY=your_ebay_api_key
GMAPS_API_KEY=your_gmaps_api_key
```
Run the Flask app:
```console
python run.py
```
The app should now be running at http://localhost:5000/.

# Usage 📚
Access the web interface at http://localhost:5000/.
Choose a search engine or a combination of search engines.
Enter your query and any additional parameters (e.g., city for Google Maps).
Click "Search" to start the scraping process.
The app will save the results in a CSV file in the output directory.
Tests 🧪
Run the tests using pytest:
```console
pytest
```
## Contributing 🤝
Contributions are welcome! Please read the contributing guidelines for more information.

## License ⚖️
This project is licensed under the MIT License.

## Questions or Issues ❓
If you have any questions or issues, please open an issue on GitHub.

Made with 💙 by Your Name