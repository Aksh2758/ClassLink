import React from 'react';

const FacultyProfile = ({ facultyDetails }) => {
  return (
    <div>
      <h2>Faculty Profile</h2>
      <p>View and update your personal and professional information.</p>
      {facultyDetails ? (
        <div>
          <p><strong>Name:</strong> {facultyDetails.name}</p>
          <p><strong>Email:</strong> {facultyDetails.email}</p>
          <p><strong>Department:</strong> {facultyDetails.department}</p>
          {/* Add more profile fields as available */}
        </div>
      ) : (
        <p>Loading profile details...</p>
      )}
      <img src="https://via.placeholder.com/600x400?text=Faculty+Profile" alt="Profile Module Placeholder" style={{ maxWidth: '100%', height: 'auto', borderRadius: '8px' }}/>
    </div>
  );
};

export default FacultyProfile;