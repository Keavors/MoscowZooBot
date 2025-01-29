def calculate_result(scores):
    """Определяет тотемное животное на основе баллов."""
    return max(scores, key=scores.get)

def update_scores(scores, question_weights):
    """Обновляет баллы на основе ответа пользователя."""
    for animal, weight in question_weights.items():
        scores[animal] += weight
    return scores