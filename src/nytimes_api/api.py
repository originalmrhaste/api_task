import argparse
import logging
import os
import requests
import time

from dotenv import load_dotenv
from nytimes_api.helpers import flatten_dict
from pprint import pprint

"""
Skeleton for Squirro Delivery Hiring Coding Challenge
January 2024
"""
log = logging.getLogger(__name__)
BASE_URL = "https://api.nytimes.com/svc/search/v2/articlesearch.json"
MAX_ARTICLES_PER_REQUEST = 10
MAX_TOTAL_ARTICLES = 1000  # NY Times API limit (100 pages * 10 articles)


class NYTimesSource:
    """
    A data loader plugin for the NY Times API.
    """

    def __init__(self, config):
        # I changed this to use the config dict instead of args,
        # since args are arbitrarily called by the caller and class
        # then doesn't have control over the config
        self.payload = {
            "q": config.get("query", None),
            "api-key": config.get("api_key", None),
            "page": config.get("page", 0),
            "sort": config.get("sort", "newest"),
        }
        self.force_newest = False
        self.inc_column = None
        self.max_inc_value = None

    def _check_total_hits(self):
        """Check total number of articles matching the query and warn if exceeding API limits."""
        response = requests.get(url=BASE_URL, params=self.payload)
        if response.status_code == 200:
            total_hits = response.json()["response"].get("meta", {}).get("hits", 0)
            if total_hits > MAX_TOTAL_ARTICLES:
                log.warning(
                    f"Search returned {total_hits:,} articles, but only {MAX_TOTAL_ARTICLES:,} can be retrieved "
                    "due to API limitations. Consider using date filters (begin_date, end_date) "
                    "to narrow down your search."
                )
            return total_hits
        return None

    def connect(self, inc_column=None, max_inc_value=None):
        """Connect to the source"""
        log.debug("Incremental Column: %r", inc_column)
        log.debug("Incremental Last Value: %r", max_inc_value)
        if inc_column and inc_column not in self.getIncrementalColumns():
            raise ValueError("Incremental loading is only supported on the pub_date column.")
        else:
            self.inc_column = inc_column
            self.max_inc_value = max_inc_value
            self.force_newest = True

    def getIncrementalColumns(self):
        return ["pub_date"]

    def disconnect(self):
        """Disconnect from the source."""
        # Nothing to do
        pass

    def getDataBatch(self, batch_size=10):
        """
        Generator - Get data from source on batches.
        :returns One list for each batch. Each of those is a
        list of
        dictionaries with the defined rows.
        """
        if self.force_newest:
            self.payload["sort"] = "newest"

        articles = []
        for article in self.getArticles():
            articles.append(flatten_dict(article))
            if len(articles) >= batch_size:
                yield articles
                articles = []

        if articles:  # Yield any remaining articles in the last batch
            yield articles

    def getArticles(self):
        """
        Generator that yields articles from the NY Times API.
        Handles pagination and respects API limits.
        """
        while True:
            if self.payload["page"] >= 100:
                return
                
            response = requests.get(url=BASE_URL, params=self.payload)
            match response.status_code:
                case 200:
                    docs = response.json()["response"]["docs"]
                    if not docs:
                        return
                    
                    for article in docs:
                        if self.max_inc_value and article[self.inc_column] <= self.max_inc_value:
                            return
                        yield article

                    if len(docs) < MAX_ARTICLES_PER_REQUEST:
                        return
                        
                case 401:
                    raise Exception("Unauthorized request. Make sure api-key is set.")
                case 429:
                    raise Exception(
                        "Too many requests. You reached your per minute or per day rate limit."
                    )
                case _:
                    raise Exception(f"Unknown error: {response.status_code}")
            
            self.payload["page"] += 1
            time.sleep(12)  # Respect rate limits

    def getSchema(self):
        """
            Return the schema of the dataset
        :returns a List containing the names of the columns
        retrieved from the
        source
        """
        if not hasattr(self, "_schema"):
            for article in self.getArticles():
                flattened = flatten_dict(article)
                self._schema = list(flattened.keys())
                break
        return self._schema


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    def print_batch(batch):
        for item in batch:
            print(f" - {item['_id']} - {item['headline.main']}")
            for key, value in item.items():
                if "date" in key:
                    print(f" - {key} - {value}")

    load_dotenv()
    #
    config = {
        "api_key": os.getenv("NYTIMES_API_KEY"),
        "query": "Silicon Valley",
        # "page": 20,
        "sort": "newest",
    }
    # pprint(config)
    source = NYTimesSource(config)
    source.connect(inc_column="pub_date", max_inc_value="2025-01-14T23:00:00Z")

    print("Fetching articles in batches...")
    for idx, batch in enumerate(source.getDataBatch(batch_size=10)):
        print(f"\nBatch {idx + 1} ({len(batch)} articles):")
        print_batch(batch)
