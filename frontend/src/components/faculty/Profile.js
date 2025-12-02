import React, { useState, useEffect } from 'react';

const FacultyProfile = () => {
  // --- State Management ---
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [isEditing, setIsEditing] = useState(false);

  const [formData, setFormData] = useState({
    name: '',
    designation: '',
    dept_code: '',
    email: '',
    dept_name: ''
  });

  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });

  // --- Helpers & API Calls ---
  const getToken = () => localStorage.getItem('token');

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/profile/', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${getToken()}`,
          'Content-Type': 'application/json'
        }
      });
      const data = await response.json();

      if (data.success) {
        setProfile(data.profile);
        setFormData({
          name: data.profile.name || '',
          designation: data.profile.designation || '',
          dept_code: data.profile.dept_code || '',
          email: data.profile.email || '',
          dept_name: data.profile.dept_name || ''
        });
      } else {
        setMessage({ type: 'error', text: data.error || 'Failed to load profile.' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Server error while fetching profile.' });
    } finally {
      setLoading(false);
    }
  };

  const handleProfileUpdate = async (e) => {
    e.preventDefault();
    setMessage({ type: '', text: '' });

    try {
      const response = await fetch('http://localhost:5000/api/profile/', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${getToken()}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: formData.name,
          designation: formData.designation,
          dept_code: formData.dept_code
        })
      });

      const data = await response.json();

      if (data.success) {
        setMessage({ type: 'success', text: data.message });
        setIsEditing(false);
        fetchProfile();
      } else {
        setMessage({ type: 'error', text: data.error || 'Update failed.' });
      }
    } catch {
      setMessage({ type: 'error', text: 'Server error updating profile.' });
    }
  };

  const handlePasswordChange = async (e) => {
    e.preventDefault();

    if (passwordData.new_password !== passwordData.confirm_password) {
      setMessage({ type: 'error', text: 'New passwords do not match.' });
      return;
    }

    try {
      const response = await fetch('http://localhost:5000/api/profile/change-password', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${getToken()}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          current_password: passwordData.current_password,
          new_password: passwordData.new_password
        })
      });

      const data = await response.json();

      if (data.success) {
        setMessage({ type: 'success', text: data.message });
        setPasswordData({ current_password: '', new_password: '', confirm_password: '' });
      } else {
        setMessage({ type: 'error', text: data.error || 'Password change failed.' });
      }
    } catch {
      setMessage({ type: 'error', text: 'Server error changing password.' });
    }
  };

  // --- Styling Object (CSS-in-JS) ---
  const styles = {
    container: {
        maxWidth: "1100px",
        margin: "0 auto",
        padding: "20px",
        fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    },
    header: {
        marginBottom: "30px",
    },
    title: {
        fontSize: "2rem",
        fontWeight: "700",
        color: "#2c3e50",
        margin: "0 0 5px 0",
    },
    subtitle: {
        color: "#7f8c8d",
        fontSize: "1rem",
        margin: 0,
    },
    grid: {
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(400px, 1fr))",
        gap: "30px",
        alignItems: "start",
    },
    // Left Card (Profile)
    profileCard: {
        backgroundColor: "white",
        borderRadius: "16px",
        overflow: "hidden",
        boxShadow: "0 4px 20px rgba(0,0,0,0.08)",
        border: "1px solid #eee",
    },
    gradientHeader: {
        // Using a slightly different gradient (Teal/Blue) to distinguish Faculty from Student
        background: "linear-gradient(135deg, #11998e 0%, #38ef7d 100%)", 
        padding: "30px",
        color: "white",
        position: "relative",
        display: "flex",
        alignItems: "center",
        gap: "20px",
    },
    avatarCircle: {
        width: "70px",
        height: "70px",
        backgroundColor: "white",
        borderRadius: "50%",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontSize: "2.5rem",
        color: "#11998e",
    },
    headerText: {
        display: "flex",
        flexDirection: "column",
    },
    nameText: {
        fontSize: "1.5rem",
        fontWeight: "600",
        margin: 0,
    },
    subText: {
        fontSize: "0.95rem",
        opacity: 0.9,
        margin: "4px 0 0 0",
    },
    editButton: {
        position: "absolute",
        top: "20px",
        right: "20px",
        backgroundColor: "rgba(255, 255, 255, 0.2)",
        border: "1px solid rgba(255,255,255,0.4)",
        color: "white",
        padding: "6px 16px",
        borderRadius: "20px",
        fontSize: "0.85rem",
        cursor: "pointer",
        backdropFilter: "blur(4px)",
        transition: "background 0.2s",
    },
    cardBody: {
        padding: "30px",
    },
    infoGroup: {
        marginBottom: "20px",
    },
    label: {
        display: "block",
        fontSize: "0.9rem",
        color: "#7f8c8d",
        marginBottom: "5px",
        fontWeight: "500",
    },
    value: {
        fontSize: "1.05rem",
        color: "#2c3e50",
        fontWeight: "500",
        paddingBottom: "10px",
        borderBottom: "1px solid #f0f0f0",
    },
    input: {
        width: "100%",
        padding: "10px 12px",
        borderRadius: "8px",
        border: "1px solid #ddd",
        fontSize: "1rem",
        outline: "none",
        boxSizing: "border-box", 
        transition: "border-color 0.2s",
    },
    // Right Card (Security)
    securityCard: {
        backgroundColor: "white",
        borderRadius: "16px",
        padding: "30px",
        boxShadow: "0 4px 20px rgba(0,0,0,0.08)",
        border: "1px solid #eee",
    },
    cardTitle: {
        fontSize: "1.25rem",
        fontWeight: "600",
        color: "#2c3e50",
        marginBottom: "25px",
        display: "flex",
        alignItems: "center",
        gap: "10px",
    },
    formGroup: {
        marginBottom: "20px",
    },
    submitBtn: {
        width: "100%",
        padding: "12px",
        backgroundColor: "#2c3e50",
        color: "white",
        border: "none",
        borderRadius: "8px",
        fontSize: "1rem",
        cursor: "pointer",
        marginTop: "10px",
    },
    messageBox: {
        padding: "15px",
        borderRadius: "8px",
        marginBottom: "20px",
        fontSize: "0.95rem",
        backgroundColor: message.type === "success" ? "#d4edda" : "#f8d7da",
        color: message.type === "success" ? "#155724" : "#721c24",
        border: message.type === "success" ? "1px solid #c3e6cb" : "1px solid #f5c6cb",
    }
  };

  if (loading) return <div style={{ padding: "40px", textAlign: "center", color: "#666" }}>Loading Profile...</div>;

  return (
    <div style={styles.container}>
      {/* Page Header */}
      <div style={styles.header}>
        <h1 style={styles.title}>Faculty Profile</h1>
        <p style={styles.subtitle}>Manage your teaching details and account security</p>
      </div>

      {/* Message/Alert Box */}
      {message.text && (
        <div style={styles.messageBox}>
          {message.text}
        </div>
      )}

      <div style={styles.grid}>
        {/* --- LEFT CARD: PROFILE INFO --- */}
        <div style={styles.profileCard}>
          {/* Gradient Header */}
          <div style={styles.gradientHeader}>
            <div style={styles.avatarCircle}>
              👨‍🏫
            </div>
            <div style={styles.headerText}>
              <h2 style={styles.nameText}>{formData.name}</h2>
              <p style={styles.subText}>{formData.designation || 'Faculty Member'}</p>
            </div>
            <button 
                style={styles.editButton} 
                onClick={() => setIsEditing(!isEditing)}
            >
                {isEditing ? "Cancel" : "✏️ Edit Profile"}
            </button>
          </div>

          {/* Card Body */}
          <div style={styles.cardBody}>
            
            {/* Email (Read Only) */}
            <div style={styles.infoGroup}>
              <label style={styles.label}>✉️ Email</label>
              <div style={styles.value}>{formData.email}</div>
            </div>

            {/* Department (Read Only Name) */}
            <div style={styles.infoGroup}>
              <label style={styles.label}>🎓 Department</label>
              <div style={styles.value}>{formData.dept_name}</div>
            </div>

            {/* Editable Fields: Name, Designation, Dept Code */}
            <div style={styles.infoGroup}>
              <label style={styles.label}>📋 Faculty Details</label>
              
              {isEditing ? (
                <div style={{ display: 'grid', gap: '15px', marginTop: '10px' }}>
                  {/* Name Edit */}
                  <div>
                    <label style={{fontSize: '0.8rem', color: '#999'}}>Full Name</label>
                    <input 
                      name="name" 
                      value={formData.name} 
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      style={styles.input} 
                    />
                  </div>

                  {/* Designation Edit */}
                  <div>
                    <label style={{fontSize: '0.8rem', color: '#999'}}>Designation</label>
                    <input 
                      name="designation" 
                      value={formData.designation} 
                      onChange={(e) => setFormData({ ...formData, designation: e.target.value })}
                      style={styles.input} 
                    />
                  </div>

                  {/* Dept Code Edit */}
                  <div>
                    <label style={{fontSize: '0.8rem', color: '#999'}}>Department Code</label>
                    <input 
                      name="dept_code" 
                      value={formData.dept_code} 
                      onChange={(e) => setFormData({ ...formData, dept_code: e.target.value })}
                      style={styles.input} 
                    />
                  </div>

                  <button 
                    style={{...styles.submitBtn, backgroundColor: '#11998e'}} 
                    onClick={handleProfileUpdate}
                  >
                    Save Changes
                  </button>
                </div>
              ) : (
                // View Mode for Details
                <div style={styles.value}>
                  Designation: {formData.designation} • Dept Code: {formData.dept_code}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* --- RIGHT CARD: SECURITY --- */}
        <div style={styles.securityCard}>
          <h2 style={styles.cardTitle}>🔒 Account Security</h2>

          <form onSubmit={handlePasswordChange}>
            <div style={styles.formGroup}>
              <label style={styles.label}>Current Password</label>
              <input
                type="password"
                name="current_password"
                value={passwordData.current_password}
                onChange={(e) => setPasswordData({ ...passwordData, current_password: e.target.value })}
                placeholder="Enter current password"
                style={styles.input}
              />
            </div>

            <div style={styles.formGroup}>
              <label style={styles.label}>New Password</label>
              <input
                type="password"
                name="new_password"
                value={passwordData.new_password}
                onChange={(e) => setPasswordData({ ...passwordData, new_password: e.target.value })}
                placeholder="Enter new password"
                style={styles.input}
              />
            </div>

            <div style={styles.formGroup}>
              <label style={styles.label}>Confirm New Password</label>
              <input
                type="password"
                name="confirm_password"
                value={passwordData.confirm_password}
                onChange={(e) => setPasswordData({ ...passwordData, confirm_password: e.target.value })}
                placeholder="Confirm new password"
                style={styles.input}
              />
            </div>

            <button type="submit" style={styles.submitBtn}>
              Update Password
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default FacultyProfile;