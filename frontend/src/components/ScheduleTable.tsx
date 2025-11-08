import type { Slot } from "../api/types";

type Props = { slots: Slot[], courts: Record<string,string>, groups: Record<string,string> };

export default function ScheduleTable({ slots, courts, groups }: Props) {
  if (!slots.length) return <div>Расписание пусто</div>;
  return (
    <table border={1} cellPadding={6} style={{width:"100%"}}>
      <thead>
        <tr>
          <th>Время (начало–конец)</th>
          <th>Площадка</th>
          <th>Группа</th>
          <th>Дисциплина</th>
          <th>Судья</th>
          <th>Комментарий</th>
        </tr>
      </thead>
      <tbody>
        {slots.map((s, i)=>(
          <tr key={i}>
            <td>{s.start}—{s.end}</td>
            <td>{courts[s.courtId] ?? s.courtId}</td>
            <td>{groups[s.groupId] ?? s.groupId}</td>
            <td>{s.item ?? ""}</td>
            <td>{s.judge ?? ""}</td>
            <td>{s.comment ?? ""}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
