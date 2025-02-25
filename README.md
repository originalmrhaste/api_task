# NY Times Article Search API Client

 Fetches articles from NY Times API with support for:
- Incremental loading based on publication date
- Batch processing of articles
- Schema discovery
- Pagination handling
- Basic rate limiting

## Setup

```bash
# Clone the repository
git clone https://github.com/originalmrhaste/api_task.git
cd src/nytimes-api

# Install with uv (recommended)
uv sync
```

## Configuration

Create a `.env` file in the project root with your NY Times API key:

```
NYTIMES_API_KEY=your_api_key_here
```

You can obtain an API key from the [NY Times Developer Portal](https://developer.nytimes.com/).

## Usage

### Basic Usage

```python
from nytimes_api import NYTimesSource

# Configure the API client
config = {
    "api_key": "your_api_key",  # or use os.getenv("NYTIMES_API_KEY")
    "query": "Silicon Valley",
    "sort": "newest",
}

# Initialize and connect
source = NYTimesSource(config)

# Get articles in batches
for idx, batch in enumerate(source.getDataBatch(batch_size=10)):
    print(f"Batch {idx + 1} has {len(batch)} articles")
    for article in batch:
        print(f"- {article['headline.main']} ({article['pub_date']})")
```

### Incremental Loading

```python
# Only fetch articles newer than this date
source.connect(inc_column="pub_date", max_inc_value="2024-01-01T00:00:00Z")

# Process articles
for batch in source.getDataBatch():
    process_articles(batch)
```

## Running Tests

Run the tests with uv:

```bash
uv run -- pytest
```