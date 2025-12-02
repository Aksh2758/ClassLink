import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { FaCheckCircle, FaTimesCircle, FaChartPie, FaExclamationTriangle } from 'react-icons/fa';

const StudentAttendance = () => {
    const [attendanceData, setAttendanceData] = useState([]);
    const [overallStats, setOverallStats] = useState({ percentage: 0, totalClasses: 0, presentClasses: 0 });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const token = localStorage.getItem('token');

    useEffect(() => {
        fetchAttendance();
    }, []);

    const fetchAttendance = async () => {
        try {
            const response = await axios.get('http://127.0.0.1:5000/api/attendance/student/my-attendance', {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (response.data.success) {
                const data = response.data.attendance;
                setAttendanceData(data);
                calculateOverall(data);
            } else {
                setError("Failed to fetch attendance records.");
            }
        } catch (err) {
            console.error(err);
            setError("Error connecting to server.");
        } finally {
            setLoading(false);
        }
    };

    // --- MODIFIED CALCULATION LOGIC ---
    // Calculates the Average of Percentages (Sum of % / Count of Subjects)
    const calculateOverall = (data) => {
        if (!data || data.length === 0) return;

        let totalSessionsForDisplay = 0; // Just for the text stats
        let totalPresentForDisplay = 0;  // Just for the text stats
        
        let sumOfSubjectPercentages = 0; 
        let activeSubjectsCount = 0;

        data.forEach(sub => {
            const subTotal = Number(sub.total_sessions || 0);
            const subPresent = Number(sub.present_sessions || 0);

            // 1. Update text counters
            totalSessionsForDisplay += subTotal;
            totalPresentForDisplay += subPresent;

            // 2. Calculate percentage for THIS subject specifically
            if (subTotal > 0) {
                const subjectPercent = (subPresent / subTotal) * 100;
                sumOfSubjectPercentages += subjectPercent;
                activeSubjectsCount++;
            }
        });

        // 3. Final Calculation: Average of the percentages
        // Example: (100% + 50%) / 2 = 75%
        const finalPercentage = activeSubjectsCount > 0 
            ? (sumOfSubjectPercentages / activeSubjectsCount) 
            : 0;

        setOverallStats({
            percentage: parseFloat(finalPercentage.toFixed(2)),
            totalClasses: totalSessionsForDisplay,
            presentClasses: totalPresentForDisplay
        });
    };

    // Helper to determine color based on percentage
    const getStatusColor = (percentage) => {
        if (percentage >= 85) return '#2ecc71'; // Green (Safe)
        if (percentage >= 75) return '#f1c40f'; // Yellow (Warning)
        return '#e74c3c'; // Red (Danger)
    };

    if (loading) return <div style={styles.loading}>Loading Attendance Data...</div>;

    if (error) return <div style={styles.errorContainer}>{error}</div>;

    return (
        <div style={styles.container}>
            <h2 style={styles.pageTitle}>My Attendance</h2>

            {/* --- TOP SECTION: OVERALL SUMMARY --- */}
            <div style={styles.heroCard}>
                <div style={styles.heroLeft}>
                    <h3 style={styles.heroTitle}>Overall Attendance (Average)</h3>
                    <div style={styles.statRow}>
                        <span style={styles.statLabel}>Total Classes:</span>
                        <span style={styles.statValue}>{overallStats.totalClasses}</span>
                    </div>
                    <div style={styles.statRow}>
                        <span style={styles.statLabel}>Classes Attended:</span>
                        <span style={styles.statValue}>{overallStats.presentClasses}</span>
                    </div>
                    <div style={styles.statRow}>
                        <span style={styles.statLabel}>Classes Missed:</span>
                        <span style={styles.statValue}>{overallStats.totalClasses - overallStats.presentClasses}</span>
                    </div>
                </div>

                <div style={styles.heroRight}>
                    <div style={{...styles.circleOuter, borderColor: getStatusColor(overallStats.percentage)}}>
                        <div style={styles.circleInner}>
                            <span style={{...styles.percentageText, color: getStatusColor(overallStats.percentage)}}>
                                {overallStats.percentage}%
                            </span>
                        </div>
                    </div>
                    {overallStats.percentage < 75 && (
                        <div style={styles.warningBadge}>
                            <FaExclamationTriangle /> Low Attendance
                        </div>
                    )}
                </div>
            </div>

            {/* --- BOTTOM SECTION: SUBJECT WISE CARDS --- */}
            <h3 style={styles.sectionTitle}>Subject-wise Breakdown</h3>
            
            <div style={styles.grid}>
                {attendanceData.length > 0 ? (
                    attendanceData.map((subject, index) => {
                        const subTotal = Number(subject.total_sessions || 0);
                        const subPresent = Number(subject.present_sessions || 0);
                        
                        // Calculate percent per subject safely
                        let percentRaw = 0;
                        if(subTotal > 0) {
                            percentRaw = (subPresent / subTotal) * 100;
                        }
                        
                        const percentDisplay = percentRaw.toFixed(1);
                        const color = getStatusColor(percentRaw);

                        return (
                            <div key={index} style={styles.card}>
                                <div style={styles.cardHeader}>
                                    <div style={styles.subjectCode}>{subject.subject_code}</div>
                                    <div style={{...styles.percentBadge, backgroundColor: color}}>
                                        {percentDisplay}%
                                    </div>
                                </div>
                                
                                <h4 style={styles.subjectName}>{subject.subject_name}</h4>
                                <p style={styles.semester}>Semester: {subject.semester}</p>

                                {/* Progress Bar */}
                                <div style={styles.progressBarContainer}>
                                    <div style={{...styles.progressBarFill, width: `${Math.min(percentRaw, 100)}%`, backgroundColor: color}}></div>
                                </div>

                                <div style={styles.cardStats}>
                                    <div style={styles.miniStat}>
                                        <FaCheckCircle color="#2ecc71" style={{marginRight: '5px'}}/>
                                        <span>Present: <strong>{subPresent}</strong></span>
                                    </div>
                                    <div style={styles.miniStat}>
                                        <FaTimesCircle color="#e74c3c" style={{marginRight: '5px'}}/>
                                        <span>Absent: <strong>{subTotal - subPresent}</strong></span>
                                    </div>
                                    <div style={styles.miniStat}>
                                        <FaChartPie color="#3498db" style={{marginRight: '5px'}}/>
                                        <span>Total: <strong>{subTotal}</strong></span>
                                    </div>
                                </div>
                            </div>
                        );
                    })
                ) : (
                    <div style={styles.noData}>No attendance records found.</div>
                )}
            </div>
        </div>
    );
};

// --- CSS STYLES ---
const styles = {
    container: {
        padding: '30px',
        backgroundColor: '#f4f7f6',
        minHeight: '100vh',
        fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    },
    loading: {
        padding: '50px',
        textAlign: 'center',
        fontSize: '18px',
        color: '#666'
    },
    errorContainer: {
        padding: '20px',
        color: 'red',
        textAlign: 'center'
    },
    pageTitle: {
        color: '#2c3e50',
        marginBottom: '20px',
        fontSize: '24px',
        fontWeight: 'bold'
    },
    heroCard: {
        backgroundColor: 'white',
        borderRadius: '15px',
        padding: '30px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        boxShadow: '0 4px 15px rgba(0,0,0,0.05)',
        marginBottom: '40px',
        flexWrap: 'wrap',
        gap: '20px'
    },
    heroLeft: {
        flex: 1,
        minWidth: '250px'
    },
    heroTitle: {
        margin: '0 0 20px 0',
        color: '#34495e',
        fontSize: '20px'
    },
    statRow: {
        display: 'flex',
        justifyContent: 'space-between',
        maxWidth: '300px',
        marginBottom: '10px',
        fontSize: '16px',
        borderBottom: '1px solid #eee',
        paddingBottom: '5px'
    },
    statLabel: {
        color: '#7f8c8d'
    },
    statValue: {
        fontWeight: 'bold',
        color: '#2c3e50'
    },
    heroRight: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minWidth: '150px'
    },
    circleOuter: {
        width: '120px',
        height: '120px',
        borderRadius: '50%',
        border: '8px solid #ddd', 
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: '#fff'
    },
    circleInner: {
        textAlign: 'center'
    },
    percentageText: {
        fontSize: '28px',
        fontWeight: 'bold',
    },
    warningBadge: {
        marginTop: '10px',
        backgroundColor: '#fff3cd',
        color: '#856404',
        padding: '5px 10px',
        borderRadius: '20px',
        fontSize: '12px',
        display: 'flex',
        alignItems: 'center',
        gap: '5px'
    },
    sectionTitle: {
        color: '#34495e',
        fontSize: '18px',
        marginBottom: '20px',
        borderLeft: '4px solid #3498db',
        paddingLeft: '10px'
    },
    grid: {
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
        gap: '20px'
    },
    card: {
        backgroundColor: 'white',
        borderRadius: '10px',
        padding: '20px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
        transition: 'transform 0.2s',
        border: '1px solid #eee'
    },
    cardHeader: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '10px'
    },
    subjectCode: {
        backgroundColor: '#ecf0f1',
        color: '#7f8c8d',
        padding: '4px 8px',
        borderRadius: '4px',
        fontSize: '12px',
        fontWeight: 'bold'
    },
    percentBadge: {
        color: 'white',
        padding: '4px 10px',
        borderRadius: '12px',
        fontSize: '12px',
        fontWeight: 'bold'
    },
    subjectName: {
        margin: '10px 0 5px 0',
        fontSize: '16px',
        color: '#2c3e50',
        height: '45px', 
        overflow: 'hidden',
        display: '-webkit-box',
        WebkitLineClamp: 2,
        WebkitBoxOrient: 'vertical'
    },
    semester: {
        fontSize: '13px',
        color: '#95a5a6',
        marginBottom: '15px'
    },
    progressBarContainer: {
        width: '100%',
        height: '8px',
        backgroundColor: '#ecf0f1',
        borderRadius: '4px',
        marginBottom: '15px',
        overflow: 'hidden'
    },
    progressBarFill: {
        height: '100%',
        borderRadius: '4px',
        transition: 'width 0.5s ease-in-out'
    },
    cardStats: {
        display: 'flex',
        justifyContent: 'space-between',
        fontSize: '13px',
        color: '#555',
        marginTop: '10px',
        borderTop: '1px solid #f9f9f9',
        paddingTop: '10px'
    },
    miniStat: {
        display: 'flex',
        alignItems: 'center'
    },
    noData: {
        gridColumn: '1 / -1',
        textAlign: 'center',
        padding: '40px',
        color: '#7f8c8d',
        fontStyle: 'italic'
    }
};

export default StudentAttendance;