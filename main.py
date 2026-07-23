Paste your FastAPI application code containing the RSS feed parser, background scheduler, and API routes into main.
```
  from fastapi import FastAPI, HTTPException, Query
import requests
import xml.etree.ElementTree as ET
from typing import Optional, List, Dict

app = FastAPI(
    title="NY Post Headlines API",
    description="A simple API to fetch headlines from the New York Post RSS feeds."
)

# Supported section mappings to NY Post RSS feed URLs
CATEGORY_FEEDS = {
    "main": "https://nypost.com/feed/",
    "metro": "https://nypost.com/metro/feed/",
    "sports": "https://nypost.com/sports/feed/",
    "business": "https://nypost.com/business/feed/",
    "entertainment": "https://nypost.com/entertainment/feed/",
    "tech": "https://nypost.com/tech/feed/",
}

def parse_rss_feed(feed_url: str, limit: int) -> List[Dict[str, str]]:
    """Fetches and parses headlines from a given RSS feed URL."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    response = requests.get(feed_url, headers=headers, timeout=10)
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code, 
            detail="Failed to fetch headlines from New York Post feed."
        )

    # Parse XML content
    root = ET.fromstring(response.content)
    channel = root.find("channel")
    
    if channel is None:
        return []

    articles = []
    items = channel.findall("item")[:limit]

    for item in items:
        title = item.find("title")
        link = item.find("link")
        pub_date = item.find("pubDate")
        creator = item.find("{http://purl.org/dc/elements/1.1/}creator")

        articles.append({
            "title": title.text if title is not None else "",
            "url": link.text if link is not None else "",
            "published_at": pub_date.text if pub_date is not None else "",
            "author": creator.text if creator is not None else None
        })

    return articles


@app.get("/")
def root():
    return {
        "message": "Welcome to the NY Post Headlines API",
        "endpoints": {
            "/headlines": "Get main headlines",
            "/categories": "List available news categories"
        }
    }


@app.get("/categories")
def get_categories():
    return {"categories": list(CATEGORY_FEEDS.keys())}


@app.get("/headlines")
def get_headlines(
    category: str = Query(
        default="main", 
        description="Category: main, metro, sports, business, entertainment, tech"
    ),
    limit: int = Query(
        default=10, 
        ge=1, 
        le=50, 
        description="Number of headlines to retrieve"
    )
):
    category = category.lower()
    if category not in CATEGORY_FEEDS:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid category '{category}'. Valid options: {list(CATEGORY_FEEDS.keys())}"
        )

    feed_url = CATEGORY_FEEDS[category]
    headlines = parse_rss_feed(feed_url, limit)
    
    return {
        "category": category,
        "count": len(headlines),
        "articles": headlines
    }
  ```
