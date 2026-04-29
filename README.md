# Event Management API

A feature-rich Event Management API built with FastAPI, now with a responsive frontend interface.

## Features

- **Frontend Interface**: A beautiful, responsive web UI for interacting with the API, built with HTML, CSS, and JavaScript.
- **Authentication**: JWT-based sign-up and login.
- **Role-Based Access**: Regular users can register for events; admins can create events and manage registrations.
- **Event Management**: Create and list events.
- **Registration**: Register for an event, optionally with a team code.
- **Admin Dashboard**: Filter registrations, mark attendance.
- **Extras**:
  - Download a QR code for your registration.
  - Automatically generate a PDF certificate upon attending an event.
  - Export event registration data to CSV or Excel.

## Setup

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```

3. Visit the Application:
   - **Frontend UI**: `http://127.0.0.1:8000/`
   - **API documentation (Swagger UI)**: `http://127.0.0.1:8000/docs`

## Running Tests
Run `pytest` in the root directory.
