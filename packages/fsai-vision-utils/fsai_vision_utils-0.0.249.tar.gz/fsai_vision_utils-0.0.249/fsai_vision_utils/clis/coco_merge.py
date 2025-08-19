import argparse
import copy
import json
from pathlib import Path


def load_json(path):
    with open(path, "r") as f:
        return json.load(f)


def save_json(data, path):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def update_categories(coco_dict, desired_name2id):
    id_map = {}
    new_categories = []

    # Create mapping from old category IDs to new category IDs
    for cat in coco_dict["categories"]:
        name = cat["name"]
        if name in desired_name2id:
            new_id = desired_name2id[name]
            id_map[cat["id"]] = new_id
            # Only add category if we haven't already added it
            if not any(c["id"] == new_id for c in new_categories):
                new_categories.append(
                    {
                        "id": new_id,
                        "name": name,
                        "supercategory": cat.get("supercategory", name),
                    }
                )

    # Update annotation category IDs
    for ann in coco_dict["annotations"]:
        old_id = ann["category_id"]
        if old_id in id_map:
            ann["category_id"] = id_map[old_id]
        else:
            # If category ID not found in mapping, this is an error
            print(
                f"Warning: Annotation {ann['id']} references unknown category ID {old_id}"
            )

    # Update categories in the dataset
    coco_dict["categories"] = new_categories
    return coco_dict


def merge_multiple_coco_datasets(coco_paths, output_json_path):
    """
    Merge multiple COCO datasets into a single dataset.

    Args:
        coco_paths (list): List of paths to COCO JSON files
        output_json_path (str): Path to output merged COCO JSON
    """
    if len(coco_paths) < 2:
        raise ValueError("At least 2 COCO JSON files are required for merging")

    # Load all COCO datasets
    coco_datasets = []
    for path in coco_paths:
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"COCO JSON file '{path}' does not exist.")
        try:
            coco_data = load_json(path)
            coco_datasets.append(coco_data)
            print(
                f"Loaded {path}: {len(coco_data.get('images', []))} images, {len(coco_data.get('annotations', []))} annotations"
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON file '{path}' - {e}")

    # Create consistent category mapping across all datasets
    all_cats = []
    for coco_data in coco_datasets:
        all_cats.extend(coco_data.get("categories", []))

    # Create unique category mapping by name
    name2id = {}
    merged_categories = []
    for i, cat in enumerate({c["name"]: c for c in all_cats}.values()):
        name2id[cat["name"]] = i
        merged_categories.append(
            {
                "id": i,
                "name": cat["name"],
                "supercategory": cat.get("supercategory", cat["name"]),
            }
        )

    print(f"Found {len(name2id)} unique categories across all datasets")
    print("Category mapping:")
    for name, cat_id in name2id.items():
        print(f"  '{name}' -> ID {cat_id}")

    # Update categories in all datasets
    updated_datasets = []
    for i, coco_data in enumerate(coco_datasets):
        print(f"\nUpdating categories for dataset {i + 1}...")
        updated_data = update_categories(copy.deepcopy(coco_data), name2id)
        updated_datasets.append(updated_data)

        # Verify category-annotation consistency
        cat_ids_in_dataset = set(cat["id"] for cat in updated_data["categories"])
        ann_cat_ids = set(ann["category_id"] for ann in updated_data["annotations"])
        missing_cats = ann_cat_ids - cat_ids_in_dataset
        if missing_cats:
            print(
                f"  Warning: Dataset {i + 1} has annotations referencing missing categories: {missing_cats}"
            )
        else:
            print(f"  Dataset {i + 1}: All annotations reference valid categories")

    # Merge datasets sequentially, updating IDs as we go
    merged_images = []
    merged_annotations = []

    current_max_img_id = 0
    current_max_ann_id = 0

    for i, coco_data in enumerate(updated_datasets):
        print(f"Processing dataset {i + 1}/{len(updated_datasets)}...")

        # Update image IDs
        for img in coco_data.get("images", []):
            img["id"] += current_max_img_id + 1
            merged_images.append(img)

        # Update annotation IDs and image references
        for ann in coco_data.get("annotations", []):
            ann["id"] += current_max_ann_id + 1
            ann["image_id"] += current_max_img_id + 1
            merged_annotations.append(ann)

        # Update current max IDs for next iteration
        if coco_data.get("images"):
            current_max_img_id = max([img["id"] for img in merged_images])
        if coco_data.get("annotations"):
            current_max_ann_id = max([ann["id"] for ann in merged_annotations])

    # Create final merged dataset
    merged = {
        "images": merged_images,
        "annotations": merged_annotations,
        "categories": merged_categories,
    }

    # Save merged dataset
    save_json(merged, output_json_path)
    print(f"\nMerged COCO saved to {output_json_path}")
    print(f"Total images: {len(merged_images)}")
    print(f"Total annotations: {len(merged_annotations)}")
    print(f"Total categories: {len(merged_categories)}")

    # Final verification
    merged_cat_ids = set(cat["id"] for cat in merged_categories)
    merged_ann_cat_ids = set(ann["category_id"] for ann in merged_annotations)
    missing_cats = merged_ann_cat_ids - merged_cat_ids
    if missing_cats:
        print(
            f"ERROR: Final merged dataset has annotations referencing missing categories: {missing_cats}"
        )
    else:
        print("✓ All annotations in merged dataset reference valid categories")

    # Show category distribution
    print("\nCategory distribution in merged dataset:")
    cat_counts = {}
    for ann in merged_annotations:
        cat_id = ann["category_id"]
        cat_counts[cat_id] = cat_counts.get(cat_id, 0) + 1

    for cat in merged_categories:
        count = cat_counts.get(cat["id"], 0)
        print(f"  {cat['name']} (ID {cat['id']}): {count} annotations")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Merge multiple COCO datasets without absolute file paths."
    )
    parser.add_argument(
        "--input-coco-json-files",
        nargs="+",
        required=True,
        help="Paths to COCO JSON files to merge",
    )
    parser.add_argument(
        "--output-coco-json", required=True, help="Path to output merged COCO JSON"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    merge_multiple_coco_datasets(
        coco_paths=args.input_coco_json_files, output_json_path=args.output_coco_json
    )


if __name__ == "__main__":
    main()
