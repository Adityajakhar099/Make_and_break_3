import axios from "axios";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

const api = axios.create({
  baseURL: API_BASE,
});

export async function listBoards() {
  const r = await api.get("/boards");
  return r.data;
}

export async function createBoard(title) {
  const r = await api.post("/boards", { title });
  return r.data;
}

export async function listTasks(board_id = null) {
  const r = await api.get("/tasks", { params: board_id ? { board_id } : {} });
  return r.data;
}

export async function createTask(payload) {
  const r = await api.post("/tasks", payload);
  return r.data;
}

export async function patchTask(id, payload) {
  const r = await api.patch(`/tasks/${id}`, payload);
  return r.data;
}
