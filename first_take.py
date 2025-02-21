import argparse
from dotenv import load_dotenv
from pprint import pprint
import logging
import requests
import os
import json

"""
Skeleton for Squirro Delivery Hiring Coding Challenge
January 2024
"""
log = logging.getLogger(__name__)
BASE_URL = "https://api.nytimes.com/svc/search/v2/articlesearch.json"


class NYTimesSource:
    """
    A data loader plugin for the NY Times API.
    """

    def __init__(self):
        self.args = {}

    def connect(self, inc_column=None, max_inc_value=None):
        """Connect to the source"""
        log.debug("Incremental Column: %r", inc_column)
        log.debug("Incremental Last Value: %r", max_inc_value)

    def disconnect(self):
        """Disconnect from the source."""
        # Nothing to do
        pass

    def getDataBatch(self, batch_size=0):
        """
        Generator - Get data from source on batches.
        :returns One list for each batch. Each of those is a
        list of
        dictionaries with the defined rows.
        """
        # TODO: implement - this dummy implementation returns one batch of data

        payload = {
            "q": getattr(self.args, "query", None),
            "api-key": getattr(self.args, "api_key", None),
        }
        response = requests.get(url=BASE_URL, params=payload)
        return response.json()
        # yield [
        #     {
        #         "headline.main": "The main headline",
        #         "_id": "1234",
        #     }
        # ]

    def getSchema(self):
        """
            Return the schema of the dataset
        :returns a List containing the names of the columns
        retrieved from the
        source
        """
        schema = [
            "title",
            "body",
            "created_at",
            "id",
            "summary",
            "abstract",
            "keywords",
        ]
        return schema


if __name__ == "__main__":
    load_dotenv()
    config = {"api_key": os.getenv("NYTIMES_API_KEY"), "query": "Silicon Valley", "filter": "title"}
    pprint(config)
    source = NYTimesSource()
    # This looks like an argparse dependency - but theNamespace class is just
    # a simple way to create an object holding attributes.
    source.args = argparse.Namespace(**config)
    response = source.getDataBatch()
    pprint(response)
    with open("response.json", "w") as f:
        json.dump(response, f)
    # for idx, batch in enumerate(source.getDataBatch(10)):
    #     print(f"{idx} Batch of {len(batch)} items")
    #     for item in batch:
    #         print(f" - {item['_id']} - {item['headline.main']}")
