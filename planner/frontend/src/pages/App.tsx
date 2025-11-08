import { useState } from "react";
import Dashboard from "./Dashboard";
import DataUpload from "./DataUpload";
import ConstraintsForm from "./ConstraintsForm";
import ScheduleView from "./ScheduleView";

type Page = "dashboard" | "upload" | "constraints" | "schedule";

export default function App() {
  const [page, setPage] = useState<Page>("dashboard");
  const [planId, setPlanId] = useState<string | null>(null);

  return (
    <div style={{ maxWidth: 1100, margin: "0 auto", padding: 16 }}>
      <h1>Планировщик соревнований</h1>
      <nav style={{ display: "flex", justifyContent: "center", gap: 16, marginBottom: 12 }}>
        <button onClick={() => setPage("dashboard")}>Главная</button>
        <button onClick={() => setPage("upload")}>Загрузка данных</button>
        <button onClick={() => setPage("constraints")}>Параметры</button>
        <button onClick={() => setPage("schedule")} disabled={!planId}>Расписание</button>
      </nav>

      {page === "dashboard" && <Dashboard goto={setPage} />}
      {page === "upload" && <DataUpload />}
      {page === "constraints" && <ConstraintsForm onPlanned={(id)=>{ setPlanId(id); setPage("schedule"); }} />}
      {page === "schedule" && <ScheduleView planId={planId} />}
    </div>
  );
}
