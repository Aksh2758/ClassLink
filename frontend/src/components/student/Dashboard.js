import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

// Import your Student-specific components
import StudentTimetable from "./StudentTimetable";
import StudentProfile from "./Profile";
import StudentNotes from "./StudentNotes";
import StudentAttendance from "./attendance";
import CircularsSection from "./circular";
import InternalMarksPage from "./IAMark";
import StudentNavBar from "./StudentNavbar"; 

// --- Reusable Card Component (Defined inside the file for consolidation) ---
const DashboardCard = ({ title, description, icon, onClick }) => {
    // State for handling the hover effect style
    const [isHovered, setIsHovered] = useState(false);

    // Dynamic style based on hover state
    const cardStyle = {
        backgroundColor: "white",
        padding: "30px",
        borderRadius: "16px",
        boxShadow: isHovered 
            ? "0 15px 35px rgba(0,0,0,0.15)"
            : "0 8px 25px rgba(0,0,0,0.1)",
        textAlign: "center",
        cursor: "pointer",
        transition: "all 0.3s ease",
        border: "1px solid #e0e0e0",
        transform: isHovered ? "translateY(-10px)" : "translateY(0)"
    };

    const iconStyle = { fontSize: "3.5rem", marginBottom: "15px" };
    const titleStyle = { margin: "0 0 10px 0", color: "#2c3e50", fontSize: "1.4rem" };
    const descriptionStyle = { color: "#7f8c8d", margin: "0" };

    return (
        <div
            onClick={onClick}
            style={cardStyle}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
        >
            <div style={iconStyle}>{icon}</div>
            <h3 style={titleStyle}>{title}</h3>
            <p style={descriptionStyle}>{description}</p>
        </div>
    );
};
// --------------------------------------------------------------------------

// Use environment variable for API base URL (Defaulting to localhost if not set)
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || "http://127.0.0.1:5000";

const StudentDashboard = () => {
    const [student, setStudent] = useState(null);
    const [selectedModule, setSelectedModule] = useState(null);
    const token = localStorage.getItem("token");
    const navigate = useNavigate();

    useEffect(() => {
        if (!token) {
            navigate("/login");
            return;
        }

        const fetchDetails = async () => {
            try {
                // Use the environment variable for the API call
                const res = await axios.get(`${API_BASE_URL}/api/student/details`, {
                    headers: { Authorization: `Bearer ${token}` },
                });
                setStudent(res.data.student);
            } catch (err) {
                console.error("Error fetching student:", err);
                if (err.response?.status === 401) {
                    localStorage.removeItem("token");
                    navigate("/login");
                }
            }
        };

        fetchDetails();
    }, [token, navigate]);

    if (!student) {
        return (
            <div style={{ padding: "40px", textAlign: "center" }}>
                <h2>Loading your dashboard...</h2>
            </div>
        );
    }

    const renderModule = () => {
        const gridStyle = {
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '25px',
            marginTop: '40px'
        };

        switch (selectedModule) {
            case "timetable":
                return <StudentTimetable studentId={student.usn} />;
            case "notes":
                return <StudentNotes studentId={student.usn} />;
            case "attendance":
                return <StudentAttendance studentId={student.usn} />;
            case "circulars":
                return <CircularsSection />;
            case "profile":
                return <StudentProfile studentId={student.usn} />;
            case "iamarks":
                return <InternalMarksPage studentId={student.usn} />;

            default:
                return (
                    <div style={gridStyle}>
                        <DashboardCard
                            title="Timetable"
                            description="View your class schedule"
                            icon="🗓"
                            onClick={() => setSelectedModule("timetable")}
                        />
                        <DashboardCard
                            title="Study Notes"
                            description="Access uploaded notes & materials"
                            icon="📚"
                            onClick={() => setSelectedModule("notes")}
                        />
                        <DashboardCard
                            title="Attendance"
                            description="Check your attendance records"
                            icon="✅"
                            onClick={() => setSelectedModule("attendance")}
                        />
                        <DashboardCard
                            title="Circulars"
                            description="Latest announcements & notices"
                            icon="📢"
                            onClick={() => setSelectedModule("circulars")}
                        />
                        <DashboardCard
                            title="Profile"
                            description="View and update your details"
                            icon="👤"
                            onClick={() => setSelectedModule("profile")}
                        />
                        <DashboardCard
                            title="IA Marks"
                            description="View your internal assessment scores"
                            icon="📝"
                            onClick={() => setSelectedModule("iamarks")}
                        />
                    </div>
                );
        }
    };

    // Style for the back button to handle hover effect
    const backButtonBaseStyle = {
        marginBottom: "20px",
        padding: "12px 24px",
        backgroundColor: "#e74c3c",
        color: "white",
        border: "none",
        borderRadius: "8px",
        fontSize: "1rem",
        cursor: "pointer",
        boxShadow: "0 4px 10px rgba(231, 76, 60, 0.3)",
        transition: "all 0.3s"
    };

    return (
        <div style={{ minHeight: "100vh", backgroundColor: "#f5f7fa" }}>
            {/* Navbar */}
            <StudentNavBar
                studentName={student.name}
                studentUSN={student.usn}
                onModuleSelect={setSelectedModule}
            />

            <div style={{ padding: "30px" }}>
                {/* Welcome Header */}
                {!selectedModule && (
                    <div style={{ marginBottom: "30px" }}>
                        <h1 style={{ fontSize: "2.2rem", color: "#2c3e50" }}>
                            Welcome back, {student.name}!
                        </h1>
                        <p style={{ color: "#7f8c8d", fontSize: "1.1rem" }}>
                            USN: <strong>{student.usn}</strong> | Semester: {student.semester || "N/A"}
                        </p>
                    </div>
                )}

                {/* Back Button */}
                {selectedModule && (
                    <button
                        onClick={() => setSelectedModule(null)}
                        style={backButtonBaseStyle}
                        onMouseOver={(e) => e.target.style.backgroundColor = "#c0392b"}
                        onMouseOut={(e) => e.target.style.backgroundColor = "#e74c3c"}
                    >
                        ← Back to Dashboard
                    </button>
                )}

                {/* Render Selected Module or Cards */}
                {renderModule()}
            </div>
        </div>
    );
};

export default StudentDashboard;