from nytimes_api import NYTimesSource
import argparse
import pytest


def test_correct_url_and_params(mocker):
    mocker.patch("time.sleep")

    # First call returns articles, subsequent calls return empty to simulate end of data
    def get_response(**kwargs):
        if kwargs["params"]["page"] == 10:
            return mocker.Mock(
                status_code=200,
                json=lambda: {
                    "response": {
                        "docs": [{"headline": {"main": f"test_article_{i}"}} for i in range(10)]
                    }
                },
            )
        return mocker.Mock(status_code=200, json=lambda: {"response": {"docs": []}})

    mock_get = mocker.patch("requests.get", side_effect=get_response)

    test_config = {"query": "test_query", "api_key": "test_api_key", "page": 10}
    nytimes = NYTimesSource(test_config)
    list(nytimes.getDataBatch())

    # Check the last call was for fetching articles
    result_params = {"q": "test_query", "api-key": "test_api_key", "page": 11, "sort": "newest"}
    result_url = "https://api.nytimes.com/svc/search/v2/articlesearch.json"
    mock_get.assert_called_with(url=result_url, params=result_params)


def test_incremental_loading(mocker):
    mocker.patch("time.sleep")
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "response": {
            "docs": [
                {"pub_date": "2024-01-15T10:00:00+0000", "headline": {"main": "Article 1"}},
                {"pub_date": "2024-01-14T10:00:00+0000", "headline": {"main": "Article 2"}},
                {"pub_date": "2024-01-13T10:00:00+0000", "headline": {"main": "Article 3"}},
            ]
        }
    }
    mocker.patch("requests.get", return_value=mock_response)

    test_config = {"query": "test", "api_key": "test_key"}
    source = NYTimesSource(test_config)

    # Test 1: No incremental loading
    batches = list(source.getDataBatch(3))
    assert len(batches[0]) == 3

    # Test 2: Incremental loading with cutoff date
    source = NYTimesSource(test_config)
    source.connect(inc_column="pub_date", max_inc_value="2024-01-14T10:00:00+0000")
    batches = list(source.getDataBatch(3))
    assert len(batches[0]) == 1


def test_invalid_incremental_column(mocker):
    source = NYTimesSource({"query": "test", "api_key": "test_key"})

    with pytest.raises(
        ValueError, match="Incremental loading is only supported on the pub_date column"
    ):
        source.connect(inc_column="invalid_column", max_inc_value="2024-01-14T10:00:00+0000")


def test_schema_retrieval(mocker):
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "response": {
            "docs": [
                {
                    "headline": {"main": "Article 1"},
                    "pub_date": "2025-02-24T10:00:00+0000",
                    "abstract": "Abstract 1",
                    "keywords": ["Keyword 1", "Keyword 2"],
                },
            ]
        }
    }
    mocker.patch("requests.get", return_value=mock_response)

    source = NYTimesSource({"query": "test", "api_key": "test_key"})
    schema = source.getSchema()
    assert schema == ["headline.main", "pub_date", "abstract", "keywords.0", "keywords.1"]


def test_get_all_articles(mocker):
    mocker.patch("time.sleep")

    # Simulate 17 articles across two pages (10 + 7)
    def get_response(**kwargs):
        page = kwargs["params"]["page"]
        if page == 0:
            articles = [{"headline": {"main": f"article_{i}"}} for i in range(10)]
        elif page == 1:
            articles = [{"headline": {"main": f"article_{i}"}} for i in range(10, 17)]
        else:
            articles = []

        return mocker.Mock(status_code=200, json=lambda: {"response": {"docs": articles}})

    mock_get = mocker.patch("requests.get", side_effect=get_response)

    source = NYTimesSource({"query": "test", "api_key": "test_key"})

    # Collect all articles from all batches
    all_articles = []
    for batch in source.getDataBatch(batch_size=5):  # Use smaller batch size to test batching
        all_articles.extend(batch)

    assert len(all_articles) == 17
    # Verify we got all articles in correct order
    for i in range(17):
        assert all_articles[i]["headline.main"] == f"article_{i}"
