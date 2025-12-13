import React, { useEffect, useState } from "react";
import { getClasses } from "../utils/api";
import { useNavigate, useParams } from "react-router-dom";

export default function ClassSelect() {
  const [classes, setClasses] = useState([]);
  const nav = useNavigate();
  const { mode } = useParams(); // 'empty' or 'update'

  useEffect(() => {
    getClasses()
      .then((c) => setClasses(c))
      .catch((err) => {
        console.error("Failed to load classes", err);
        setClasses([]);
      });
  }, []);

  return (
    <div style={{ maxWidth: 800, margin: "0 auto" }}>
      <h2>Select Class ({mode === "empty" ? "Empty Timetable" : "Update Timetable"})</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: 12, marginTop: 16 }}>
        {classes.length === 0 && <div>No classes found</div>}
        {classes.map((cls) => (
          <div key={cls} style={{ padding: 12, border: "1px solid #e6e6e6", borderRadius: 8 }}>
            <div style={{ fontWeight: 700 }}>{cls}</div>
            <div style={{ marginTop: 8 }}>
              <button onClick={() => nav(mode === "empty" ? `/empty/${cls}` : `/week/${cls}`)} style={cardBtn}>Open</button>
              {mode === "update" && <button onClick={() => nav(`/day/${cls}/Monday`)} style={cardBtnAlt}>Day Edit</button>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

const cardBtn = { marginRight: 8, padding: "6px 10px", borderRadius: 6, border: "none", background: "#06b6d4", color: "#fff", cursor: "pointer" };
const cardBtnAlt = { padding: "6px 10px", borderRadius: 6, border: "1px solid #ccc", background: "#fff", cursor: "pointer" };
