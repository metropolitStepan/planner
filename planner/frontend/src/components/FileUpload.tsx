import { useState } from "react";
import { uploadFile } from "../api/client";
import "../styles/custom.css";

export default function FileUpload() {
  const [status, setStatus] = useState<string>("");
  const [dragActive, setDragActive] = useState(false);
  const [uploaded, setUploaded] = useState(false);

  async function handleFile(file: File) {
    setStatus("Загрузка...");
    setUploaded(false);
    try {
      const res = await uploadFile(file);
      setStatus(`Загружено: ${res.filename}`);
      setUploaded(true);
    } catch (e: any) {
      setStatus(`Ошибка: ${e.message}`);
      setUploaded(false);
    }
  }

  function onChange(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    if (f) handleFile(f);
  }

  function handleDrag(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(e.type === "dragenter" || e.type === "dragover");
  }

  function handleDrop(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  }

  return (
    <div
      className={`drop-zone ${dragActive ? "dragover" : ""} ${uploaded ? "uploaded" : ""
        }`}
      onDragEnter={handleDrag}
      onDragOver={handleDrag}
      onDragLeave={handleDrag}
      onDrop={handleDrop}
      onClick={() => document.getElementById("fileInput")?.click()}
    >
      <p>
        Перетащите сюда файл или <strong>нажмите, чтобы выбрать</strong>
      </p>
      <small>(поддерживаются .xlsx и .csv)</small>

      <input
        id="fileInput"
        type="file"
        accept=".xlsx,.csv"
        onChange={onChange}
        style={{ display: "none" }}
      />

      {status && <p style={{ marginTop: "1.2rem", color: "#000000ff" }}>{status}</p>}
    </div>
  );
}
