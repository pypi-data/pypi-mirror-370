import argparse
import concurrent.futures
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Union

from sahi.utils.cv import read_image_as_pil
from sahi.utils.file import load_json, save_json
from shapely.errors import TopologicalError

from fsai_vision_utils.libs.sahi.slicing import slice_image
from fsai_vision_utils.libs.sahi.utils.coco import Coco, create_coco_dict

logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s -   %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
    level=os.environ.get("LOGLEVEL", "INFO").upper(),
)


def process_image(
    image_idx,
    coco_image,
    image_dir,
    output_dir,
    slice_height,
    slice_width,
    overlap_height_ratio,
    overlap_width_ratio,
    min_area_ratio,
    out_ext,
    verbose,
):
    """
    Process a single image by slicing it into smaller tiles with annotations.

    This function takes a COCO image object and slices it into smaller tiles while
    preserving the bounding box annotations. It handles TopologicalError exceptions
    that may occur with invalid annotations.

    Args:
        image_idx (int): Index of the image being processed
        coco_image: COCO image object containing file_name and annotations
        image_dir (str): Directory path containing the input images
        output_dir (str): Directory path where sliced images will be saved
        slice_height (int): Height of each image slice in pixels
        slice_width (int): Width of each image slice in pixels
        overlap_height_ratio (float): Overlap ratio for height between slices (0.0-1.0)
        overlap_width_ratio (float): Overlap ratio for width between slices (0.0-1.0)
        min_area_ratio (float): Minimum area ratio for annotations to be preserved
        out_ext (str): Output file extension (e.g., '.jpg', '.png')
        verbose (bool): Whether to print verbose output during processing

    Returns:
        list: List of COCO image objects representing the sliced images with annotations

    Raises:
        TopologicalError: If invalid annotations are found in the image
    """
    image_path = os.path.join(image_dir, coco_image.file_name)

    try:
        pil_image = read_image_as_pil(image_path)  # Load image once
        slice_image_result = slice_image(
            image=pil_image,  # Pass preloaded image
            coco_annotation_list=coco_image.annotations,
            output_file_name=f"{Path(coco_image.file_name).stem}_{image_idx}",
            output_dir=output_dir,
            slice_height=slice_height,
            slice_width=slice_width,
            overlap_height_ratio=overlap_height_ratio,
            overlap_width_ratio=overlap_width_ratio,
            min_area_ratio=min_area_ratio,
            out_ext=out_ext,
            verbose=verbose,
        )
        print(f"Completed: {image_idx + 1}")
        return slice_image_result.coco_images
    except TopologicalError:
        logger.warning(f"Invalid annotation found, skipping: {image_path}")
        return []


def slice_coco_json(
    coco_annotation_file_path: str,
    image_dir: str,
    output_coco_annotation_file_name: str,
    output_dir: Optional[str] = None,
    ignore_negative_samples: bool = True,
    slice_height: int = 512,
    slice_width: int = 512,
    overlap_height_ratio: float = 0.2,
    overlap_width_ratio: float = 0.2,
    min_area_ratio: float = 0.1,
    out_ext: Optional[str] = None,
    verbose: bool = False,
    num_workers: int = 4,
    output_json: Optional[str] = None,
) -> List[Union[Dict, str]]:
    """
    Slice COCO dataset images and annotations into smaller tiles using parallel processing.

    This function takes a COCO annotation file and corresponding images, then slices
    each image into smaller tiles while preserving the bounding box annotations.
    The processing is done in parallel using ProcessPoolExecutor for improved performance.

    Args:
        coco_annotation_file_path (str): Path to the input COCO annotations JSON file
        image_dir (str): Directory containing the input images referenced in COCO annotations
        output_coco_annotation_file_name (str): Base name for the output COCO annotations file
        output_dir (Optional[str]): Directory to save sliced images and annotations.
                                  If None, only the JSON is returned
        ignore_negative_samples (bool): Whether to ignore images with no annotations (default: True)
        slice_height (int): Height of each image slice in pixels (default: 512)
        slice_width (int): Width of each image slice in pixels (default: 512)
        overlap_height_ratio (float): Overlap ratio for height between slices (default: 0.2)
        overlap_width_ratio (float): Overlap ratio for width between slices (default: 0.2)
        min_area_ratio (float): Minimum area ratio for annotations to be preserved (default: 0.1)
        out_ext (Optional[str]): Output file extension for sliced images (default: None)
        verbose (bool): Whether to print verbose output during processing (default: False)
        num_workers (int): Number of parallel workers for processing (default: 4)
        output_json (Optional[str]): Specific path for output JSON file. If None, uses
                                   output_dir/output_coco_annotation_file_name_coco.json

    Returns:
        tuple: A tuple containing:
            - coco_dict (Dict): The processed COCO annotations dictionary
            - save_path (str): Path where the JSON file was saved (empty string if not saved)

    Example:
        >>> coco_dict, save_path = slice_coco_json(
        ...     coco_annotation_file_path="annotations.json",
        ...     image_dir="images/",
        ...     output_coco_annotation_file_name="sliced",
        ...     output_dir="output/",
        ...     slice_height=1024,
        ...     slice_width=1024
        ... )
    """

    # Read COCO file
    coco_dict: Dict = load_json(coco_annotation_file_path)
    coco = Coco.from_coco_dict_or_path(coco_dict)
    sliced_coco_images: List = []

    # for img in coco.images:
    #     for annotation in img.annotations:
    #         print(annotation.json)
    #     exit()
    # Run in parallel using ProcessPoolExecutor
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = {
            executor.submit(
                process_image,
                idx,
                img,
                image_dir,
                output_dir,
                slice_height,
                slice_width,
                overlap_height_ratio,
                overlap_width_ratio,
                min_area_ratio,
                out_ext,
                verbose,
            ): img
            for idx, img in enumerate(coco.images)
        }

        for future in concurrent.futures.as_completed(futures):
            sliced_coco_images.extend(future.result())

    # Create and save COCO dict
    coco_dict = create_coco_dict(
        sliced_coco_images,
        coco_dict["categories"],
        ignore_negative_samples=ignore_negative_samples,
    )

    save_path = ""
    if output_coco_annotation_file_name and output_dir:
        if output_json:
            save_path = Path(output_json)
        else:
            save_path = (
                Path(output_dir) / f"{output_coco_annotation_file_name}_coco.json"
            )
        save_json(coco_dict, save_path)

    return coco_dict, save_path


def main():
    parser = argparse.ArgumentParser(
        description="Slice COCO dataset images and annotations"
    )
    parser.add_argument(
        "--input-coco-json",
        type=str,
        required=True,
        help="Path to the input COCO annotations JSON file",
    )
    parser.add_argument(
        "--image-dir",
        type=str,
        required=True,
        help="Directory containing the input images",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        required=True,
        help="Directory to save the sliced images and annotations",
    )
    parser.add_argument(
        "--slice-height",
        type=int,
        default=1024,
        help="Height of each image slice (default: 1024)",
    )
    parser.add_argument(
        "--slice-width",
        type=int,
        default=1024,
        help="Width of each image slice (default: 1024)",
    )
    parser.add_argument(
        "--overlap-height-ratio",
        type=float,
        default=0.2,
        help="Overlap ratio for height between slices (default: 0.2)",
    )
    parser.add_argument(
        "--overlap-width-ratio",
        type=float,
        default=0.2,
        help="Overlap ratio for width between slices (default: 0.2)",
    )
    parser.add_argument(
        "--output-coco-json",
        type=str,
        default=None,
        help="Path to save the output COCO JSON file (default: output_dir/coco-annotations-sliced_coco.json)",
    )

    args = parser.parse_args()

    try:
        coco_dict, coco_path = slice_coco_json(
            coco_annotation_file_path=args.input_coco_json,
            image_dir=args.image_dir,
            output_coco_annotation_file_name="coco-annotations-sliced.json",
            output_dir=args.output_dir,
            ignore_negative_samples=True,
            slice_height=args.slice_height,
            slice_width=args.slice_width,
            overlap_height_ratio=args.overlap_height_ratio,
            overlap_width_ratio=args.overlap_width_ratio,
            min_area_ratio=0.4,
            out_ext=".jpg",
            verbose=True,
            num_workers=8,
            output_json=args.output_coco_json,
        )
    except KeyboardInterrupt:
        print("\nProcess terminated by user. Exiting forcefully... 🚀")
        import sys

        sys.exit(1)


if __name__ == "__main__":
    main()
