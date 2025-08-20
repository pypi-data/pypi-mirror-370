import argparse
import json
from pathlib import Path
from typing import List, Dict, Any

from .engine.core.engine import TetrisEngine
from .engine.core.exceptions import GameOver
from .engine.sculptor.metrics import (
    calculate_final_metric,
)


class LogVerifier:
    def __init__(
        self,
        engine: TetrisEngine,
        history: List[Dict[str, Any]],
        max_score: int = 200000,
    ):
        self.engine = engine
        self.history = history
        self.max_possible_score = max_score

    def run(self) -> Dict[str, Any]:
        """Воспроизводит историю ходов и возвращает рассчитанные метрики."""
        total_lines_cleared = 0
        total_error_A = 0.0

        for i, step in enumerate(self.history):
            move = step.get("move")
            if not isinstance(move, list) or len(move) != 2:
                print(
                    f"❌ Ошибка верификации: Некорректный формат хода на шаге {i + 1}."
                )
                return {"verification_error": f"Invalid move format at step {i + 1}"}

            best_x, best_rot = move

            try:
                current_piece_type = self.engine.current_piece_type
                log_piece_type = step.get("piece_type")
                if current_piece_type != log_piece_type:
                    print(
                        f"❌ Ошибка верификации: Расхождение в типе фигуры на шаге {i + 1}."
                    )
                    print(
                        f"  - Ожидалась: {current_piece_type}, в логе: {log_piece_type}"
                    )
                    return {"verification_error": f"Piece mismatch at step {i + 1}"}

                lines_cleared = self.engine.place_piece(best_x, best_rot)
                total_lines_cleared += lines_cleared
                current_error = self.engine.get_approximation_error()
                total_error_A += current_error

            except GameOver as e:
                print(
                    f"❌ Ошибка верификации: Игра окончена на шаге {i + 1} при выполнении хода {move}."
                )
                print(f"   Причина: {e}")
                return {"verification_error": f"Game Over at step {i + 1}: {e}"}
            except Exception as e:
                print(
                    f"❌ Ошибка верификации: Критическая ошибка движка на шаге {i + 1} при выполнении хода {move}."
                )
                print(f"   Причина: {e}")
                return {"verification_error": f"Engine error at step {i + 1}: {e}"}

        total_pieces = len(self.history)
        final_error_A = total_error_A / total_pieces if total_pieces > 0 else 0.0
        final_score_S = self.engine.score

        final_metric = calculate_final_metric(
            final_score_S, final_error_A, self.max_possible_score
        )

        return {
            "seed": self.engine.seed,
            "total_pieces": len(self.history),
            "total_lines_cleared": total_lines_cleared,
            "final_score_S": final_score_S,
            "final_error_A": final_error_A,
            "final_metric": final_metric,
            "history": self.history,
        }


def run_verification(log_path: Path):
    """Верифицирует лог-файл."""
    print(f"--- Запуск верификации для файла: {log_path.name} ---")
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            original_log = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ Ошибка: Не удалось прочитать файл лога: {e}")
        return

    seed = original_log.get("seed")
    history = original_log.get("history")

    if seed is None or history is None:
        print("❌ Ошибка: В файле лога отсутствуют 'seed' или 'history'.")
        return

    # Инициализируем движок с тем же сидом
    engine = TetrisEngine(width=10, height=20, seed=seed)
    
    # Запускаем верификатор
    verifier = LogVerifier(engine, history)
    verified_results = verifier.run()

    if "verification_error" in verified_results:
        print(f"❌ Ошибка верификации: {verified_results['verification_error']}")
        return

    # Сравниваем ключевые метрики
    metrics_to_check = [
        "total_pieces",
        "total_lines_cleared",
        "final_score_S",
        "final_error_A",
        "final_metric",
    ]

    all_metrics_ok = True
    print("\n--- Сверка итоговых метрик ---")
    for key in metrics_to_check:
        val_orig = original_log.get(key)
        val_ver = verified_results.get(key)

        if val_orig is None or val_ver is None:
            print(f"  - Метрика '{key}': не найдена в одном из логов.")
            all_metrics_ok = False
            continue

        is_equal = abs(val_orig - val_ver) < 1e-9 if isinstance(val_orig, float) else val_orig == val_ver

        if is_equal:
            print(f"  ✅ {key}: OK ({val_orig})")
        else:
            print(f"  ❌ {key}: Расхождение ({val_orig} vs {val_ver})")
            all_metrics_ok = False

    print("\n--- Итог ---")
    if all_metrics_ok:
        print("✅ Верификация успешно пройдена! Лог соответствует симуляции.")
    else:
        print("❌ Верификация НЕ пройдена! Метрики в логе не совпадают.")


def main():
    parser = argparse.ArgumentParser(description="Верификация лог-файла")
    parser.add_argument("log_file", type=str, help="Путь к лог-файлу для верификации.")
    args = parser.parse_args()
    
    run_verification(Path(args.log_file))

if __name__ == "__main__":
    main()