import argparse

import fiftyone as fo


def visualize_coco_dataset(data_path, labels_path, name="coco_dataset"):
    dataset = fo.Dataset.from_dir(
        dataset_type=fo.types.COCODetectionDataset,
        data_path=data_path,
        labels_path=labels_path,
        name=name,
    )
    session = fo.launch_app(dataset)
    session.wait()


def main():
    parser = argparse.ArgumentParser(
        description="Visualize a COCO dataset using FiftyOne"
    )
    parser.add_argument(
        "--image-dir", required=True, help="Path to the image directory"
    )
    parser.add_argument(
        "--input-coco-json", required=True, help="Path to the COCO JSON annotation file"
    )
    parser.add_argument(
        "--dataset-name",
        default="coco_dataset",
        help="Optional name for the FiftyOne dataset",
    )

    args = parser.parse_args()
    visualize_coco_dataset(args.image_dir, args.input_coco_json, args.dataset_name)


if __name__ == "__main__":
    main()
