import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from "react-router-dom";
import axios from 'axios';
import { FaArrowLeft, FaFileDownload, FaCalendarAlt, FaUserTie } from 'react-icons/fa';

const CircularDetails = () => {
    const { circular_id } = useParams();
    const navigate = useNavigate();
    const [circular, setCircular] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    const SERVER_URL = "http://localhost:5000";
    const API_BASE_URL = `${SERVER_URL}/api/circulars`;

    useEffect(() => {
        const fetchCircular = async () => {
            try {
                const token = localStorage.getItem("token");
                const res = await axios.get(`${API_BASE_URL}/${circular_id}`, {
                    headers: { Authorization: `Bearer ${token}` }
                });

                if (res.data.success) {
                    setCircular(res.data.circular);
                } else {
                    setError("Circular not found");
                }
            } catch (err) {
                console.error(err);
                setError("Error loading circular details");
            } finally {
                setLoading(false);
            }
        };

        fetchCircular();
    }, [circular_id]);

    if (loading) return <div style={styles.centerText}>Loading details...</div>;
    if (error) return <div style={{...styles.centerText, color: 'red'}}>{error}</div>;
    if (!circular) return <div style={styles.centerText}>Circular not found.</div>;

    // Construct the full URL for the attachment
    // Backend stores "circular_attachments/filename.ext"
    // Static folder is served at "/uploads"
    const attachmentUrl = circular.attachment_path 
        ? `${SERVER_URL}/uploads/${circular.attachment_path.replace(/\\/g, "/")}` 
        : null;

    const isImage = attachmentUrl && (attachmentUrl.endsWith('.jpg') || attachmentUrl.endsWith('.png') || attachmentUrl.endsWith('.jpeg'));

    return (
        <div style={styles.container}>
            <button onClick={() => navigate(-1)} style={styles.backButton}>
                <FaArrowLeft /> Back to List
            </button>

            <div style={styles.card}>
                <h1 style={styles.title}>{circular.title}</h1>
                
                <div style={styles.metaContainer}>
                    <div style={styles.metaItem}>
                        <FaCalendarAlt style={{marginRight: '8px'}} />
                        {new Date(circular.posted_at).toLocaleDateString(undefined, {
                            weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
                        })}
                    </div>
                    <div style={styles.metaItem}>
                        <FaUserTie style={{marginRight: '8px'}} />
                        Posted by: {circular.posted_by_faculty || 'Admin'}
                    </div>
                </div>

                <hr style={styles.divider} />

                <div style={styles.content}>
                    {circular.content}
                </div>

                {attachmentUrl && (
                    <div style={styles.attachmentSection}>
                        <h3>Attachment</h3>
                        {isImage ? (
                            <img src={attachmentUrl} alt="Attachment" style={styles.imagePreview} />
                        ) : (
                            <div style={styles.fileBox}>
                                <p>This circular has an attached document.</p>
                                <a 
                                    href={attachmentUrl} 
                                    target="_blank" 
                                    rel="noopener noreferrer"
                                    style={styles.downloadButton}
                                >
                                    <FaFileDownload style={{marginRight: '8px'}}/> 
                                    View / Download Attachment
                                </a>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

// Styles
const styles = {
    container: {
        maxWidth: '900px',
        margin: '40px auto',
        padding: '20px',
        fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
    },
    centerText: {
        textAlign: 'center',
        marginTop: '50px',
        fontSize: '18px',
        color: '#666'
    },
    backButton: {
        background: 'none',
        border: 'none',
        color: '#555',
        cursor: 'pointer',
        fontSize: '16px',
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        marginBottom: '20px'
    },
    card: {
        backgroundColor: '#fff',
        borderRadius: '12px',
        boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
        padding: '40px',
    },
    title: {
        fontSize: '28px',
        color: '#2c3e50',
        marginBottom: '20px',
        marginTop: 0
    },
    metaContainer: {
        display: 'flex',
        gap: '30px',
        color: '#7f8c8d',
        fontSize: '14px',
        marginBottom: '20px'
    },
    metaItem: {
        display: 'flex',
        alignItems: 'center'
    },
    divider: {
        border: 'none',
        borderTop: '1px solid #eee',
        margin: '20px 0'
    },
    content: {
        fontSize: '16px',
        lineHeight: '1.8',
        color: '#34495e',
        whiteSpace: 'pre-wrap', // Preserves newlines from the textarea
        marginBottom: '30px'
    },
    attachmentSection: {
        marginTop: '30px',
        paddingTop: '20px',
        borderTop: '1px dashed #ccc'
    },
    imagePreview: {
        maxWidth: '100%',
        borderRadius: '8px',
        marginTop: '15px',
        border: '1px solid #eee'
    },
    fileBox: {
        backgroundColor: '#f8f9fa',
        padding: '20px',
        borderRadius: '8px',
        marginTop: '10px'
    },
    downloadButton: {
        display: 'inline-flex',
        alignItems: 'center',
        backgroundColor: '#3498db',
        color: '#fff',
        padding: '10px 20px',
        borderRadius: '6px',
        textDecoration: 'none',
        fontWeight: 'bold',
        marginTop: '10px',
        transition: 'background 0.3s'
    }
};

export default CircularDetails;