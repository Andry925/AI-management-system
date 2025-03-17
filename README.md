# AI-Powered Notes Application

This project is an AI-powered note application that meets all the specified task requirements:

## Features
1. **Authentication with JWT:** Secure user authentication.
2. **CRUD Operations for Notes:** Create, read, update, and delete notes.
3. **Note History:** View historical versions of notes.
4. **Summarization:** Summarize notes using the OpenAI API.
5. **Analytical Endpoints:** Calculate various statistics such as:
   - Total word count across all notes.
   - Average note length.
   - Most common words or phrases.
   - Top 3 longest and shortest notes.
6. **Testing:** Unit and integration tests with 80% coverage.

## Implementation
- **Authentication:** Implemented using JWT for secure access.
- **Database & Models:**  
  - Two main models: `User` and `Note`, linked via a foreign key.  
  - Versioning is handled with SQLAlchemy-Continuum to track note history.
- **Performance:**  
  - Pagination is implemented in endpoints (e.g., retrieving all notes and note history) to reduce database load.
- **AI Integration:**  
  - Utilizes an asynchronous OpenAI client since the API is completely asynchronous.  
  - Uses an async SQLAlchemy driver for database communications.
- **Analytics:**  
  - Provides a separate asynchronous endpoint for data analysis.  
  - Uses synchronous utilities with Pandas and NLTK to calculate statistics and clean stop words.
- **Testing:**  
  - Testing is performed using an SQLite environment with asynchronous tests ensuring 80% coverage.

## How to Run

1. **Environment Setup:**  
   - Configuration details are provided in the `.env` file. Ensure you set your `OPENAI_API_KEY`.
2. **Development:**  
   - Build and run the application using Docker Compose:
     ```bash
     docker-compose --build
     ```
3. **Testing:**  
   - Run tests with (docker-compose must be run as well):
     ```bash
     pytest -v -s
     ```

