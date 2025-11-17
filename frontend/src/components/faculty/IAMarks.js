import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './MarksEntryForm.css'; // Assuming you'll create this CSS file

const FacultyInternalMarks = () => {
    const [selectedClass, setSelectedClass] = useState('XII-A');
    const [selectedSubject, setSelectedSubject] = useState('PHYSICS');
    const [students, setStudents] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [successMessage, setSuccessMessage] = useState(null);

    // Hardcoded mappings for demonstration based on your image and backend logic
    // In a real app, these would come from API calls (e.g., /api/dropdowns/classes, /api/dropdowns/subjects)
    const classOptions = [
        { label: 'XII-A', dept_code: 'CSE', semester: 6, section: 'A' },
        { label: 'XII-B', dept_code: 'CSE', semester: 6, section: 'B' },
        { label: 'XI-A', dept_code: 'CSE', semester: 5, section: 'A' },
    ];
    const subjectOptions = [
        { label: 'PHYSICS', subject_code: 'PH101' },
        { label: 'CHEMISTRY', subject_code: 'CH101' },
        { label: 'MATHS', subject_code: 'MA101' },
    ];
    const iaTypes = ['IA1', 'IA2', 'IA3']; // These should ideally also come from backend if dynamic

    const currentClassDetails = classOptions.find(opt => opt.label === selectedClass);
    const currentSubjectDetails = subjectOptions.find(opt => opt.label === selectedSubject);

    const fetchStudentMarks = async () => {
        if (!currentClassDetails || !currentSubjectDetails) {
            setError("Please select a valid class and subject.");
            return;
        }

        setLoading(true);
        setError(null);
        setSuccessMessage(null);

        const token = localStorage.getItem('token'); // Assuming JWT token is stored here
        if (!token) {
            setError("Authentication token not found. Please log in.");
            setLoading(false);
            return;
        }

        try {
            const response = await axios.get('http://localhost:5000/api/marks/class-scores', { // Adjust URL as needed
                params: {
                    dept_code: currentClassDetails.dept_code,
                    semester: currentClassDetails.semester,
                    section: currentClassDetails.section,
                    subject_code: currentSubjectDetails.subject_code,
                },
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            if (response.data.success) {
                // Initialize marks state for each student
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
            console.error("Error fetching student marks:", err);
            setError("Failed to load student data. Please try again.");
            setStudents([]);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchStudentMarks();
    }, [selectedClass, selectedSubject]); // Refetch when class or subject changes

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

        const token = localStorage.getItem('token');
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
            const response = await axios.post('http://localhost:5000/api/marks/update', { // Adjust URL
                dept_code: currentClassDetails.dept_code,
                semester: currentClassDetails.semester,
                subject_code: currentSubjectDetails.subject_code,
                marks_entries: marksEntries,
            }, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.data.success) {
                setSuccessMessage(response.data.message || "Marks updated successfully!");
                // Optionally refetch to confirm saved state
                // fetchStudentMarks();
            } else {
                setError(response.data.error || "Failed to update marks.");
            }
        } catch (err) {
            console.error("Error updating marks:", err.response ? err.response.data : err);
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
                    <label htmlFor="selectClass">Select Class</label>
                    <select
                        id="selectClass"
                        value={selectedClass}
                        onChange={(e) => setSelectedClass(e.target.value)}
                        className="dropdown"
                    >
                        {classOptions.map(option => (
                            <option key={option.label} value={option.label}>{option.label}</option>
                        ))}
                    </select>
                </div>
                <div className="filter-group">
                    <label htmlFor="selectSubject">Select Subject</label>
                    <select
                        id="selectSubject"
                        value={selectedSubject}
                        onChange={(e) => setSelectedSubject(e.target.value)}
                        className="dropdown"
                    >
                        {subjectOptions.map(option => (
                            <option key={option.label} value={option.label}>{option.label}</option>
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
                <p className="no-data-message">No students found for the selected class and subject, or no data available.</p>
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