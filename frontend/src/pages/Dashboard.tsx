export default function Dashboard({goto}:{goto:(p:any)=>void}) {
  return (
    <div>
      <p>Шаги: 1) Загрузите входные данные (XLSX/CSV). 2) Задайте параметры. 3) Сформируйте расписание.</p>
      <div style={{display:"flex", gap:8}}>
        <button onClick={()=>goto("upload")}>Загрузка данных</button>
        <button onClick={()=>goto("constraints")}>Параметры</button>
      </div>
    </div>
  );
}
