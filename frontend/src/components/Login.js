import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from 'react-router-dom'; // Import useNavigate
import collegeBackground from './college.jpg'; // Import your image

const Login = () => {
  const [role, setRole] = useState("");
  const [identifier, setIdentifier] = useState(""); // Changed from 'login_id' to 'identifier'
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [isHoveringLogin, setIsHoveringLogin] = useState(false); // For button hover
  const [isHoveringSelect, setIsHoveringSelect] = useState(false); // For select dropdown hover

  const navigate = useNavigate(); // Initialize useNavigate

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!role) {
      setMessage("Please select a role before logging in.");
      return;
    }
    if (!identifier || !password) { // Changed from 'login_id' to 'identifier'
      setMessage("Please enter both ID/Email and password.");
      return;
    }

    try {
      const response = await axios.post("http://localhost:5000/login", {
        identifier, // Changed from login_id
        password,
        role,
      });
      if (response.data.success) {
        localStorage.setItem("token", response.data.token);
        if (role === "faculty") navigate("/faculty/dashboard");
        else if (role === "student") navigate("/student/dashboard");
        else if (role === "admin") navigate("/admin/dashboard"); // Assuming an admin dashboard exists
      } else {
        setMessage(response.data.message || "Login failed.");
      }
    } catch (error) {
      console.error("Login error:", error);
      if (error.response && error.response.data && error.response.data.message) {
        setMessage(error.response.data.message);
      } else {
        setMessage("Login failed. Please check your network or try again.");
      }
      setPassword(""); // Clear password on error for security
    }
  };

  // ... (rest of your component code, styles, etc. remains the same)
  const backgroundStyle = {
    minHeight: "100vh",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    backgroundImage: `url(${collegeBackground})`,
    backgroundSize: "cover",
    backgroundPosition: "center",
    backgroundRepeat: "no-repeat",
    transition: "background-image 0.5s ease-in-out",
  };

  const loginBoxStyle = {
    maxWidth: "400px",
    width: "90%",
    padding: "30px",
    backgroundColor: "rgba(255, 255, 255, 0.7)",
    borderRadius: "15px",
    boxShadow: "0 10px 25px rgba(0,0,0,0.3)",
    textAlign: "center",
  }

  const inputStyle = {
    width: "calc(100% - 20px)",
    padding: "10px",
    marginBottom: "15px",
    borderRadius: "8px",
    border: "1px solid #ccc",
    fontSize: "16px",
    boxSizing: "border-box",
  };

  const selectWrapperStyle = {
    position: 'relative',
    marginBottom: "15px",
  };

  const selectStyle = {
    ...inputStyle,
    appearance: 'none',
    paddingRight: '30px',
    cursor: 'pointer',
    backgroundColor: isHoveringSelect ? "#e0e0e0" : "white",
    transition: "background-color 0.3s ease",
  };

  const selectArrowStyle = {
    position: 'absolute',
    right: '10px',
    top: '50%',
    transform: 'translateY(-50%)',
    pointerEvents: 'none',
    color: '#555',
  };

  const buttonStyle = {
    width: "100%",
    padding: "12px",
    backgroundColor: isHoveringLogin ? "#0056b3" : "#007bff",
    color: "white",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
    fontSize: "18px",
    fontWeight: "bold",
    boxShadow: isHoveringLogin ? "0 8px 16px rgba(0, 123, 255, 0.4)" : "none",
    transition: "background-color 0.3s ease, box-shadow 0.3s ease",
  };

  const messageStyle = {
    marginTop: "20px",
    fontSize: "1.1em",
    color: message.includes("successful") ? "green" : "#dc3545",
    fontWeight: "bold",
  };

  return (
    <div style={backgroundStyle}>
      <div style={loginBoxStyle}>
        <h2 style={{ marginBottom: "25px", color: "#333", fontSize: "2em" }}>Welcome!</h2>

        <form onSubmit={handleSubmit}>
          <div style={selectWrapperStyle}
            onMouseEnter={() => setIsHoveringSelect(true)}
            onMouseLeave={() => setIsHoveringSelect(false)}
          >
            <label htmlFor="role-select" style={{ display: "block", marginBottom: "8px", fontWeight: "bold", textAlign: "left", color: "#555" }}>
              Login as:
            </label>
            <select
              id="role-select"
              value={role}
              onChange={(e) => {
                setRole(e.target.value);
                setIdentifier(""); // Changed from setId to setIdentifier
                setMessage("");
              }}
              required
              style={selectStyle}
            >
              <option value="">-- Select Role --</option>
              <option value="student">Student</option>
              <option value="faculty">Faculty</option>
              <option value="admin">Admin</option> {/* Added admin role */}
            </select>
            <span style={selectArrowStyle}>&#9662;</span>
          </div>

          {role && (
            <div style={{ marginBottom: "15px" }}>
              <label htmlFor="id-input" style={{ display: "block", marginBottom: "8px", fontWeight: "bold", textAlign: "left", color: "#555" }}>
                {role === "student" ? "USN:" : "Email:"}
              </label>
              <input
                id="id-input" // Corrected attribute from login_id to id
                type={role === "student" ? "text" : "email"}
                placeholder={role === "student" ? "Enter your USN" : "Enter your Email"}
                value={identifier} // Changed from login_id
                onChange={(e) => setIdentifier(e.target.value)} // Changed from setId to setIdentifier
                required
                style={inputStyle}
              />
            </div>
          )}

          <div style={{ marginBottom: "25px" }}>
            <label htmlFor="password-input" style={{ display: "block", marginBottom: "8px", fontWeight: "bold", textAlign: "left", color: "#555" }}>
              Password:
            </label>
            <input
              id="password-input"
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              style={inputStyle}
            />
          </div>

          <button
            type="submit"
            style={buttonStyle}
            onMouseEnter={() => setIsHoveringLogin(true)}
            onMouseLeave={() => setIsHoveringLogin(false)}
          >
            Login
          </button>
        </form>

        {message && <p style={messageStyle}>{message}</p>}
      </div>
    </div>
  );
};

export default Login;