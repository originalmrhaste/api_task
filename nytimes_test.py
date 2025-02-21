from first_take import NYTimesSource
import argparse


def test_correct_url_and_params(mocker):
    mock_get = mocker.patch("requests.get")

    test_config = {"query": "test_query", "api_key": "test_api_key"}
    nytimes = NYTimesSource()
    nytimes.args = argparse.Namespace(**test_config)
    nytimes.getDataBatch()

    mock_get.assert_called_once()

    result_params = {"q": "test_query", "api-key": "test_api_key"}
    result_url = "https://api.nytimes.com/svc/search/v2/articlesearch.json"
    mock_get.assert_called_with(url=result_url, params=result_params)
