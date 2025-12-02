import React, { useState, useEffect } from "react";
import axios from "axios";
import { Link } from "react-router-dom";
import { HiSpeakerphone } from "react-icons/hi";
import { FaArrowRight } from "react-icons/fa";

const StudentCirculars = () => {
    const [circulars, setCirculars] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const API_BASE_URL = "http://localhost:5000/api/circulars";

    useEffect(() => {
        fetchMyCirculars();
    }, []);

    const fetchMyCirculars = async () => {
        try {
            const token = localStorage.getItem("token");
            // Using the root endpoint which automatically filters for the student
            const response = await axios.get(`${API_BASE_URL}/`, {
                headers: { Authorization: `Bearer ${token}` },
            });

            if (response.data.success) {
                setCirculars(response.data.circulars);
            } else {
                setError("Failed to fetch circulars.");
            }
        } catch (err) {
            console.error(err);
            setError("Error loading announcements.");
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div style={styles.loading}>Loading announcements...</div>;

    return (
        <div style={styles.container}>
            <div style={styles.headerContainer}>
                <h2 style={styles.mainTitle}>Important Announcements</h2>
                <p style={styles.subTitle}>Stay updated with the latest news from your department and college.</p>
            </div>

            {error && <div style={styles.errorMsg}>{error}</div>}

            <div style={styles.listContainer}>
                {circulars.length === 0 ? (
                    <div style={styles.emptyState}>No announcements available at the moment.</div>
                ) : (
                    circulars.map((circ) => (
                        <Link 
                            to={`/circulars/${circ.circular_id}`} 
                            key={circ.circular_id} 
                            style={styles.cardLink}
                        >
                            <div style={styles.card}>
                                <div style={styles.iconBox}>
                                    <HiSpeakerphone size={24} color="#fff" />
                                </div>
                                <div style={styles.contentBox}>
                                    <h3 style={styles.cardTitle}>{circ.title}</h3>
                                    <div style={styles.cardMeta}>
                                        <span>
                                            {new Date(circ.posted_at).toLocaleDateString(undefined, {
                                                month: 'short', day: 'numeric', year: 'numeric'
                                            })}
                                        </span>
                                        <span style={styles.dot}>•</span>
                                        <span>{circ.dept_name || "General"}</span>
                                    </div>
                                </div>
                                <div style={styles.arrowBox}>
                                    <FaArrowRight color="#bbb" />
                                </div>
                            </div>
                        </Link>
                    ))
                )}
            </div>
        </div>
    );
};

// --- CSS-in-JS Styles ---
const styles = {
    container: {
        padding: "40px 20px",
        maxWidth: "800px",
        margin: "0 auto",
        fontFamily: "'Inter', sans-serif",
    },
    loading: {
        textAlign: "center",
        padding: "50px",
        color: "#666",
        fontSize: "18px"
    },
    headerContainer: {
        marginBottom: "30px",
        textAlign: "center"
    },
    mainTitle: {
        fontSize: "28px",
        color: "#1e293b",
        marginBottom: "10px",
        fontWeight: "700"
    },
    subTitle: {
        fontSize: "16px",
        color: "#64748b"
    },
    errorMsg: {
        backgroundColor: "#fee2e2",
        color: "#991b1b",
        padding: "15px",
        borderRadius: "8px",
        marginBottom: "20px",
        textAlign: "center"
    },
    listContainer: {
        display: "flex",
        flexDirection: "column",
        gap: "15px"
    },
    cardLink: {
        textDecoration: "none",
        color: "inherit",
        display: "block"
    },
    card: {
        backgroundColor: "#fff",
        borderRadius: "12px",
        padding: "20px",
        display: "flex",
        alignItems: "center",
        boxShadow: "0 2px 10px rgba(0,0,0,0.03)",
        border: "1px solid #f1f5f9",
        transition: "transform 0.2s, box-shadow 0.2s",
        cursor: "pointer",
        ':hover': { // Note: Inline styles don't support pseudo-classes. 
                    // To get hover effects, you'd typically use CSS classes or a library like styled-components.
                    // Functionally, this looks clean without hover states too.
        }
    },
    iconBox: {
        width: "50px",
        height: "50px",
        borderRadius: "50%",
        backgroundColor: "#3b82f6", // Blue
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        marginRight: "20px",
        flexShrink: 0
    },
    contentBox: {
        flex: 1
    },
    cardTitle: {
        fontSize: "18px",
        fontWeight: "600",
        color: "#334155",
        margin: "0 0 5px 0"
    },
    cardMeta: {
        fontSize: "14px",
        color: "#94a3b8",
        display: "flex",
        alignItems: "center"
    },
    dot: {
        margin: "0 8px"
    },
    arrowBox: {
        marginLeft: "15px"
    },
    emptyState: {
        textAlign: "center",
        padding: "40px",
        color: "#94a3b8",
        backgroundColor: "#f8fafc",
        borderRadius: "12px",
        border: "1px dashed #cbd5e1"
    }
};

export default StudentCirculars;