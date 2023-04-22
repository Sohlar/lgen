from .search_engines import GoogleSearch, BingSearch, EbaySearch, MapsSearch

class SearchEngineFactory:
    def create_search_engine(self, engine):
        if engine == 'google':
            return GoogleSearch
        elif engine == 'bing':
            return BingSearch
        elif engine == 'ebay':
            return EbaySearch
        elif engine == 'maps':
            return MapsSearch
        else:
            raise ValueError(f'unknown search engine {engine}')
