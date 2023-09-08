from .search_engines import GoogleSearch


class SearchEngineFactory:
    def create_search_engine(engine):
        if engine == "google":
            return GoogleSearch()
        else:
            raise ValueError(f"unknown search engine {engine}")
