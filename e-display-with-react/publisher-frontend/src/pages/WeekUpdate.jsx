import React, { useEffect, useState } from "react";
import { getTimetable, saveTimetable, publishTimetable } from "../utils/api";
import { useParams } from "react-router-dom";

export default function WeekUpdate() {
  const { classname } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [publishing, setPublishing] = useState(false);

  useEffect(() => {
    getTimetable(classname)
      .then((d) => setData(d))
      .catch((e) => {
        console.error(e);
        alert("Failed to load timetable");
      })
      .finally(() => setLoading(false));
  }, [classname]);

  const updateCell = (day, idx, value) => {
    setData((prev) => {
      const next = { ...prev, week: { ...prev.week } };
      next.week[day] = [...next.week[day]];
      next.week[day][idx] = value;
      next.updatedAt = new Date().toISOString();
      return next;
    });
  };

  const onSaveAndPublish = async () => {
    await saveTimetable(classname, data);
    setPublishing(true);
    await publishTimetable(classname, data);
    setPublishing(false);
    alert("Week updated and published");
  };

  if (loading || !data) return <div>Loading...</div>;

  return (
    <div style={{ maxWidth: 1000, margin: "0 auto" }}>
      <h2>Week Update — {classname}</h2>
      <p style={{ color: "#666" }}>Edit any slot in the week and publish when done.</p>

      <div style={{ overflowX: "auto", marginTop: 12 }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr>
              <th style={thStyle}>Period</th>
              {Object.keys(data.week).map((day) => <th key={day} style={thStyle}>{day}</th>)}
            </tr>
          </thead>
          <tbody>
            {data.periods.map((period, idx) => (
              <tr key={idx}>
                <td style={tdStyle}>{period}</td>
                {Object.keys(data.week).map((day) => (
                  <td key={day} style={tdStyle}>
                    <input
                      value={data.week[day][idx]}
                      onChange={(e) => updateCell(day, idx, e.target.value)}
                      style={{ width: "100%", padding: 6, borderRadius: 6, border: "1px solid #ddd" }}
                    />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div style={{ marginTop: 16 }}>
        <button onClick={onSaveAndPublish} style={primaryBtn} disabled={publishing}>{publishing ? "Publishing..." : "Save & Publish"}</button>
      </div>
    </div>
  );
}

const thStyle = { textAlign: "left", padding: 8, borderBottom: "1px solid #eee", background: "#f8fafc" };
const tdStyle = { padding: 8, borderBottom: "1px solid #f1f5f9", verticalAlign: "top" };
const primaryBtn = { padding: "8px 14px", background: "#06b6d4", color: "#fff", border: "none", borderRadius: 6, cursor: "pointer" };
