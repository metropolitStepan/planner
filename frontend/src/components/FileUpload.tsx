import { useState } from "react";
import { uploadFile } from "../api/client";

export default function FileUpload() {
  const [status, setStatus] = useState<string>("");

  async function onChange(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    if (!f) return;
    setStatus("Загрузка...");
    try {
      const res = await uploadFile(f);
      setStatus(`Загружено: ${res.filename}`);
    } catch (e:any) {
      setStatus(`Ошибка: ${e.message}`);
    }
  }
  return (
    <div>
      <input type="file" accept=".xlsx,.csv" onChange={onChange} />
      <p>{status}</p>
    </div>
  );
}
