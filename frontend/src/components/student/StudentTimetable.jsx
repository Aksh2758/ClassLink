import React, { useEffect, useState } from "react";
import axios from "axios";

const StudentTimetable = () => {
  const [timetableData, setTimetableData] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
  const periods = [1, 2, 3, 4, 5, 6];

  useEffect(() => {
    const fetchStudentTimetable = async () => {
      setLoading(true);
      setError(null);

      try {
        const token = localStorage.getItem("token");

        const res = await axios.get(
          "http://localhost:5000/api/timetable/student",
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        const rawTimetable = res.data.timetable || [];

        const transformedData = {};
        rawTimetable.forEach(entry => {
          const day = entry.day_of_week;
          const period = entry.period_number;  // backend uses period_number
          const subject = entry.subject_code || entry.subject_name;

          if (!transformedData[day]) {
            transformedData[day] = {};
          }
          transformedData[day][period] = subject;
        });

        setTimetableData(transformedData);
      } catch (err) {
        console.error("Error fetching student timetable:", err);
        setError("Failed to load timetable. Please try again later.");
      } finally {
        setLoading(false);
      }
    };

    fetchStudentTimetable();
  }, []);

  if (loading) return <h3 style={{ padding: 20 }}>Loading timetable…</h3>;
  if (error) return <h3 style={{ padding: 20, color: "red" }}>{error}</h3>;

  return (
    <div style={{ padding: "20px" }}>
      <h2>My Timetable</h2>
      <table border="1" cellPadding="6" style={{ width: "100%", borderCollapse: "collapse", marginTop: 20 }}>
        <thead>
          <tr>
            <th style={tableHeaderStyle}>Day</th>
            {periods.map(p => (
              <th key={p} style={tableHeaderStyle}>Period {p}</th>
            ))}
          </tr>
        </thead>

        <tbody>
          {days.map(day => (
            <tr key={day}>
              <td style={tableCellStyle}>{day}</td>
              {periods.map(p => (
                <td key={p} style={tableCellStyle}>
                  {timetableData[day]?.[p] || "-"}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

const tableHeaderStyle = {
  backgroundColor: "#3498db",
  color: "#fff",
  padding: "10px",
  textAlign: "center",
  border: "1px solid #ccc",
};

const tableCellStyle = {
  padding: "10px",
  textAlign: "center",
  border: "1px solid #eee",
};

export default StudentTimetable;
