# Olyptik Python SDK
The Olyptik Python SDK provides a simple and intuitive interface for web crawling and content extraction. It supports both synchronous and asynchronous programming patterns with full type hints.

## Installation

Install the SDK using pip:

```bash
pip install olyptik
```

## Configuration

First, you'll need to initialize the SDK with your API key - you can get it from the [settings page](https://app.olyptik.io/settings/crawl). You can either pass it directly or use environment variables.

```python
from olyptik import Olyptik

# Initialize with API key
client = Olyptik(api_key="your_api_key_here")
```

## Synchronous Usage

### Start a crawl

<CodeGroup>

```python Minimal Example
crawl = client.run_crawl({
    "startUrl": "https://example.com",
    "maxResults": 50
})

print(f"Crawl started with ID: {crawl.id}")
print(f"Status: {crawl.status}")
```

```python Full Example
# Start a crawl
crawl = client.run_crawl({
    "startUrl": "https://example.com",
    "maxResults": 50,
    "maxDepth": 2,
    "engineType": "auto",
    "includeLinks": True,
    "timeout": 60,
    "useSitemap": False,
    "useStaticIps": False
})

print(f"Crawl started with ID: {crawl.id}")
print(f"Status: {crawl.status}")
```
</CodeGroup>

### Get crawl results

```python
results = client.get_crawl_results(crawl.id)
for result in results.results:
    print(f"URL: {result.url}")
    print(f"Title: {result.title}")
    print(f"Depth: {result.depthOfUrl}")
```

### Abort a crawl

```python
aborted_crawl = client.abort_crawl(crawl.id)
print(f"Crawl aborted with ID: {aborted_crawl.id}")
```

## Asynchronous Usage

For better performance with I/O operations, use the async client:

### Start a crawl

<CodeGroup>

```python Minimal Example
import asyncio
from olyptik import AsyncOlyptik

async def main():
    async with AsyncOlyptik(api_key="your_api_key_here") as client:
        crawl = await client.run_crawl({
            "startUrl": "https://example.com",
            "maxResults": 50
        })

        print(f"Crawl started with ID: {crawl.id}")
        print(f"Status: {crawl.status}")

asyncio.run(main())
```

```python Full Example
import asyncio
from olyptik import AsyncOlyptik

async def main():
    async with AsyncOlyptik(api_key="your_api_key_here") as client:
        # Start a crawl
        crawl = await client.run_crawl({
            "startUrl": "https://example.com",
            "maxResults": 50,
            "maxDepth": 2,
            "engineType": "auto",
            "includeLinks": True,
            "timeout": 60,
            "useSitemap": False,
            "useStaticIps": False
        })

        print(f"Crawl started with ID: {crawl.id}")
        print(f"Status: {crawl.status}")

asyncio.run(main())
```

</CodeGroup>

### Get crawl results

```python
import asyncio
from olyptik import AsyncOlyptik

async def main():
    async with AsyncOlyptik(api_key="your_api_key_here") as client:
        # First start a crawl
        crawl = await client.run_crawl({
            "startUrl": "https://example.com",
            "maxResults": 50
        })
        
        # Get crawl results
        results = await client.get_crawl_results(crawl.id)
        for result in results.results:
            print(f"URL: {result.url}")
            print(f"Title: {result.title}")
            print(f"Depth: {result.depthOfUrl}")

asyncio.run(main())
```

### Abort a crawl

```python
import asyncio
from olyptik import AsyncOlyptik

async def main():
    async with AsyncOlyptik(api_key="your_api_key_here") as client:
        # First start a crawl
        crawl = await client.run_crawl({
            "startUrl": "https://example.com",
            "maxResults": 50
        })
        
        # Abort the crawl
        aborted_crawl = await client.abort_crawl(crawl.id)
        print(f"Crawl aborted with ID: {aborted_crawl.id}")

asyncio.run(main())
```

## Configuration Options

### StartCrawlPayload

The crawl configuration options available:

The run crawl payload:
| Property | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| startUrl | string | ✅ | - | The URL to start crawling from |
| maxResults | number | ✅ | - | Maximum number of results to collect (1-10,000) |
| maxDepth | number | ❌ | 10 | Maximum depth of pages to crawl (1-100) |
| includeLinks | boolean | ❌ | true | Whether to include links in the crawl results' markdown |
| useSitemap | boolean | ❌ | false | Whether to use sitemap.xml to crawl the website |
| timeout | number | ❌ | 60 | Timeout duration in minutes |
| engineType | string | ❌ | "auto" | The engine to use: "auto", "cheerio" (fast, static sites), "playwright" (dynamic sites) |
| useStaticIps | boolean | ❌ | false | Whether to use static IPs for the crawl |

### Engine Types

Choose the appropriate engine for your crawling needs:

```python
from olyptik import EngineType

# Available engine types
EngineType.AUTO        # Automatically choose the best engine
EngineType.PLAYWRIGHT  # Use Playwright for JavaScript-heavy sites
EngineType.CHEERIO     # Use Cheerio for faster, static content crawling
```

### Crawl Status

Monitor your crawl status using the `CrawlStatus` enum:

```python
from olyptik import CrawlStatus

# Possible status values
CrawlStatus.RUNNING    # Crawl is currently running
CrawlStatus.SUCCEEDED  # Crawl completed successfully
CrawlStatus.FAILED     # Crawl failed due to an error
CrawlStatus.TIMED_OUT  # Crawl exceeded timeout limit
CrawlStatus.ABORTED    # Crawl was manually aborted
CrawlStatus.ERROR      # Crawl encountered an error
```

### Error Handling

The SDK provides comprehensive error handling:

```python
from olyptik import Olyptik, OlyptikError, ApiError

client = Olyptik(api_key="your_api_key_here")

try:
    crawl = client.run_crawl({
        "startUrl": "https://example.com",
        "maxResults": 10
    })
except ApiError as e:
    print(f"API Error: {e.message}")
    print(f"Status Code: {e.status_code}")
except OlyptikError as e:
    print(f"SDK Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Data Models

### CrawlResult

Each crawl result contains:

```python
@dataclass
class CrawlResult:
    crawlId: str          # Unique identifier for the crawl
    brandId: str          # Brand identifier
    url: str              # The crawled URL
    title: str            # Page title
    markdown: str         # Extracted content in markdown format
    depthOfUrl: int       # How deep this URL was in the crawl
    createdAt: str        # When the result was created
```

### Crawl

Crawl metadata includes:

```python
@dataclass
class Crawl:
    id: str                    # Unique crawl identifier
    status: CrawlStatus        # Current status
    startUrls: List[str]       # Starting URLs
    includeLinks: bool         # Whether links are included
    maxDepth: int              # Maximum crawl depth
    maxResults: int            # Maximum number of results
    brandId: str               # Brand identifier
    createdAt: str             # Creation timestamp
    completedAt: Optional[str] # Completion timestamp
    durationInSeconds: int     # Total duration
    numberOfResults: int       # Number of results found
    useSitemap: bool          # Whether sitemap was used
    timeout: int              # Timeout setting
```

## Best Practices

### 1. Use Async for Better Performance

```python
# ✅ Good: Use async for I/O intensive operations
async with AsyncOlyptik(api_key="your_api_key") as client:
    crawl = await client.run_crawl(payload)
    results = await client.get_crawl_results(crawl.id)

# ❌ Avoid: Blocking operations in async context
client = Olyptik(api_key="your_api_key")  # In async function
```

### 4. Choose the Right Engine

```python
# ✅ Good: Choose engine based on site type
# For JavaScript-heavy sites
crawl = client.run_crawl({
    "startUrl": "https://spa-app.com",
    "engineType": EngineType.PLAYWRIGHT
})

# For static content sites
crawl = client.run_crawl({
    "startUrl": "https://blog.example.com", 
    "engineType": EngineType.CHEERIO
})
```

## Troubleshooting

### Common Issues

**Import Error**: Make sure you have installed the package correctly:
```bash
pip install --upgrade olyptik
```

**Authentication Error**: Verify your API key is correct and has sufficient permissions.

**Timeout Issues**: Increase the timeout value for large crawls:
```python
crawl = client.run_crawl({
    "startUrl": "https://example.com",
    "timeout": 300  # 5 minutes
})
```

**Rate Limiting**: The SDK automatically handles retries, but you can implement additional backoff:
```python
import time
from olyptik import ApiError

try:
    crawl = client.run_crawl(payload)
except ApiError as e:
    if e.status_code == 429:
        time.sleep(60)  # Wait 1 minute
        crawl = client.run_crawl(payload)
```

## Support

- 📧 Email: support@olyptik.io
- 📚 API Reference: [API Documentation](/api-reference/introduction)