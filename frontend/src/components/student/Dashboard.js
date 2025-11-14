import React, { useEffect, useState } from "react";
import axios from "axios";
import StudentTimetable from "./StudentTimetable";

const StudentDashboard = () => {
  const [student, setStudent] = useState(null);
  const token = localStorage.getItem("token");

  useEffect(() => {
    console.log("Token from localStorage:", token); // debug log

    const fetchDetails = async () => {
      if (!token) {
        console.error("No token found. Redirect to login.");
        return;
      }

      try {
        const res = await axios.get("http://127.0.0.1:5000/api/student/details", {
          headers: { Authorization: `Bearer ${token}` },
        });
        console.log("Fetched student data:", res.data);
        setStudent(res.data.student);
      } catch (err) {
        if (err.response) {
          console.error("Backend error:", err.response.status, err.response.data);
        } else {
          console.error("Network error:", err);
        }
      }
    };

    fetchDetails();
  }, [token]);

  if (!student) return <h3>Loading...</h3>;

  return (
    <div style={{ padding: "20px" }}>
      <h1>Welcome, {student.name}</h1>
      <p><strong>USN:</strong> {student.usn}</p>
      <p><strong>Email:</strong> {student.email}</p>
      <button>Profile</button>
      <StudentTimetable studentId={student.usn}/>
    </div>
  );
};

export default StudentDashboard;
