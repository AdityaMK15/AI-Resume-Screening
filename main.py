import argparse
import json

from src.pipeline import process_resumes


def main():
    parser = argparse.ArgumentParser(
        description="AI Resume Screening & Ranking System"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Directory containing resume PDFs",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path for the output JSON file",
    )

    args = parser.parse_args()

    results = process_resumes(args.input)

    with open(args.output, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=2, ensure_ascii=False)

    print("\nResume screening completed.")
    print(f"Results saved to: {args.output}")

    print("\n--- BATCH SUMMARY ---")
    print(json.dumps(results["batch_summary"], indent=2))


if __name__ == "__main__":
    main()