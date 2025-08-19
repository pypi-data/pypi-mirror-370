from typing import List, Optional, Literal
import numpy as np
import cv2
from fsai_vision_utils.libs.sahi.prediction import ObjectPrediction
from fsai_vision_utils.libs.sahi.annotation import Keypoints, Keypoint
from sahi.postprocess.combine import (
    GreedyNMMPostprocess,
    LSNMSPostprocess,
    NMMPostprocess,
    NMSPostprocess,
    PostprocessPredictions,
)

POSTPROCESS_NAME_TO_CLASS = {
    "GREEDYNMM": GreedyNMMPostprocess,
    "NMM": NMMPostprocess,
    "NMS": NMSPostprocess,
    "LSNMS": LSNMSPostprocess,
}

KeypointMergeStrategy = Literal["SIMPLE", "WEIGHTED", "CLOSEST_TO_BOX", "OVERLAP_AWARE", "DISTRIBUTED", "HIGHEST_SCORE", "LARGEST_BOX", "LARGEST_DISTANCE"]

class KeypointAwarePostprocess:
    """
    A postprocessing class that handles merging of predictions with keypoints.
    Uses a base postprocess method for box merging and custom logic for keypoint merging.
    """
    def __init__(
        self,
        match_threshold: float = 0.5,  # Threshold for matching boxes
        match_metric: str = "IOS",     # Metric for matching boxes (IOS or IOU)
        class_agnostic: bool = False,  # Whether to ignore class labels when matching
        postprocess_subtype: str = "GREEDYNMM",  # Base postprocess method to use
        keypoint_merge_strategy: KeypointMergeStrategy = "WEIGHTED",  # Strategy for merging keypoints
        debug: bool = False,           # Enable debug visualization
        debug_dir: str = None,         # Directory for debug visualizations
        overlap_height_ratio: float = 0.2,  # Overlap ratio for height
        overlap_width_ratio: float = 0.2,   # Overlap ratio for width
        disable_merging: bool = False,  # Whether to disable merging of predictions
    ):
        # Store configuration parameters
        self.match_threshold = match_threshold
        self.match_metric = match_metric
        self.class_agnostic = class_agnostic
        self.keypoint_merge_strategy = keypoint_merge_strategy
        self.debug = debug
        self.debug_dir = debug_dir
        self.overlap_height_ratio = overlap_height_ratio
        self.overlap_width_ratio = overlap_width_ratio
        self.disable_merging = disable_merging
        
        # Initialize the base postprocess for box merging
        if postprocess_subtype not in POSTPROCESS_NAME_TO_CLASS:
            raise ValueError(
                f"postprocess_subtype should be one of {list(POSTPROCESS_NAME_TO_CLASS.keys())} but given as {postprocess_subtype}"
            )
        self.base_postprocess = POSTPROCESS_NAME_TO_CLASS[postprocess_subtype](
            match_threshold=match_threshold,
            match_metric=match_metric,
            class_agnostic=class_agnostic,
        )

    def _merge_keypoints_simple(self, valid_preds: List[ObjectPrediction]) -> List[float]:
        """
        Simple averaging of all keypoints.
        Takes the mean position of each keypoint across all predictions.
        Only considers visible keypoints.
        """
        # Convert keypoints to numpy arrays for easier computation
        keypoint_arrays = []
        for pred in valid_preds:
            # Only include visible keypoints
            visible_kps = [(kp.x, kp.y, kp.v) for kp in pred.keypoints if kp.v > 0]
            if visible_kps:
                keypoint_arrays.append(np.array(visible_kps))
        
        if not keypoint_arrays:
            # If no visible keypoints, return all zeros
            return [0.0] * (len(valid_preds[0].keypoints) * 3)
        
        # Average the keypoints
        avg_keypoints = np.mean(keypoint_arrays, axis=0)
        return avg_keypoints.flatten().tolist()

    def _merge_keypoints_weighted(self, valid_preds: List[ObjectPrediction], merged_box: List[float]) -> List[float]:
        """
        Weighted averaging based on keypoint confidence and box overlap.
        Weights are determined by keypoint confidence and box overlap with merged box.
        Only considers visible keypoints.
        """
        weights = []
        keypoint_arrays = []
        
        for pred in valid_preds:
            # Base weight is the keypoint confidence
            weight = pred.keypoints.confidence if pred.keypoints.confidence is not None else 0.0
            
            # Adjust weight based on box overlap with merged box
            box_overlap = self._calculate_ios(merged_box, pred.bbox.to_xyxy())
            weight *= box_overlap
            
            # Only include visible keypoints
            visible_kps = [(kp.x, kp.y, kp.v) for kp in pred.keypoints if kp.v > 0]
            if visible_kps:
                weights.append(weight)
                keypoint_arrays.append(np.array(visible_kps))
        
        if not keypoint_arrays:
            # If no visible keypoints, return all zeros
            return [0.0] * (len(valid_preds[0].keypoints) * 3)
        
        # Normalize weights
        weights = np.array(weights)
        weights = weights / np.sum(weights)
        
        # Weighted average of keypoints
        weighted_keypoints = np.zeros_like(keypoint_arrays[0])
        for i, kp_array in enumerate(keypoint_arrays):
            weighted_keypoints += kp_array * weights[i]
        
        return weighted_keypoints.flatten().tolist()

    def _merge_keypoints_closest_to_box(self, valid_preds: List[ObjectPrediction], merged_box: List[float], image=None) -> List[float]:
        """
        Select individual keypoints that are closest to the merged box.
        For each keypoint position, selects the keypoint closest to the merged box center,
        weighted by keypoint confidence.
        Only considers visible keypoints.
        """
        # Get merged box center
        merged_center_x = (merged_box[0] + merged_box[2]) / 2
        merged_center_y = (merged_box[1] + merged_box[3]) / 2
        
        # Get the number of keypoints from the first valid prediction
        num_keypoints = len(valid_preds[0].keypoints)
        
        # For each keypoint position, find the best keypoint from all predictions
        best_keypoints = []
        for kp_idx in range(num_keypoints):
            best_kp = None
            best_score = float('inf')
            
            for pred in valid_preds:
                kp = pred.keypoints[kp_idx]
                if kp.v > 0:  # Only consider visible keypoints
                    # Calculate distance from keypoint to merged box center
                    dx = kp.x - merged_center_x
                    dy = kp.y - merged_center_y
                    distance = np.sqrt(dx*dx + dy*dy)
                    
                    # Score combines distance and keypoint confidence
                    # Higher confidence reduces the effective distance
                    kp_confidence = pred.keypoints.confidence if pred.keypoints.confidence is not None else 0.0
                    score = distance / (kp_confidence + 1e-6)
                    
                    if score < best_score:
                        best_score = score
                        best_kp = kp
            
            # If no valid keypoint found for this position, use the one from highest confidence detection
            if best_kp is None:
                best_pred = max(valid_preds, key=lambda p: p.keypoints.confidence if p.keypoints.confidence is not None else 0.0)
                best_kp = best_pred.keypoints[kp_idx]
                # If the keypoint is not visible, set visibility to 0
                if best_kp.v <= 0:
                    best_kp = Keypoint(best_kp.x, best_kp.y, 0.0)
            
            best_keypoints.append(best_kp)
        
        # Convert best keypoints to list format
        return [coord for kp in best_keypoints for coord in [kp.x, kp.y, kp.v]]

    def _calculate_keypoint_confidence(self, kp, box, merged_box):
        """
        Calculate confidence score for a keypoint based on its position relative to boxes.
        Considers the keypoint's position in both its original box and the merged box.
        """
        # Get box dimensions
        box_width = box[2] - box[0]
        box_height = box[3] - box[1]
        merged_width = merged_box[2] - merged_box[0]
        merged_height = merged_box[3] - merged_box[1]
        
        # Calculate relative position of keypoint within its box
        rel_x = (kp.x - box[0]) / box_width
        rel_y = (kp.y - box[1]) / box_height
        
        # Calculate relative position in merged box
        merged_rel_x = (kp.x - merged_box[0]) / merged_width
        merged_rel_y = (kp.y - merged_box[1]) / merged_height
        
        # Calculate overlap regions
        overlap_x_start = max(box[0], merged_box[0])
        overlap_x_end = min(box[2], merged_box[2])
        overlap_y_start = max(box[1], merged_box[1])
        overlap_y_end = min(box[3], merged_box[3])
        
        # Calculate relative position in overlap region
        if overlap_x_end > overlap_x_start and overlap_y_end > overlap_y_start:
            overlap_rel_x = (kp.x - overlap_x_start) / (overlap_x_end - overlap_x_start)
            overlap_rel_y = (kp.y - overlap_y_start) / (overlap_y_end - overlap_y_start)
            
            # Check if keypoint is in overlap region
            in_overlap = (overlap_x_start <= kp.x <= overlap_x_end and 
                         overlap_y_start <= kp.y <= overlap_y_end)
        else:
            in_overlap = False
            overlap_rel_x = 0.5
            overlap_rel_y = 0.5
        
        # Calculate position confidence
        # Higher confidence for keypoints in overlap regions
        # Higher confidence for keypoints closer to center of overlap
        if in_overlap:
            # Calculate distance from center of overlap
            center_x = (overlap_x_start + overlap_x_end) / 2
            center_y = (overlap_y_start + overlap_y_end) / 2
            dist_to_center = np.sqrt((kp.x - center_x)**2 + (kp.y - center_y)**2)
            max_dist = np.sqrt((overlap_x_end - overlap_x_start)**2 + 
                             (overlap_y_end - overlap_y_start)**2) / 2
            position_confidence = 1 - (dist_to_center / max_dist) if max_dist > 0 else 0
        else:
            # Calculate distance from center of merged box
            center_x = (merged_box[0] + merged_box[2]) / 2
            center_y = (merged_box[1] + merged_box[3]) / 2
            dist_to_center = np.sqrt((kp.x - center_x)**2 + (kp.y - center_y)**2)
            max_dist = np.sqrt(merged_width**2 + merged_height**2) / 2
            position_confidence = 0.5 * (1 - (dist_to_center / max_dist)) if max_dist > 0 else 0
        
        return position_confidence

    def _merge_keypoints_overlap_aware(self, valid_preds: List[ObjectPrediction], merged_box: List[float], image=None) -> List[float]:
        """
        Select keypoints based on their position relative to overlap regions and merged box.
        Prioritizes keypoints in overlap regions and considers their relative positions.
        Only considers visible keypoints.
        """
        # Get the number of keypoints from the first valid prediction
        num_keypoints = len(valid_preds[0].keypoints)
        
        # For each keypoint position, find the best keypoint from all predictions
        best_keypoints = []
        for kp_idx in range(num_keypoints):
            best_kp = None
            best_score = float('-inf')
            
            for pred in valid_preds:
                kp = pred.keypoints[kp_idx]
                if kp.v > 0:  # Only consider visible keypoints
                    # Calculate position confidence
                    position_confidence = self._calculate_keypoint_confidence(
                        kp, pred.bbox.to_xyxy(), merged_box
                    )
                    
                    # Combine position confidence with keypoint confidence
                    kp_confidence = pred.keypoints.confidence if pred.keypoints.confidence is not None else 0.0
                    score = position_confidence * kp_confidence
                    
                    if score > best_score:
                        best_score = score
                        best_kp = kp
            
            # If no valid keypoint found for this position, use the one from highest confidence detection
            if best_kp is None:
                best_pred = max(valid_preds, key=lambda p: p.keypoints.confidence if p.keypoints.confidence is not None else 0.0)
                best_kp = best_pred.keypoints[kp_idx]
                # If the keypoint is not visible, set visibility to 0
                if best_kp.v <= 0:
                    best_kp = Keypoint(best_kp.x, best_kp.y, 0.0)
            
            best_keypoints.append(best_kp)
        
        # Convert best keypoints to list format
        return [coord for kp in best_keypoints for coord in [kp.x, kp.y, kp.v]]

    def _calculate_spatial_distribution_score(self, keypoints, merged_box):
        """
        Calculate how well distributed the keypoints are within the merged box.
        Considers both minimum distance between keypoints and coverage of the box.
        Only considers visible keypoints.
        """
        # Filter for visible keypoints only
        visible_keypoints = [kp for kp in keypoints if kp.v > 0]
        if not visible_keypoints:
            return 0.0
            
        # Get box dimensions
        box_width = merged_box[2] - merged_box[0]
        box_height = merged_box[3] - merged_box[1]
        
        # Calculate relative positions of keypoints
        rel_positions = []
        for kp in visible_keypoints:
            # Ensure coordinates are within box bounds
            x = max(merged_box[0], min(merged_box[2], kp.x))
            y = max(merged_box[1], min(merged_box[3], kp.y))
            rel_x = (x - merged_box[0]) / box_width
            rel_y = (y - merged_box[1]) / box_height
            rel_positions.append((rel_x, rel_y))
        
        if not rel_positions:
            return 0.0
            
        # Calculate minimum distance between any two keypoints
        min_dist = float('inf')
        for i in range(len(rel_positions)):
            for j in range(i + 1, len(rel_positions)):
                dx = rel_positions[i][0] - rel_positions[j][0]
                dy = rel_positions[i][1] - rel_positions[j][1]
                dist = np.sqrt(dx*dx + dy*dy)
                min_dist = min(min_dist, dist)
        
        # Calculate how well the keypoints cover the box
        # Divide box into a grid and count how many cells contain keypoints
        grid_size = 4  # 4x4 grid
        grid = np.zeros((grid_size, grid_size))
        for rel_x, rel_y in rel_positions:
            # Ensure grid indices are within bounds
            grid_x = min(max(0, int(rel_x * grid_size)), grid_size - 1)
            grid_y = min(max(0, int(rel_y * grid_size)), grid_size - 1)
            grid[grid_y, grid_x] = 1
        
        coverage = np.sum(grid) / (grid_size * grid_size)
        
        # Combine minimum distance and coverage
        # Higher score for well-distributed keypoints
        distribution_score = (min_dist * 0.7 + coverage * 0.3)
        
        return distribution_score

    def _calculate_corner_proximity_score(self, kp, merged_box):
        """
        Calculate how close a keypoint is to the corners of the merged box.
        Returns a score between 0 and 1, where 1 means the keypoint is very close to a corner.
        Only considers visible keypoints.
        """
        # Return 0 for invisible keypoints
        if kp.v <= 0:
            return 0.0
            
        # Get box corners
        corners = [
            (merged_box[0], merged_box[1]),  # top-left
            (merged_box[2], merged_box[1]),  # top-right
            (merged_box[2], merged_box[3]),  # bottom-right
            (merged_box[0], merged_box[3])   # bottom-left
        ]
        
        # Calculate distance to each corner
        min_dist = float('inf')
        for corner_x, corner_y in corners:
            dx = kp.x - corner_x
            dy = kp.y - corner_y
            dist = np.sqrt(dx*dx + dy*dy)
            min_dist = min(min_dist, dist)
        
        # Normalize distance by box diagonal
        box_diagonal = np.sqrt(
            (merged_box[2] - merged_box[0])**2 + 
            (merged_box[3] - merged_box[1])**2
        )
        normalized_dist = min_dist / box_diagonal
        
        # Higher score for points closer to corners
        corner_score = 1 - normalized_dist
        
        return corner_score

    def _merge_keypoints_distributed(self, valid_preds: List[ObjectPrediction], merged_box: List[float], image=None) -> List[float]:
        """
        Select keypoints that are well-distributed within the merged box and close to corners when appropriate.
        Uses simple averaging for the first keypoint and the specified strategy for the rest.
        Only considers visible keypoints.
        """
        num_keypoints = len(valid_preds[0].keypoints)
        best_keypoints = []
        
        # First pass: collect all valid keypoints for each position
        all_keypoints = [[] for _ in range(num_keypoints)]
        for pred in valid_preds:
            for i, kp in enumerate(pred.keypoints):
                if kp.v > 0:  # Only consider visible keypoints
                    all_keypoints[i].append((kp, pred.score.value, pred.bbox.to_xyxy()))
        
        # Handle first keypoint with simple averaging
        if all_keypoints[0]:
            # Convert first keypoints to numpy arrays
            first_keypoint_arrays = []
            for kp, _, _ in all_keypoints[0]:
                first_keypoint_arrays.append([kp.x, kp.y, kp.v])
            
            # Average the first keypoints
            avg_first_keypoint = np.mean(first_keypoint_arrays, axis=0)
            best_keypoints.append(Keypoint(avg_first_keypoint[0], avg_first_keypoint[1], avg_first_keypoint[2]))
        else:
            # If no valid first keypoint, use the one from highest confidence detection
            best_pred = max(valid_preds, key=lambda p: p.score.value)
            best_kp = best_pred.keypoints[0]
            # If the keypoint is not visible, set visibility to 0
            if best_kp.v <= 0:
                best_kp = Keypoint(best_kp.x, best_kp.y, 0.0)
            best_keypoints.append(best_kp)
        
        # Handle remaining keypoints with the specified strategy
        for kp_idx in range(1, num_keypoints):
            if not all_keypoints[kp_idx]:
                # If no valid keypoints, use the one from highest confidence detection
                best_pred = max(valid_preds, key=lambda p: p.score.value)
                best_kp = best_pred.keypoints[kp_idx]
                # If the keypoint is not visible, set visibility to 0
                if best_kp.v <= 0:
                    best_kp = Keypoint(best_kp.x, best_kp.y, 0.0)
                best_keypoints.append(best_kp)
                continue
            
            # Try each keypoint and calculate scores
            best_score = float('-inf')
            best_kp = None
            
            for kp, detection_score, pred_box in all_keypoints[kp_idx]:
                # Calculate position confidence
                position_confidence = self._calculate_keypoint_confidence(
                    kp, pred_box, merged_box
                )
                
                # Calculate distribution score with this keypoint
                temp_keypoints = best_keypoints + [kp]
                distribution_score = self._calculate_spatial_distribution_score(
                    temp_keypoints, merged_box
                )
                
                # Calculate corner proximity score
                corner_score = self._calculate_corner_proximity_score(kp, merged_box)
                
                # Combine scores with weights
                # Higher weight for corner proximity when keypoint is near a corner
                corner_weight = 0.3 if corner_score > 0.7 else 0.1
                score = (position_confidence * 0.3 + 
                        distribution_score * (0.4 - corner_weight) + 
                        corner_score * corner_weight +
                        detection_score * 0.2)
                
                if score > best_score:
                    best_score = score
                    best_kp = kp
            
            best_keypoints.append(best_kp)
        
        # Convert best keypoints to list format
        return [coord for kp in best_keypoints for coord in [kp.x, kp.y, kp.v]]

    def _merge_keypoints_highest_score(self, valid_preds: List[ObjectPrediction], merged_box: List[float]) -> List[float]:
        """
        Select keypoints with the highest keypoint confidence for each keypoint index.
        For each keypoint position, picks the keypoint from the detection with the highest keypoint confidence.
        Only considers keypoints from predictions that have sufficient overlap with the merged box.
        """
        if not valid_preds:
            return []
            
        # Get the number of keypoints from the first valid prediction
        num_keypoints = len(valid_preds[0].keypoints)
        
        # For each keypoint position, find the keypoint from highest confidence detection
        best_keypoints = []
        for kp_idx in range(num_keypoints):
            best_kp = None
            best_score = float('-inf')
            
            for pred in valid_preds:
                # Skip predictions with low keypoint confidence
                kp_confidence = pred.keypoints.confidence if pred.keypoints.confidence is not None else 0.0
                if kp_confidence < 0.1:  # Minimum confidence threshold
                    continue
                    
                # Skip predictions with low overlap
                box_overlap = self._calculate_ios(merged_box, pred.bbox.to_xyxy())
                if box_overlap < 0.1:  # Minimum overlap threshold
                    continue
                
                kp = pred.keypoints[kp_idx]
                if kp.v > 0:  # Only consider visible keypoints
                    # Combine keypoint confidence with box overlap
                    combined_score = kp_confidence * box_overlap
                    if combined_score > best_score:
                        best_score = combined_score
                        best_kp = kp
            
            # If no valid keypoint found for this position, try to find one from high confidence detections
            if best_kp is None:
                # Sort predictions by keypoint confidence and try to find a visible keypoint
                sorted_preds = sorted(valid_preds, key=lambda p: p.keypoints.confidence if p.keypoints.confidence is not None else 0.0, reverse=True)
                for pred in sorted_preds:
                    kp_confidence = pred.keypoints.confidence if pred.keypoints.confidence is not None else 0.0
                    if kp_confidence < 0.1:  # Stop if confidence is too low
                        break
                    kp = pred.keypoints[kp_idx]
                    if kp.v > 0:  # Only use visible keypoints
                        best_kp = kp
                        break
            
            # If still no valid keypoint, use the one from highest confidence detection
            if best_kp is None:
                best_pred = max(valid_preds, key=lambda p: p.keypoints.confidence if p.keypoints.confidence is not None else 0.0)
                best_kp = best_pred.keypoints[kp_idx]
            
            best_keypoints.append(best_kp)
        
        # Convert best keypoints to list format
        return [coord for kp in best_keypoints for coord in [kp.x, kp.y, kp.v]]

    def _merge_keypoints_largest_box(self, valid_preds: List[ObjectPrediction], merged_box: List[float], image=None) -> List[float]:
        """
        Select keypoints from the prediction with the largest bounding box area.
        Optionally visualize all candidate boxes and the largest box if debug is enabled.
        """
        print("\nIn _merge_keypoints_largest_box:")
        print(f"Number of valid predictions: {len(valid_preds)}")
        
        def box_area(box):
            return max(0, (box[2] - box[0])) * max(0, (box[3] - box[1]))
        
        # Print all valid predictions and their keypoints
        for i, pred in enumerate(valid_preds):
            print(f"\nPrediction {i}:")
            print(f"  Box: {pred.bbox.to_xyxy()}")
            print(f"  Area: {box_area(pred.bbox.to_xyxy())}")
            print(f"  Has keypoints: {hasattr(pred, 'keypoints') and pred.keypoints is not None}")
            if hasattr(pred, 'keypoints') and pred.keypoints is not None:
                print(f"  Keypoints: {pred.keypoints}")
        
        # Find the largest box among valid_preds
        largest_pred = max(valid_preds, key=lambda p: box_area(p.bbox.to_xyxy()))
        largest_box = largest_pred.bbox.to_xyxy()
        largest_area = box_area(largest_box)
        
        print(f"\nSelected largest prediction:")
        print(f"  Box: {largest_box}")
        print(f"  Area: {largest_area}")
        print(f"  Has keypoints: {hasattr(largest_pred, 'keypoints') and largest_pred.keypoints is not None}")
        if hasattr(largest_pred, 'keypoints') and largest_pred.keypoints is not None:
            print(f"  Keypoints: {largest_pred.keypoints}")

        # Debug visualization only if image is provided
        if image is not None:
            debug_img = image.copy()
            for pred in valid_preds:
                box = pred.bbox.to_xyxy()
                area = box_area(box)
                color = (0, 0, 255)  # Red for all boxes
                thickness = 2
                # Draw rectangle
                cv2.rectangle(debug_img, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), color, thickness)
                # Annotate area
                cv2.putText(debug_img, f"A:{area:.0f}", (int(box[0]), int(box[1]) - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            # Draw the largest box in blue
            cv2.rectangle(debug_img, (int(largest_box[0]), int(largest_box[1])), (int(largest_box[2]), int(largest_box[3])), (255, 0, 0), 2)
            cv2.putText(debug_img, f"LARGEST", (int(largest_box[0]), int(largest_box[1]) - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            # Optionally save or show the debug image
            if self.debug_dir:
                import os
                os.makedirs(self.debug_dir, exist_ok=True)
                debug_path = os.path.join(self.debug_dir, f"largest_box_debug.jpg")
                cv2.imwrite(debug_path, debug_img)
            else:
                cv2.imshow("Largest Box Debug", debug_img)
                cv2.waitKey(0)
                cv2.destroyAllWindows()

        # If the largest prediction doesn't have keypoints, try to find one that does
        if not hasattr(largest_pred, 'keypoints') or largest_pred.keypoints is None:
            print("\nLargest prediction has no keypoints, looking for alternative...")
            for pred in valid_preds:
                if hasattr(pred, 'keypoints') and pred.keypoints is not None:
                    print(f"Found prediction with keypoints: {pred.keypoints}")
                    largest_pred = pred
                    break

        result = [coord for kp in largest_pred.keypoints for coord in [kp.x, kp.y, kp.v]] if hasattr(largest_pred, 'keypoints') and largest_pred.keypoints is not None else []
        print(f"\nReturning keypoints: {result}")
        return result

    def _calculate_keypoint_distance(self, keypoints1, keypoints2, index):
        """
        Calculate the Euclidean distance between keypoints of the same index from two different predictions.
        Returns 0 if either keypoint is not visible.
        """
        if len(keypoints1) <= index or len(keypoints2) <= index:
            return 0.0
        
        kp1 = keypoints1[index]
        kp2 = keypoints2[index]
        
        # Only consider visible keypoints
        if kp1.v <= 0 or kp2.v <= 0:
            return 0.0
            
        dx = kp1.x - kp2.x
        dy = kp1.y - kp2.y
        return np.sqrt(dx*dx + dy*dy)

    def _merge_keypoints_largest_distance(self, valid_preds: List[ObjectPrediction], merged_box: List[float], image=None) -> List[float]:
        """
        Select keypoints from the prediction that has the largest distance between keypoints of the same index.
        For each keypoint index, finds the prediction pair with the largest distance between their keypoints,
        and uses the keypoint from the prediction with higher confidence.
        """
        print("\nIn _merge_keypoints_largest_distance:")
        print(f"Number of valid predictions: {len(valid_preds)}")
        
        # Get all predictions with valid keypoints
        valid_keypoint_preds = [p for p in valid_preds if hasattr(p, 'keypoints') and p.keypoints is not None]
        if not valid_keypoint_preds:
            print("No predictions with valid keypoints found")
            return []
            
        # Get the number of keypoints from the first valid prediction
        num_keypoints = len(valid_keypoint_preds[0].keypoints)
        print(f"Number of keypoints per prediction: {num_keypoints}")
        
        # For each keypoint index, find the prediction pair with largest distance
        best_keypoints = []
        for kp_idx in range(num_keypoints):
            print(f"\nProcessing keypoint index {kp_idx}:")
            max_distance = 0.0
            best_pred = None
            
            # Compare each pair of predictions
            for i, pred1 in enumerate(valid_keypoint_preds):
                for j, pred2 in enumerate(valid_keypoint_preds[i+1:], i+1):
                    distance = self._calculate_keypoint_distance(pred1.keypoints, pred2.keypoints, kp_idx)
                    print(f"  Distance between pred {i} and {j}: {distance}")
                    
                    if distance > max_distance:
                        max_distance = distance
                        # Choose the prediction with higher confidence
                        if pred1.keypoints.confidence > pred2.keypoints.confidence:
                            best_pred = pred1
                        else:
                            best_pred = pred2
            
            if best_pred is not None:
                print(f"  Selected prediction with distance {max_distance}")
                print(f"  Keypoint: {best_pred.keypoints[kp_idx]}")
                best_keypoints.append(best_pred.keypoints[kp_idx])
            else:
                # If no valid keypoint found, use the one from highest confidence detection
                best_pred = max(valid_keypoint_preds, key=lambda p: p.keypoints.confidence if p.keypoints.confidence is not None else 0.0)
                best_keypoints.append(best_pred.keypoints[kp_idx])
                print(f"  No valid distance found, using keypoint from highest confidence prediction")
                print(f"  Keypoint: {best_pred.keypoints[kp_idx]}")

        # Debug visualization only if image is provided
        if image is not None:
            debug_img = image.copy()
            for pred in valid_preds:
                box = pred.bbox.to_xyxy()
                color = (0, 0, 255)  # Red for all boxes
                thickness = 2
                # Draw rectangle
                cv2.rectangle(debug_img, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), color, thickness)
                # Draw keypoints if present
                if hasattr(pred, 'keypoints') and pred.keypoints is not None:
                    for kp in pred.keypoints:
                        if kp.v > 0:  # Only draw visible keypoints
                            cv2.circle(debug_img, (int(kp.x), int(kp.y)), 3, (0, 255, 0), -1)
            
            # Draw the selected keypoints in blue
            for kp in best_keypoints:
                if kp.v > 0:  # Only draw visible keypoints
                    cv2.circle(debug_img, (int(kp.x), int(kp.y)), 5, (255, 0, 0), -1)
            
            # Optionally save or show the debug image
            if self.debug_dir:
                import os
                os.makedirs(self.debug_dir, exist_ok=True)
                debug_path = os.path.join(self.debug_dir, f"largest_distance_debug.jpg")
                cv2.imwrite(debug_path, debug_img)
            else:
                cv2.imshow("Largest Distance Debug", debug_img)
                cv2.waitKey(0)
                cv2.destroyAllWindows()

        # Convert best keypoints to list format
        result = [coord for kp in best_keypoints for coord in [kp.x, kp.y, kp.v]]
        print(f"\nReturning keypoints: {result}")
        return result

    def __call__(self, object_prediction_list: List[ObjectPrediction], image=None) -> List[ObjectPrediction]:
        """
        Main method to process predictions and merge keypoints.
        First merges boxes using the base postprocess, then merges keypoints using the selected strategy.
        If disable_merging is True, returns the original predictions without any merging.
        """
        if len(object_prediction_list) == 0:
            return object_prediction_list

        # If merging is disabled, return original predictions
        if self.disable_merging:
            return object_prediction_list

        print("Starting keypoint merging process...")
        print(f"Number of input predictions: {len(object_prediction_list)}")
        print(f"Keypoint merge strategy: {self.keypoint_merge_strategy}")

        # First, use the base postprocess to merge boxes
        merged_predictions = self.base_postprocess(object_prediction_list)
        print(f"Number of merged predictions: {len(merged_predictions)}")

        # Now handle keypoint merging for each merged prediction
        final_predictions = []
        for merged_pred in merged_predictions:
            # Find all predictions that contributed to this merged box
            contributing_preds = []
            for pred in object_prediction_list:
                if self._boxes_match(merged_pred.bbox.to_xyxy(), pred.bbox.to_xyxy()):
                    contributing_preds.append(pred)

            print(f"\nProcessing merged prediction with {len(contributing_preds)} contributing predictions")

            # If we have multiple predictions with keypoints, merge them
            if len(contributing_preds) > 1:
                # Get all valid keypoints
                valid_preds = [p for p in contributing_preds if hasattr(p, 'keypoints') and p.keypoints is not None]
                print(f"Found {len(valid_preds)} predictions with valid keypoints")
                
                if valid_preds:
                    merged_box = merged_pred.bbox.to_xyxy()
                    print(f"Using {self.keypoint_merge_strategy} strategy for keypoint merging")
                    
                    # Apply selected merging strategy
                    if self.keypoint_merge_strategy == "SIMPLE":
                        flat_keypoints = self._merge_keypoints_simple(valid_preds)
                    elif self.keypoint_merge_strategy == "WEIGHTED":
                        flat_keypoints = self._merge_keypoints_weighted(valid_preds, merged_box)
                    elif self.keypoint_merge_strategy == "CLOSEST_TO_BOX":
                        flat_keypoints = self._merge_keypoints_closest_to_box(valid_preds, merged_box, image)
                    elif self.keypoint_merge_strategy == "OVERLAP_AWARE":
                        flat_keypoints = self._merge_keypoints_overlap_aware(valid_preds, merged_box, image)
                    elif self.keypoint_merge_strategy == "HIGHEST_SCORE":
                        flat_keypoints = self._merge_keypoints_highest_score(valid_preds, merged_box)
                    elif self.keypoint_merge_strategy == "LARGEST_BOX":
                        flat_keypoints = self._merge_keypoints_largest_box(valid_preds, merged_box, image)
                    elif self.keypoint_merge_strategy == "LARGEST_DISTANCE":
                        flat_keypoints = self._merge_keypoints_largest_distance(valid_preds, merged_box, image)
                    else:  # DISTRIBUTED
                        flat_keypoints = self._merge_keypoints_distributed(valid_preds, merged_box, image)
                    
                    merged_pred.keypoints = Keypoints(flat_keypoints)
                    print(f"Merged keypoints: {merged_pred.keypoints}")
                    
                    # Visualize debug information if enabled
                    if self.debug and image is not None:
                        self._visualize_debug(image, merged_pred, contributing_preds, valid_preds, merged_box)

            final_predictions.append(merged_pred)

        print(f"\nFinal number of predictions: {len(final_predictions)}")
        return final_predictions

    def _boxes_match(self, box1, box2):
        """
        Check if two boxes match based on the configured metric and threshold.
        Uses either IOU or IOS metric.
        """
        if self.match_metric == "IOS":
            match_score = self._calculate_ios(box1, box2)
        else:  # IOU
            match_score = self._calculate_iou(box1, box2)
        return match_score > self.match_threshold

    def _calculate_iou(self, box1, box2):
        """
        Calculate Intersection over Union between two boxes.
        Returns a value between 0 and 1.
        """
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])

        intersection = max(0, x2 - x1) * max(0, y2 - y1)
        box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
        box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
        union = box1_area + box2_area - intersection

        return intersection / union if union > 0 else 0

    def _calculate_ios(self, box1, box2):
        """
        Calculate Intersection over Smaller area between two boxes.
        Returns a value between 0 and 1.
        """
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])

        intersection = max(0, x2 - x1) * max(0, y2 - y1)
        box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
        box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
        smaller_area = min(box1_area, box2_area)

        return intersection / smaller_area if smaller_area > 0 else 0 