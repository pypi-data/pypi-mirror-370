#!/usr/bin/env python3
"""
Script to count annotations by category name in multiple COCO JSON files.
"""

import argparse
import json
from collections import Counter
from pathlib import Path


def count_annotations_by_category(coco_file_path):
    """
    Count annotations by category name in a COCO JSON file.

    Args:
        coco_file_path (str): Path to the COCO JSON file

    Returns:
        dict: Dictionary with category names as keys and annotation counts as values
    """
    # Read the COCO JSON file
    with open(coco_file_path, "r") as f:
        coco_data = json.load(f)

    # Create a mapping from category ID to category name
    category_id_to_name = {}
    for category in coco_data.get("categories", []):
        category_id_to_name[category["id"]] = category["name"]

    # Count annotations by category
    annotation_counts = Counter()

    for annotation in coco_data.get("annotations", []):
        category_id = annotation["category_id"]
        category_name = category_id_to_name.get(
            category_id, f"Unknown (ID: {category_id})"
        )
        annotation_counts[category_name] += 1

    return dict(annotation_counts)


def process_multiple_files(input_coco_json_files):
    """
    Process multiple COCO JSON files and return combined counts.

    Args:
        input_coco_json_files (list): List of paths to COCO JSON files

    Returns:
        tuple: (combined_counts, individual_counts, file_stats)
    """
    combined_counts = Counter()
    individual_counts = {}
    file_stats = {}

    for coco_file in input_coco_json_files:
        file_path = Path(coco_file)
        if not file_path.exists():
            raise FileNotFoundError(f"COCO JSON file '{coco_file}' does not exist.")

        try:
            counts = count_annotations_by_category(coco_file)
            individual_counts[coco_file] = counts
            combined_counts.update(counts)

            total_in_file = sum(counts.values())
            file_stats[coco_file] = {
                "total_annotations": total_in_file,
                "total_categories": len(counts),
            }

        except json.JSONDecodeError as e:
            print(f"Warning: Invalid JSON file '{coco_file}' - {e}, skipping.")
            continue
        except Exception as e:
            print(f"Warning: Error processing '{coco_file}' - {e}, skipping.")
            continue

    return dict(combined_counts), individual_counts, file_stats


def main():
    parser = argparse.ArgumentParser(
        description="Count annotations by category name in multiple COCO JSON files"
    )
    parser.add_argument(
        "input_coco_json_files",
        nargs="+",
        type=str,
        help="Paths to one or more COCO JSON files",
    )
    parser.add_argument(
        "--individual",
        action="store_true",
        help="Show individual file statistics in addition to combined totals",
    )

    args = parser.parse_args()

    try:
        # Process all files
        combined_counts, individual_counts, file_stats = process_multiple_files(
            args.input_coco_json_files
        )

        # Print combined results
        print(f"\nCombined annotation counts across {len(individual_counts)} files:")
        print("-" * 60)

        if not combined_counts:
            print("No annotations found in any of the files.")
            return 0

        # Sort by count (descending) and then by category name
        sorted_counts = sorted(combined_counts.items(), key=lambda x: (-x[1], x[0]))

        total_annotations = sum(combined_counts.values())
        print(f"Total annotations: {total_annotations}")
        print(f"Total categories: {len(combined_counts)}")
        print()

        for category_name, count in sorted_counts:
            percentage = (count / total_annotations) * 100
            print(f"{category_name:<30} {count:>8} ({percentage:>5.1f}%)")

        # Print individual file statistics if requested
        if args.individual and individual_counts:
            print(f"\n{'=' * 60}")
            print("Individual file statistics:")
            print("-" * 60)

            for coco_file, stats in file_stats.items():
                print(f"\nFile: {coco_file}")
                print(f"  Total annotations: {stats['total_annotations']}")
                print(f"  Total categories: {stats['total_categories']}")

                if individual_counts[coco_file]:
                    file_counts = individual_counts[coco_file]
                    sorted_file_counts = sorted(
                        file_counts.items(), key=lambda x: (-x[1], x[0])
                    )

                    for category_name, count in sorted_file_counts:
                        percentage = (count / stats["total_annotations"]) * 100
                        print(
                            f"    {category_name:<25} {count:>6} ({percentage:>5.1f}%)"
                        )

        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    main()
