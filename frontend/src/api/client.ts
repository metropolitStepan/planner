import axios from "axios";
import type { PlanRequest, PlanResponse } from "./types";

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

export async function health() {
  const { data } = await axios.get(`${API_BASE}/health`);
  return data;
}

export async function uploadFile(file: File) {
  const form = new FormData();
  form.append("file", file);
  const { data } = await axios.post(`${API_BASE}/upload`, form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data as { uploadId: string; filename: string; path: string };
}

export async function planSchedule(payload: PlanRequest) {
  const { data } = await axios.post(`${API_BASE}/schedule/plan`, payload, {
    headers: { "Content-Type": "application/json" },
  });
  return data as PlanResponse;
}

export async function fetchSchedule(id: string) {
  const { data } = await axios.get(`${API_BASE}/schedule/${id}`);
  return data as PlanResponse;
}
