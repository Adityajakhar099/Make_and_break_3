import React, { useEffect, useState } from "react";
import { listBoards, listTasks, createBoard, createTask, patchTask } from "../services/api";
import TaskCard from "./TaskCard";

export default function Kanban() {
  const [boards, setBoards] = useState([]);
  const [currentBoard, setCurrentBoard] = useState(null);
  const [columns, setColumns] = useState({ todo: [], doing: [], done: [] });
  const [ws, setWs] = useState(null);

  useEffect(() => {
    (async () => {
      const b = await listBoards();
      setBoards(b);
      if (b.length) setCurrentBoard(b[0]);
    })();
  }, []);

  useEffect(() => {
    if (!currentBoard) return;
    (async () => {
      const tasks = await listTasks(currentBoard.id);
      setColumns({ todo: tasks.filter(t=>t.status==="todo"), doing: tasks.filter(t=>t.status==="doing"), done: tasks.filter(t=>t.status==="done") });
    })();
    // setup ws
    const socket = new WebSocket(`ws://localhost:8000/ws/${currentBoard.id}`);
    socket.onmessage = (ev) => {
      const data = JSON.parse(ev.data);
      if (data.type === "task_created" || data.type === "task_updated") {
        // refresh
        listTasks(currentBoard.id).then(tasks => setColumns({ todo: tasks.filter(t=>t.status==="todo"), doing: tasks.filter(t=>t.status==="doing"), done: tasks.filter(t=>t.status==="done") }));
      }
    }
    setWs(socket);
    return () => socket.close();
  }, [currentBoard]);

  const addBoard = async () => {
    const title = prompt("Board title");
    if (!title) return;
    const b = await createBoard(title);
    setBoards(prev => [...prev, b]);
    setCurrentBoard(b);
  }

  const addTask = async () => {
    const title = prompt("Task title");
    if (!title) return;
    const t = await createTask({ title, board_id: currentBoard.id });
    // refresh
    const tasks = await listTasks(currentBoard.id);
    setColumns({ todo: tasks.filter(t=>t.status==="todo"), doing: tasks.filter(t=>t.status==="doing"), done: tasks.filter(t=>t.status==="done") });
    // broadcast via ws is done on backend
  }

  const moveTask = async (task, newStatus) => {
    await patchTask(task.id, { status: newStatus });
    const tasks = await listTasks(currentBoard.id);
    setColumns({ todo: tasks.filter(t=>t.status==="todo"), doing: tasks.filter(t=>t.status==="doing"), done: tasks.filter(t=>t.status==="done") });
  }

  return (
    <div style={{padding: 20, fontFamily: "Inter, Arial", background: "#0b1220", minHeight: "100vh", color: "#fff"}}>
      <h1>FlowSpace — Minimal Kanban</h1>
      <div style={{marginBottom: 12}}>
        <button onClick={addBoard}>+ New Board</button>
        <button onClick={addTask} disabled={!currentBoard} style={{marginLeft: 8}}>+ New Task</button>
        <select style={{marginLeft: 8}} onChange={(e)=> {
          const id = e.target.value;
          const b = boards.find(bb => String(bb.id) === String(id));
          setCurrentBoard(b);
        }} value={currentBoard?.id || ""}>
          {boards.map(b => <option key={b.id} value={b.id}>{b.title}</option>)}
        </select>
      </div>

      <div style={{display: "flex", gap: 12, alignItems: "flex-start"}}>
        {["todo","doing","done"].map(col => (
          <div key={col} style={{flex:1, minWidth: 250}}>
            <h3 style={{textTransform:"uppercase"}}>{col}</h3>
            <div style={{minHeight: 200}}>
              {columns[col].map(t => <TaskCard key={t.id} task={t} onMove={moveTask} />)}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
