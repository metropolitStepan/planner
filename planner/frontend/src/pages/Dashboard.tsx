export default function Dashboard({ goto }: { goto: (p: any) => void }) {
  return (
    <div style={{ maxWidth: 800, margin: "0 auto", textAlign: "center" }}>
      <h2 style={{ marginBottom: 16 }}>Как работает планировщик:</h2>
      <ol style={{ textAlign: "left", display: "inline-block", marginBottom: 24, lineHeight: 1.6 }}>
        <li><strong>Загрузите</strong> входные данные - файл в формате <code>XLSX</code> или <code>CSV</code>.</li>
        <li><strong>Задайте</strong> параметры расписания - корты, интервалы, перерывы и другие настройки.</li>
        <li><strong>Сформируйте</strong> расписание автоматически одним нажатием кнопки.</li>
      </ol>
    </div>
  );
}
