Event Management API
RESTful API for managing events, attendees, venues, and bookings with MongoDB Atlas.

Setup
Create virtual environment:
   python -m venv .venv
   .venv\Scripts\activate


Install dependencies:
   pip install -r requirements.txt


Create .env file with your MongoDB connection string

Run the application:
   uvicorn main:app --reload


API Documentation
Once running, visit: http://127.0.0.1:8000/docs