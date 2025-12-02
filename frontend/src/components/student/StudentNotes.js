import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { FaFileAlt, FaSearch, FaCloudDownloadAlt, FaFilter } from 'react-icons/fa';

const StudentNotes = () => {
    const [notes, setNotes] = useState([]);
    const [filteredNotes, setFilteredNotes] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Get token from local storage (adjust key if yours is different)
    const token = localStorage.getItem('token');

    useEffect(() => {
        fetchNotes();
    }, []);

    // 1. Fetch Notes from Backend
    const fetchNotes = async () => {
        try {
            const response = await axios.get('http://127.0.0.1:5000/api/notes/', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (response.data.success) {
                setNotes(response.data.notes);
                setFilteredNotes(response.data.notes);
            } else {
                setError("Failed to fetch notes.");
            }
        } catch (err) {
            console.error(err);
            setError("Error connecting to server.");
        } finally {
            setLoading(false);
        }
    };

    // 2. Handle Search (Client-side filtering)
    const handleSearch = (e) => {
        const term = e.target.value.toLowerCase();
        setSearchTerm(term);

        if (term === '') {
            setFilteredNotes(notes);
        } else {
            const filtered = notes.filter(note => 
                note.subject_name.toLowerCase().includes(term) || 
                note.subject_code.toLowerCase().includes(term) ||
                note.title.toLowerCase().includes(term)
            );
            setFilteredNotes(filtered);
        }
    };

    // 3. Handle Download
    const handleDownload = async (noteId, fileName) => {
        try {
            const response = await axios.get(`http://127.0.0.1:5000/api/notes/download/${noteId}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                responseType: 'blob', // Important for file downloads
            });

            // Create a temporary URL to trigger download
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            
            // Try to extract extension from the actual file or default to backend info
            link.setAttribute('download', fileName); 
            document.body.appendChild(link);
            link.click();
            link.parentNode.removeChild(link);
        } catch (err) {
            console.error("Download failed", err);
            alert("Failed to download file.");
        }
    };

    if (loading) return <div style={styles.loading}>Loading Course Materials...</div>;

    return (
        <div style={styles.container}>
            {/* Header Section */}
            <div style={styles.header}>
                <h2 style={styles.title}>Course Materials / Notes</h2>
                <button style={styles.filterBtn}>
                    Filter <FaFilter style={{ marginLeft: '5px' }} />
                </button>
            </div>

            {/* Search Bar */}
            <div style={styles.searchContainer}>
                <div style={styles.searchWrapper}>
                    <FaSearch style={styles.searchIcon} />
                    <input 
                        type="text" 
                        placeholder="Search by Subject Name or Code..." 
                        style={styles.searchInput}
                        value={searchTerm}
                        onChange={handleSearch}
                    />
                </div>
                <button style={styles.downloadAllBtn}>
                    <FaCloudDownloadAlt size={20} />
                </button>
            </div>

            <h3 style={styles.subTitle}>Available Notes</h3>

            {/* Error Message */}
            {error && <div style={styles.error}>{error}</div>}

            {/* Notes Grid */}
            <div style={styles.grid}>
                {filteredNotes.length > 0 ? (
                    filteredNotes.map((note) => (
                        <div key={note.note_id} style={styles.card}>
                            {/* Icon Section */}
                            <div style={styles.iconContainer}>
                                <FaFileAlt size={24} color="#fff" />
                            </div>

                            {/* Details Section */}
                            <div style={styles.cardContent}>
                                <h4 style={styles.cardTitle}>
                                    {note.subject_code} {note.subject_name}
                                </h4>
                                <p style={styles.cardSubtitle}>
                                    {note.title}
                                </p>
                                <p style={styles.cardMeta}>
                                    By: {note.faculty_name} • {new Date(note.uploaded_at).toLocaleDateString()}
                                </p>
                            </div>

                            {/* Download Button */}
                            <button 
                                style={styles.downloadBtn}
                                onClick={() => handleDownload(note.note_id, `${note.title}.${note.file_url.split('.').pop()}`)}
                            >
                                Download
                            </button>
                        </div>
                    ))
                ) : (
                    <p style={{ color: '#666' }}>No notes found matching your search.</p>
                )}
            </div>
        </div>
    );
};

// --- CSS Styles (Inline for easy copy-paste) ---
const styles = {
    container: {
        padding: '30px',
        backgroundColor: '#f8f9fa',
        minHeight: '100vh',
        fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
    },
    loading: {
        padding: '50px',
        textAlign: 'center',
        fontSize: '1.2rem',
        color: '#555'
    },
    header: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '20px'
    },
    title: {
        fontSize: '24px',
        color: '#333',
        margin: 0,
        fontWeight: '600'
    },
    subTitle: {
        fontSize: '18px',
        color: '#333',
        marginTop: '30px',
        marginBottom: '15px',
        fontWeight: 'bold'
    },
    filterBtn: {
        backgroundColor: '#82b1ff',
        color: 'white',
        border: 'none',
        padding: '8px 20px',
        borderRadius: '5px',
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        fontSize: '14px',
        fontWeight: 'bold'
    },
    searchContainer: {
        display: 'flex',
        gap: '10px',
        marginBottom: '20px'
    },
    searchWrapper: {
        position: 'relative',
        flex: 1,
        display: 'flex',
        alignItems: 'center'
    },
    searchIcon: {
        position: 'absolute',
        left: '15px',
        color: '#aaa'
    },
    searchInput: {
        width: '100%',
        padding: '12px 15px 12px 45px',
        borderRadius: '8px',
        border: '1px solid #ddd',
        fontSize: '14px',
        outline: 'none',
        boxShadow: '0 2px 5px rgba(0,0,0,0.05)'
    },
    downloadAllBtn: {
        backgroundColor: '#82b1ff',
        color: 'white',
        border: 'none',
        borderRadius: '8px',
        width: '50px',
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
    },
    grid: {
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
        gap: '20px'
    },
    card: {
        backgroundColor: 'white',
        borderRadius: '12px',
        padding: '15px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        boxShadow: '0 4px 6px rgba(0,0,0,0.05)',
        border: '1px solid #eaeaea',
        transition: 'transform 0.2s',
    },
    iconContainer: {
        backgroundColor: '#2c3e50',
        borderRadius: '8px',
        width: '50px',
        height: '50px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        marginRight: '15px'
    },
    cardContent: {
        flex: 1,
        marginRight: '15px'
    },
    cardTitle: {
        margin: '0 0 5px 0',
        fontSize: '16px',
        color: '#333',
        fontWeight: 'bold'
    },
    cardSubtitle: {
        margin: '0 0 5px 0',
        fontSize: '13px',
        color: '#555'
    },
    cardMeta: {
        margin: 0,
        fontSize: '11px',
        color: '#999'
    },
    downloadBtn: {
        backgroundColor: '#82b1ff',
        color: 'white',
        border: 'none',
        padding: '8px 15px',
        borderRadius: '6px',
        cursor: 'pointer',
        fontSize: '13px',
        fontWeight: 'bold',
        whiteSpace: 'nowrap'
    },
    error: {
        color: 'red',
        marginBottom: '20px'
    }
};

export default StudentNotes;