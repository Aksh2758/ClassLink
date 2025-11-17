// StudentList.js
import React from 'react';

export default function StudentList({ students, setStudents }) {
  const handleStatusChange = (index, newStatus) => {
    const updatedStudents = [...students];
    updatedStudents[index].status = newStatus;
    setStudents(updatedStudents);
  };

  return (
    <div style={{ marginTop: 20 }}>
      <h3>Students for Attendance</h3>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th style={{ border: '1px solid #ddd', padding: 8 }}>USN</th>
            <th style={{ border: '1px solid #ddd', padding: 8 }}>Name</th>
            <th style={{ border: '1px solid #ddd', padding: 8 }}>Status</th>
          </tr>
        </thead>
        <tbody>
          {students.map((student, index) => (
            <tr key={student.student_id}>
              <td style={{ border: '1px solid #ddd', padding: 8 }}>{student.usn}</td>
              <td style={{ border: '1px solid #ddd', padding: 8 }}>{student.name}</td>
              <td style={{ border: '1px solid #ddd', padding: 8 }}>
                <select
                  value={student.status}
                  onChange={e => handleStatusChange(index, e.target.value)}
                >
                  <option value="P">Present</option>
                  <option value="A">Absent</option>
                </select>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}