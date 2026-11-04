from fastapi import FastAPI,HTTPException,Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from dataclasses import dataclass
from database import get_db_connection
from datetime import time,datetime,timedelta
import logging
from psycopg2 import IntegrityError
from fastapi.middleware.cors import CORSMiddleware

app=FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Invalid request: {request.url} | Errors: {exc.errors()}")

    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )

logging.basicConfig(level=logging.INFO)
logger=logging.getLogger(__name__)

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
    connection=get_db_connection()
    cursor=connection.cursor()
    cursor.execute("select * from facilities")
    facilities=cursor.fetchall()
    cursor.close()

    x=[]
    for i in facilities:
        x.append({"id":i[0],"name":i[1],"weekday_price":i[2],"weekend_price":i[3]})
    return x

@app.get("/slots")
def get_slots(facility_id:int, date:str):
    booking_date = datetime.strptime(date, "%Y-%m-%d").date()

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT start_time
        FROM bookings
        WHERE facility_id = %s AND booking_date = %s
        """,
        (facility_id, booking_date)
    )

    booked_times = {row[0] for row in cursor.fetchall()}

    slots = []

    for hour in range(6, 22):
        start = time(hour, 0)
        end = f"{hour + 1:02d}:00"

        slots.append({
            "start_time": f"{hour:02d}:00",
            "end_time": end,
            "available": start not in booked_times
        })

    cursor.close()
    connection.close()

    return {
        "facility_id": facility_id,
        "date": date,
        "slots": slots
    }

next_booking_id=1
@app.post("/bookings")
def create_booking(member_id: int, facility_id: int, date: str, start_time: str):
    logger.info(
        f"Booking request: member={member_id}, facility={facility_id}, "
        f"date={date}, time={start_time}"
    )
    booking_date = datetime.strptime(date, "%Y-%m-%d").date()
    if booking_date > datetime.now().date() + timedelta(days=7):
        raise HTTPException(status_code=400, detail="Bookings can only be made 7 days in advance")
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, member_id, facility_id, booking_date, start_time
        FROM bookings
        WHERE booking_date >= CURRENT_DATE
    """)

    rows = cursor.fetchall()

    active_bookings = [
        Booking(row[0], row[1], row[2], str(row[3]), str(row[4]), "confirmed")
        for row in rows
    ]

    if not validate_booking_limit(member_id, active_bookings):
        logger.warning(f"Booking rejected: member {member_id} already has 3 bookings")
        cursor.close()
        connection.close()
        raise HTTPException(status_code=400, detail="Maximum 3 bookings allowed")

    try:
        cursor.execute("""
            INSERT INTO bookings (member_id, facility_id, booking_date, start_time)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (member_id, facility_id, date, start_time))

        booking_id = cursor.fetchone()[0]
        connection.commit()
        logging.info(f"Booking created successfully: booking_id={booking_id}")
    except IntegrityError as e:
        connection.rollback()
        logger.exception("Database integrity error: %s", e)
        raise HTTPException(
            status_code=400,
            detail="Database error. Check backend terminal."
        )
        
    cursor.close()
    connection.close()

    return {
        "message": "Booking created successfully",
        "booking": Booking(booking_id, member_id, facility_id, date, start_time, "confirmed")
    }

@app.get("/bookings")
def get_bookings(member_id:int):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            member_id,
            facility_id,
            booking_date,
            start_time,
            created_at
        FROM bookings
        WHERE member_id = %s
        ORDER BY booking_date, start_time
    """,(member_id,))

    bookings = cursor.fetchall()

    cursor.close()
    connection.close()

    return [
        {
            "booking_id": row[0],
            "member_id": row[1],
            "facility_id": row[2],
            "booking_date": row[3],
            "start_time": row[4],
            "created_at": row[5]
        }
        for row in bookings
    ]
