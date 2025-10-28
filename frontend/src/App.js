import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./components/Login";
import StudentDashboard from "./student/StudentDashboard";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/student/StudentDashboard" element={<StudentDashboard />} />
      </Routes>
    </Router>
  );
}

export default App;
