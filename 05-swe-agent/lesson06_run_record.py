import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


LOG_DIR = Path(__file__).resolve().parent / "logs"


def save_run_record(result):
    record = {
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "result": result,
    }

    json_text = json.dumps(
        record,
        ensure_ascii=False,
        indent=2,
    )

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    record_path = LOG_DIR / f"run_{uuid4().hex}.json"

    with record_path.open("x", encoding="utf-8") as file:
        file.write(json_text)

    return record_path