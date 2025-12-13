import React from "react";
import { Routes, Route, Link } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import ClassSelect from "./pages/ClassSelect";
import EmptyTimetable from "./pages/EmptyTimetable";
import WeekUpdate from "./pages/WeekUpdate";
import DayUpdate from "./pages/DayUpdate";

export default function App() {
  return (
    <div>
      <nav style={{ padding: 12, background: "#0f172a", color: "#fff", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div style={{ fontWeight: 700 }}>E-Display • Publisher</div>
        <div>
          <Link to="/" style={{ color: "#fff", marginRight: 12 }}>Dashboard</Link>
          <Link to="/class-select/empty" style={{ color: "#fff", marginRight: 12 }}>Empty Timetable</Link>
          <Link to="/class-select/update" style={{ color: "#fff" }}>Update Timetable</Link>
        </div>
      </nav>

      <main style={{ padding: 20 }}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/class-select/:mode" element={<ClassSelect />} />
          <Route path="/empty/:classname" element={<EmptyTimetable />} />
          <Route path="/week/:classname" element={<WeekUpdate />} />
          <Route path="/day/:classname/:day" element={<DayUpdate />} />
          <Route path="*" element={<div>Page not found</div>} />
        </Routes>
      </main>
    </div>
  );
}
