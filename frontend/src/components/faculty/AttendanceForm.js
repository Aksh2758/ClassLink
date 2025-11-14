import { useState } from "react";
import axios from "axios";
import StudentList from "./StudentList";

export default function AttendanceForm() {
  const [semester, setSemester] = useState("");
  const [department, setDepartment] = useState("");
  const [section, setSection] = useState("");
  const [subjectId, setSubjectId] = useState("");

  const [students, setStudents] = useState([]);

  const fetchStudents = async () => {
    if (!semester || !department || !section) {
      alert("Select all fields");
      return;
    }

    try {
      const res = await axios.get("http://localhost:5000/api/students", {
        params: { semester, department, section }
      });
      setStudents(res.data.map(s => ({ ...s, status: "P" }))); // default P
    } catch (err) {
      console.error(err);
      alert("Failed to fetch students");
    }
  };

  const submitAttendance = async () => {
    if (!subjectId) {
      alert("Select subject");
      return;
    }

    const payload = {
      date: new Date().toISOString().split("T")[0],
      semester,
      department,
      section,
      subject_id: subjectId,
      faculty_id: "FAC001", // replace with logged-in faculty ID
      attendance: students.map(s => ({
        student_user_id: s.user_id,
        status: s.status
      }))
    };

    try {
      await axios.post("http://localhost:5000/api/attendance", payload);
      alert("Attendance Saved!");
    } catch (err) {
      console.error(err);
      alert("Failed to submit attendance");
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>Mark Attendance</h2>

      <div style={{ display: "flex", gap: 10 }}>
        <select value={semester} onChange={e => setSemester(e.target.value)}>
          <option value="">Semester</option>
          <option value="1">1</option>
          <option value="2">2</option>
          <option value="3">3</option>
          <option value="4">4</option>
          <option value="5">5</option>
          {/* Add more */}
        </select>

        <select value={department} onChange={e => setDepartment(e.target.value)}>
          <option value="">Department</option>
          <option value="AIML">AIML</option>
          <option value="CSE">CSE</option>
          <option value="ISE">ISE</option>
          <option value="ECE">ECE</option>
        </select>

        <select value={section} onChange={e => setSection(e.target.value)}>
          <option value="">Section</option>
          <option value="A">A</option>
          <option value="B">B</option>
          <option value="C">C</option>
        </select>

        <select value={subjectId} onChange={e => setSubjectId(e.target.value)}>
          <option value="">Subject</option>
          <option value="1">Subject 1</option>
          <option value="2">Subject 2</option>
        </select>

        <button onClick={fetchStudents}>Fetch Students</button>
      </div>

      {students.length > 0 && (
        <>
          <StudentList students={students} setStudents={setStudents} />
          <button 
            onClick={submitAttendance}
            style={{ marginTop: 20, padding: "8px 16px" }}
          >
            Submit Attendance
          </button>
        </>
      )}
    </div>
  );
}
