from first_take import NYTimesSource
import argparse


def test_correct_url_and_params(mocker):
    mocker.patch("time.sleep")
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "response": {
            "docs": [{"headline": {"main": f"test_article_{i}"}} for i in range(10)]
        }
    }
    mock_get = mocker.patch("requests.get", return_value=mock_response)

    test_config = {"query": "test_query", "api_key": "test_api_key", "page": 10}
    nytimes = NYTimesSource(test_config)
    list(nytimes.getDataBatch())

    mock_get.assert_called_once()

    # its 11 because the payload passed to mock updates in place
    result_params = {"q": "test_query", "api-key": "test_api_key", "page": 11}
    result_url = "https://api.nytimes.com/svc/search/v2/articlesearch.json"
    mock_get.assert_called_with(url=result_url, params=result_params)
