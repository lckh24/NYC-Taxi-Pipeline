from ingestion.batch import Batch
from ingestion.download import download_batch
from ingestion.load import load_raw_batch
from ingestion.validate import validate_raw_file


def main() -> None:
    batch = Batch("green", 2025, 2)
    raw_path = download_batch(batch)
    result = validate_raw_file(batch, raw_path)
    if result.is_valid:
        print("Batch is valid.")
        row_count = load_raw_batch(batch, raw_path)
        print(f"Loaded {row_count:,} rows into DuckDB.")
    else:
        print("Batch has issues:")
        for error in result.errors:
            print(f"- {error}")

    if result.warnings:
        print("Warnings:")
        for warning in result.warnings:
            print(f"- {warning}")


if __name__ == "__main__":
    main()
