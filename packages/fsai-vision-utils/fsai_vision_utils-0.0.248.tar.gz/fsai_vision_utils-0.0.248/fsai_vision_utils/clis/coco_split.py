import argparse
import json
from collections import defaultdict

import numpy as np
from iterstrat.ml_stratifiers import MultilabelStratifiedShuffleSplit


def parse_args():
    parser = argparse.ArgumentParser(
        description="Split COCO dataset into train/val/test sets"
    )
    parser.add_argument(
        "--input-coco-json",
        type=str,
        required=True,
        help="Path to input COCO JSON file",
    )
    parser.add_argument(
        "--output-coco-dir",
        type=str,
        required=True,
        help="Directory to save output JSON files",
    )
    parser.add_argument(
        "--train-ratio",
        type=float,
        default=0.7,
        help="Ratio of training data (default: 0.7)",
    )
    parser.add_argument(
        "--val-ratio",
        type=float,
        default=0.15,
        help="Ratio of validation data (default: 0.15)",
    )
    parser.add_argument(
        "--test-ratio",
        type=float,
        default=0.15,
        help="Ratio of test data (default: 0.15)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Load COCO-style dataset
    with open(args.input_coco_json, "r") as f:
        data = json.load(f)

    images = data["images"]
    annotations = data["annotations"]
    categories = data["categories"]

    # Map image_id to its category_ids
    image_to_labels = defaultdict(set)
    for ann in annotations:
        image_to_labels[ann["image_id"]].add(ann["category_id"])

    image_ids = list(image_to_labels.keys())
    id_to_image = {img["id"]: img for img in images}
    X = [id_to_image[iid] for iid in image_ids]

    # Multi-hot encode labels
    cat_id_to_index = {cat["id"]: idx for idx, cat in enumerate(categories)}
    Y = np.zeros((len(image_ids), len(categories)), dtype=int)
    for i, img_id in enumerate(image_ids):
        for cat_id in image_to_labels[img_id]:
            Y[i, cat_id_to_index[cat_id]] = 1

    # Split ratios
    train_ratio = args.train_ratio
    val_ratio = args.val_ratio
    test_ratio = args.test_ratio

    # First split: train vs temp (val + test)
    sss1 = MultilabelStratifiedShuffleSplit(
        n_splits=1, test_size=(1 - train_ratio), random_state=42
    )
    train_idx, temp_idx = next(sss1.split(X, Y))

    # Second split: val vs test
    if test_ratio > 0:
        val_size = val_ratio / (val_ratio + test_ratio)
        sss2 = MultilabelStratifiedShuffleSplit(
            n_splits=1, test_size=(1 - val_size), random_state=42
        )
        val_idx, test_idx = next(sss2.split([X[i] for i in temp_idx], Y[temp_idx]))

        # Remap temp indices to global
        val_idx = np.array(temp_idx)[val_idx]
        test_idx = np.array(temp_idx)[test_idx]
    else:
        # If test_ratio is 0, all remaining data goes to validation
        val_idx = temp_idx
        test_idx = np.array([], dtype=int)

    # Ensure all classes are in train
    min_samples_per_class = 5
    class_counts = Y[train_idx].sum(axis=0)

    for class_idx in range(Y.shape[1]):
        if class_counts[class_idx] < min_samples_per_class:
            all_indices = np.where(Y[:, class_idx] == 1)[0]
            np.random.shuffle(all_indices)

            candidates = [idx for idx in all_indices if idx not in train_idx]
            needed = min_samples_per_class - class_counts[class_idx]
            added = 0
            for idx in candidates:
                if idx in val_idx:
                    val_idx = val_idx[val_idx != idx]
                    train_idx = np.append(train_idx, idx)
                    added += 1
                elif idx in test_idx:
                    test_idx = test_idx[test_idx != idx]
                    train_idx = np.append(train_idx, idx)
                    added += 1
                if added >= needed:
                    break

    # Helper functions
    def get_annotations(images_subset):
        image_ids = {img["id"] for img in images_subset}
        return [ann for ann in annotations if ann["image_id"] in image_ids]

    def save_split(name, image_indices):
        print(f"Saving {name} split...")
        split_images = [X[i] for i in image_indices]
        split_annotations = get_annotations(split_images)
        split_data = {
            "images": split_images,
            "annotations": split_annotations,
            "categories": categories,
        }

        # Ensure output directory exists
        import os

        os.makedirs(args.output_coco_dir, exist_ok=True)

        output_path = os.path.join(args.output_coco_dir, f"{name}.json")
        print(f"Writing to {output_path}")
        with open(output_path, "w") as f:
            json.dump(split_data, f)
        print(f"Successfully saved {name} split")

    # Save to disk
    print("\nSaving splits to disk...")
    save_split("train", train_idx)
    save_split("val", val_idx)
    if len(test_idx) > 0:
        save_split("test", test_idx)
    else:
        print("No test split to save (test_ratio = 0)")
    print("All splits saved successfully")


if __name__ == "__main__":
    main()
