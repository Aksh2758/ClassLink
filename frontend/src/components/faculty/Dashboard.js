import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

// Import Faculty-specific components (ensure these files exist)
import FacultyTimetable from "./timetable";
import NotesUpload from "./notes";
import AttendanceForm from "./AttendanceForm";
import FacultyIAMarks from "./IAMarks";
import FacultyCirculars from "./Circular";
import FacultyProfile from "./Profile";
import FacultyNavBar from "./Navbar"; // Assuming this is the Faculty-specific navigation bar

// --- Reusable Card Component (Copied from Student Dashboard) ---
// This component provides the clean white card, shadow, and hover effect.
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
            {/* Note: The icon prop here should be a string (like the emoji '🗓') 
               or a React component/element (e.g., <CalendarDays size={56} />) */}
            <div style={iconStyle}>{icon}</div>
            <h3 style={titleStyle}>{title}</h3>
            <p style={descriptionStyle}>{description}</p>
        </div>
    );
};
// --------------------------------------------------------------------------

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || "http://127.0.0.1:5000";

const FacultyDashboard = () => {
    const [faculty, setFaculty] = useState(null);
    const [selectedModule, setSelectedModule] = useState(null);
    const [loading, setLoading] = useState(true);

    // Removed 'message' state since the inline-style template doesn't use the Tailwind alert box

    const navigate = useNavigate();
    const token = localStorage.getItem("token");

    useEffect(() => {
        if (!token) {
            navigate("/login");
            return;
        }

        const fetchDetails = async () => {
            try {
                const res = await axios.get(
                    `${API_BASE_URL}/api/faculty/details`,
                    {
                        headers: { Authorization: `Bearer ${token}` },
                    }
                );
                setFaculty(res.data.faculty);
            } catch (err) {
                console.error("Error fetching faculty:", err);

                if (err.response?.status === 401) {
                    localStorage.removeItem("token");
                    navigate("/login");
                }
            } finally {
                setLoading(false);
            }
        };

        fetchDetails();
    }, [token, navigate]);

    if (loading || !faculty) {
        return (
            <div style={{ padding: "40px", textAlign: "center" }}>
                <h2>{loading ? "Loading your dashboard..." : "Error loading faculty details."}</h2>
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
                return <FacultyTimetable facultyId={faculty.faculty_id} />;
            case "notes":
                return <NotesUpload facultyId={faculty.faculty_id} />;
            case "attendance":
                return <AttendanceForm facultyId={faculty.faculty_id} />;
            case "internal-marks":
                return <FacultyIAMarks facultyId={faculty.faculty_id} />;
            case "circulars":
                return <FacultyCirculars facultyId={faculty.faculty_id} />;
            case "profile":
                return <FacultyProfile facultyId={faculty.faculty_id} />;

            default:
                return (
                    <div style={gridStyle}>
                        <DashboardCard
                            title="Timetable"
                            description="View your class schedule"
                            icon="🗓️" // Using emojis for visual consistency with the student template
                            onClick={() => setSelectedModule("timetable")}
                        />
                        <DashboardCard
                            title="Upload Notes"
                            description="Share study materials with students"
                            icon="📂"
                            onClick={() => setSelectedModule("notes")}
                        />
                        <DashboardCard
                            title="Attendance"
                            description="Mark student attendance"
                            icon="📝"
                            onClick={() => setSelectedModule("attendance")}
                        />
                        <DashboardCard
                            title="Internal Marks"
                            description="Enter student assessment scores"
                            icon="💯"
                            onClick={() => setSelectedModule("internal-marks")}
                        />
                        <DashboardCard
                            title="Circulars"
                            description="Post announcements & notices"
                            icon="📢"
                            onClick={() => setSelectedModule("circulars")}
                        />
                        <DashboardCard
                            title="Profile"
                            description="View and update your details"
                            icon="🧑‍🏫"
                            onClick={() => setSelectedModule("profile")}
                        />
                    </div>
                );
        }
    };

    // Style for the back button to handle hover effect (copied from student template)
    const backButtonBaseStyle = {
        marginBottom: "20px",
        padding: "12px 24px",
        backgroundColor: "#e74c3c", // Red color for consistency
        color: "white",
        border: "none",
        borderRadius: "8px",
        fontSize: "1rem",
        cursor: "pointer",
        boxShadow: "0 4px 10px rgba(231, 76, 60, 0.3)",
        transition: "all 0.3s"
    };
    
    // Inline style for the secondary background
    const secondaryBgStyle = {
        backgroundColor: "white", 
        borderRadius: "16px",
        boxShadow: "0 8px 25px rgba(0,0,0,0.1)",
        padding: "30px", // Added padding for module content
        minHeight: "70vh"
    };


    return (
        <div style={{ minHeight: "100vh", backgroundColor: "#f5f7fa" }}>
            {/* Navbar */}
            <FacultyNavBar
                facultyName={faculty.name}
                facultyID={faculty.faculty_id}
                onModuleSelect={setSelectedModule}
            />

            <div style={{ padding: "30px" }}>
                {/* Welcome Header */}
                {!selectedModule && (
                    <div style={{ marginBottom: "30px" }}>
                        
                    </div>
                )}

                {/* Back Button */}
                {selectedModule && (
                    <button
                        onClick={() => setSelectedModule(null)}
                        style={backButtonBaseStyle}
                        // Inline hover effects
                        onMouseOver={(e) => e.target.style.backgroundColor = "#c0392b"}
                        onMouseOut={(e) => e.target.style.backgroundColor = "#e74c3c"}
                    >
                        ← Back to Dashboard
                    </button>
                )}

                {/* Render Selected Module or Cards */}
                {selectedModule ? (
                    <div style={secondaryBgStyle}>
                        {renderModule()}
                    </div>
                ) : (
                    renderModule() // Renders the dashboard cards grid
                )}
            </div>
        </div>
    );
};

export default FacultyDashboard;