import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv
import motor.motor_asyncio
import io

# 1. Load the variables from your .env file
load_dotenv()

app = FastAPI()

# 2. Get the URI from the environment variable
MONGO_URI = os.getenv("MONGO_URI")

# 3. Connect to MongoDB
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client.event_management_db  # This matches the name in your URI

# Data Models

class Event(BaseModel):
 name: str
 description: str
 date: str
 venue_id: str
 max_attendees: int

class Attendee(BaseModel):
 name: str
 email: str
 phone: Optional[str] = None

class Venue(BaseModel):
 name: str
 address: str
 capacity: int

class Booking(BaseModel):
 event_id: str
 attendee_id: str
 ticket_type: str
 quantity: int

# Event Endpoints

    #
    #Endpoints for dummies

    #the line below me is for creating events 
    #@app.post("/events")

    #the line below me is for making data readable by mongo db
    # event_doc = event.dict()

    #  the line below me is for inserting the newely made data in the events section (event_doc)
    # result = await db.events.insert_one(event_doc)
    
    # the line below me returns a message and the id of the newly created event
    # return {"message": "Event created", "id": str(result.inserted_id)}

    #the line below me is for getting events from the database
    #@app.get("/events")

    # the line below me is for making a list of events from the database
    #async def get_events():

    # the line below me is for finding events in the database and making a list of 100 events
    # events = await db.events.find().to_list(100)
    
    # the lines below me are for converting the event IDs to strings for JSON serialization in a for loop
    # for event in events:
    #   event["_id"] = str(event["_id"])

    # the line below me is for returning the list of events
    # return events


@app.post("/events")
async def create_event(event: Event):
 event_doc = event.dict()
 result = await db.events.insert_one(event_doc)
 return {"message": "Event created", "id": str(result.inserted_id)}

@app.get("/events")
async def get_events():
 events = await db.events.find().to_list(100)
 for event in events:
    event["_id"] = str(event["_id"])
 return events
# Upload Event Poster (Image)
    
@app.post("/attendees")
async def create_attendee(attendee: Attendee):
  attendee_doc = attendee.dict()
  result = await db.attendees.insert_one(attendee_doc)
  return {"message": "Attendee created", "id": str(result.inserted_id)}

@app.get("/attendees")
async def get_attendees():
 attendees = await db.attendees.find().to_list(100)
 for attendee in attendees:
    attendee["_id"] = str(attendee["_id"])
 return attendees

# --- VENUE ENDPOINTS ---

@app.post("/venues")
async def create_venue(venue: Venue):
    venue_doc = venue.dict()
    result = await db.venues.insert_one(venue_doc)
    return {"message": "Venue created", "id": str(result.inserted_id)}

@app.get("/venues")
async def get_venues():
    venues = await db.venues.find().to_list(100)
    for venue in venues:
        venue["_id"] = str(venue["_id"])
    return venues


# --- BOOKING ENDPOINTS ---

@app.post("/bookings")
async def create_booking(booking: Booking):
    booking_doc = booking.dict()
    result = await db.bookings.insert_one(booking_doc)
    return {"message": "Booking successful", "id": str(result.inserted_id)}

@app.get("/bookings")
async def get_bookings():
    bookings = await db.bookings.find().to_list(100)
    for booking in bookings:
        booking["_id"] = str(booking["_id"])
    return bookings



@app.post("/upload_event_poster/{event_id}")
async def upload_event_poster(event_id: str, file: UploadFile = File(...)):
 content = await file.read()
 poster_doc = {
 "event_id": event_id,
 "filename": file.filename,
 "content_type": file.content_type,
 "content": content,
 "uploaded_at": datetime.utcnow()
 }
 result = await db.event_posters.insert_one(poster_doc)
 return {"message": "Event poster uploaded", "id": str(result.inserted_id)}

@app.get("/get_poster/{event_id}")
async def get_poster(event_id: str):
    # Find the data using Motor
    poster = await db.event_posters.find_one({"event_id": event_id})
    
    if not poster:
        raise HTTPException(status_code=404, detail="File not found")

    # Use 'io' to wrap the 'content' bytes from your list
    # Use 'StreamingResponse' from your list to send it to the client
    return StreamingResponse(io.BytesIO(poster["content"]), media_type=poster["content_type"])

#   POST Promo Videos
@app.post("/upload_promo_video/{event_id}")
async def upload_promo_video(event_id: str, file: UploadFile = File(...)):
    content = await file.read()
    video_doc = {
        "event_id": event_id,
        "filename": file.filename,
        "content_type": file.content_type,
        "content": content,
        "uploaded_at": datetime.utcnow()
    }
    result = await db.promo_videos.insert_one(video_doc)
    return {"message": "Promotional video uploaded", "id": str(result.inserted_id)}

#   GET Promo Videos
@app.get("/get_promo_video/{event_id}")
async def get_promo_video(event_id: str):
    # Find the video document in the 'promo_videos' collection
    video = await db.promo_videos.find_one({"event_id": event_id})
    
    if not video:
        raise HTTPException(status_code=404, detail="Promotional video not found")
    
    # Return the binary content as a stream so it plays in the browser/Postman
    return StreamingResponse(
        io.BytesIO(video["content"]), 
        media_type=video["content_type"]
    )

#   POST Venue Photos
@app.post("/upload_venue_photo/{venue_id}")
async def upload_venue_photo(venue_id: str, file: UploadFile = File(...)):
    content = await file.read()
    photo_doc = {
        "venue_id": venue_id,
        "filename": file.filename,
        "content_type": file.content_type,
        "content": content,
        "uploaded_at": datetime.utcnow()
    }
    result = await db.venue_photos.insert_one(photo_doc)
    return {"message": "Venue photo uploaded", "id": str(result.inserted_id)}



#  GET Venue Photos 
@app.get("/get_venue_photo/{venue_id}")
async def get_venue_photo(venue_id: str):
    # Find the photo document in the 'venue_photos' collection
    photo = await db.venue_photos.find_one({"venue_id": venue_id})
    
    if not photo:
        raise HTTPException(status_code=404, detail="Venue photo not found")
    
    # Return the binary content as an image stream
    return StreamingResponse(
        io.BytesIO(photo["content"]), 
        media_type=photo["content_type"]
    )