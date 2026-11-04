import { useState } from "react";

function ViewSlots() {
  const [facilityId, setFacilityId] = useState("");
  const [date, setDate] = useState("");
  const [slots, setSlots] = useState([]);
  const [message, setMessage] = useState("");

  const fetchSlots = async () => {
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/slots?facility_id=${facilityId}&date=${date}`
      );

      const data = await response.json();

      if (response.ok) {
        setSlots(data.slots);
        setMessage("");
      } else {
        setMessage(data.detail || "Could not fetch slots");
      }
    } catch (error) {
      setMessage("Could not connect to backend");
    }
  };

  return (
    <div>
      <h2>View Available Slots</h2>

      <label>Choose Facility:</label>
      <select
        value={facilityId}
        onChange={(e) => setFacilityId(e.target.value)}
      >
        <option value="">Select facility</option>
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

      <button
        onClick={fetchSlots}
        disabled={!facilityId || !date}
      >
        Check Availability
      </button>

      <p>{message}</p>

      {slots.map((slot) => (
        <div key={slot.start_time}>
          {slot.start_time} - {slot.end_time}
          {" : "}
          {slot.available ? "Available" : "Booked"}
        </div>
      ))}
    </div>
  );
}

export default ViewSlots;