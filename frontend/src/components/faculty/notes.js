import React, { useState } from "react"; 
import axios from "axios";
import "./NotesUpload.css"; 

const NotesUpload = ({ FacultyId }) => { 
  const [subjectCode, setSubjectCode] = useState("");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [file, setFile] = useState(null);
  const [fileName, setFileName] = useState("No file selected"); 
  const [message, setMessage] = useState("");

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    setFileName(selectedFile ? selectedFile.name : "No file selected");
  };

  const handleUpload = async (e) => {
    const authToken = localStorage.getItem('token');

    if (!authToken) {
        setMessage("Upload failed: User not logged in. Please log in first.");
        console.error("No authentication token found. User is not logged in.");
        return; 
    }
    e.preventDefault();
    if (!file) {
      setMessage("Please select a file first!");
      return;
    }
    if (!subjectCode || !title) {
        setMessage("Please fill in Subject Code and Title.");
        return;
    }

    const formData = new FormData();
    formData.append("subject_code", subjectCode);
    formData.append("title", title);
    formData.append("description", description);
    formData.append("file", file);
    formData.append("faculty_id", FacultyId);

    try {
      const res = await axios.post("http://localhost:5000/api/notes/upload", formData, {
        headers: { "Content-Type": "multipart/form-data", "Authorization": `Bearer ${authToken}` },
      });
      setMessage(res.data.message || "Upload successful!");
      setSubjectCode("");
      setTitle("");
      setDescription("");
      setFile(null);
      setFileName("No file selected");
    } catch (err) {
      console.error(err);
      setMessage("Upload failed: " + (err.response?.data?.error || err.message));
    }
  };

  return (
    <div className="notes-upload-container">
      <h1>Upload Study Notes</h1>
      <form onSubmit={handleUpload} className="notes-upload-form">
        <div className="form-group file-upload-wrapper">
          <input
            type="file"
            id="file-input"
            className="file-input"
            onChange={handleFileChange}
            required
          />
          <label htmlFor="file-input" className="choose-file-button">
            Choose File
          </label>
          <span className="file-name">{fileName}</span>
        </div>

        <div className="form-group">
          <input
            type="text"
            placeholder="Title (e.g., Lecture 1 Notes)"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="input-field"
            required
          />
        </div>

        <div className="form-group">
          <textarea
            placeholder="Description (Optional, e.g., Covers chapters 1-3)"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="input-field textarea-field"
          ></textarea>
        </div>

        <div className="form-group">
            <input
              type="text"
              placeholder="Subject Code (e.g., CS101)"
              value={subjectCode}
              onChange={(e) => setSubjectCode(e.target.value)}
              className="input-field"
              required
            />
        </div>

        <button type="submit" className="upload-button">
          Upload Notes
        </button>
      </form>

      {message && <p className="message">{message}</p>}
    </div>
  );
};

export default NotesUpload;