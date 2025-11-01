import React from "react";

export default function TaskCard({ task, onMove }) {
  return (
    <div style={{
      padding: 8,
      borderRadius: 8,
      background: "#111827",
      color: "#fff",
      marginBottom: 8,
      boxShadow: "0 2px 8px rgba(0,0,0,0.3)"
    }}>
      <div style={{fontWeight: 700}}>{task.title}</div>
      <div style={{fontSize: 12, opacity: 0.8}}>{task.description}</div>
      <div style={{marginTop: 6, display: "flex", gap: 6}}>
        <button onClick={() => onMove && onMove(task, "todo")}>To Do</button>
        <button onClick={() => onMove && onMove(task, "doing")}>Doing</button>
        <button onClick={() => onMove && onMove(task, "done")}>Done</button>
      </div>
    </div>
  );
}
