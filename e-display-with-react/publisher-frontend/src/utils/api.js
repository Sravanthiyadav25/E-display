export const API_BASE = "http://localhost:5000";

export async function getClasses() {
  const res = await fetch(`${API_BASE}/api/classes`);
  return res.json();
}

export async function getTimetable(cls) {
  const res = await fetch(`${API_BASE}/api/timetable/${cls}`);
  return res.json();
}

export async function saveTimetable(cls, data) {
  return fetch(`${API_BASE}/api/timetable/${cls}`,{
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
}

export async function publishTimetable(cls, data) {
  const res = await fetch(`${API_BASE}/api/timetable/${cls}/publish`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    throw new Error("Publish failed");
  }

  return res.json();   // 🔥 THIS WAS MISSING
}

