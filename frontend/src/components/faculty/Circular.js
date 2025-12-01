import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from "react-router-dom";
import './Circulars.css';

const FacultyCirculars = () => {
    const [title, setTitle] = useState('');
    const [content, setContent] = useState('');
    const [audience, setAudience] = useState('all'); // Default to 'all'
    const [deptCode, setDeptCode] = useState(''); // For 'specific_dept'
    const [attachment, setAttachment] = useState(null); // For file attachment
    const [recentCirculars, setRecentCirculars] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [successMessage, setSuccessMessage] = useState('');

    const API_BASE_URL = 'http://localhost:5000/api/circulars'; 

    useEffect(() => {
        fetchRecentCirculars();
    }, []);

    const getAuthToken = () => {
        return localStorage.getItem('token');
    };

    const fetchRecentCirculars = async () => {
        setLoading(true);
        setError('');
        try {
            const token = getAuthToken();
            const response = await axios.get(`${API_BASE_URL}/recent`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            if (response.data.success) {
                setRecentCirculars(response.data.recent_circulars);
            } else {
                setError(response.data.error || "Failed to fetch recent circulars.");
            }
        } catch (err) {
            console.error("Error fetching recent circulars:", err);
            setError("Failed to fetch recent circulars. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    const handleFileChange = (e) => {
        setAttachment(e.target.files[0]);
    };

    const handleSubmitCircular = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setSuccessMessage('');

        const formData = new FormData();
        formData.append('title', title);
        formData.append('content', content);
        formData.append('audience', audience);
        if (audience === 'specific_dept' && deptCode) {
            formData.append('dept_code', deptCode);
        }
        if (attachment) {
            formData.append('attachment', attachment);
        }

        try {
            const token = getAuthToken();
            const response = await axios.post("http://localhost:5000/api/circulars/upload", formData, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'multipart/form-data'
                }
            });

            if (response.data.success) {
                setSuccessMessage("Circular posted successfully!");
                setTitle('');
                setContent('');
                setAudience('');
                setDeptCode('');
                setAttachment(null);
                document.getElementById('attachment-input').value = ''; // Clear file input
                fetchRecentCirculars(); // Refresh the list
            } else {
                setError(response.data.error || "Failed to post circular.");
            }
        } catch (err) {
            console.error("Error posting circular:", err);
            setError(err.response?.data?.error || "Failed to post circular. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="circulars-module-container">
            <div className="circulars-header">
                <h1>Circulars Module</h1>
            </div>

            <div className="circulars-main-content">
                <div className="compose-circular-section">
                    <h2>Compose New Circular</h2>
                    <form onSubmit={handleSubmitCircular}>
                        <div className="form-group">
                            <label htmlFor="title">Title:</label>
                            <input
                                type="text"
                                id="title"
                                value={title}
                                onChange={(e) => setTitle(e.target.value)}
                                placeholder="Enter circular title"
                                required
                            />
                        </div>
                        <div className="form-group">
                            <label htmlFor="content">Content:</label>
                            <textarea
                                id="content"
                                value={content}
                                onChange={(e) => setContent(e.target.value)}
                                placeholder="Eiter 'sculd's Renner"
                                rows="5"
                                required
                            ></textarea>
                        </div>
                        <div className="form-group">
                            <label htmlFor="audience">Audience:</label>
                            <select
                                id="audience"
                                value={audience}
                                onChange={(e) => setAudience(e.target.value)}
                            >
                                <option value="all">All</option>
                                <option value="students">Students</option>
                                <option value="faculty">Faculty</option>
                                <option value="specific_dept">Specific Department</option>
                            </select>
                        </div>
                        {audience === 'specific_dept' && (
                            <div className="form-group">
                                <label htmlFor="deptCode">Department Code:</label>
                                <input
                                    type="text"
                                    id="deptCode"
                                    value={deptCode}
                                    onChange={(e) => setDeptCode(e.target.value)}
                                    placeholder="e.g., CSE, ECE"
                                    required={audience === 'specific_dept'}
                                />
                            </div>
                        )}
                        <div className="form-group">
                            <label htmlFor="attachment">Attachment (Image/PDF):</label>
                            <input
                                type="file"
                                id="attachment-input"
                                onChange={handleFileChange}
                                accept="image/*,.pdf" // Accept images and PDFs
                            />
                        </div>
                        <button type="submit" className="post-circular-button" disabled={loading}>
                            {loading ? 'Posting...' : 'Post Circular'}
                        </button>
                    </form>
                    {error && <p className="error-message">{error}</p>}
                    {successMessage && <p className="success-message">{successMessage}</p>}
                </div>

                <div className="recent-announcements-section">
                    <div className="section-header">
                        <h2>Recent Announcements</h2>
                        <button className="view-all-button">View All</button> {/* This could be 'View All' */}
                    </div>
                    {loading && <p>Loading recent circulars...</p>}
                    {recentCirculars.length === 0 && !loading && <p>No recent announcements.</p>}
                    <ul>
                        {recentCirculars.map((circular) => (
                            <li key={circular.circular_id}>
                                <Link to={`/circulars/${circular.circular_id}`}>
                                    <span>{circular.title}</span>
                                    <span>{new Date(circular.posted_at).getFullYear()}</span>
                                </Link>
                            </li>
                        ))}
                    </ul>
                    <a href="/send-notification" className="send-notification-link">Send Notification</a>
                </div>
            </div>
        </div>
    );

};

export default FacultyCirculars;