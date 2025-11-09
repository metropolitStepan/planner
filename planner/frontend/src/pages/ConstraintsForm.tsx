import { useState } from "react";
import { planSchedule } from "../api/client";
import type { PlanRequest } from "../api/types";
import Loading from "../components/Loading";
import ErrorBanner from "../components/ErrorBanner";

const defaultReq: PlanRequest = {
  window: { date: "2025-10-04", startTime: "09:30", endTime: "17:00" },
  slotMinutes: 15,
  parallelLimit: 2,
  options: {}
};

export default function ConstraintsForm({onPlanned}:{onPlanned:(id:string)=>void}) {
  const [req, setReq] = useState<PlanRequest>(defaultReq);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function submit() {
    setLoading(true); setErr(null);
    try {
      const res = await planSchedule(req);
      onPlanned(res.id);
    } catch (e:any) {
      // Извлекаем детальное сообщение об ошибке из ответа API
      const errorMessage = e.response?.data?.detail || e.message || "Не удалось сформировать расписание";
      setErr(errorMessage);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="constraints-form">
      <h2>Параметры планирования</h2>
      <div className="constraints-grid">
        <label>Дата
          <input type="date" value={req.window.date} onChange={e=>setReq({...req, window:{...req.window, date:e.target.value}})} />
        </label>
        <label>Начало
          <input type="time" value={req.window.startTime} onChange={e=>setReq({...req, window:{...req.window, startTime:e.target.value}})} />
        </label>
        <label>Окончание
          <input type="time" value={req.window.endTime} onChange={e=>setReq({...req, window:{...req.window, endTime:e.target.value}})} />
        </label>
        <label>Длительность слота (мин)
          <input type="number" min={5} max={180} value={req.slotMinutes} onChange={e=>setReq({...req, slotMinutes:+e.target.value})}/>
        </label>
        <label>Параллельных потоков
          <input type="number" min={1} max={10} value={req.parallelLimit} onChange={e=>setReq({...req, parallelLimit:+e.target.value})}/>
        </label>
      </div>

      {err && <ErrorBanner message={err} />}
      {loading ? <Loading /> : <button onClick={submit}>Сформировать расписание</button>}
    </div>
  );
}
