"""Mood card queue, selection, undo, and trait profile for swipe sessions."""

from collections import deque
from typing import Any, Literal

MIN_LIKES_FOR_RECOMMENDATION = 5

ActionType = Literal["like", "skip", "custom"]


class MoodEngine:
    """Tracks mood swipes; selected moods drive trait scores (recalculated each change)."""

    def __init__(self, cards: list[dict[str, Any]] | None = None):
        self.reset(cards)

    def reset(self, cards: list[dict[str, Any]] | None = None) -> None:
        self._all_cards = list(cards or [])
        self.card_queue: deque[dict[str, Any]] = deque(self._all_cards)
        self.seen_cards: set[str] = set()
        self.selected_moods: list[dict[str, Any]] = []
        self.action_history: list[dict[str, Any]] = []
        self.accepted_traits: set[str] = set()
        self.trait_scores: dict[str, float] = {}
        self.last_feedback: str = ""
        self._recalculate_from_selected()

    @property
    def liked_count(self) -> int:
        return len(self.selected_moods)

    @property
    def is_profile_ready(self) -> bool:
        return self.liked_count >= MIN_LIKES_FOR_RECOMMENDATION

    def can_like_more(self) -> bool:
        return self.liked_count < MIN_LIKES_FOR_RECOMMENDATION

    def can_undo(self) -> bool:
        return bool(self.action_history)

    def _recalculate_from_selected(self) -> None:
        """Rebuild traits and weighted scores from the full selected mood list."""
        self.accepted_traits = set()
        self.trait_scores = {}
        for card in self.selected_moods:
            for trait in card.get("traits", []):
                self.accepted_traits.add(trait)
            for trait, weight in card.get("weights", {}).items():
                self.trait_scores[trait] = self.trait_scores.get(trait, 0) + weight

    def get_current_card(self) -> dict[str, Any] | None:
        if self.is_profile_ready:
            return None
        if not self.card_queue:
            return None
        return self.card_queue[0]

    def skip(self) -> str:
        if self.is_profile_ready:
            self.last_feedback = "Your mood profile is already complete."
            return self.last_feedback

        card = self.get_current_card()
        if card is None:
            self.last_feedback = "No more mood cards to show."
            return self.last_feedback

        self._advance_card(card)
        self.action_history.append({"action": "skip", "card": card})
        self.last_feedback = f"Mood skipped: {card['title']}"
        return self.last_feedback

    def like(self) -> str:
        if not self.can_like_more():
            self.last_feedback = "Your mood profile is already complete."
            return self.last_feedback

        card = self.get_current_card()
        if card is None:
            self.last_feedback = "No more mood cards to show."
            return self.last_feedback

        self.selected_moods.append(card)
        self._advance_card(card)
        self.action_history.append({"action": "like", "card": card})
        self._recalculate_from_selected()
        self.last_feedback = f"Mood accepted: {card['title']}"
        return self.last_feedback

    def add_custom_mood(self, card: dict[str, Any]) -> str:
        if not self.can_like_more():
            self.last_feedback = "Your mood profile is already complete."
            return self.last_feedback

        self.selected_moods.append(card)
        self.action_history.append({"action": "custom", "card": card})
        self._recalculate_from_selected()
        self.last_feedback = f"Custom mood added: {card['title']}"
        return self.last_feedback

    def remove_selected(self, card_id: str) -> str:
        card = next((c for c in self.selected_moods if c["id"] == card_id), None)
        if card is None:
            self.last_feedback = "Could not find that mood."
            return self.last_feedback

        self.selected_moods = [c for c in self.selected_moods if c["id"] != card_id]
        self._recalculate_from_selected()

        if not card.get("is_custom"):
            self.seen_cards.discard(card["id"])
            if not any(c["id"] == card["id"] for c in self.card_queue):
                self.card_queue.appendleft(card)

        self.last_feedback = f"Removed mood: {card['title']}"
        return self.last_feedback

    def undo(self) -> str:
        if not self.action_history:
            self.last_feedback = "Nothing to undo."
            return self.last_feedback

        last = self.action_history.pop()
        card = last["card"]
        action: ActionType = last["action"]

        if action in ("like", "custom"):
            self.selected_moods = [c for c in self.selected_moods if c["id"] != card["id"]]
            self._recalculate_from_selected()
            if action == "like":
                self.seen_cards.discard(card["id"])
                if not any(c["id"] == card["id"] for c in self.card_queue):
                    self.card_queue.appendleft(card)
            self.last_feedback = f"Undid: {card['title']}"
        elif action == "skip":
            self.seen_cards.discard(card["id"])
            if not any(c["id"] == card["id"] for c in self.card_queue):
                self.card_queue.appendleft(card)
            self.last_feedback = f"Undid skip: {card['title']}"

        return self.last_feedback

    def _advance_card(self, card: dict[str, Any]) -> None:
        self.seen_cards.add(card["id"])
        if self.card_queue and self.card_queue[0]["id"] == card["id"]:
            self.card_queue.popleft()

    def can_recommend(self) -> bool:
        return self.is_profile_ready

    def get_top_traits(self, limit: int = 5) -> list[tuple[str, float]]:
        ranked = sorted(self.trait_scores.items(), key=lambda item: item[1], reverse=True)
        return ranked[:limit]

    def progress_label(self) -> str:
        if self.is_profile_ready:
            return "Mood profile ready"
        return f"{self.liked_count} of {MIN_LIKES_FOR_RECOMMENDATION} liked moods selected"
