export default function ErrorBanner({message}:{message:string}) {
  return <div style={{background:"#ffe6e6", padding:8, border:"1px solid #f99"}}>Ошибка: {message}</div>;
}
