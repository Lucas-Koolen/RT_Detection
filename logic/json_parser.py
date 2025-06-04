import json
from config.config import STACKASSIST_JSON_PATH, MATCH_TOLERANCE

with open(STACKASSIST_JSON_PATH, "r") as f:
    STACK_DATA = json.load(f)

def match_dimensions(length, width, height):
    measured = sorted([length, width, height])
    best_match = None
    lowest_total_error = float("inf")

    for item in STACK_DATA:
        try:
            dims = sorted([
                item["length_mm"],
                item["width_mm"],
                item["height_mm"]
            ])
            diffs = [abs(a - b) / b for a, b in zip(measured, dims)]

            if all(d <= MATCH_TOLERANCE for d in diffs):
                total_error = sum(diffs)
                if total_error < lowest_total_error:
                    lowest_total_error = total_error
                    best_match = item.get("product_id")

        except Exception as e:
            print(f"⚠️ Fout bij vergelijken met item: {item}")
            continue

    return best_match, best_match is not None
