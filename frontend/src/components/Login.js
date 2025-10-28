import React, { useState } from "react";
import axios from "axios";

const Login = () => {
  const [role, setRole] = useState("");
  const [id, setId] = useState(""); // USN or email
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  
  const handleSubmit = async (e) => {
    console.log("handleSubmit called!"); 
    e.preventDefault(); 
    console.log("preventDefault executed!"); 

    if (!role) {
      setMessage("Please select a role before logging in.");
      return;
    }
    if (!id || !password) {
        setMessage("Please enter both ID and password.");
        return;
    }

    try {
      const response = await axios.post("http://localhost:5000/login", {
        id, 
        password, 
        role, 
      });
      if (response.data.success) {
        localStorage.setItem("token", response.data.token);
        if (role === "faculty") window.location.href = "/faculty/FacultyDashboad";
        else if (role === "student") window.location.href = "/student/StudentDashboard";
        else if (role === "admin") window.location.href = "/admin/AdminDashboard";
      }
    } catch (error) {
      console.error("Login error:", error);
      if (error.response && error.response.data && error.response.data.message) {
        setMessage(error.response.data.message);
      } else {
        setMessage("Login failed. Please check your network or try again.");
      }
    }
  };

  return (
    <div style={{ maxWidth: "400px",alignItems: "center", margin: "auto", textAlign: "center", padding: "20px", border: "1px solid #ccc", borderRadius: "8px", boxShadow: "0 2px 4px rgba(0,0,0,0.1)" }}>
      <h2>Login</h2>

      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: "15px" }}>
          <label htmlFor="role-select" style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>Select Role:</label>
          <select
            id="role-select"
            value={role}
            onChange={(e) => {
              setRole(e.target.value);
              setId(""); 
              setMessage(""); 
            }}
            required
            style={{ width: "100%", padding: "8px", borderRadius: "4px", border: "1px solid #ddd" }}
          >
            <option value=""> Login as </option>
            <option value="student">Student</option>
            <option value="faculty">Faculty</option>
            <option value="admin">Admin</option>
          </select>
        </div>

        {role && (
          <div style={{ marginBottom: "15px" }}>
            <label htmlFor="id-input" style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
                {role === "student" ? "USN:" : "Email:"}
            </label>
            <input
              id="id-input"
              type={role === "student" ? "text" : "email"}
              placeholder={role === "student" ? "Enter your USN" : "Enter your Email"}
              value={id}
              onChange={(e) => setId(e.target.value)}
              required
              style={{ width: "100%", padding: "8px", borderRadius: "4px", border: "1px solid #ddd" }}
            />
          </div>
        )}

        <div style={{ marginBottom: "20px" }}>
          <label htmlFor="password-input" style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>Password:</label>
          <input
            id="password-input"
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{ width: "100%", padding: "8px", borderRadius: "4px", border: "1px solid #ddd" }}
          />
        </div>

        <button
          type="submit"
          style={{
            width: "100%",
            padding: "10px",
            backgroundColor: "#007bff",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
            fontSize: "16px"
          }}
        >
          Login
        </button>
      </form>

      {message && <p style={{ marginTop: "20px", color: message.includes("successful") ? "green" : "red" }}>{message}</p>}
    </div>
  );
};

export default Login;
