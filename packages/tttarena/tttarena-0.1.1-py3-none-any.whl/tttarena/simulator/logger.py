import json
from pathlib import Path
from typing import Dict, Any

LOG_DIR = Path("run_logs")


def save_log(results: Dict[str, Any], seed: int):
    try:
        LOG_DIR.mkdir(exist_ok=True)
        run_id = len(list(LOG_DIR.glob("run*-seed*.json"))) + 1

        file_name = f"run{run_id}-seed{seed}.json"
        file_path = LOG_DIR / file_name

        results_to_save = results.copy()
        if "target_curve" in results_to_save:
            del results_to_save["target_curve"]

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(results_to_save, f, indent=4)

        print(f"Лог симуляции сохранен в: {file_path}")

    except (IOError, OSError) as e:
        print(f"Ошибка при сохранении лога: {e}")