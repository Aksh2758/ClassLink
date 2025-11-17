import React, { useState, useEffect, useCallback } from "react";
import axios from "axios";

const getAuthToken = () => localStorage.getItem("token");

// (Styles component is omitted for brevity, assume it's included as in the original)

const FacultyTimetable = ({ facultyId }) => { // facultyId here is the ID of the CURRENTLY LOGGED-IN faculty
  const effectiveFacultyId = parseInt(facultyId, 10);
  if (isNaN(effectiveFacultyId)) {
    console.error("Invalid facultyId provided:", facultyId);
  }

  const [semester, setSemester] = useState("");
  const [departmentCode, setDepartmentCode] = useState("");
  const [section, setSection] = useState("");
  const [timetable, setTimetable] = useState({});
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const [loadingTimetable, setLoadingTimetable] = useState(false);

  const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
  const periods = [1, 2, 3, 4, 5, 6];

  const departments = ["AIML", "CSE", "ECE", "MECH"];
  const allSections = ["A", "B", "C"];

  const departmentHasSections = (deptCode) => {
    return ["CSE", "ECE"].includes(deptCode);
  };

  const fetchExistingTimetable = useCallback(async () => {
    setMessage("");
    setIsError(false);
    if (!semester || !departmentCode) {
      setTimetable({});
      return;
    }

    const requestSection = departmentHasSections(departmentCode) && section ? `/${section}` : "";

    setLoadingTimetable(true);
    try {
      // 1. UPDATED URL to match the backend route: /faculty/<int:semester>/<string:department_name>/<string:section>
      // We use departmentCode as department_name here.
      const url = `http://localhost:5000/api/timetable/faculty/${semester}/${departmentCode}${requestSection}`;
      console.log("Fetching timetable from URL:", url);
      const token = getAuthToken();
      if (!token) {
        throw new Error("Authentication token not found.");
      }

      const res = await axios.get(url, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      const fetchedEntries = res.data.timetable || [];

      const newTimetable = {};
      fetchedEntries.forEach(entry => {
        if (!newTimetable[entry.day_of_week]) {
          newTimetable[entry.day_of_week] = {};
        }
        newTimetable[entry.day_of_week][entry.period_number] = {
          subject_code: entry.subject_code,
          faculty_name: entry.faculty_name // This is the ASSIGNED faculty's name
        };
      });
      setTimetable(newTimetable);
      setIsError(false);
    } catch (err) {
      console.error("Error fetching existing timetable:", err);
      setIsError(true);
      if (err.response && err.response.status === 404) {
        setTimetable({});
        setMessage("No timetable found for this selection. You can create one.");
      } else if (err.response && err.response.status === 401) {
        setMessage("Unauthorized: Please log in again.");
      } else {
        setMessage("Failed to load existing timetable.");
        setTimetable({});
      }
    } finally {
      setLoadingTimetable(false);
    }
  }, [semester, departmentCode, section]);

  useEffect(() => {
    fetchExistingTimetable();
  }, [fetchExistingTimetable]);

  const handleInputChange = (day, period, value) => {
    setTimetable((prev) => ({
      ...prev,
      [day]: {
        ...prev[day],
        [period]: {
          // Preserve existing data like faculty_name if present
          ...prev?.[day]?.[period], 
          subject_code: value,
        },
      },
    }));
  };

  const handleSave = async () => {
    setMessage("");
    setIsError(false);

    if (!semester || !departmentCode) {
      setMessage("Please select semester and department code first before saving.");
      setIsError(true);
      return;
    }
    if (isNaN(effectiveFacultyId)) {
        setMessage("Faculty ID is invalid. Cannot save timetable. Please ensure you are logged in as a valid faculty member.");
        setIsError(true);
        return;
    }

    const token = getAuthToken();
    if (!token) {
      setMessage("Authentication token not found. Please log in.");
      setIsError(true);
      return;
    }

    const entries = [];
    for (const day of days) {
      for (const period of periods) {
        const subjectCode = timetable?.[day]?.[period]?.subject_code || "";

        // Only include entries that have a subject code
        if (subjectCode.trim()) {
            entries.push({
                day: day,
                period: period,
                subject_code: subjectCode.trim(),
                // 2. ADDED subject_name and moved faculty_id into the entry, as required by the backend
                subject_name: subjectCode.trim(), // Placeholder: Subject Name is set to be the same as subject_code
                faculty_id: effectiveFacultyId, // ASSUMPTION: The current user is assigning themselves
            });
        }
      }
    }
    
    // Check if there are any entries to save
    if (entries.length === 0) {
        setMessage("Timetable is empty. Nothing to save.");
        setIsError(true);
        return;
    }


    const payloadSection = departmentHasSections(departmentCode) && section ? section : ''; 

    const payloadToSend = {
      semester: parseInt(semester, 10),
      // 3. UPDATED KEY NAMES to match backend expectations
      department_name: departmentCode, // Department Name (e.g., "AIML")
      department_code: departmentCode, // Department Code (e.g., "AIML" - assuming code and name are the same in the select box)
      section: payloadSection,
      // faculty_id is NOT needed here, it's now in each entry
      entries: entries,
    };
    console.log("JSON Payload being sent to backend:", JSON.stringify(payloadToSend, null, 2));

    try {
      // 4. UPDATED URL to match the backend route: /api/timetable/faculty/save
      const res = await axios.post("http://localhost:5000/api/timetable/faculty/save", payloadToSend, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      setMessage(res.data.message || "Timetable saved successfully!");
      if (res.data.errors && res.data.errors.length > 0) {
        setIsError(true);
        setMessage(prev => `${prev}\nDetails: ${res.data.errors.join("; ")}`);
      }
    } catch (err) {
      console.error("Error saving timetable:", err);
      setIsError(true);
      if (err.response) {
        const errorMessage = err.response.data.error || err.response.statusText;
        let fullMessage = `Error: ${errorMessage}`;
        if (err.response.data.details) {
            fullMessage += `\nDetails: ${JSON.stringify(err.response.data.details)}`;
        } else if (err.response.data.errors) {
            fullMessage += `\nDetails: ${JSON.stringify(err.response.data.errors)}`;
        }
        setMessage(fullMessage);
      } else if (err.request) {
        setMessage("Error: No response from server. Is the backend running? (Check console for CORS issues)");
      } else {
        setMessage("Error: Could not send request. (Check console)");
      }
    }
  };

  // ... (rest of the component's JSX remains the same) ...
  return (
    <div style={containerStyle}>
      <h2 style={titleStyle}>CLASS TIMETABLE - EDIT/UPLOAD</h2>

      <div style={selectContainerStyle}>
        <select value={semester} onChange={(e) => setSemester(e.target.value)} style={selectButtonStyle}>
          <option value="">SELECT SEMESTER</option>
          {[1, 2, 3, 4, 5, 6, 7, 8].map((sem) => (
            <option key={sem} value={sem}>
              SEMESTER {sem}
            </option>
          ))}
        </select>

        <select value={departmentCode} onChange={(e) => { // Use departmentCode
          setDepartmentCode(e.target.value);
          if (!departmentHasSections(e.target.value)) { // Use departmentCode
            setSection("");
          }
        }} style={selectButtonStyle}>
          <option value="">SELECT DEPARTMENT</option>
          {departments.map((deptCode) => ( // Iterate with deptCode
            <option key={deptCode} value={deptCode}>
              {deptCode}
            </option>
          ))}
        </select>

        {departmentHasSections(departmentCode) && ( // Use departmentCode
          <select value={section} onChange={(e) => setSection(e.target.value)} style={selectButtonStyle}>
            <option value="">SELECT SECTION (Optional)</option>
            {allSections.map((sec) => (
              <option key={sec} value={sec}>
                SECTION {sec}
              </option>
            ))}
          </select>
        )}
      </div>

      {loadingTimetable && <p style={{ textAlign: 'center', color: '#555' }}>Loading existing timetable...</p>}
      
      {!loadingTimetable && (semester && departmentCode) ? ( // Use departmentCode
        <>
          <table style={tableStyle}>
            <thead>
              <tr>
                <th style={tableHeaderStyle}></th>
                {periods.map((p) => (
                  <th key={p} style={tableHeaderStyle}>PERIOD {p}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {days.map((day) => (
                <tr key={day}>
                  <td style={dayHeaderStyle}>{day.toUpperCase()}</td>
                  {periods.map((p) => (
                    <td key={p} style={cellStyle}>
                      <input
                        type="text"
                        placeholder="Sub Code"
                        // Display subject_code from the nested object
                        value={timetable?.[day]?.[p]?.subject_code || ""}
                        onChange={(e) => handleInputChange(day, p, e.target.value)}
                        style={inputStyle}
                      />
                      {/* Optionally display faculty name below the subject code */}
                      {timetable?.[day]?.[p]?.faculty_name && (
                        <div style={{ fontSize: '0.8em', color: '#666', marginTop: '3px' }}>
                          ({timetable[day][p].faculty_name})
                        </div>
                      )}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>

          <button onClick={handleSave} style={saveButtonStyle}>
            SAVE TIMETABLE
          </button>
        </>
      ) : (
        <p style={{ textAlign: 'center', color: '#555', marginTop: '30px' }}>Please select a Semester and Department Code to view or edit the timetable.</p>
      )}


      {message && (
        <p style={{ marginTop: "20px", color: isError ? "#e74c3c" : "#27ae60", textAlign: "center", whiteSpace: "pre-wrap" }}>
          {message}
        </p>
      )}
    </div>
  );
};

const containerStyle = {
  backgroundColor: '#f0f8ff', 
  borderRadius: '10px',
  padding: '30px',
  boxShadow: '0 4px 15px rgba(0, 0, 0, 0.1)',
  maxWidth: '900px',
  margin: '40px auto',
  fontFamily: 'Arial, sans-serif',
};

const titleStyle = {
  textAlign: 'center',
  color: '#2c3e50',
  marginBottom: '30px',
  fontSize: '28px',
  fontWeight: 'bold',
};

const selectContainerStyle = {
  display: 'flex',
  justifyContent: 'center',
  gap: '20px',
  marginBottom: '40px',
};

const selectButtonStyle = {
  padding: '12px 25px',
  backgroundColor: '#3498db',
  color: 'white',
  border: 'none',
  borderRadius: '5px',
  fontSize: '16px',
  cursor: 'pointer',
  fontWeight: 'bold',
  letterSpacing: '0.5px',
  appearance: 'none',
  backgroundImage: 'url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23ffffff%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%00-13-5.4H18.4c-6.5%200-12.3%203.2-16.1%208.1-3.8%204.9-4.9%2011-3.2%2017.3l138.6%20147.1c2.8%203%206.7%204.7%2010.7%204.7s7.9-1.7%2010.7-4.7l138.6-147.1c1.7-6.3.6-12.4-3.2-17.3z%22%2F%3E%3C%2Fsvg%3E")',
  backgroundRepeat: 'no-repeat',
  backgroundPosition: 'right 15px top 50%',
  backgroundSize: '12px auto',
  minWidth: '200px',
};

const tableStyle = {
  width: '100%',
  borderCollapse: 'separate',
  borderSpacing: '8px',
  backgroundColor: 'white',
  borderRadius: '10px',
  overflow: 'hidden',
};

const tableHeaderStyle = {
  backgroundColor: '#2980b9',
  color: 'white',
  padding: '15px 10px',
  textAlign: 'center',
  fontSize: '16px',
  fontWeight: 'bold',
  border: 'none',
};

const dayHeaderStyle = {
  backgroundColor: '#34495e',
  color: 'white',
  padding: '15px 10px',
  textAlign: 'center',
  fontSize: '16px',
  fontWeight: 'bold',
  whiteSpace: 'nowrap',
  borderRadius: '5px',
};

const cellStyle = {
  backgroundColor: '#ecf0f1',
  padding: '8px',
  textAlign: 'center',
  borderRadius: '5px',
};

const inputStyle = {
  width: '100%',
  padding: '8px',
  border: '1px solid #bdc3c7',
  borderRadius: '4px',
  fontSize: '14px',
  textAlign: 'center',
  boxSizing: 'border-box',
};

const saveButtonStyle = {
  display: 'block',
  width: '250px',
  margin: '40px auto 10px auto',
  padding: '15px 30px',
  backgroundColor: '#27ae60',
  color: 'white',
  border: 'none',
  borderRadius: '8px',
  fontSize: '18px',
  fontWeight: 'bold',
  cursor: 'pointer',
  transition: 'background-color 0.3s ease',
  '&:hover': {
    backgroundColor: '#2ecc71',
  },
};

export default FacultyTimetable;