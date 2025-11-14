import React, { useEffect, useState } from "react";
import axios from "axios";

const StudentTimetable = ({ studentId }) => {
  const [timetableData, setTimetableData] = useState({}); // Transformed data for display
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
  const periods = [1, 2, 3, 4, 5, 6];

  useEffect(() => {
    const fetchStudentTimetable = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await axios.get(`http://localhost:5000/api/timetable/student/${studentId}`);
        const rawTimetable = res.data;

        // Transform the raw data into a more display-friendly format
        const transformedData = {};
        rawTimetable.forEach(entry => {
          if (!transformedData[entry.day_of_week]) {
            transformedData[entry.day_of_week] = {};
          }
          transformedData[entry.day_of_week][entry.period] = entry.subject_code;
        });
        setTimetableData(transformedData);
      } catch (err) {
        console.error("Error fetching student timetable:", err);
        setError("Failed to load timetable. Please try again later.");
      } finally {
        setLoading(false);
      }
    };

    if (studentId) { // Only fetch if studentId is available
      fetchStudentTimetable();
    }
  }, [studentId]);

  if (loading) {
    return <div style={{ padding: "20px" }}><h3>Loading timetable...</h3></div>;
  }

  if (error) {
    return <div style={{ padding: "20px", color: "red" }}><h3>{error}</h3></div>;
  }

  if (Object.keys(timetableData).length === 0) {
    return <div style={{ padding: "20px" }}><h3>No timetable available for your class yet.</h3></div>;
  }

  return (
    <div style={{ padding: "20px" }}>
      <h2>My Timetable</h2>
      <table border="1" cellPadding="6" style={{ width: '100%', borderCollapse: 'collapse', marginTop: '20px' }}>
        <thead>
          <tr>
            <th style={tableHeaderStyle}>Day</th>
            {periods.map((p) => (
              <th key={p} style={tableHeaderStyle}>Period {p}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {days.map((day) => (
            <tr key={day}>
              <td style={tableCellStyle}>{day}</td>
              {periods.map((p) => (
                <td key={p} style={tableCellStyle}>
                  {timetableData[day]?.[p] || "-"} {/* Display subject or "-" if empty */}
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
    backgroundColor: '#3498db',
    color: 'white',
    padding: '10px',
    textAlign: 'center',
    border: '1px solid #ccc'
};

const tableCellStyle = {
    padding: '10px',
    textAlign: 'center',
    border: '1px solid #eee'
};


export default StudentTimetable;