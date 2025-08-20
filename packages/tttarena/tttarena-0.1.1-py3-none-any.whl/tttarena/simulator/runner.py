from typing import List, Dict, Any, Optional
import time
from tqdm.auto import tqdm

from ..engine.core.engine import TetrisEngine
from ..engine.core.exceptions import GameOver, NoValidMovesError
from ..bots.base_bot import BaseBot
from ..engine.sculptor.metrics import (
    calculate_final_metric,
)
from .visualizers.base_visualizer import BaseVisualizer 


class SimulationRunner:
    """Управляет полным циклом симуляции игры."""

    def __init__(self, engine: TetrisEngine, bot: BaseBot, max_score: int = 200000):
        self.engine = engine
        self.bot = bot
        self.max_possible_score = max_score
        self.history: List[Dict[str, Any]] = []

    def run(
        self,
        start_time: float,
        visualizer: Optional[BaseVisualizer] = None, 
    ) -> Dict[str, Any]:
        """Запускает симуляцию."""
        piece_count = 0
        total_lines_cleared = 0
        total_error_A = 0.0

        with tqdm(total=100000, desc="Simulating Game") as pbar:
            while not self.engine.game_over:
                if visualizer and not visualizer.is_running():
                    break

                current_piece = self.engine.current_piece_type
                if current_piece is None:
                    break

                try:
                    best_x, best_rot = self.bot.find_best_move(self.engine)
                except NoValidMovesError as e:
                    print(f"Игра окончена: {e}")
                    self.engine.game_over = True
                    break
                except Exception as e:
                    print(f"Ошибка в работе бота: {e}")
                    self.engine.game_over = True
                    break

                try:
                    lines_cleared = self.engine.place_piece(best_x, best_rot)
                    total_lines_cleared += lines_cleared
                    current_error = self.engine.get_approximation_error()
                    total_error_A += current_error

                    piece_count += 1
                    if piece_count >= 100000:
                        break

                    elapsed_time = time.time() - start_time
                    rps = piece_count / elapsed_time if elapsed_time > 0 else 0.0
                    
                    pbar.update(1)

                    step_info = {
                        "piece_index": piece_count,
                        "piece_type": current_piece,
                        "move": (best_x, best_rot),
                        "lines_cleared": lines_cleared,
                        "score": self.engine.score,
                    }
                    self.history.append(step_info)

                    
                    if visualizer:
                        state_for_visualizer = self.engine.get_game_state()
                        state_for_visualizer["error_A"] = current_error
                        state_for_visualizer["total_lines_cleared"] = total_lines_cleared
                        state_for_visualizer["piece_index"] = piece_count

                        elapsed_time = time.time() - start_time
                        rps = piece_count / elapsed_time if elapsed_time > 0 else 0.0
                        state_for_visualizer["rps"] = rps

                        visualizer.handle_events()
                        visualizer.update_state(state_for_visualizer)
                        visualizer.render()

                        sleep_duration = visualizer.get_speed_delay()
                        if sleep_duration > 0:
                            time.sleep(sleep_duration)

                except GameOver as e:
                    print(f"Игра окончена: {e}")
                    break
                except Exception as e:
                    print(f"Критическая ошибка движка: {e}")
                    self.engine.game_over = True
                    break
            
            if visualizer:
                visualizer.quit()

        final_error_A = total_error_A / piece_count if piece_count > 0 else 0.0
        final_score_S = self.engine.score
        final_rps = piece_count / (time.time() - start_time) if (time.time() - start_time) > 0 else 0.0

        final_metric = calculate_final_metric(
            final_score_S, final_error_A, self.max_possible_score
        )

        return {
            "seed": self.engine.seed,
            "total_pieces": piece_count,
            "total_lines_cleared": total_lines_cleared,
            "final_score_S": final_score_S,
            "final_error_A": final_error_A,
            "final_metric": final_metric,
            "final_rps": final_rps,
            "history": self.history,
        }


