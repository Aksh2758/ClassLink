import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom"; // Import useNavigate
import axios from "axios";
import FacultyNavBar from "./Navbar";
import FacultyTimetable from './timetable';
import NotesUpload from './notes'; // Assuming you'll create these
// import FacultyAttendance from './attendance'; // Assuming you'll create these
import FacultyIAMarks from './IAMarks'; // Assuming you'll create these
import FacultyCirculars from './Circular'; // Assuming you'll create these
import FacultyProfile from './Profile'; // Assuming you'll create these
import AttendanceForm from "./AttendanceForm";

const FacultyDashboard = () => {
    const [faculty, setFaculty] = useState(null); // Renamed to 'faculty' for consistency
    const [selectedModule, setSelectedModule] = useState(null); // New state to track selected module
    const token = localStorage.getItem("token");
    const navigate = useNavigate(); // Initialize useNavigate

    useEffect(() => {
        console.log("Token from localStorage:", token);
        const fetchDetails = async () => {
            if (!token) {
                console.error("No token found. Redirect to login.");
                navigate('/login'); // Redirect to login if no token
                return;
            }

            try {
                const res = await axios.get("http://127.0.0.1:5000/api/faculty/details", {
                    headers: { Authorization: `Bearer ${token}` },
                });
                console.log("Fetched Faculty data:", res.data);
                setFaculty(res.data.faculty);
            } catch (err) {
                if (err.response) {
                    console.error("Backend error:", err.response.status, err.response.data);
                    // You might want to display this error to the user
                    if (err.response.status === 401) { // e.g., token expired or invalid
                        localStorage.removeItem("token");
                        navigate('/'); // Go back to login
                    }
                } else {
                    console.error("Network error:", err);
                }
            }
        };

        fetchDetails();
    }, [token, navigate]); // Add navigate to dependency array

    if (!faculty) {
        return <div style={{ padding: "20px" }}><h3>Loading faculty details...</h3></div>;
    }

    const renderModule = () => {
        switch (selectedModule) {
            case 'timetable':
                return <FacultyTimetable facultyId={faculty.faculty_id} />; 
            case 'notes':         
                return <NotesUpload FacultyId={faculty.faculty_id} />;
            case 'attendance':
                return <AttendanceForm />;
            case 'internal-marks':
                return <FacultyIAMarks facultyId={faculty.faculty_id} />;
            case 'circulars':
                return <FacultyCirculars />;
            case 'profile':
                return <FacultyProfile facultyId={faculty.faculty_id} />;
            default:
                return (
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', marginTop: '30px' }}>
                        <DashboardCard title="Timetable" description="Manage class schedules." onClick={() => setSelectedModule('timetable')} />
                        <DashboardCard title="Notes" description="Upload and manage study materials." onClick={() => setSelectedModule('notes')} />
                        <DashboardCard title="Attendance" description="Record and view student attendance." onClick={() => setSelectedModule('attendance')} />
                        <DashboardCard title="Internal Marks" description="Enter and update internal assessment scores." onClick={() => setSelectedModule('internal-marks')} />
                        <DashboardCard title="Circulars" description="Send announcements to students." onClick={() => setSelectedModule('circulars')} />
                        <DashboardCard title="Profile" description="View and update your personal details." onClick={() => setSelectedModule('profile')} />
                    </div>
                );
        }
    };

    return (
        <div style={{ padding: "20px" }}>
            <FacultyNavBar facultyID={faculty.faculty_id} facultyName={faculty.name} />
            {selectedModule && (
                <button
                    onClick={() => setSelectedModule(null)}
                    style={{ marginBottom: '20px', padding: '10px 20px', backgroundColor: '#f44336', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }}
                >
                    Back to Dashboard
                </button>
            )}
            {renderModule()}
        </div>
    );
};

// Modified DashboardCard to take an onClick prop instead of a link
const DashboardCard = ({ title, description, onClick }) => (
    <div style={cardStyle} onClick={onClick}>
        <h3>{title}</h3>
        <p>{description}</p>
        <button style={cardLinkStyle}>Go to {title}</button> {/* Changed Link to button */}
    </div>
);

const cardStyle = {
    backgroundColor: '#e0eaf0',
    padding: '20px',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    textAlign: 'center',
    cursor: 'pointer', // Make it look clickable
    transition: 'transform 0.2s ease-in-out', // Add a subtle hover effect
    '&:hover': {
        transform: 'scale(1.03)',
    }
};

const cardLinkStyle = {
    display: 'inline-block',
    marginTop: '15px',
    padding: '8px 15px',
    backgroundColor: '#3498db',
    color: 'white',
    textDecoration: 'none',
    borderRadius: '4px',
    border: 'none', // Added border: none for consistency
    cursor: 'pointer',
    transition: 'background-color 0.3s ease',
};

export default FacultyDashboard;