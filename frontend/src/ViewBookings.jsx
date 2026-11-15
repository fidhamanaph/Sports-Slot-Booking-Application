import { useState } from "react";

function ViewBookings() {
  const [memberId, setMemberId] = useState("");
  const [bookings, setBookings] = useState([]);
  const [message, setMessage] = useState("");

  const fetchBookings = async () => {
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/bookings?member_id=${memberId}`
      );

      const data = await response.json();

      if (response.ok) {
        setBookings(data);
        setMessage(data.length === 0 ? "No bookings found." : "");
      } else {
        setMessage(data.detail || "Could not fetch bookings.");
      }
    } catch (error) {
      setMessage("Could not connect to the backend.");
    }
  };

  return (
    <div>
      <h2>View My Bookings</h2>

      <label>Enter Member ID:</label>
      <input
        type="number"
        value={memberId}
        onChange={(e) => setMemberId(e.target.value)}
      />

      <button onClick={fetchBookings} disabled={!memberId}>
        View Bookings
      </button>

      <p>{message}</p>

      {bookings.map((booking) => (
        <div key={booking.booking_id}>
          <p>Booking ID: {booking.booking_id}</p>
          <p>Facility ID: {booking.facility_id}</p>
          <p>Date: {booking.booking_date}</p>
          <p>Time: {booking.start_time}</p>
          <hr />
        </div>
      ))}
    </div>
  );
}

export default ViewBookings;