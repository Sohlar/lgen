from .config import EBAY_APP_ID
from .search_engines import GoogleSearch, BingSearch, EbaySearch, MapsSearch
from .search_engine_factory import SearchEngineFactory
from .utils import search_and_record, drop_non_results

def main():
    filepath = 'output'
    
    print("Choose search engine(s):")
    print("1. Google and Bing")
    print("2. eBay")
    print("3. Maps")

    choice = int(input("Enter your choice (1, 2, or 3): ").strip())

    if choice not in [1, 2, 3]:
        print("Invalid choice. Exiting.")
        return

    engines = []

    if choice == 1:
        engines = ['google', 'bing']
        query = input("Enter your Search Engine query: ").strip()
    elif choice == 2:
        engines = ['ebay']
        query = input("Enter your eBay query: ").strip()
    elif choice == 3:
        enginers = ['maps']
        query = input("Enter your google maps query: ").strip()
        city_query = input("Enter city for your google maps query").strip()

    
    with ThreadPoolExecutor(max_workers=len(engines)) as executor:
        futures = [executor.submit(
            search_and_record,
            engine,
            query,
            filepath,
            city_query,
            EBAY_APP_ID if engine == 'ebay' else None
            ) for engine in engines
        ]

    for future in futures:
        future.result()

if __name__ == '__main__':
    main()