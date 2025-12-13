import React from "react";
import { useNavigate } from "react-router-dom";

export default function Dashboard() {
  const nav = useNavigate();

  return (
    <div style={{ maxWidth: 900, margin: "0 auto" }}>
      <h1 style={{ marginBottom: 8 }}>Publisher Dashboard</h1>
      <p style={{ color: "#555" }}>Choose an action to prepare or update timetables and publish to displays.</p>

      <div style={{ display: "flex", gap: 16, marginTop: 20 }}>
        <div style={{ flex: 1, padding: 20, borderRadius: 8, border: "1px solid #ddd" }}>
          <h3>Empty Timetable</h3>
          <p>Create or fill a blank timetable skeleton for a class.</p>
          <button onClick={() => nav("/class-select/empty")} style={btnStyle}>Open</button>
        </div>

        <div style={{ flex: 1, padding: 20, borderRadius: 8, border: "1px solid #ddd" }}>
          <h3>Update Timetable</h3>
          <p>Choose week update (full-week edits) or day update (single-day edits).</p>
          <button onClick={() => nav("/class-select/update")} style={btnStyle}>Open</button>
        </div>
      </div>

      <div style={{ marginTop: 32 }}>
        <h3>Quick Links</h3>
        <div style={{ display: "flex", gap: 8 }}>
          <button onClick={() => nav("/empty/CSEA")} style={smallBtn}>Open CSEA Empty</button>
          <button onClick={() => nav("/week/CSEA")} style={smallBtn}>Open CSEA Week</button>
          <button onClick={() => nav("/day/CSEA/Monday")} style={smallBtn}>Open CSEA Monday</button>
        </div>
      </div>
    </div>
  );
}

const btnStyle = {
  marginTop: 12, padding: "8px 14px", background: "#0ea5e9", color: "#fff", border: "none", borderRadius: 6, cursor: "pointer"
};

const smallBtn = { padding: "6px 10px", borderRadius: 6, border: "1px solid #ccc", cursor: "pointer" };
