import pandas as pd
import re
from concurrent.futures import ThreadPoolExecutor
from search_engine_factory import SearchEngineFactory

def search_and_record(engine, query, filepath, num_urls, **kwargs):
    
    search_engine = SearchEngineFactory().create_search_engine(engine)
    results = search_engine.search(query, num_rurls=num_urls)

    sanitized_query = re.sub(r'\W+', '', query.replace(' ', '_'))

    df = pd.DataFrame(results)
    df_filtered = drop_non_results(df)
    df_filtered.to_csv(f'{filepath}/{sanitized_query}.csv')

    print(f"Results saved. output to {sanitized_query}")

def drop_non_results(df):
    new_df = df.dropna()
    df_filtered = new_df.loc[(new_df['email'].astype(str) != '[]') | (new_df['phone'].astype(str) != '[]')]
    return df_filtered