import { useEffect, useState } from "react";
import { fetchSchedule } from "../api/client";
import type { PlanResponse } from "../api/types";
import ScheduleTable from "../components/ScheduleTable";
import Loading from "../components/Loading";

export default function ScheduleView({planId}:{planId:string|null}) {
  const [data, setData] = useState<PlanResponse | null>(null);
  const [loading,setLoading] = useState(false);
  const [err,setErr] = useState<string|null>(null);

  useEffect(()=>{
    if (!planId) return;
    setLoading(true); setErr(null);
    fetchSchedule(planId).then(setData).catch(e=>setErr(e.message)).finally(()=>setLoading(false));
  },[planId]);

  if (!planId) return <div>Нет активного плана</div>;
  if (loading) return <Loading />;
  if (err) return <div>Ошибка: {err}</div>;
  if (!data) return null;

  const courts = Object.fromEntries((data.slots ?? []).map(s=>[s.courtId, s.courtId]));
  const groups = Object.fromEntries((data.slots ?? []).map(s=>[s.groupId, s.groupId]));

  return (
    <div>
      <h2>Расписание на {data.date}</h2>
      <ScheduleTable slots={data.slots} courts={courts} groups={groups} />
    </div>
  );
}
