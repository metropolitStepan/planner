export default function Loading({text="Загрузка..."}:{text?:string}) {
  return <div style={{opacity:.7}}>{text}</div>;
}
