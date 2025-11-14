import React from 'react';
import { Link } from 'react-router-dom';
// import FacultyTimetable from './timetable';
// import NotesUpload from './notes'; // Assuming you'll create these
// import FacultyAttendance from './attendance'; // Assuming you'll create these
// import FacultyIAMarks from './IAMarks'; // Assuming you'll create these
// import FacultyCirculars from './Circular'; // Assuming you'll create these
// import FacultyProfile from './Profile'; // Assuming you'll create these

const FacultyNavBar = ({ facultyID, facultyName }) => {
  return (
    <nav style={navStyle}>
      <div style={brandStyle}>
        Welcome, {facultyName}
      </div>
      <ul style={ulStyle}>
        <li style={liStyle}>
          <Link to="/Dashboard" style={linkStyle}>Dashboard</Link>
        </li>
        <li style={liStyle}>
          <Link to="/timetable" style={linkStyle}>Timetable</Link>
        </li>
        <li style={liStyle}>
          <Link to="/notes" style={linkStyle}>Notes</Link>
        </li>
        <li style={liStyle}>
          <Link to="/faculty/attendance" style={linkStyle}>Attendance</Link>
        </li>
        <li style={liStyle}>
          <Link to="/faculty/internal-marks" style={linkStyle}>Internal Marks</Link>
        </li>
        <li style={liStyle}>
          <Link to="/faculty/circulars" style={linkStyle}>Circulars</Link>
        </li>
        <li style={liStyle}>
          <Link to="/faculty/profile" style={linkStyle}>Profile</Link>
        </li>
        <li style={liStyle}>
          <button onClick={() => { localStorage.clear(); window.location.href = '/login'; }} style={logoutButtonStyle}>Logout</button>
        </li>
      </ul>
    </nav>
  );
};

// Basic Inline Styles (You can replace these with CSS classes)
const navStyle = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  backgroundColor: '#2c3e50', // Dark blue/grey
  color: '#ecf0f1', // Light grey text
  padding: '10px 20px',
  boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
};

const brandStyle = {
  fontSize: '1.5em',
  fontWeight: 'bold',
};

const ulStyle = {
  listStyle: 'none',
  margin: 0,
  padding: 0,
  display: 'flex',
};

const liStyle = {
  margin: '0 15px',
};

const linkStyle = {
  color: '#ecf0f1',
  textDecoration: 'none',
  padding: '8px 12px',
  borderRadius: '4px',
  transition: 'background-color 0.3s ease',
};

// Add hover effect with JavaScript if needed, or use a CSS file
// For example, in a CSS file:
// .nav-link:hover { background-color: #34495e; }

const logoutButtonStyle = {
  backgroundColor: '#e74c3c', // Red for logout
  color: 'white',
  border: 'none',
  padding: '8px 15px',
  borderRadius: '4px',
  cursor: 'pointer',
  fontSize: '1em',
  transition: 'background-color 0.3s ease',
};

// Add hover for logout button
// logoutButtonStyle:hover { background-color: #c0392b; }

export default FacultyNavBar;