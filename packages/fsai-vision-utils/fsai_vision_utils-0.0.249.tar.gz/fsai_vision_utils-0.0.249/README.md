# fsai-vision-utils

Vision utility functions and tools for batch processing and data management.

## Installation
```shell
poetry add fsai-vision-utils
```

## Tools

### AWS Batch Download Tool

Download multiple files from S3 using file IDs with multi-threading and retry logic.

#### Usage

```bash
python -m fsai_vision_utils.clis.aws_batch_download \
    --ids_txt_file ids.txt \
    --aws_path s3://bucket/folder \
    --output_path ./images
```

#### Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--ids_txt_file` | Yes | - | Text file with file IDs (one per line) |
| `--aws_path` | Yes | - | S3 base path (e.g., `s3://bucket/folder`) |
| `--output_path` | Yes | - | Local output directory |
| `--file_extension` | No | `jpg` | File extension to download |
| `--max_workers` | No | `50` | Number of concurrent downloads |
| `--max_retries` | No | `3` | Retry attempts per file |
| `--log_level` | No | `INFO` | Logging level |

#### Input Format

Create a text file with one file ID per line:
```
image_001
image_002
image_003
```

The tool downloads: `{aws_path}/{file_id}.{file_extension}`

#### Examples

**Basic download:**
```bash
python -m fsai_vision_utils.clis.aws_batch_download \
    --ids_txt_file image_ids.txt \
    --aws_path s3://my-bucket/images \
    --output_path ./images
```

**Custom settings:**
```bash
python -m fsai_vision_utils.clis.aws_batch_download \
    --ids_txt_file image_ids.txt \
    --aws_path s3://my-bucket/images \
    --output_path ./images \
    --file_extension png \
    --max_workers 100
```

#### Features

- Multi-threaded downloads (configurable workers)
- Automatic retry with exponential backoff
- Skips already downloaded files
- Progress tracking and statistics
- Graceful shutdown (Ctrl+C)
- Comprehensive logging

#### Requirements

- AWS CLI installed and configured
- Valid AWS credentials with S3 read access

### COCO Dataset Slicer

Slice COCO dataset images and annotations into smaller tiles for training or inference on large images.

#### Usage

```bash
python -m fsai_vision_utils.clis.coco_slice_dataset \
    --input-coco-json annotations.json \
    --image-dir ./images \
    --output-dir ./sliced_output \
    --slice-height 1024 \
    --slice-width 1024
```

#### Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--input-coco-json` | Yes | - | Path to the input COCO annotations JSON file |
| `--image-dir` | Yes | - | Directory containing the input images |
| `--output-dir` | Yes | - | Directory to save the sliced images and annotations |
| `--slice-height` | No | `1024` | Height of each image slice in pixels |
| `--slice-width` | No | `1024` | Width of each image slice in pixels |
| `--overlap-height-ratio` | No | `0.2` | Overlap ratio for height between slices (0.0-1.0) |
| `--overlap-width-ratio` | No | `0.2` | Overlap ratio for width between slices (0.0-1.0) |
| `--output-coco-json` | No | `output_dir/coco-annotations-sliced_coco.json` | Path to save the output COCO JSON file |

#### Input Format

The tool expects:
- A COCO format JSON file with annotations
- Images referenced in the COCO file located in the specified image directory
- Images can be in common formats (JPG, PNG, etc.)

#### Examples

**Basic slicing with default settings:**
```bash
python -m fsai_vision_utils.clis.coco_slice_dataset \
    --input-coco-json annotations.json \
    --image-dir ./images \
    --output-dir ./sliced_output
```

**Custom slice size and overlap:**
```bash
python -m fsai_vision_utils.clis.coco_slice_dataset \
    --input-coco-json annotations.json \
    --image-dir ./images \
    --output-dir ./sliced_output \
    --slice-height 512 \
    --slice-width 512 \
    --overlap-height-ratio 0.3 \
    --overlap-width-ratio 0.3
```

**Specify custom output JSON path:**
```bash
python -m fsai_vision_utils.clis.coco_slice_dataset \
    --input-coco-json annotations.json \
    --image-dir ./images \
    --output-dir ./sliced_output \
    --output-coco-json ./custom_output.json
```

#### Features

- **Parallel Processing**: Uses ProcessPoolExecutor for efficient multi-core processing
- **Annotation Preservation**: Maintains bounding box annotations across slices
- **Overlap Control**: Configurable overlap ratios to ensure no objects are missed
- **Area Filtering**: Automatically filters annotations based on minimum area ratio
- **Error Handling**: Gracefully handles invalid annotations and continues processing
- **Progress Tracking**: Shows completion status for each image
- **Flexible Output**: Supports custom output paths and formats

#### Output Structure

The tool creates:
- Sliced images in the output directory with naming pattern: `{original_name}_{slice_index}.jpg`
- A new COCO JSON file with updated annotations for all slices
- Preserved category information from the original dataset

#### Technical Details

- **Minimum Area Ratio**: Default 0.4 (40% of annotation must be visible in slice)
- **File Extension**: Output images are saved as JPG format
- **Workers**: Uses 8 parallel workers by default for optimal performance
- **Memory Efficient**: Loads images once per processing thread
- **Topology Safe**: Handles invalid polygon annotations gracefully

#### Use Cases

- **Large Image Processing**: Break down high-resolution images for model training
- **Memory Optimization**: Reduce memory requirements for inference
- **Data Augmentation**: Create overlapping slices for better model generalization
- **Edge Case Handling**: Ensure small objects aren't missed at slice boundaries