# Drupal-Solr-Bot

This Drupal Solr chat Bot application provides an API that allows end-users to communicate with and receive generated responses from a chatbot.

## Getting Started

To get the server running locally, follow these steps:

1. **Clone the repository**

   git clone <repository-url>
   cd <repository-name>

2. Install the requirements

Install the required packages using pip

3. Run the development server

uvicorn main:app --port 8086 --reload

4. Replace the Solr core name

Ensure that you replace the Solr core name in the application as per your specific application setup.

API Endpoints
POST /search

Submit a question and receive a response from the chatbot.

{"question":"Hello I want to know about the....", "langcode":"en"}