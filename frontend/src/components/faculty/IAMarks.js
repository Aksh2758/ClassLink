import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './MarksEntryForm.css'; // Assuming you'll create this CSS file

const FacultyInternalMarks = () => {
    const getAuthToken = () => localStorage.getItem('token'); // Helper from your attendance module
    const [semester, setSemester] = useState('');
    const [dept_code, setDept_code] = useState('');
    const [section, setSection] = useState('');
    const [subject_code, setSubject_code] = useState('');

    // States for fetched data
    const [subjects, setSubjects] = useState([]); // To store subjects for the selected dept/semester
    const [students, setStudents] = useState([]); // Students with their marks

    // UI states
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [successMessage, setSuccessMessage] = useState(null);

    // Hardcoded IA types for now, ideally these could also come from an API if dynamic
    const iaTypes = ['IA1', 'IA2', 'IA3'];

    // Effect to fetch subjects when dept_code or semester changes
    useEffect(() => {
        const fetchSubjects = async () => {
            if (!dept_code || !semester) {
                setSubjects([]); // Clear subjects if department or semester is not selected
                setSubject_code(''); // Reset subject selection
                return;
            }
            try {
                const token = getAuthToken();
                if (!token) {
                    setError("Authentication token not found. Please log in.");
                    return;
                }
                const res = await axios.get(`http://localhost:5000/api/subjects/by-dept-semester`, { // Adjust API path if needed
                    params: { dept_code, semester },
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                });
                setSubjects(res.data.subjects || []);
                setSubject_code(''); // Reset selected subject when options change
            } catch (err) {
                console.error("Failed to fetch subjects:", err.response ? err.response.data : err.message);
                setError("Failed to fetch subjects. Please try again.");
                setSubjects([]);
            }
        };
        fetchSubjects();
    }, [dept_code, semester]);

    // Effect to fetch students and their marks when all filter criteria are selected
    useEffect(() => {
        const fetchStudentMarks = async () => {
            if (!dept_code || !semester || !section || !subject_code) {
                setStudents([]); // Clear students if any filter is missing
                return;
            }

            setLoading(true);
            setError(null);
            setSuccessMessage(null);

            const token = getAuthToken();
            if (!token) {
                setError("Authentication token not found. Please log in.");
                setLoading(false);
                return;
            }

            try {
                const response = await axios.get('http://localhost:5000/api/marks/class-scores', {
                    params: {
                        dept_code,
                        semester: parseInt(semester), // Ensure semester is an integer
                        section,
                        subject_code,
                    },
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (response.data.success) {
                    const studentsWithEditableMarks = response.data.students.map(student => {
                        const iaScores = { ...student.ia_scores };
                        iaTypes.forEach(ia => {
                            if (iaScores[ia] === undefined) {
                                iaScores[ia] = ''; // Initialize empty for editing
                            }
                        });
                        return { ...student, ia_scores: iaScores };
                    });
                    setStudents(studentsWithEditableMarks);
                } else {
                    setError(response.data.error || "Failed to fetch student marks.");
                    setStudents([]);
                }
            } catch (err) {
                console.error("Error fetching student marks:", err.response ? err.response.data : err.message);
                setError("Failed to load student data. Please try again.");
                setStudents([]);
            } finally {
                setLoading(false);
            }
        };
        fetchStudentMarks();
    }, [dept_code, semester, section, subject_code]); // Refetch when any of these change

    const handleMarkChange = (studentId, iaName, value) => {
        setStudents(prevStudents =>
            prevStudents.map(student =>
                student.student_id === studentId
                    ? {
                        ...student,
                        ia_scores: {
                            ...student.ia_scores,
                            [iaName]: value === '' ? '' : Math.max(0, Math.min(100, Number(value))), // Ensure 0-100
                        },
                    }
                    : student
            )
        );
    };

    const handleSubmitMarks = async () => {
        setLoading(true);
        setError(null);
        setSuccessMessage(null);

        const token = getAuthToken();
        if (!token) {
            setError("Authentication token not found. Please log in.");
            setLoading(false);
            return;
        }

        const marksEntries = [];
        students.forEach(student => {
            iaTypes.forEach(iaName => {
                const score = student.ia_scores[iaName];
                if (score !== '' && score !== undefined && score !== null) {
                    marksEntries.push({
                        student_id: student.student_id,
                        ia_name: iaName,
                        score: Number(score),
                    });
                }
            });
        });

        if (marksEntries.length === 0) {
            setSuccessMessage("No marks to update.");
            setLoading(false);
            return;
        }

        try {
            const response = await axios.post('http://localhost:5000/api/marks/update', {
                dept_code,
                semester: parseInt(semester),
                subject_code,
                marks_entries: marksEntries,
            }, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.data.success) {
                setSuccessMessage(response.data.message || "Marks updated successfully!");
                // Optionally refetch to confirm saved state (if marks can be updated by others)
                // fetchStudentMarks();
            } else {
                setError(response.data.error || "Failed to update marks.");
            }
        } catch (err) {
            console.error("Error updating marks:", err.response ? err.response.data : err.message);
            setError("Failed to update marks. Please check your input and try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="marks-entry-container">
            <h1 className="form-title">ENTER INTERNAL ASSESSMENT MARKS</h1>

            <div className="filters">
                <div className="filter-group">
                    <label htmlFor="semesterSelect">Semester</label>
                    <select
                        id="semesterSelect"
                        value={semester}
                        onChange={e => {
                            setSemester(e.target.value);
                            setSubject_code(''); // Reset subject when semester changes
                        }}
                        className="dropdown"
                    >
                        <option value="">Select Semester</option>
                        {[1, 2, 3, 4, 5, 6, 7, 8].map(s => (
                            <option key={s} value={s}>{s}</option>
                        ))}
                    </select>
                </div>

                <div className="filter-group">
                    <label htmlFor="deptCodeSelect">Department</label>
                    <select
                        id="deptCodeSelect"
                        value={dept_code}
                        onChange={e => {
                            setDept_code(e.target.value);
                            setSubject_code(''); // Reset subject when department changes
                        }}
                        className="dropdown"
                    >
                        <option value="">Select Department</option>
                        <option value="AIML">AIML</option>
                        <option value="CSE">CSE</option>
                        <option value="ISE">ISE</option>
                        <option value="ECE">ECE</option>
                    </select>
                </div>

                <div className="filter-group">
                    <label htmlFor="sectionSelect">Section</label>
                    <select
                        id="sectionSelect"
                        value={section}
                        onChange={e => setSection(e.target.value)}
                        className="dropdown"
                    >
                        <option value="">Select Section</option>
                        <option value="A">A</option>
                        <option value="B">B</option>
                    </select>
                </div>

                <div className="filter-group">
                    <label htmlFor="subjectCodeSelect">Subject</label>
                    <select
                        id="subjectCodeSelect"
                        value={subject_code}
                        onChange={e => setSubject_code(e.target.value)}
                        className="dropdown"
                        disabled={!dept_code || !semester} // Disable if dept or semester not selected
                    >
                        <option value="">Select Subject</option>
                        {subjects.map(sub => (
                            <option key={sub.subject_code} value={sub.subject_code}>
                                {sub.subject_name} ({sub.subject_code})
                            </option>
                        ))}
                    </select>
                </div>
            </div>

            {loading && <p className="message loading-message">Loading students and marks...</p>}
            {error && <p className="message error-message">{error}</p>}
            {successMessage && <p className="message success-message">{successMessage}</p>}

            {!loading && !error && students.length > 0 && (
                <div className="marks-table-container">
                    <table className="marks-table">
                        <thead>
                            <tr>
                                <th>Student Name</th>
                                <th>Roll No</th>
                                {iaTypes.map(ia => (
                                    <th key={ia}>{ia} Marks</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {students.map(student => (
                                <tr key={student.student_id}>
                                    <td>{student.student_name}</td>
                                    <td>{student.roll_no}</td>
                                    {iaTypes.map(ia => (
                                        <td key={`${student.student_id}-${ia}`}>
                                            <input
                                                type="number"
                                                min="0"
                                                max="100"
                                                value={student.ia_scores[ia]}
                                                onChange={(e) => handleMarkChange(student.student_id, ia, e.target.value)}
                                                className="marks-input"
                                            />
                                        </td>
                                    ))}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
            {!loading && !error && students.length === 0 && (
                <p className="no-data-message">
                    {!dept_code || !semester || !section || !subject_code
                        ? "Please select all filters (Semester, Department, Section, Subject) to view student marks."
                        : "No students found for the selected criteria, or no marks available."
                    }
                </p>
            )}

            <button
                onClick={handleSubmitMarks}
                className="update-button"
                disabled={loading || students.length === 0}
            >
                {loading ? 'Updating...' : 'UPDATE MARKS'}
            </button>
        </div>
    );
};

export default FacultyInternalMarks;