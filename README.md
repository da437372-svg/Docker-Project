# Docker-Project

## Puropse of the Project- 📰 New York Post Scheduled Headlines API
* Create an API that fetches and updates New York Post headlines, then containerize it and push the image to Docker Hub.

## 🚀 Pre-requisites - Basic Docker cycle Understanding , Docker desktop Pre-installed and ruuning, and Expereince with pushing docker image to docker-hub.
## Part A - Installing the core python packages in the terminal-
* FastAPI (web framework)
* Uvicorn (ASGI web server)
* Requests (HTTP client)
* APScheduler (task scheduling engine)
  
```
pip install fastapi uvicorn requests apscheduler
```
## Part B - Create the Project Directory
* Initialize a dedicated directory on your local filesystem to organize all code, configuration files, and container definitions:
```
mkdir nypost-api
```
* Then Navigate to the workspace where you will change your current working directory to the newly created project folder:
```
cd nypost-api
```

## 🛠️ Part C - Create and Configure the Application Entry Point

* Launch Visual Studio Code (or your preferred editor) from the terminal to create the primary Python application script:
```
code main.py
```
* Paste your FastAPI application code containing the RSS feed parser, background scheduler, and API routes into main.py.
 ``` 
  from contextlib import asynccontextmanager
from typing import Dict, List
import xml.etree.ElementTree as ET
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, HTTPException, Query
import requests

# Feed sources configuration
CATEGORY_FEEDS = {
    "main": "https://nypost.com/feed/",
    "metro": "https://nypost.com/metro/feed/",
    "sports": "https://nypost.com/sports/feed/",
    "business": "https://nypost.com/business/feed/",
    "entertainment": "https://nypost.com/entertainment/feed/",
    "tech": "https://nypost.com/tech/feed/",
}

# In-memory storage for cached headlines
HEADLINES_CACHE: Dict[str, List[Dict[str, str]]] = {
    category: [] for category in CATEGORY_FEEDS
}


def fetch_and_parse_feed(category: str, feed_url: str) -> List[Dict[str, str]]:
    """Helper to pull and parse RSS xml."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        response = requests.get(feed_url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"[!] Warning: Failed to fetch {category} feed (Status {response.status_code})")
            return HEADLINES_CACHE.get(category, [])  # Return previous cache on failure

        root = ET.fromstring(response.content)
        channel = root.find("channel")
        if channel is None:
            return []

        articles = []
        for item in channel.findall("item"):
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

    except Exception as e:
        print(f"[!] Error updating {category} feed: {e}")
        return HEADLINES_CACHE.get(category, [])


def refresh_all_headlines():
    """Background task to update all category feeds into cache."""
    print("[*] Scheduled task triggered: Refreshing NY Post headlines...")
    for category, url in CATEGORY_FEEDS.items():
        HEADLINES_CACHE[category] = fetch_and_parse_feed(category, url)
    print("[+] All feeds successfully refreshed.")


# Initialize Scheduler
scheduler = BackgroundScheduler()
# Run background job every 15 minutes
scheduler.add_job(refresh_all_headlines, "interval", minutes=15)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    print("[*] Starting initial feed fetch...")
    refresh_all_headlines()  # Initial fetch when app boots
    scheduler.start()        # Start background schedule
    
    yield
    
    # --- Shutdown ---
    print("[*] Shutting down background scheduler...")
    scheduler.shutdown()


app = FastAPI(
    title="NY Post Headlines API (Scheduled)",
    description="Serves cached NY Post headlines that auto-refresh on a timer.",
    lifespan=lifespan
)


@app.get("/")
def root():
    return {
        "message": "Welcome to the NY Post Scheduled Headlines API",
        "status": "Running",
        "refresh_interval": "15 minutes"
    }


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
    cat_lower = category.lower()
    if cat_lower not in CATEGORY_FEEDS:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid category '{category}'. Valid choices: {list(CATEGORY_FEEDS.keys())}"
        )

    # Fast response pulled directly from cache
    cached_articles = HEADLINES_CACHE.get(cat_lower, [])
    
    return {
        "category": cat_lower,
        "count": len(cached_articles[:limit]),
        "articles": cached_articles[:limit]
    }
```
* Save the file (Ctrl + S or Cmd + S).

  ## Part D - Define the Container Environment (Dockerfile)

* Create a file named Dockerfile (without any file extension) in the root of your project directory using VS Code or a basic text editor like Notepad.

* Paste the following container build instructions:

 ```
 FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies inside the container
RUN pip install --no-cache-dir fastapi uvicorn requests apscheduler

# Copy application source code
COPY main.py .

# Expose the service port
EXPOSE 8000

# Start the web server with a single worker to maintain scheduler consistency
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"] 
```
> 💡 **Pro Tip for Readers:** Ensure that Docker Desktop (or your local Docker daemon) is actively running in the background. If Docker is not running, container operations in the next step will fail to connect.

## Part E - Build and Execute the Container
* Build the Docker Image: Compile the application code and dependencies into an image tagged nypost-api:
  ```
  docker build -t nypost-api .
  ```
* Run the Container Service: Instantiate and run the container in detached mode (-d), binding host port 8000 to container port 8000:
```
docker run -d -p 8000:8000 --name nypost-container nypost-api
```
## Part F - ☁️ Publishing to Docker Hub
* To share your image online or deploy it to cloud servers, and push your container image to Docker Hub, first login via the terminal to connect them to each other using the following command:
  ```
  Docker login
  ```
  > Enter your Docker Hub username and password when prompted.

 * Tag your local nypost-api image so Docker knows which account repository it belongs to:
    ```
    docker tag nypost-api YOUR_DOCKERHUB_USERNAME/nypost-api:v1
    ```
  * Upload your packaged image up to your public Docker Hub registry:
     ```
     docker push YOUR_DOCKERHUB_USERNAME/nypost-api:v1
     ```
  * Once uploaded, anyone can pull and run your app anywhere in the world using
       ```
       docker run -d -p 8000:8000 YOUR_DOCKERHUB_USERNAME/nypost-api:v1
       ```
 ## Part G - 🌐 Accessing the API

* Once deployed, verify the service is functioning by visiting the following links:

* Live JSON Headlines: http://localhost:8000/headlines

Interactive Documentation (Swagger UI): http://localhost:8000/docs



       
