import random
from collections import defaultdict
from data.animals import ANIMAL_RANGES
from utils import calculate_result

def simulate_users(num_users: int = 100000):
    results = defaultdict(int)
    score_distribution = defaultdict(int)

    animals = list(ANIMAL_RANGES.keys())
    if not animals:
        raise ValueError("ANIMAL_RANGES is empty")

    for _ in range(num_users):
        score = random.randint(50, 250)
        excluded = set()
        if random.random() < 0.2 and animals:
            excluded.add(random.choice(animals))

        animal = calculate_result(score, excluded)
        results[animal] += 1
        score_distribution[score // 10 * 10] += 1

    print("\n📊 Статистика распределения:")
    total = sum(results.values())
    for animal, count in sorted(results.items(), key=lambda x: x[1], reverse=True):
        print(f"• {animal}: {count / total * 100:.1f}%")

    print("\n📈 Распределение баллов:")
    for score_group in sorted(score_distribution):
        count = score_distribution[score_group]
        bar_length = count // (num_users // 100) if num_users >= 100 else count
        print(f"{score_group}-{score_group + 10}: {'█' * bar_length}")