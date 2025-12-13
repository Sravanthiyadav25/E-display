import React, { useEffect, useState } from "react";
import mqtt from "mqtt";
import "./styles.css";
import TimetableView from "./TimetableView";

import collegeLogo from "./assets/college_logo.png";
import naacLogo from "./assets/naac_logo.png";

export default function Display() {
  const [now, setNow] = useState(new Date());
  const [week, setWeek] = useState({});

  /* ===== GET CLASS FROM URL ===== */
  const params = new URLSearchParams(window.location.search);
  const className = params.get("class") || "CSEA";

  const periods = [
    "9:00am-10:00am",
    "10:00am-10:50am",
    "10:50-11:00",
    "11:00am-11:50am",
    "11:50am-12:40pm",
    "12:40-1:30",
    "1:30pm-2:20pm",
    "2:20pm-3:10pm",
    "3:10pm-4:00pm",
  ];

  /* ===== LIVE CLOCK ===== */
  useEffect(() => {
    const t = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  /* ======================================================
     1️⃣ LOAD SAVED TIMETABLE FROM BACKEND (REST)
     ====================================================== */
  useEffect(() => {
    fetch(`http://localhost:5000/api/timetable/${className}`)
      .then((res) => res.json())
      .then((data) => {
        console.log("📘 REST timetable loaded:", data);

        const rawWeek = data.week || data;
        const normalizedWeek = {};

        Object.keys(rawWeek || {}).forEach((day) => {
          normalizedWeek[day] = rawWeek[day].map((slot) =>
            typeof slot === "string"
              ? { subject: slot, professor: "" }
              : slot
          );
        });

        setWeek(normalizedWeek);
      })
      .catch((err) =>
        console.error("❌ Failed to load timetable from REST", err)
      );
  }, [className]);

  /* ======================================================
     2️⃣ MQTT SUBSCRIBER (LIVE UPDATES)
     ====================================================== */
  useEffect(() => {
    const client = mqtt.connect(
      "wss://db89b31f17b343648adedb9f54f0aa40.s1.eu.hivemq.cloud:8884/mqtt",
      {
        username: "E-display",
        password: "Sphoorthy1",
        reconnectPeriod: 2000,
      }
    );

    client.on("connect", () => {
      console.log("✅ Subscriber MQTT connected");
      const topic = `edisplay/timetable/${className}`;
      console.log("📡 Subscribed to:", topic);
      client.subscribe(topic);
    });

    client.on("message", (topic, message) => {
      try {
        const payload = JSON.parse(message.toString());
        console.log("📩 MQTT PAYLOAD:", payload);

        const rawWeek = payload.week;
        if (!rawWeek) return;

        const normalizedWeek = {};
        Object.keys(rawWeek).forEach((day) => {
          normalizedWeek[day] = rawWeek[day].map((slot) =>
            typeof slot === "string"
              ? { subject: slot, professor: "" }
              : slot
          );
        });

        setWeek(normalizedWeek);
      } catch (err) {
        console.error("❌ MQTT parse error", err);
      }
    });

    return () => client.end();
  }, [className]);

  const currentDay = now.toLocaleDateString(undefined, { weekday: "long" });
  const currentIdx = null; // (can be added later)

  return (
    <div className="screen">
      {/* ===== HEADER ===== */}
      <div className="top-header">
        <img src={collegeLogo} className="logo" alt="college" />
        <div className="college-title">SPHOORTHY ENGINEERING COLLEGE</div>
        <img src={naacLogo} className="logo" alt="naac" />
      </div>

      {/* ===== ACADEMIC BAR ===== */}
      <div className="academic-bar">
        {className} 2ND YEAR B.TECH 1ST SEMESTER ACADEMIC YEAR: 2024–2025
      </div>

      {/* ===== INFO STRIP ===== */}
      <div className="info-strip">
        <div className="info green">
          CLASS INCHARGE : DR. KAJA MASTHAN AND D. MAMATHA REDDY
        </div>

        <div className="info yellow">Lecture Hall : 406</div>

        <div className="info yellow">
          {now.toLocaleTimeString()} |{" "}
          {now.toLocaleDateString(undefined, {
            weekday: "long",
            day: "2-digit",
            month: "long",
            year: "numeric",
          })}
        </div>
      </div>

      {/* ===== NOTICE ===== */}
      <div className="notice-bar">
        <div className="notice-text">
          Tomorrow is a holiday • Tomorrow is a holiday • Tomorrow is a holiday
        </div>
      </div>

      {/* ===== TIMETABLE ===== */}
      <div className="timetable-area">
        <TimetableView
          periods={periods}
          week={week}
          currentDay={currentDay}
          currentIdx={currentIdx}
        />
      </div>

      {/* ===== EVENTS + CLOCK ===== */}
      <div className="bottom-panel">
        <div className="events-panel">
          <div className="events-title">📅 Upcoming Events</div>
          <div className="events-buttons">
            <div className="event-btn">Seminar</div>
            <div className="event-btn">Workshop</div>
            <div className="event-btn">Exam</div>
          </div>
        </div>

        <div className="clock-panel">
          <div className="clock">{now.toLocaleTimeString()}</div>
        </div>
      </div>
    </div>
  );
}
