import warnings

import numpy as np


def prefilter_boxes(boxes, scores, labels, weights, pass_through_data, thr):
    new_boxes = dict()
    new_pass_through = dict()

    for t in range(len(boxes)):
        if (
            len(boxes[t]) != len(scores[t])
            or len(boxes[t]) != len(labels[t])
            or len(boxes[t]) != len(pass_through_data[t])
        ):
            print(
                "Error. Mismatch in length of boxes, scores, labels, or pass-through data"
            )
            exit()

        for j in range(len(boxes[t])):
            score = scores[t][j]
            if score < thr:
                continue
            label = int(labels[t][j])
            box_part = boxes[t][j]
            x1 = float(box_part[0])
            y1 = float(box_part[1])
            x2 = float(box_part[2])
            y2 = float(box_part[3])
            pass_data = pass_through_data[t][j]

            # Box data checks
            if x2 < x1:
                warnings.warn("X2 < X1 value in box. Swap them.")
                x1, x2 = x2, x1
            if y2 < y1:
                warnings.warn("Y2 < Y1 value in box. Swap them.")
                y1, y2 = y2, y1
            if x1 < 0:
                warnings.warn("X1 < 0 in box. Set it to 0.")
                x1 = 0
            if x1 > 1:
                warnings.warn(
                    "X1 > 1 in box. Set it to 1. Check that you normalize boxes in [0, 1] range."
                )
                x1 = 1
            if x2 < 0:
                warnings.warn("X2 < 0 in box. Set it to 0.")
                x2 = 0
            if x2 > 1:
                warnings.warn(
                    "X2 > 1 in box. Set it to 1. Check that you normalize boxes in [0, 1] range."
                )
                x2 = 1
            if y1 < 0:
                warnings.warn("Y1 < 0 in box. Set it to 0.")
                y1 = 0
            if y1 > 1:
                warnings.warn(
                    "Y1 > 1 in box. Set it to 1. Check that you normalize boxes in [0, 1] range."
                )
                y1 = 1
            if y2 < 0:
                warnings.warn("Y2 < 0 in box. Set it to 0.")
                y2 = 0
            if y2 > 1:
                warnings.warn(
                    "Y2 > 1 in box. Set it to 1. Check that you normalize boxes in [0, 1] range."
                )
                y2 = 1

            if (x2 - x1) * (y2 - y1) == 0.0:
                warnings.warn("Zero area box skipped: {}.".format(box_part))
                continue

            b = [int(label), float(score) * weights[t], weights[t], t, x1, y1, x2, y2]

            if label not in new_boxes:
                new_boxes[label] = []
                new_pass_through[label] = []
            new_boxes[label].append(b)
            new_pass_through[label].append(pass_data)

    for k in new_boxes:
        current_boxes = np.array(new_boxes[k])
        sorted_indices = current_boxes[:, 1].argsort()[::-1]
        new_boxes[k] = current_boxes[sorted_indices]
        new_pass_through[k] = [new_pass_through[k][i] for i in sorted_indices]

    return new_boxes, new_pass_through


def get_weighted_box(boxes, conf_type="avg"):
    """
    Create weighted box for set of boxes
    :param boxes: set of boxes to fuse
    :param conf_type: type of confidence one of 'avg' or 'max'
    :return: weighted box (label, score, weight, model index, x1, y1, x2, y2)
    """

    box = np.zeros(8, dtype=np.float32)
    conf = 0
    conf_list = []
    w = 0
    for b in boxes:
        box[4:] += b[1] * b[4:]
        conf += b[1]
        conf_list.append(b[1])
        w += b[2]
    box[0] = boxes[0][0]
    if conf_type in ("avg", "box_and_model_avg", "absent_model_aware_avg"):
        box[1] = conf / len(boxes)
    elif conf_type == "max":
        box[1] = np.array(conf_list).max()
    box[2] = w
    box[3] = -1  # model index field is retained for consistency but is not used.
    box[4:] /= conf
    return box


def find_matching_box_fast(boxes_list, new_box, match_iou):
    """
    Find a matching box in boxes_list for new_box using IoU.
    Ensure strict class matching.
    """

    def bb_iou_array(boxes, new_box):
        xA = np.maximum(boxes[:, 0], new_box[0])
        yA = np.maximum(boxes[:, 1], new_box[1])
        xB = np.minimum(boxes[:, 2], new_box[2])
        yB = np.minimum(boxes[:, 3], new_box[3])

        interArea = np.maximum(xB - xA, 0) * np.maximum(yB - yA, 0)

        boxAArea = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
        boxBArea = (new_box[2] - new_box[0]) * (new_box[3] - new_box[1])

        iou = interArea / (boxAArea + boxBArea - interArea)
        return iou

    if boxes_list.shape[0] == 0:
        return -1, match_iou

    boxes = boxes_list

    # Compute IoU
    ious = bb_iou_array(boxes[:, 4:], new_box[4:])

    # **Strict class check: only consider same class**
    same_label_mask = boxes[:, 0] == new_box[0]
    ious[~same_label_mask] = -1  # Set IoU to -1 for different classes

    # Find the best match
    best_idx = np.argmax(ious)
    best_iou = ious[best_idx]

    if best_iou <= match_iou:
        best_iou = match_iou
        best_idx = -1  # No valid match

    return best_idx, best_iou


def weighted_boxes_fusion(
    boxes_list,
    scores_list,
    labels_list,
    pass_through_data,
    weights=None,
    iou_thr=0.55,
    skip_box_thr=0.0,
    conf_type="box_and_model_avg",
    allows_overflow=False,
):
    if weights is None:
        weights = np.ones(len(boxes_list))
    if len(weights) != len(boxes_list):
        print(
            "Warning: incorrect number of weights {}. Must be: {}. Set weights equal to 1.".format(
                len(weights), len(boxes_list)
            )
        )
        weights = np.ones(len(boxes_list))
    weights = np.array(weights)

    if conf_type not in ["avg", "max", "box_and_model_avg", "absent_model_aware_avg"]:
        print(
            'Unknown conf_type: {}. Must be "avg", "max" or "box_and_model_avg", or "absent_model_aware_avg"'.format(
                conf_type
            )
        )
        exit()

    filtered_boxes, filtered_pass_through = prefilter_boxes(
        boxes_list, scores_list, labels_list, weights, pass_through_data, skip_box_thr
    )
    if len(filtered_boxes) == 0:
        return np.zeros((0, 4)), np.zeros((0,)), np.zeros((0,)), []

    overall_boxes = []
    overall_pass_through = []

    for label in filtered_boxes:
        boxes = filtered_boxes[label]
        new_boxes = []
        new_pass_data = []
        weighted_boxes = np.empty((0, 8))

        # Clusterize boxes
        for j in range(0, len(boxes)):
            index, best_iou = find_matching_box_fast(weighted_boxes, boxes[j], iou_thr)

            if index != -1:
                # Ensure labels match before merging
                if int(weighted_boxes[index][0]) != int(boxes[j][0]):
                    continue  # **Prevent incorrect class merging**

                new_boxes[index].append(boxes[j])
                new_pass_data[index].append(filtered_pass_through[label][j])
                weighted_boxes[index] = get_weighted_box(new_boxes[index], conf_type)
            else:
                new_boxes.append([boxes[j].copy()])
                new_pass_data.append([filtered_pass_through[label][j]])
                weighted_boxes = np.vstack((weighted_boxes, boxes[j].copy()))

        # Rescale confidence based on number of models and boxes
        for i in range(len(new_boxes)):
            clustered_boxes = new_boxes[i]

            if conf_type == "box_and_model_avg":
                clustered_boxes = np.array(clustered_boxes)
                weighted_boxes[i, 1] = (
                    weighted_boxes[i, 1] * len(clustered_boxes) / weighted_boxes[i, 2]
                )

                _, idx = np.unique(clustered_boxes[:, 3], return_index=True)
                weighted_boxes[i, 1] = (
                    weighted_boxes[i, 1] * clustered_boxes[idx, 2].sum() / weights.sum()
                )

            elif conf_type == "absent_model_aware_avg":
                clustered_boxes = np.array(clustered_boxes)
                models = np.unique(clustered_boxes[:, 3]).astype(int)

                mask = np.ones(len(weights), dtype=bool)
                mask[models] = False

                weighted_boxes[i, 1] = (
                    weighted_boxes[i, 1]
                    * len(clustered_boxes)
                    / (weighted_boxes[i, 2] + weights[mask].sum())
                )

            elif conf_type == "max":
                weighted_boxes[i, 1] = weighted_boxes[i, 1] / weights.max()

            elif not allows_overflow:
                weighted_boxes[i, 1] = (
                    weighted_boxes[i, 1]
                    * min(len(weights), len(clustered_boxes))
                    / weights.sum()
                )

            else:
                weighted_boxes[i, 1] = (
                    weighted_boxes[i, 1] * len(clustered_boxes) / weights.sum()
                )

        overall_boxes.append(weighted_boxes)
        overall_pass_through.extend(new_pass_data)

    # overall_boxes = np.concatenate(overall_boxes, axis=0)
    # overall_boxes = overall_boxes[overall_boxes[:, 1].argsort()[::-1]]
    # boxes = overall_boxes[:, 4:]
    # scores = overall_boxes[:, 1]
    # labels = overall_boxes[:, 0]

    overall_boxes = np.concatenate(overall_boxes, axis=0)
    # Fix: Sort by confidence score to ensure overall_pass_through is in the same order
    sorted_indices = overall_boxes[:, 1].argsort()[::-1]
    overall_boxes = overall_boxes[sorted_indices]
    boxes = overall_boxes[:, 4:]
    scores = overall_boxes[:, 1]
    labels = overall_boxes[:, 0]

    # Apply the same sorting order to pass-through data
    overall_pass_through = [overall_pass_through[i] for i in sorted_indices]

    return boxes, scores, labels, overall_pass_through


class EnsembleModel:
    def __init__(
        self,
        orig_img_width,
        orig_img_height,
        category_config=None,
        iou_thr=0.55,
        skip_box_thr=0.0001,
        conf_type="max",
    ):
        self.models = {}
        self.ensemble_config = {
            "iou_thr": iou_thr,
            "skip_box_thr": skip_box_thr,
            "conf_type": conf_type,
        }
        self.category_config = category_config or {}
        self.orig_img_width = orig_img_width
        self.orig_img_height = orig_img_height

    def add_model(self, model_name, weight=1):
        if model_name not in self.models:
            self.models[model_name] = {
                "bboxes": [],
                "scores": [],
                "category_ids": [],
                "pass_through_data": [],
                "weight": weight,
            }

    def normalize_box(self, box):
        x1, y1, x2, y2 = box
        return [
            x1 / self.orig_img_width,
            y1 / self.orig_img_height,
            x2 / self.orig_img_width,
            y2 / self.orig_img_height,
        ]

    def add_detection(
        self, model_name, category_id, bbox, score, pass_data=None, normalized=False
    ):
        if model_name not in self.models:
            raise ValueError(
                f"Model '{model_name}' is not registered. Call `add_model()` first."
            )

        bbox = bbox if normalized else self.normalize_box(bbox)

        self.models[model_name]["bboxes"].append(bbox)
        self.models[model_name]["scores"].append(score)
        self.models[model_name]["category_ids"].append(category_id)
        self.models[model_name]["pass_through_data"].append(pass_data)

    def ensemble_detections(self):
        if not self.models:
            raise ValueError("No models have been added. Use `add_model()` first.")

        bboxes_list = []
        scores_list = []
        category_ids_list = []
        pass_through_list = []
        weights = []

        for model_name, data in self.models.items():
            bboxes_list.append(data["bboxes"])
            scores_list.append(data["scores"])
            category_ids_list.append(data["category_ids"])
            pass_through_list.append(data["pass_through_data"])
            weights.append(data["weight"])

        boxes, scores, category_ids, pass_through_data = weighted_boxes_fusion(
            bboxes_list,
            scores_list,
            category_ids_list,
            pass_through_data=pass_through_list,
            weights=weights,
            **self.ensemble_config,
        )

        # Apply category-specific score filtering
        filtered_boxes = []
        filtered_scores = []
        filtered_category_ids = []
        filtered_pass_through_data = []

        for i, cat_id in enumerate(category_ids):
            min_score = self.category_config.get(cat_id, {}).get("min_score", 0.0)
            if scores[i] >= min_score:
                filtered_boxes.append(boxes[i])
                filtered_scores.append(scores[i])
                filtered_category_ids.append(cat_id)
                filtered_pass_through_data.append(pass_through_data[i])

        denormalized_boxes = [
            {
                "min_x": int(x1 * self.orig_img_width),
                "min_y": int(y1 * self.orig_img_height),
                "max_x": int(x2 * self.orig_img_width),
                "max_y": int(y2 * self.orig_img_height),
            }
            for x1, y1, x2, y2 in filtered_boxes
        ]

        category_names = [
            self.category_config.get(cat_id, {}).get("enum", "Unknown")
            for cat_id in filtered_category_ids
        ]

        return (
            denormalized_boxes,
            filtered_scores,
            filtered_category_ids,
            category_names,
            filtered_pass_through_data,
        )
