import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { FaChartBar, FaExclamationCircle } from 'react-icons/fa'; // Make sure to npm install react-icons

const InternalMarksPage = () => {
  const [scores, setScores] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchScores = async () => {
      try {
        const token = localStorage.getItem('token');
        
        // FIX 1: Use the full URL including localhost:5000
        const response = await axios.get('http://localhost:5000/api/marks/my-scores', {
          headers: { Authorization: `Bearer ${token}` }
        });

        if (response.data.success) {
          setScores(response.data.scores);
        } else {
          setError('Failed to load scores');
        }
      } catch (err) {
        console.error("Error fetching internal marks:", err);
        setError('Error fetching internal marks. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchScores();
  }, []);

  if (loading) return <div style={styles.loading}>Loading your scores...</div>;

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <h2 style={styles.title}><FaChartBar style={{marginRight: '10px'}}/>Internal Assessment Scores</h2>
      </header>

      {error && (
        <div style={styles.errorMsg}>
            <FaExclamationCircle /> {error}
        </div>
      )}

      <div style={styles.tableContainer}>
        <table style={styles.table}>
          <thead>
            <tr style={styles.headerRow}>
              <th style={styles.th}>Subject Code</th>
              <th style={styles.th}>Subject Name</th>
              <th style={styles.thCenter}>IA 1 (30)</th>
              <th style={styles.thCenter}>IA 2 (30)</th>
              <th style={styles.thCenter}>IA 3 (30)</th>
              <th style={styles.thCenter}>Average</th>
            </tr>
          </thead>
          <tbody>
            {scores.length === 0 ? (
              <tr>
                <td colSpan="6" style={styles.noData}>No marks available yet.</td>
              </tr>
            ) : (
              scores.map((subject) => {
                // Calculate simplistic average for display
                const s1 = subject.scores['IA1'] || 0;
                const s2 = subject.scores['IA2'] || 0;
                const s3 = subject.scores['IA3'] || 0;
                // Logic depends on college rule (e.g., Best of 2, or Average of 3). 
                // Showing simple sum/avg here as placeholder
                const avg = ((s1 + s2 + s3) / 3).toFixed(1);

                return (
                  <tr key={subject.subject_code} style={styles.row}>
                    <td style={styles.tdCode}>{subject.subject_code}</td>
                    <td style={styles.tdName}>{subject.subject_name}</td>
                    
                    {/* Display Score or a Dash if null */}
                    <td style={styles.tdCenter}>
                        <span style={getScoreStyle(subject.scores['IA1'])}>
                            {subject.scores['IA1'] !== undefined ? subject.scores['IA1'] : '-'}
                        </span>
                    </td>
                    <td style={styles.tdCenter}>
                        <span style={getScoreStyle(subject.scores['IA2'])}>
                            {subject.scores['IA2'] !== undefined ? subject.scores['IA2'] : '-'}
                        </span>
                    </td>
                    <td style={styles.tdCenter}>
                        <span style={getScoreStyle(subject.scores['IA3'])}>
                            {subject.scores['IA3'] !== undefined ? subject.scores['IA3'] : '-'}
                        </span>
                    </td>
                    <td style={{...styles.tdCenter, fontWeight: 'bold', color: '#555'}}>
                        {avg > 0 ? avg : '-'}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// Helper to color code marks
const getScoreStyle = (score) => {
    if (score === undefined || score === null) return {};
    if (score < 12) return { color: 'red', fontWeight: 'bold' }; // Fail < 12
    if (score >= 25) return { color: 'green', fontWeight: 'bold' }; // Excellent
    return { color: '#333' };
};

// --- CSS-in-JS Styles ---
const styles = {
  container: {
    padding: '30px',
    backgroundColor: '#f8f9fa',
    minHeight: '100vh',
    fontFamily: "'Segoe UI', sans-serif"
  },
  loading: {
    textAlign: 'center',
    padding: '50px',
    fontSize: '18px',
    color: '#666'
  },
  header: {
    marginBottom: '30px',
    borderBottom: '2px solid #e9ecef',
    paddingBottom: '15px'
  },
  title: {
    color: '#2c3e50',
    margin: 0,
    display: 'flex',
    alignItems: 'center'
  },
  errorMsg: {
    backgroundColor: '#f8d7da',
    color: '#721c24',
    padding: '15px',
    borderRadius: '8px',
    marginBottom: '20px',
    display: 'flex',
    alignItems: 'center',
    gap: '10px'
  },
  tableContainer: {
    backgroundColor: 'white',
    borderRadius: '12px',
    boxShadow: '0 4px 6px rgba(0,0,0,0.05)',
    overflow: 'hidden',
    overflowX: 'auto'
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
    minWidth: '600px'
  },
  headerRow: {
    backgroundColor: '#3498db',
    color: 'white',
    textAlign: 'left'
  },
  th: {
    padding: '15px 20px',
    fontWeight: '600',
    fontSize: '14px',
    textTransform: 'uppercase',
    letterSpacing: '0.5px'
  },
  thCenter: {
    padding: '15px 20px',
    fontWeight: '600',
    fontSize: '14px',
    textAlign: 'center',
    textTransform: 'uppercase'
  },
  row: {
    borderBottom: '1px solid #f1f1f1',
    transition: 'background-color 0.2s'
  },
  tdCode: {
    padding: '15px 20px',
    color: '#7f8c8d',
    fontWeight: '500',
    fontSize: '14px'
  },
  tdName: {
    padding: '15px 20px',
    color: '#2c3e50',
    fontWeight: '600',
    fontSize: '15px'
  },
  tdCenter: {
    padding: '15px 20px',
    textAlign: 'center',
    fontSize: '15px'
  },
  noData: {
    padding: '40px',
    textAlign: 'center',
    color: '#999',
    fontStyle: 'italic'
  }
};

export default InternalMarksPage;