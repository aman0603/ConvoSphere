# ConvoSphere: OSINT-Powered Person Profile Enrichment

ConvoSphere is an Open Source Intelligence (OSINT) framework designed to create comprehensive, sales-ready profiles of individuals by leveraging the Google Gemini API and various specialized data collection tools. It orchestrates a multi-step enrichment process to gather and synthesize information from diverse online sources.

## Features

*   **Gemini API Integration**: Utilizes Google's Gemini API for intelligent parsing of initial information, filtering search results, extracting relevant data from scraped content, and generating final, verified person summaries.
*   **Modular Tooling**: Integrates with several external APIs and services for specific data collection tasks:
    *   **Phone Validation**: Verifies phone numbers and retrieves country details using the Numverify API.
    *   **Social Media Intelligence (Twitter/X)**: Fetches user profiles and timelines from Twitter (now X) to understand digital footprint.
    *   **Professional Networking (LinkedIn)**: Collects structured LinkedIn profile information using the BrightData API.
    *   **Web Search (SerpAPI)**: Performs targeted Google searches to discover relevant online presence.
    *   **Web Scraping (Firecrawl)**: Scrapes content from identified URLs to extract detailed information.
*   **Orchestrated Workflow**: Manages a systematic, multi-wave enrichment process to ensure thorough data collection and verification.
*   **Sales-Ready Profiles**: Generates detailed person profiles including basic info, contact details, professional background, digital footprint analysis, company context, and actionable sales intelligence (talking points, pain points, interests, best contact methods).
*   **Ground Truth Verification**: Compares collected data against initial input to flag discrepancies and provide confidence scores.
*   **API-driven Backend**: A FastAPI backend manages sessions, messages, and triggers background processing.
*   **Streamlit Frontend**: An interactive Streamlit application provides a user interface for sales agents.

## Architecture

The system is built around a central API backend that orchestrates the flow and interacts with various services.

*   `api/main.py`: The core FastAPI application that defines endpoints for session management, message handling, and triggering background tasks.
*   `api/schemas.py`: Pydantic models defining the data structures (sessions, messages, OSINT results, LLM analysis, etc.) for API requests/responses and database storage.
*   `db/database.py`: Handles connections to MongoDB (for persistent storage) and Redis (for caching/queueing).
*   `db/models.py`: Contains utility functions for interacting with database collections.
*   `services/local_llm_service.py`: Provides an interface for local Large Language Model (LLM) interactions, including analysis and message suggestions.
*   `services/telegram_router.py`: Handles outbound messaging via Telegram and includes a placeholder for webhook reception.
*   **Fetcher Scripts**: Individual Python scripts responsible for interacting with specific external APIs:
    *   `numverify_fetcher.py`: Numverify API client.
    *   `twitter_info_fetcher.py`: Twitter (X) API client (using `tweepy`).
    *   `linkedin_info_fetcher.py`: BrightData API client for LinkedIn data.
    *   `serpapi_tester.py`: SerpAPI client for Google searches.
    *   `firecrawler_linkcrawler.py`: Firecrawl API client for web scraping.
*   `orchestrator.py`: (Original orchestrator script, parts of its logic are being integrated into API background tasks).
*   `gemini_client.py`: Handles interactions with the Google Gemini API for advanced AI tasks.
*   `ui/streamlit_app.py`: The Streamlit frontend application.

## Setup and Installation

1.  **Prerequisites: MongoDB and Redis**
    This project requires **MongoDB** (for persistent storage) and **Redis** (for caching/queues) to be installed and running. For detailed installation instructions for your operating system, please refer to the [IMPLEMENTATION_README.md](./IMPLEMENTATION_README.md) file. Ensure both are running on their default ports (MongoDB: 27017, Redis: 6379) or configure your `.env` accordingly.

2.  **Clone the Repository**:
    ```bash
    git clone https://github.com/your-username/ConvoSphere.git
    cd ConvoSphere
    ```

3.  **Create a Virtual Environment (Recommended)**:
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

4.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

5.  **Environment Variables Configuration**:
    Create a `.env` file in the project root based on `.env.example` and fill in your API keys and database connection details. Refer to `.env.example` for all required variables.

## Usage

This project consists of a FastAPI backend and a Streamlit frontend. Ensure your MongoDB and Redis instances are running before starting the applications.

### 1. Run the FastAPI Backend

The FastAPI application provides the core API for managing sessions, messages, and triggering background tasks.

```bash
uvicorn api.main:app --reload
```
The API will be available at `http://127.0.0.1:8000`. You can access the interactive API documentation (Swagger UI) at `http://127.0.0.1:8000/docs`.

#### Implemented API Endpoints:
*   `POST /api/sessions`: Create a new sales session.
*   `GET /api/sessions/{session_id}`: Retrieve details of a specific session.
*   `POST /api/sessions/{session_id}/messages`: Add a new message to a session.
*   `POST /api/sessions/{session_id}/send`: Send an outbound message (e.g., via Telegram) related to a session.
*   `POST /webhook/telegram`: Placeholder webhook endpoint for incoming Telegram messages.
*   `POST /api/sessions/{session_id}/trigger_gemini`: Manually trigger a Gemini analysis task for a session.

### 2. Run the Streamlit Frontend

The Streamlit application provides an interactive user interface for sales agents.

```bash
streamlit run ui/streamlit_app.py
```
The Streamlit app will open in your web browser, typically at `http://localhost:8501`.

## Running Individual Tools (for development/testing)

You can still run individual fetcher scripts independently for testing or specific tasks:

*   **Numverify**: `python numverify_fetcher.py +15551234567`
*   **Twitter**: `python twitter_info_fetcher.py get your_twitter_username`
*   **SerpAPI**: `python serpapi_tester.py "John Doe LinkedIn profile"`
*   **Firecrawl**: `python firecrawler_linkcrawler.py https://example.com/some-page`
*   **Telegram**: `python telegram_talker.py` (This will guide you through authentication and then allow you to send/receive messages.)

## Testing

Unit and integration tests are available.

*   `tests/test_api.py`: Contains tests for the FastAPI backend endpoints.
*   `test_gemini_client.py`: Contains unit tests for the `GeminiClient`.
*   `test_orchestrator.py`: Contains tests for the original `PersonOSINTOrchestrator` workflow.
*   `test.py`: General tests.

To run tests:

```bash
pip install pytest httpx # if not already installed
pytest
```

---

*This README was generated by a Gemini-powered agent.*
