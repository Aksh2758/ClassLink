export default function StudentList({ students, setStudents }) {

  const toggleStatus = (index) => {
    const updated = [...students];
    updated[index].status = updated[index].status === "P" ? "A" : "P";
    setStudents(updated);
  };

  return (
    <table style={{ width: "100%", marginTop: 20, borderCollapse: "collapse" }}>
      <thead>
        <tr>
          <th>USN</th>
          <th>Name</th>
          <th>Status</th>
        </tr>
      </thead>

      <tbody>
        {students.map((s, i) => (
          <tr key={s.user_id} style={{ borderBottom: "1px solid #ccc" }}>
            <td>{s.usn}</td>
            <td>{s.name}</td>
            <td>
              <button
                onClick={() => toggleStatus(i)}
                style={{
                  padding: "5px 10px",
                  background: s.status === "P" ? "lightgreen" : "lightcoral",
                  border: "none",
                  cursor: "pointer"
                }}
              >
                {s.status}
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
