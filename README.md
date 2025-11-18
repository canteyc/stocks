# Stock Price Search Application

A simple web application that allows users to sign up, log in, and search for real-time stock prices.

## Description

This project consists of a frontend single-page application and a Django backend API. It provides user authentication and access to stock market data through the [Finnhub API](https://finnhub.io/). The application is fully containerized using Docker and Docker Compose for easy setup and deployment.

## Features

-   **User Authentication**: Secure user signup, login, and logout functionality.
-   **Stock Price Search**: Logged-in users can search for the opening price of any US stock by its symbol.
-   **Symbol Autocomplete**: The search box provides real-time suggestions for stock symbols as the user types, making it easy to find the desired stock.

## Tech Stack

-   **Backend**: Django, Gunicorn
-   **Frontend**: HTML, CSS, vanilla JavaScript
-   **Database**: SQLite
-   **Containerization**: Docker, Docker Compose
-   **Web Server / Reverse Proxy**: Nginx

## Running the Application with Docker Compose

Follow these instructions to get the application running on your local machine.

### Prerequisites

-   [Docker](https://docs.docker.com/get-docker/)
-   [Docker Compose](https://docs.docker.com/compose/install/)

### Setup

1.  **Clone the repository (if you haven't already):**
    ```bash
    git clone https://github.com/canteyc/stocks.git
    cd stocks
    ```

2.  **Create the environment file:**
    Make sure you have a `.env` file inside the `backend/` directory with your Finnhub API key:
    ```
    # backend/.env
    FINNHUB_API_KEY=your_api_key_here
    ```

### Run the Application

1.  From the root directory of the project (`stocks/`), run the following command:
    ```bash
    docker compose up --build
    ```
    This command will build the Docker images for the frontend and backend services and start the containers.

2.  **Access the application:**
    Open your web browser and navigate to `http://localhost:8080`.

### Running Tests

The project includes a suite of backend tests. To run the tests, use the following Docker Compose command from the root directory:

```bash
docker compose run --rm backend-test
```

This will start a temporary container, run the Django test suite, and then remove the container upon completion.