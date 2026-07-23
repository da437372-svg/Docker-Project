# Docker-Project

## Puropse of the Project- 📰 Headlines Docker Image
* Create a Docker image that prints latest newspaper headlines

## 🚀 Pre-requisites - Basic Docker lifecycle understanding , Docker desktop Pre-installed and ruuning, and Expereince with pushing docker image to docker-hub.
## Part A - Installing the core python packages in the terminal-
* FastAPI - Installs the web framework used to build and handle your API routes and endpoints.
* Uvicorn - Installs the web server needed to run and serve your FastAPI application.
* Requests - Installs a library that allows your Python code to send HTTP requests to external APIs or websites.
* APScheduler - Installs a task scheduler to run specific Python code automatically on a set schedule or interval.
  
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

## 🛠️ Part C - Typed Query from Chatgpt to generate the python program
* Suggested Query to generate the python program for the API
  ```
  Use Python to create a python script for an API that fetches and returns New York Post headlines on scheduled, 15 minute interval.
  ```
* Launch Visual Studio Code (or your preferred editor) from the terminal to create the primary Python application script:
```
code main.py
```
* Paste your FastAPI application code containing the RSS feed parser, background scheduler, and API routes into main.py.
* [View the Python Script](./main.py)
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

       
