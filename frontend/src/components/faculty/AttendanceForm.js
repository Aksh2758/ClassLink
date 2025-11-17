import { useState, useEffect } from "react";
import axios from "axios";
import StudentList from "./StudentList";
const getAuthToken = () => localStorage.getItem("token");

export default function AttendanceForm() {
  const [semester, setSemester] = useState("");
  const [dept_code, setDept_code] = useState("");
  const [section, setSection] = useState("");
  const [subject_code, setSubject_code] = useState(""); // State for subject code
  const [subjects, setSubjects] = useState([]); // New state to store fetched subjects

  const [students, setStudents] = useState([]);

  useEffect(() => {
    const fetchSubjects = async () => {
      if (!dept_code || !semester) {
        setSubjects([]); // Clear subjects if department or semester is not selected
        return;
      }
      try {
        const token = getAuthToken();
        const res = await axios.get(`http://localhost:5000/api/subjects/by-dept-semester`, { // Updated API path example
          params: { dept_code, semester },
          headers: {
            Authorization: `Bearer ${token}` // IMPORTANT: Add JWT token
          }
        });
        // Assuming response has a 'subjects' key, and each subject has 'subject_code' and 'subject_name'
        setSubjects(res.data.subjects || []);
      } catch (err) {
        console.error("Failed to fetch subjects:", err.response ? err.response.data : err.message);
        setSubjects([]);
      }
    };
    fetchSubjects();
  }, [dept_code, semester]);


  const fetchStudents = async () => {
    if (!semester || !dept_code || !section) {
      alert("Please select Semester, Department, and Section.");
      return;
    }

    try {
      const token = getAuthToken();
      const res = await axios.get("http://localhost:5000/api/attendance/class/students", {
        params: { semester, dept_code, section },
        headers: {
          Authorization: `Bearer ${token}` // IMPORTANT: Add JWT token
        }
      });
      // Assuming 'students' is the key in the response data and it contains student_id, name, usn
      setStudents(res.data.students.map(s => ({ ...s, status: "P" }))); // default P
    } catch (err) {
      console.error("Failed to fetch students:", err.response ? err.response.data : err.message);
      alert("Failed to fetch students. Check console for details.");
    }
  };

  const submitAttendance = async () => {
    if (!subject_code || students.length === 0) { // --- MODIFIED: Removed periodNumber check ---
      alert("Please select Subject and fetch students first.");
      return;
    }

    const payload = {
      date: new Date().toISOString().split("T")[0],
      dept_code,
      semester: parseInt(semester),
      subject_code, // Use subject_code, as agreed
      section,
      attendance_list: students.map(s => ({
        student_id: s.student_id,
        status: s.status === "P" ? "present" : "absent"
      }))
    };

    try {
      const token = getAuthToken();
      await axios.post("http://localhost:5000/api/attendance/", payload, {
        headers: {
          'Authorization': `Bearer ${token}` // IMPORTANT: Add JWT token
        }
      });
      alert("Attendance Saved!");
      setStudents([]); 
    } catch (err) {
      console.error("Failed to submit attendance:", err.response ? err.response.data : err.message);
      alert("Failed to submit attendance. Check console for details.");
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>Mark Attendance</h2>

      <div style={{ display: "flex", gap: 10, marginBottom: 20 }}>
        <select value={semester} onChange={e => {
          setSemester(e.target.value);
          setSubject_code(""); // Reset subject selection when semester changes
        }}>
          <option value="">Semester</option>
          <option value="1">1</option>
          <option value="2">2</option>
          <option value="3">3</option>
          <option value="4">4</option>
          <option value="5">5</option>
          <option value="6">6</option>
          <option value="7">7</option>
          <option value="8">8</option>
        </select>

        <select value={dept_code} onChange={e => {
          setDept_code(e.target.value);
          setSubject_code(""); // Reset subject selection when department changes
        }}>
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
        </select>

        {/* --- MODIFIED: Dynamically load subjects --- */}
        <select value={subject_code} onChange={e => setSubject_code(e.target.value)} disabled={!dept_code || !semester}>
          <option value="">Subject Code</option>
          {subjects.map(sub => (
            <option key={sub.subject_code} value={sub.subject_code}>
              {sub.subject_name} ({sub.subject_code}) {/* Display both name and code */}
            </option>
          ))}
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