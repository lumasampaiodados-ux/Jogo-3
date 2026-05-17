# ranking.py — Camada de ranking (banco + estado em jogo)

from database import init_db, save_score, get_top, get_best_score


class RankingManager:
    """Interface simples para o sistema de ranking."""

    def __init__(self):
        init_db()
        self._best = get_best_score() or 0

    @property
    def best_score(self) -> int:
        return self._best

    def submit(self, name: str, score: int, avatar: int = 0):
        save_score(name, score, avatar)
        if score > self._best:
            self._best = score

    def top(self, n: int = 5) -> list:
        return get_top(n)
