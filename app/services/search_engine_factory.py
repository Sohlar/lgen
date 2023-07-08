from .search_engines import GoogleSearch

class SearchEngineFactory:
    def create_search_engine(engine):
        if engine == 'google':
            return GoogleSearch()
        elif engine == 'bing':
            return BingSearch
        elif engine == 'ebay':
            return EbaySearch
        elif engine == 'maps':
            return MapsSearch
        else:
            raise ValueError(f'unknown search engine {engine}')
