import React from 'react';

const StudentNavBar = ({ studentName, studentUSN, onModuleSelect }) => {
  const handleLogout = () => {
    localStorage.removeItem('token');
    window.location.href = '/'; // Full redirect to login page
  };

  return (
    <nav style={navStyle}>
      {/* Left Side - Welcome Message */}
      <div style={brandStyle}>
        Welcome, <strong>{studentName}</strong>
      </div>

      {/* Right Side - Navigation Links */}
      <ul style={ulStyle}>
        <li style={liStyle}>
          <button onClick={() => onModuleSelect(null)} style={linkButtonStyle}>
            Dashboard
          </button>
        </li>
        <li style={liStyle}>
          <button onClick={() => onModuleSelect('timetable')} style={linkButtonStyle}>
            Timetable
          </button>
        </li>
        <li style={liStyle}>
          <button onClick={() => onModuleSelect('notes')} style={linkButtonStyle}>
            Study Notes
          </button>
        </li>
        <li style={liStyle}>
          <button onClick={() => onModuleSelect('attendance')} style={linkButtonStyle}>
            Attendance
          </button>
        </li>
        <li style={liStyle}>
          <button onClick={() => onModuleSelect('circulars')} style={linkButtonStyle}>
            Circulars
          </button>
        </li>
        <li style={liStyle}>
          <button onClick={() => onModuleSelect('profile')} style={linkButtonStyle}>
            Profile
          </button>
        </li>

        {/* Logout Button */}
        <li style={liStyle}>
          <button onClick={handleLogout} style={logoutButtonStyle}>
            Logout
          </button>
        </li>
      </ul>
    </nav>
  );
};

// Professional & Responsive Styles
const navStyle = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  background: 'linear-gradient(135deg, #1e3c72, #2a5298)',
  color: '#fff',
  padding: '14px 30px',
  boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
  position: 'sticky',
  top: 0,
  zIndex: 1000,
  fontFamily: '"Segoe UI", Arial, sans-serif',
};

const brandStyle = {
  fontSize: '1.4rem',
  fontWeight: '600',
  letterSpacing: '0.5px',
};

const ulStyle = {
  listStyle: 'none',
  margin: 0,
  padding: 0,
  display: 'flex',
  alignItems: 'center',
  flexWrap: 'wrap',
  gap: '8px',
};

const liStyle = {
  margin: 0,
};

const linkButtonStyle = {
  background: 'none',
  border: 'none',
  color: '#ecf0f1',
  cursor: 'pointer',
  padding: '10px 16px',
  fontSize: '1.02rem',
  fontWeight: '500',
  borderRadius: '6px',
  transition: 'all 0.3s ease',
};

const logoutButtonStyle = {
  backgroundColor: '#e74c3c',
  color: 'white',
  border: 'none',
  padding: '10px 18px',
  borderRadius: '6px',
  cursor: 'pointer',
  fontSize: '1rem',
  fontWeight: '600',
  transition: 'all 0.3s ease',
  boxShadow: '0 2px 8px rgba(231, 76, 60, 0.4)',
};

// Hover Effects (using inline for simplicity)
const hoverStyle = {
  '&:hover': {
    backgroundColor: 'rgba(255, 255, 255, 0.15)',
  },
};

// Apply hover using onMouseEnter/out if needed (or use CSS file later)
export default StudentNavBar;