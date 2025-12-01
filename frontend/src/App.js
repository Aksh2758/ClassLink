import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./components/Login";
import StudentDashboard from "./components/student/Dashboard";
import FacultyDashboard from "./components/faculty/Dashboard";
import CircularDetails from "./components/faculty/CircularDetails";


function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/student/dashboard" element={<StudentDashboard />} />
        <Route path="/faculty/dashboard" element={<FacultyDashboard />} />
        <Route path="/circulars/:circular_id" element={<CircularDetails />} />
      </Routes>
    </Router>
  );
}

export default App;