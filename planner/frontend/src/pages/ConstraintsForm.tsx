import { useState } from "react";
import { planSchedule } from "../api/client";
import type { PlanRequest } from "../api/types";
import Loading from "../components/Loading";
import ErrorBanner from "../components/ErrorBanner";

const defaultReq: PlanRequest = {
  window: { date: "2025-10-04", startTime: "09:30", endTime: "17:00" },
  courts: [{ id: "c1", name: "Зал 1" }, { id: "c2", name: "Зал 2" }],
  groups: [
    { id: "g1", name: "Мужчины инд.", size: 20, tags:["мужчины"] },
    { id: "g2", name: "Женщины инд.", size: 18, tags:["женщины"] },
    { id: "g3", name: "Смешанные двойки", size: 10, tags:["смешанные"] },
  ],
  slotMinutes: 15,
  parallelLimit: 2,
  constraints: [
    { groupId:"g1", earliestStart:"10:00", minBreakMinutes:5 },
    { groupId:"g2", latestEnd:"16:00" },
    { groupId:"g3", notOverlapWith:["g1","g2"] }
  ],
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
      setErr(e.message ?? "Не удалось сформировать расписание");
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
