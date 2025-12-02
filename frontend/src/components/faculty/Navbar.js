import React from 'react';
// Link is no longer needed for internal module navigation
// We only use standard buttons to trigger state changes in the parent

const FacultyNavBar = ({ facultyID, facultyName, onModuleSelect }) => {
  return (
    <nav style={navStyle}>
      <div style={brandStyle}>
        Welcome, {facultyName}
      </div>
      <ul style={ulStyle}>
        {/* Dashboard Home - sets module to null */}
        <li style={liStyle}>
          <button onClick={() => onModuleSelect(null)} style={linkButtonStyle}>Dashboard</button>
        </li>
        
        {/* Modules - sets specific string identifiers */}
        <li style={liStyle}>
          <button onClick={() => onModuleSelect('timetable')} style={linkButtonStyle}>Timetable</button>
        </li>
        <li style={liStyle}>
          <button onClick={() => onModuleSelect('notes')} style={linkButtonStyle}>Notes</button>
        </li>
        <li style={liStyle}>
          <button onClick={() => onModuleSelect('attendance')} style={linkButtonStyle}>Attendance</button>
        </li>
        <li style={liStyle}>
          <button onClick={() => onModuleSelect('internal-marks')} style={linkButtonStyle}>Internal Marks</button>
        </li>
        <li style={liStyle}>
          <button onClick={() => onModuleSelect('circulars')} style={linkButtonStyle}>Circulars</button>
        </li>
        <li style={liStyle}>
          <button onClick={() => onModuleSelect('profile')} style={linkButtonStyle}>Profile</button>
        </li>
        
        {/* Logout */}
        <li style={liStyle}>
          <button 
            onClick={() => { 
              localStorage.removeItem('token'); 
              window.location.href = '/'; 
            }} 
            style={logoutButtonStyle}
          >
            Logout
          </button>
        </li>
      </ul>
    </nav>
  );
};

// --- STYLES ---

const navStyle = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  backgroundColor: '#2c3e50',
  color: '#ecf0f1',
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
  flexWrap: 'wrap', // Allows wrapping on small screens
};

const liStyle = {
  margin: '0 5px',
};

// New style for buttons to look like links
const linkButtonStyle = {
  background: 'none',
  border: 'none',
  color: '#ecf0f1',
  cursor: 'pointer',
  padding: '8px 12px',
  fontSize: '1rem',
  textDecoration: 'none',
  borderRadius: '4px',
  transition: 'background-color 0.3s ease',
};

const logoutButtonStyle = {
  backgroundColor: '#e74c3c',
  color: 'white',
  border: 'none',
  padding: '8px 15px',
  borderRadius: '4px',
  cursor: 'pointer',
  fontSize: '1em',
  marginLeft: '10px',
  transition: 'background-color 0.3s ease',
};

export default FacultyNavBar;