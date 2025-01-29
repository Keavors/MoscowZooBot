import random
from data.animals import ANIMAL_RANGES
import logging

def calculate_result(total_score: int, excluded_animals: set) -> str:
    candidates = {}
    for animal, (min_s, max_s) in ANIMAL_RANGES.items():
        if animal not in excluded_animals and min_s <= total_score <= max_s:
            candidates[animal] = (max_s - min_s) - abs(total_score - (min_s + max_s) / 2)

    if candidates:
        return max(candidates, key=candidates.get)

    distances = {}
    for animal, (min_s, max_s) in ANIMAL_RANGES.items():
        if animal not in excluded_animals:
            avg = (min_s + max_s) / 2
            distances[animal] = abs(total_score - avg)

    return min(distances, key=distances.get) if distances else "Амурский тигр"  # Резервное значение

def update_scores(scores: dict, question_weights: dict) -> dict:
    updated = {}
    for animal in scores:
        weight = question_weights.get(animal, 0)
        updated[animal] = min(scores[animal] + weight, 300)
    logging.debug(f"Scores updated: {updated}")  # Используем логирование вместо print
    return updated