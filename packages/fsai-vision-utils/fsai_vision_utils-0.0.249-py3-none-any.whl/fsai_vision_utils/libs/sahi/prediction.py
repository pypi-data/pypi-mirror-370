import copy
from typing import Dict, List, Optional, Union
import numpy as np
from PIL import Image
from collections import defaultdict

from fsai_vision_utils.libs.sahi.annotation import ObjectAnnotation, Keypoints
from sahi.utils.coco import CocoAnnotation, CocoPrediction
from sahi.utils.cv import read_image_as_pil, visualize_object_predictions
from sahi.utils.file import Path


class PredictionScore:
    def __init__(self, value: float):
        if type(value).__module__ == "numpy":
            value = copy.deepcopy(value).tolist()
        self.value = value

    def is_greater_than_threshold(self, threshold):
        return self.value > threshold

    def __repr__(self):
        return f"PredictionScore: <value: {self.value}>"


class KeypointEstimator:
    def __init__(self):
        # Store keypoint patterns for each category
        # Format: {category_id: {aspect_ratio: {width: {height: [keypoint_positions]}}}}
        self.keypoint_patterns = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
        # Store counts for each pattern to calculate averages
        self.pattern_counts = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
        # Store majority patterns for each category
        self.majority_patterns = {}

    def add_pattern(self, category_id: int, bbox: List[float], keypoints: List[float]):
        """Add a keypoint pattern for a category based on bbox dimensions."""
        if not keypoints:
            print(f"[DEBUG] No keypoints provided for category {category_id}")
            return

        # Calculate dimensions
        x1, y1, x2, y2 = bbox
        width = x2 - x1
        height = y2 - y1
        aspect_ratio = round((width / height) * 100) / 100

        # Round dimensions to nearest 10 pixels for binning
        width = round(width / 10) * 10
        height = round(height / 10) * 10

        # Convert keypoints to relative positions within bbox
        relative_keypoints = []
        for i in range(0, len(keypoints), 3):
            x, y, v = keypoints[i:i+3]
            # Convert numpy values to float
            x = float(x)
            y = float(y)
            v = float(v)
            # Only consider keypoints with visibility > 0
            if v > 0:
                rel_x = (x - x1) / width
                rel_y = (y - y1) / height
                relative_keypoints.extend([rel_x, rel_y, 1.0])  # Use 1.0 for estimated keypoints

        if not relative_keypoints:
            print(f"[DEBUG] No valid keypoints found for category {category_id}")
            return

        print(f"[DEBUG] Adding pattern for category {category_id} with aspect ratio {aspect_ratio}, width {width}, height {height}")

        # Update patterns
        if height not in self.keypoint_patterns[category_id][aspect_ratio][width]:
            self.keypoint_patterns[category_id][aspect_ratio][width][height] = relative_keypoints
            self.pattern_counts[category_id][aspect_ratio][width][height] = 1
        else:
            # Average with existing pattern
            current = self.keypoint_patterns[category_id][aspect_ratio][width][height]
            count = self.pattern_counts[category_id][aspect_ratio][width][height]
            new_pattern = [(current[i] * count + relative_keypoints[i]) / (count + 1) 
                          for i in range(len(current))]
            self.keypoint_patterns[category_id][aspect_ratio][width][height] = new_pattern
            self.pattern_counts[category_id][aspect_ratio][width][height] += 1

        # Update majority pattern for this category
        self._update_majority_pattern(category_id)

    def _update_majority_pattern(self, category_id: int):
        """Update the majority pattern for a category based on all collected patterns."""
        if category_id not in self.keypoint_patterns:
            return

        # Collect all patterns and their counts
        all_patterns = []
        for ar in self.keypoint_patterns[category_id]:
            for w in self.keypoint_patterns[category_id][ar]:
                for h in self.keypoint_patterns[category_id][ar][w]:
                    pattern = self.keypoint_patterns[category_id][ar][w][h]
                    count = self.pattern_counts[category_id][ar][w][h]
                    all_patterns.append((pattern, count))

        if not all_patterns:
            return

        # Find the pattern with the highest count
        majority_pattern, _ = max(all_patterns, key=lambda x: x[1])
        self.majority_patterns[category_id] = majority_pattern

    def get_majority_pattern(self, category_id: int) -> Optional[List[float]]:
        """Get the majority pattern for a category."""
        return self.majority_patterns.get(category_id)

    def find_closest_dimensions(self, category_id: int, aspect_ratio: float, width: float, height: float):
        """Find the closest matching dimensions for a given aspect ratio."""
        if category_id not in self.keypoint_patterns:
            return None, None, None

        # Get all available patterns for this category and aspect ratio
        available_patterns = []
        for ar in self.keypoint_patterns[category_id]:
            if abs(ar - aspect_ratio) <= 0.1:  # Consider aspect ratios within 0.1
                for w in self.keypoint_patterns[category_id][ar]:
                    for h in self.keypoint_patterns[category_id][ar][w]:
                        # Calculate distance based on both width and height
                        width_diff = abs(w - width) / width
                        height_diff = abs(h - height) / height
                        total_diff = width_diff + height_diff
                        available_patterns.append((total_diff, ar, w, h))

        if not available_patterns:
            return None, None, None

        # Return the pattern with the smallest difference
        _, best_ar, best_w, best_h = min(available_patterns, key=lambda x: x[0])
        return best_ar, best_w, best_h

    def estimate_keypoints(self, category_id: int, bbox: List[float]) -> Optional[List[float]]:
        """Estimate keypoints for a bbox based on learned patterns."""
        if category_id not in self.keypoint_patterns:
            print(f"[DEBUG] No patterns found for category {category_id}")
            return None

        # Calculate dimensions
        x1, y1, x2, y2 = bbox
        width = x2 - x1
        height = y2 - y1
        aspect_ratio = round((width / height) * 100) / 100

        # Round dimensions to nearest 10 pixels for matching
        width = round(width / 10) * 10
        height = round(height / 10) * 10

        # Find closest matching pattern
        best_ar, best_w, best_h = self.find_closest_dimensions(category_id, aspect_ratio, width, height)
        
        if best_ar is None:
            # If no close match found, use majority pattern
            majority_pattern = self.get_majority_pattern(category_id)
            if majority_pattern:
                print(f"[DEBUG] Using majority pattern for category {category_id}")
                pattern = majority_pattern
            else:
                print(f"[DEBUG] No suitable pattern found for category {category_id}")
                return None
        else:
            pattern = self.keypoint_patterns[category_id][best_ar][best_w][best_h]
            print(f"[DEBUG] Using pattern for category {category_id} with aspect ratio {best_ar} (requested {aspect_ratio}), width {best_w} (requested {width}), height {best_h} (requested {height})")

        # Convert relative positions back to absolute coordinates
        absolute_keypoints = []
        for i in range(0, len(pattern), 3):
            rel_x, rel_y, v = pattern[i:i+3]
            abs_x = x1 + rel_x * width
            abs_y = y1 + rel_y * height
            absolute_keypoints.extend([abs_x, abs_y, v])  # Use original visibility value

        return absolute_keypoints

    def validate_keypoints(self, category_id: int, keypoints: List[float], bbox: List[float]) -> bool:
        """Validate if keypoints match the majority pattern for the category."""
        if not keypoints or category_id not in self.majority_patterns:
            return False

        # Get majority pattern
        majority_pattern = self.majority_patterns[category_id]
        
        # Calculate dimensions
        x1, y1, x2, y2 = bbox
        width = x2 - x1
        height = y2 - y1

        # Convert input keypoints to relative positions
        relative_keypoints = []
        for i in range(0, len(keypoints), 3):
            x, y, v = keypoints[i:i+3]
            if v > 0:
                rel_x = (x - x1) / width
                rel_y = (y - y1) / height
                relative_keypoints.extend([rel_x, rel_y, 1.0])

        if not relative_keypoints:
            return False

        # Calculate average distance between keypoints
        total_diff = 0
        count = 0
        for i in range(0, len(relative_keypoints), 3):
            if i + 2 < len(majority_pattern):
                rel_x1, rel_y1, _ = relative_keypoints[i:i+3]
                rel_x2, rel_y2, _ = majority_pattern[i:i+3]
                diff = ((rel_x1 - rel_x2) ** 2 + (rel_y1 - rel_y2) ** 2) ** 0.5
                total_diff += diff
                count += 1

        if count == 0:
            return False

        avg_diff = total_diff / count
        # Consider keypoints matching if average difference is less than 0.1 (10% of bbox)
        return avg_diff < 0.1


class ObjectPrediction(ObjectAnnotation):
    def __init__(
        self,
        bbox: Optional[List[int]] = None,
        category_id: Optional[int] = None,
        category_name: Optional[str] = None,
        segmentation: Optional[List[List[float]]] = None,
        score: Optional[float] = 0,
        shift_amount: Optional[List[int]] = [0, 0],
        full_shape: Optional[List[int]] = None,
        keypoints: Optional[List[float]] = None,
        keypoint_estimator: Optional[KeypointEstimator] = None,
    ):
        # Initialize keypoints first
        self.keypoints = None
        if keypoints is not None:
            if isinstance(keypoints, Keypoints):
                self.keypoints = keypoints
            elif isinstance(keypoints, list):
                if len(keypoints) % 3 != 0:
                    print(
                        f"[WARN] Dropping malformed keypoints (len={len(keypoints)}):",
                        keypoints,
                    )
                    keypoints = keypoints[
                        : len(keypoints) // 3 * 3
                    ]  # Truncate to nearest multiple of 3
                self.keypoints = Keypoints(keypoints)
            else:
                raise TypeError(
                    "keypoints must be a list of floats or a Keypoints object."
                )

        # Initialize other attributes
        self.score = PredictionScore(score)
        self.shift_amount = shift_amount
        self.full_shape = full_shape
        self.keypoint_estimator = keypoint_estimator

        # Call parent class initialization
        super().__init__(
            bbox=bbox,
            category_id=category_id,
            segmentation=segmentation,
            category_name=category_name,
            shift_amount=shift_amount,
            full_shape=full_shape,
        )

        # If no keypoints and we have an estimator, try to estimate them
        if self.keypoints is None and self.keypoint_estimator is not None and self.category is not None:
            estimated_keypoints = self.keypoint_estimator.estimate_keypoints(
                self.category.id, self.bbox.to_xyxy()
            )
            if estimated_keypoints:
                self.keypoints = Keypoints(estimated_keypoints)

    def get_shifted_object_prediction(self):
        if self.mask:
            shifted_mask = self.mask.get_shifted_mask()
            return ObjectPrediction(
                bbox=self.bbox.get_shifted_box().to_xyxy(),
                category_id=self.category.id,
                score=self.score.value,
                segmentation=shifted_mask.segmentation,
                category_name=self.category.name,
                shift_amount=[0, 0],
                full_shape=shifted_mask.full_shape,
                keypoints=self.get_shifted_keypoints(),
                keypoint_estimator=self.keypoint_estimator,
            )
        else:
            return ObjectPrediction(
                bbox=self.bbox.get_shifted_box().to_xyxy(),
                category_id=self.category.id,
                score=self.score.value,
                segmentation=None,
                category_name=self.category.name,
                shift_amount=[0, 0],
                full_shape=self.full_shape,
                keypoints=self.get_shifted_keypoints(),
                keypoint_estimator=self.keypoint_estimator,
            )

    def get_shifted_keypoints(self):
        """
        Returns shifted Keypoints object.
        """
        if not self.keypoints:
            return None
        shift_x, shift_y = self.shift_amount if self.shift_amount else [0, 0]
        return self.keypoints.get_shifted_keypoints(shift_x, shift_y)

    def to_coco_prediction(self, image_id=None):
        if self.mask:
            coco_prediction = CocoPrediction.from_coco_segmentation(
                segmentation=self.mask.segmentation,
                category_id=self.category.id,
                category_name=self.category.name,
                score=self.score.value,
                image_id=image_id,
            )
        else:
            coco_prediction = CocoPrediction.from_coco_bbox(
                bbox=self.bbox.to_xywh(),
                category_id=self.category.id,
                category_name=self.category.name,
                score=self.score.value,
                image_id=image_id,
            )
        if self.keypoints:
            coco_prediction.json["keypoints"] = self.keypoints
            coco_prediction.json["num_keypoints"] = sum(
                1 for i in range(2, len(self.keypoints), 3) if self.keypoints[i] > 0
            )
        return coco_prediction

    def to_fiftyone_detection(self, image_height: int, image_width: int):
        try:
            import fiftyone as fo
        except ImportError:
            raise ImportError(
                'Please run "pip install -U fiftyone" to install fiftyone first.'
            )

        x1, y1, x2, y2 = self.bbox.to_xyxy()
        rel_box = [
            x1 / image_width,
            y1 / image_height,
            (x2 - x1) / image_width,
            (y2 - y1) / image_height,
        ]
        return fo.Detection(
            label=self.category.name, bounding_box=rel_box, confidence=self.score.value
        )

    def __repr__(self):
        return f"""ObjectPrediction<
    bbox: {self.bbox},
    mask: {self.mask},
    score: {self.score},
    category: {self.category},
    keypoints: {self.keypoints}>"""


class PredictionResult:
    def __init__(
        self,
        object_prediction_list: List[ObjectPrediction],
        image: Union[Image.Image, str, np.ndarray],
        durations_in_seconds: Optional[Dict] = None,
    ):
        self.image: Image.Image = read_image_as_pil(image)
        self.image_width, self.image_height = self.image.size
        self.durations_in_seconds = durations_in_seconds
        
        # Store the predictions without any estimation
        self.object_prediction_list: List[ObjectPrediction] = object_prediction_list

        # print(f"[DEBUG] Total predictions: {len(self.object_prediction_list)}")
        # print(f"[DEBUG] Predictions with keypoints: {sum(1 for obj in self.object_prediction_list if hasattr(obj, 'keypoints') and obj.keypoints is not None)}")

    def export_visuals(
        self,
        export_dir: str,
        text_size: float = 0.5,
        rect_th: int = 2,
        hide_labels: bool = False,
        hide_conf: bool = False,
        file_name: str = "prediction_visual",
    ):
        import cv2
        from sahi.utils.file import Path

        Path(export_dir).mkdir(parents=True, exist_ok=True)
        image_np = np.array(self.image.convert("RGB"))

        for obj in self.object_prediction_list:
            x1, y1, x2, y2 = map(int, obj.bbox.to_xyxy())
            color = (0, 255, 0)
            cv2.rectangle(image_np, (x1, y1), (x2, y2), color, rect_th)

            label = obj.category.name if obj.category else ""
            if not hide_conf:
                label += f" {obj.score.value:.2f}"
            if not hide_labels:
                cv2.putText(
                    image_np,
                    label,
                    (x1, max(0, y1 - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    text_size,
                    color,
                    1,
                )

            if hasattr(obj, "keypoints") and obj.keypoints is not None:
                # Get keypoints directly from the object
                # because shifted_kpts = obj.get_shifted_keypoints() 
                # isn't working as expected. ObjectPrediction is coming from sahi for some reason

                # Get keypoints directly from the object
                for kp in obj.keypoints:
                    if kp.v > 0:
                        # Only draw original keypoints in green
                        color = (0, 255, 0)
                        radius = 3
                        cv2.circle(image_np, (int(kp.x), int(kp.y)), radius, color, -1)
                        
                        # Draw confidence score next to keypoint
                        confidence_text = f"{kp.v:.2f}"
                        cv2.putText(
                            image_np,
                            confidence_text,
                            (int(kp.x) + 5, int(kp.y) - 5),  # Offset slightly from keypoint
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.3,  # Smaller font size for keypoint scores
                            color,
                            1,
                        )

        output_path = str(Path(export_dir) / f"{file_name}.png")
        cv2.imwrite(output_path, cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR))
        print(f"[INFO] Visualization saved to {output_path}")
        print(f"[INFO] Total predictions: {len(self.object_prediction_list)}")
        print(f"[INFO] Predictions with keypoints: {sum(1 for obj in self.object_prediction_list if hasattr(obj, 'keypoints') and obj.keypoints is not None)}")

    def to_coco_annotations(self):
        return [obj.to_coco_prediction().json for obj in self.object_prediction_list]

    def to_coco_predictions(self, image_id: Optional[int] = None):
        return [
            obj.to_coco_prediction(image_id=image_id).json
            for obj in self.object_prediction_list
        ]

    def to_imantics_annotations(self):
        return [obj.to_imantics_annotation() for obj in self.object_prediction_list]

    def to_fiftyone_detections(self):
        try:
            import fiftyone as fo
        except ImportError:
            raise ImportError(
                'Please run "pip install -U fiftyone" to install fiftyone first.'
            )

        return [
            obj.to_fiftyone_detection(
                image_height=self.image_height, image_width=self.image_width
            )
            for obj in self.object_prediction_list
        ]