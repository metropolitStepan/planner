from __future__ import annotations
import json, os, subprocess, sys, uuid
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="Planner Adapter", version="1.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SCHEDULES: Dict[str, Dict[str, Any]] = {}
UPLOADS: Dict[str, str] = {}  # uploadId -> path

# МОДЕЛИ
class TimeWindow(BaseModel):
    date: str
    startTime: str
    endTime: str

class PlanRequest(BaseModel):
    window: TimeWindow
    slotMinutes: int = Field(15, ge=5, le=180)
    parallelLimit: int = Field(1, ge=1)
    options: Dict[str, Any] = {}

class Slot(BaseModel):
    start: str
    end: str
    courtId: str
    groupId: str
    item: Optional[str] = None
    judge: Optional[str] = None
    comment: Optional[str] = None

class PlanResponse(BaseModel):
    id: str
    date: str
    slots: List[Slot]

# ВСПОМОГАТЕЛЬНОЕ
POSSIBLE_FUNCS = ["generate_schedule", "plan", "run", "main"]

def call_planner(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    1) Пытаемся импортировать planner и вызвать одну из известных функций без изменения её контракта.
    2) Если не получилось — запускаем planner.py как CLI и ждём JSON на stdout.
    """
    sys.path.insert(0, os.getcwd())
    try:
        import planner  # noqa
        for fn_name in POSSIBLE_FUNCS:
            fn = getattr(planner, fn_name, None)
            if callable(fn):
                result = fn(params)
                if isinstance(result, str):
                    result = json.loads(result)
                if result is None:
                    raise HTTPException(
                        status_code=400, 
                        detail="Не удалось построить расписание с заданными ограничениями. Возможные причины: недостаточно времени, конфликты в расписании кортов, слишком строгие временные ограничения групп. Попробуйте увеличить временное окно, добавить больше кортов или ослабить ограничения."
                    )
                if not isinstance(result, dict):
                    raise HTTPException(status_code=500, detail="planner returned non-dict")
                return result
    except HTTPException:
        raise
    except Exception:
        # падаем в CLI режим
        pass

    try:
        proc = subprocess.run(
            [sys.executable, "planner.py"],
            input=json.dumps(params).encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        out = proc.stdout.decode("utf-8").strip()
        return json.loads(out)
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"planner.py failed: {e.stderr.decode('utf-8')}")
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"planner.py did not return JSON: {str(e)}")

def hhmm_to_min(s: str) -> int:
    h, m = s.split(":")
    return int(h)*60 + int(m)

def min_to_hhmm(x: int) -> str:
    h = x // 60
    m = x % 60
    return f"{h:02d}:{m:02d}"

def timedelta_to_hhmm(td_str: str) -> str:
    """
    Преобразует формат времени из timedelta (например "9:30:00" или "09:30:00") в HH:MM (например "09:30").
    Если время уже в формате HH:MM, возвращает его без изменений.
    """
    if not td_str:
        return td_str
    
    parts = td_str.split(":")
    if len(parts) >= 2:
        try:
            h = int(parts[0])
            m = int(parts[1])
            # Если уже в формате HH:MM (2 части), возвращаем как есть
            if len(parts) == 2:
                return f"{h:02d}:{m:02d}"
            # Если в формате H:MM:SS или HH:MM:SS (3 части), преобразуем в HH:MM
            return f"{h:02d}:{m:02d}"
        except (ValueError, IndexError):
            return td_str
    return td_str

# РОУТЫ
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    content = await file.read()
    tmp_id = str(uuid.uuid4())
    tmp_path = os.path.join(os.getcwd(), f"_upload_{tmp_id}_{file.filename}")
    with open(tmp_path, "wb") as f:
        f.write(content)
    UPLOADS[tmp_id] = tmp_path
    return {"uploadId": tmp_id, "filename": file.filename, "path": tmp_path}

@app.post("/schedule/plan", response_model=PlanResponse)
def schedule_plan(req: PlanRequest):
    params = req.dict()
    params.setdefault("options", {})
    params["options"]["lastUploadPath"] = next(iter(UPLOADS.values()), None)
    
    # Проверяем, что файл был загружен
    if not params["options"]["lastUploadPath"]:
        raise HTTPException(
            status_code=400, 
            detail="Не загружен файл с данными. Пожалуйста, сначала загрузите Excel-файл на вкладке 'Загрузка данных'."
        )
    
    # Добавляем параметры restTime и evaluateTime, если они не указаны (по умолчанию 0)
    params.setdefault("restTime", 0)
    params.setdefault("evaluateTime", 0)

    raw = call_planner(params)

    slots = raw.get("slots") or []
    # Преобразуем формат времени из timedelta ("9:30:00") в HH:MM ("09:30")
    for slot in slots:
        if "start" in slot:
            slot["start"] = timedelta_to_hhmm(slot["start"])
        if "end" in slot:
            slot["end"] = timedelta_to_hhmm(slot["end"])
    
    date = raw.get("date", req.window.date)
    plan_id = str(uuid.uuid4())
    resp = {"id": plan_id, "date": date, "slots": slots}
    SCHEDULES[plan_id] = resp
    return resp

@app.get("/schedule/{plan_id}", response_model=PlanResponse)
def schedule_get(plan_id: str):
    if plan_id not in SCHEDULES:
        raise HTTPException(404, "schedule not found")
    return SCHEDULES[plan_id]
