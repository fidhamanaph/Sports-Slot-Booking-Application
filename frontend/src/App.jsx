import { useState } from "react";
import ViewSlots from "./ViewSlots";

function App() {
  const [memberId, setMemberId] = useState("");
  const [facilityId, setFacilityId] = useState("");
  const [date, setDate] = useState("");
  const [startTime, setStartTime] = useState("");
  const [message, setMessage] = useState("");

  const handleBooking = async () => {
    if (!memberId || !facilityId || !date || !startTime) {
      setMessage("Please fill in all fields!");
      return;
    }
    try {
      const params = new URLSearchParams({
        member_id: memberId,
        facility_id: facilityId,
        date: date,
        start_time: startTime,
      });

      const response = await fetch(
        `http://127.0.0.1:8000/bookings?${params}`,
        {
          method: "POST",
        }
      );

      const data = await response.json();

      if (response.ok) {
        setMessage(data.message);
      } else {
        setMessage(data.detail);
      }
    } catch (error) {
      setMessage("Could not connect to the backend!");
    }
  };

  return (
    <div>
      <h1>Sports Slot Booking</h1>
      <h2>Book a Facility</h2>

      <label>Member ID:</label>
      <input
        type="number"
        value={memberId}
        onChange={(e) => setMemberId(e.target.value)}
      />

      <br /><br />

      <label>Choose Facility:</label>
      <select
        value={facilityId}
        onChange={(e) => setFacilityId(e.target.value)}
      >
        <option value="">Select a facility</option>
        <option value="1">Badminton Court 1</option>
        <option value="2">Badminton Court 2</option>
        <option value="3">Tennis Court</option>
      </select>

      <br /><br />

      <label>Choose Date:</label>
      <input
        type="date"
        value={date}
        onChange={(e) => setDate(e.target.value)}
      />

      <br /><br />

      <label>Choose Time:</label>
      <select
        value={startTime}
        onChange={(e) => setStartTime(e.target.value)}
      >
        <option value="">Select a time slot</option>

        {Array.from({ length: 16 }, (_, i) => {
          const hour = i + 6;
          const time = `${String(hour).padStart(2, "0")}:00`;

          return (
            <option key={time} value={time}>
              {time}
            </option>
          );
        })}
      </select>

      <br /><br />

      <button
        onClick={handleBooking}
        disabled={!memberId || !facilityId || !date || !startTime}
      >
        Book Slot
      </button>

      <p>{message}</p>
       <ViewSlots />
    </div>
  );
}

export default App;