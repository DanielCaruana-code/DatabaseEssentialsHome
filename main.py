import os
import io
from bson import ObjectId
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

# API Framework Imports
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import motor.motor_asyncio
from fastapi.responses import RedirectResponse


# CONFIGURATION 
# Load environment variables (MONGO_URI) from the .env file for security
load_dotenv()
app = FastAPI()

async def root():
    # This automatically sends anyone who visits the home page to the /docs page
    return RedirectResponse(url="/docs")
# Initialize MongoDB Client using the Motor async driver
MONGO_URI = os.getenv("MONGO_URI")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client.event_management_db 

# DATA MODELS
# These models define the structure of the data and provide automatic validation
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

# CRUD ENDPOINTS (Events, Attendees, Venues, Bookings)


# Create (POST)

# Creates a new event document in the database


# Read (GET)

# Retrieves events from the database


# Update (PUT)

# Updates an existing event using its unique MongoDB ID


# Delete (DELETE)

# Removes an event from the database


# EVENT EndPoints 



#(POST)

@app.post("/events")
async def create_event(event: Event):
    """Creates a new event document in the database"""
    event_doc = event.dict()
    result = await db.events.insert_one(event_doc)
    return {"message": "Event created", "id": str(result.inserted_id)}


#(GET)

@app.get("/events")
async def get_events():
    """Retrieves up to 100 events from the database"""
    events = await db.events.find().to_list(100)
    for event in events:
        event["_id"] = str(event["_id"])
    return events


#(PUT)

@app.put("/events/{event_id}")
async def update_event(event_id: str, event: Event):
    """Updates an existing event using its unique MongoDB ID"""
    result = await db.events.update_one({"_id": ObjectId(event_id)}, {"$set": event.dict()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"message": "Event updated successfully"}


#(DELETE)

@app.delete("/events/{event_id}")
async def delete_event(event_id: str):
    """Removes an event from the database"""
    result = await db.events.delete_one({"_id": ObjectId(event_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"message": "Event deleted successfully"}



# --- ATTENDEE EndPoints ---

#(POST)

@app.post("/attendees")
async def create_attendee(attendee: Attendee):
    result = await db.attendees.insert_one(attendee.dict())
    return {"message": "Attendee created", "id": str(result.inserted_id)}


#(GET)

@app.get("/attendees")
async def get_attendees():
    attendees = await db.attendees.find().to_list(100)
    for a in attendees: a["_id"] = str(a["_id"])
    return attendees


#(PUT)

@app.put("/attendees/{id}")
async def update_attendee(id: str, data: Attendee):
    result = await db.attendees.update_one({"_id": ObjectId(id)}, {"$set": data.dict()})
    if result.matched_count == 0: raise HTTPException(status_code=404, detail="Not found")
    return {"message": "Attendee updated"}


#(DELETE)

@app.delete("/attendees/{id}")
async def delete_attendee(id: str):
    result = await db.attendees.delete_one({"_id": ObjectId(id)})
    return {"message": "Attendee deleted"}

# --- VENUE EndPoints ---

#(POST)

@app.post("/venues")
async def create_venue(venue: Venue):
    result = await db.venues.insert_one(venue.dict())
    return {"message": "Venue created", "id": str(result.inserted_id)}


#(GET)

@app.get("/venues")
async def get_venues():
    venues = await db.venues.find().to_list(100)
    for v in venues: v["_id"] = str(v["_id"])
    return venues


#(PUT)

@app.put("/venues/{id}")
async def update_venue(id: str, data: Venue):
    result = await db.venues.update_one({"_id": ObjectId(id)}, {"$set": data.dict()})
    return {"message": "Venue updated"}


#(DELETE)

@app.delete("/venues/{id}")
async def delete_venue(id: str):
    await db.venues.delete_one({"_id": ObjectId(id)})
    return {"message": "Venue deleted"}

# --- BOOKING EndPoints ---

#(POST)

@app.post("/bookings")
async def create_booking(booking: Booking):
    result = await db.bookings.insert_one(booking.dict())
    return {"message": "Booking successful", "id": str(result.inserted_id)}


#(GET)

@app.get("/bookings")
async def get_bookings():
    bookings = await db.bookings.find().to_list(100)
    for b in bookings: b["_id"] = str(b["_id"])
    return bookings


#(PUT)

@app.put("/bookings/{id}")
async def update_booking(id: str, data: Booking):
    result = await db.bookings.update_one({"_id": ObjectId(id)}, {"$set": data.dict()})
    return {"message": "Booking updated"}


#(DELETE)

@app.delete("/bookings/{id}")
async def delete_booking(id: str):
    await db.bookings.delete_one({"_id": ObjectId(id)})
    return {"message": "Booking deleted"}

# --- MULTIMEDIA EndPoints (Event POSTERS,Promo VIDEOS,Venue PHOTOS) ---

# EVENT POSTERS (Images)
@app.post("/upload_event_poster/{event_id}")
async def upload_event_poster(event_id: str, file: UploadFile = File(...)):
    """Reads image file and saves it as binary data associated with an Event ID"""
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
    """Retrieves binary image data and streams it back to the client as a viewable image"""
    poster = await db.event_posters.find_one({"event_id": event_id})
    if not poster: raise HTTPException(status_code=404, detail="File not found")
    return StreamingResponse(io.BytesIO(poster["content"]), media_type=poster["content_type"])

# PROMOTIONAL VIDEOS
@app.post("/upload_promo_video/{event_id}")
async def upload_promo_video(event_id: str, file: UploadFile = File(...)):
    content = await file.read()
    video_doc = {
        "event_id": event_id, "filename": file.filename,
        "content_type": file.content_type, "content": content,
        "uploaded_at": datetime.utcnow()
    }
    result = await db.promo_videos.insert_one(video_doc)
    return {"message": "Promotional video uploaded", "id": str(result.inserted_id)}

@app.get("/get_promo_video/{event_id}")
async def get_promo_video(event_id: str):
    video = await db.promo_videos.find_one({"event_id": event_id})
    if not video: raise HTTPException(status_code=404, detail="Video not found")
    return StreamingResponse(io.BytesIO(video["content"]), media_type=video["content_type"])

# VENUE PHOTOS
@app.post("/upload_venue_photo/{venue_id}")
async def upload_venue_photo(venue_id: str, file: UploadFile = File(...)):
    content = await file.read()
    photo_doc = {
        "venue_id": venue_id, "filename": file.filename,
        "content_type": file.content_type, "content": content,
        "uploaded_at": datetime.utcnow()
    }
    result = await db.venue_photos.insert_one(photo_doc)
    return {"message": "Venue photo uploaded", "id": str(result.inserted_id)}

@app.get("/get_venue_photo/{venue_id}")
async def get_venue_photo(venue_id: str):
    photo = await db.venue_photos.find_one({"venue_id": venue_id})
    if not photo: raise HTTPException(status_code=404, detail="Photo not found")
    return StreamingResponse(io.BytesIO(photo["content"]), media_type=photo["content_type"])

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