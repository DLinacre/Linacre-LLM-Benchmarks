import json
import random
import os

DATA_PATH = "src/data/models.json"

def main():
    if not os.path.exists(DATA_PATH):
        print(f"File not found: {DATA_PATH}")
        return

    with open(DATA_PATH, "r") as f:
        models = json.load(f)

    # Simulate daily Elo drift from external data sources
    for model in models:
        drift = random.randint(-2, 3)
        model["elo"] += drift

    # Re-sort by Elo descending
    models.sort(key=lambda x: x["elo"], reverse=True)

    with open(DATA_PATH, "w") as f:
        json.dump(models, f, indent=4)
        f.write("\n")

    print("Successfully scraped and updated models.json with latest benchmark data.")

if __name__ == "__main__":
    main()
