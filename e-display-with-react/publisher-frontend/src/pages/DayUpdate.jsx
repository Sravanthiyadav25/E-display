import React, { useEffect, useState } from "react";
import { getTimetable, saveTimetable, publishTimetable } from "../utils/api";
import { useParams, useNavigate } from "react-router-dom";

export default function DayUpdate() {
  const { classname, day } = useParams();
  const nav = useNavigate();
  const [data, setData] = useState(null);
  const [publishing, setPublishing] = useState(false);

  useEffect(() => {
    getTimetable(classname).then(setData).catch((e) => {
      console.error(e);
      alert("Failed to load timetable");
    });
  }, [classname]);

  const updateCell = (idx, value) => {
    setData((prev) => {
      const next = { ...prev, week: { ...prev.week } };
      next.week[day] = [...next.week[day]];
      next.week[day][idx] = value;
      next.updatedAt = new Date().toISOString();
      return next;
    });
  };

  const onPublishDay = async () => {
    // Save full timetable first (so backend store is updated)
    await saveTimetable(classname, data);
    setPublishing(true);
    // Optionally you could publish only day-specific payload, but we are publishing full timetable for simplicity
    await publishTimetable(classname, data);
    setPublishing(false);
    alert(`${day} updated and published`);
  };

  if (!data) return <div>Loading...</div>;

  return (
    <div style={{ maxWidth: 800, margin: "0 auto" }}>
      <h2>Day Update — {classname} — {day}</h2>

      <div style={{ marginTop: 12 }}>
        {data.periods.map((p, idx) => (
          <div key={idx} style={{ display: "flex", gap: 12, alignItems: "center", marginBottom: 8 }}>
            <div style={{ minWidth: 110, color: "#666" }}>{p}</div>
            <input value={data.week[day][idx] || ""} onChange={(e) => updateCell(idx, e.target.value)} style={{ flex: 1, padding: 8, borderRadius: 6, border: "1px solid #ddd" }} />
          </div>
        ))}
      </div>

      <div style={{ marginTop: 18 }}>
        <button onClick={() => nav(-1)} style={{ ...primaryBtn, marginRight: 8 }}>Back</button>
        <button onClick={onPublishDay} style={primaryBtn} disabled={publishing}>{publishing ? "Publishing..." : "Publish Day"}</button>
      </div>
    </div>
  );
}

const primaryBtn = { padding: "8px 12px", background: "#0ea5e9", color: "#fff", border: "none", borderRadius: 6, cursor: "pointer" };
