# Contacts updater


This repository contains a web service for searching contacts by full text. The service allows users to search for contacts based on a given keyword. The API endpoint provided by the service returns search results in JSON format. The contact information is refreshed every 12 hours.

Technologies Used:

- PostgreSQL
- FastAPI
- Redis
- Celery

To run the API service and access the contact search functionality, please follow the setup instructions mentioned in the README above.

# Setup
1. Clone the repository to your local machine.

2. Install the required dependencies by running the following command:

  ```
  pip install -r requirements.txt
  ```

3. Ensure that you have PostgreSQL installed on your system. 
4. Start the PostgreSQL server.
5. Build the Redis Docker image using Dockerfile. Run the following command:
  ```
  docker build -t my-redis-image .
  ```
6. Run a Redis container using the image you just built:
  ```
  docker run -d --name my-redis-container my-redis-image
  ```
7. Prepare env file:
  ```
  DB_NAME=''
  DB_USER=''
  DB_PASSWORD=''
  DB_HOST=''
  DB_PORT=''
  
  NIMBLE_API_URL='https://api.nimble.com/api/v1/contacts/'
  NIMBLE_API_TOKEN='NxkA2RlXS3NiR8SKwRdDmroA992jgu'
  ```
8. Run the API service using the following command:
  ```
  
  python app.py
  ```
9. Open a new terminal or command prompt window and navigate to the project directory. Start the Celery worker and scheduler with the following command:
  ```
  celery -A tasks.task_manager worker --loglevel=INFO -B --scheduler celery.beat.PersistentScheduler -s /tmp/celerybeat-schedule
  ```

10. Enjoy :)
