# Health

Types:

```python
from cartography.types import HealthCheckResponse
```

Methods:

- <code title="get /health/">client.health.<a href="./src/cartography/resources/health.py">check</a>() -> <a href="./src/cartography/types/health_check_response.py">HealthCheckResponse</a></code>

# APIInfo

Types:

```python
from cartography.types import APIInfoRetrieveResponse
```

Methods:

- <code title="get /">client.api_info.<a href="./src/cartography/resources/api_info.py">retrieve</a>() -> <a href="./src/cartography/types/api_info_retrieve_response.py">APIInfoRetrieveResponse</a></code>

# Scrape

Types:

```python
from cartography.types import (
    BulkScrapeResult,
    ScrapeEngine,
    ScrapeScrapeBulkResponse,
    ScrapeScrapeSingleResponse,
)
```

Methods:

- <code title="post /scrape/bulk">client.scrape.<a href="./src/cartography/resources/scrape.py">scrape_bulk</a>(\*\*<a href="src/cartography/types/scrape_scrape_bulk_params.py">params</a>) -> <a href="./src/cartography/types/scrape_scrape_bulk_response.py">ScrapeScrapeBulkResponse</a></code>
- <code title="post /scrape/single">client.scrape.<a href="./src/cartography/resources/scrape.py">scrape_single</a>(\*\*<a href="src/cartography/types/scrape_scrape_single_params.py">params</a>) -> <a href="./src/cartography/types/scrape_scrape_single_response.py">ScrapeScrapeSingleResponse</a></code>

# Crawl

Types:

```python
from cartography.types import CrawlCreateGraphResponse
```

Methods:

- <code title="post /crawl/graph">client.crawl.<a href="./src/cartography/resources/crawl.py">create_graph</a>(\*\*<a href="src/cartography/types/crawl_create_graph_params.py">params</a>) -> <a href="./src/cartography/types/crawl_create_graph_response.py">CrawlCreateGraphResponse</a></code>

# Download

Types:

```python
from cartography.types import (
    BulkDownloadResult,
    DownloaderType,
    WaitUntil,
    DownloadCreateBulkResponse,
    DownloadCreateSingleResponse,
)
```

Methods:

- <code title="post /download/bulk">client.download.<a href="./src/cartography/resources/download.py">create_bulk</a>(\*\*<a href="src/cartography/types/download_create_bulk_params.py">params</a>) -> <a href="./src/cartography/types/download_create_bulk_response.py">DownloadCreateBulkResponse</a></code>
- <code title="post /download/single">client.download.<a href="./src/cartography/resources/download.py">create_single</a>(\*\*<a href="src/cartography/types/download_create_single_params.py">params</a>) -> <a href="./src/cartography/types/download_create_single_response.py">DownloadCreateSingleResponse</a></code>

# Workflows

Types:

```python
from cartography.types import WorkflowDescribeResponse, WorkflowResultsResponse
```

Methods:

- <code title="get /workflows/describe/{workflow_id}">client.workflows.<a href="./src/cartography/resources/workflows/workflows.py">describe</a>(workflow_id) -> <a href="./src/cartography/types/workflow_describe_response.py">WorkflowDescribeResponse</a></code>
- <code title="get /workflows/results/{workflow_id}">client.workflows.<a href="./src/cartography/resources/workflows/workflows.py">results</a>(workflow_id) -> <a href="./src/cartography/types/workflow_results_response.py">WorkflowResultsResponse</a></code>

## Request

Types:

```python
from cartography.types.workflows import RequestCreateDownloadResponse
```

Methods:

- <code title="post /workflows/request/download">client.workflows.request.<a href="./src/cartography/resources/workflows/request/request.py">create_download</a>(\*\*<a href="src/cartography/types/workflows/request_create_download_params.py">params</a>) -> <a href="./src/cartography/types/workflows/request_create_download_response.py">RequestCreateDownloadResponse</a></code>

### Crawl

Types:

```python
from cartography.types.workflows.request import (
    CrawlRequest,
    WorkflowResult,
    CrawlCreateBulkResponse,
)
```

Methods:

- <code title="post /workflows/request/crawl">client.workflows.request.crawl.<a href="./src/cartography/resources/workflows/request/crawl.py">create</a>(\*\*<a href="src/cartography/types/workflows/request/crawl_create_params.py">params</a>) -> <a href="./src/cartography/types/workflows/request/workflow_result.py">WorkflowResult</a></code>
- <code title="post /workflows/request/crawl/bulk">client.workflows.request.crawl.<a href="./src/cartography/resources/workflows/request/crawl.py">create_bulk</a>(\*\*<a href="src/cartography/types/workflows/request/crawl_create_bulk_params.py">params</a>) -> <a href="./src/cartography/types/workflows/request/crawl_create_bulk_response.py">CrawlCreateBulkResponse</a></code>
