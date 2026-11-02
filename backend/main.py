from fastapi import FastAPI,HTTPException
from dataclasses import dataclass

app=FastAPI()

@dataclass
class Facility:
    facility_id:int
    name:str
    weekday_price:float
    weekend_price:float

@dataclass
class Booking:
    booking_id:int
    member_id:int
    facility_id:int
    date:str
    start_time:str
    status:str

active_bookings=[]

def validate_booking_limit(member_id:int,active_bookings:list):
    count=0
    for i in active_bookings:
        if i.member_id==member_id and i.status=="confirmed":
            count+=1

    if count>=3:
        return False
    return True

def save_booking(booking:Booking):
    active_bookings.append(booking)
    return booking

@app.get("/")
def home():
    return {"status": "ok"}

@app.get("/facilities")
def get_facilities():
    facilities=[{"id":1,"name": "Badminton Court 1"},{ "id":2,"name": "Badminton Court 2"}, {"id":3, "name": "Tennis Court"}]
    return facilities

@app.get("/slots")
def get_slots(facility_id:int, date:str):
    return {"facility_id": facility_id, "date":date, "slots":["06:00-07:00", "07:00-08:00","08:00-09:00","09:00-10:00"]}

next_booking_id=1
@app.post("/bookings")
def create_booking(member_id:int, facility_id:int, date:str, start_time:str):
    global next_booking_id
    if not validate_booking_limit(member_id,active_bookings):
        raise HTTPException(status_code=400, detail="Member cannot have more than 3 active bookings")

    booking=Booking(
        booking_id=next_booking_id,
        member_id=member_id,
        facility_id=facility_id,
        date=date,
        start_time=start_time,
        status="confirmed"
    )
    next_booking_id+=1
    save_booking(booking)

    return {"message": "Booking created successfully", "booking_id": booking.booking_id}

@app.get("/bookings")
def get_bookings(member_id:int):
    return {"member_id":member_id, "bookings":[]}
