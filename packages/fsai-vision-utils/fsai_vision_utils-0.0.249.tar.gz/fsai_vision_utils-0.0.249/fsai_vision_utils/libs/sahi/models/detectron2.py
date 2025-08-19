import logging
from typing import List, Optional

import numpy as np

from sahi.models.base import DetectionModel
from fsai_vision_utils.libs.sahi.prediction import ObjectPrediction

from sahi.utils.cv import get_coco_segmentation_from_bool_mask
from sahi.utils.import_utils import check_requirements

logger = logging.getLogger(__name__)


class Detectron2DetectionModel(DetectionModel):
    def check_dependencies(self):
        check_requirements(["torch", "detectron2"])

    def load_model(self):
        from detectron2.config import get_cfg
        from detectron2.data import MetadataCatalog
        from detectron2.engine import DefaultPredictor
        from detectron2.model_zoo import model_zoo

        cfg = get_cfg()

        try:  # try to load from model zoo
            config_file = model_zoo.get_config_file(self.config_path)
            cfg.merge_from_file(config_file)
            cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url(self.config_path)
        except Exception as e:  # try to load from local
            print(e)
            if self.config_path is not None:
                cfg.merge_from_file(self.config_path)
            cfg.MODEL.WEIGHTS = self.model_path

        # set model device
        cfg.MODEL.DEVICE = self.device.type
        # set input image size
        if self.image_size is not None:
            cfg.INPUT.MIN_SIZE_TEST = self.image_size
            cfg.INPUT.MAX_SIZE_TEST = self.image_size
        # init predictor
        model = DefaultPredictor(cfg)

        self.model = model

        # detectron2 category mapping
        if self.category_mapping is None:
            try:  # try to parse category names from metadata
                metadata = MetadataCatalog.get(cfg.DATASETS.TRAIN[0])
                category_names = metadata.thing_classes
                self.category_names = category_names
                self.category_mapping = {
                    str(ind): category_name
                    for ind, category_name in enumerate(self.category_names)
                }
            except Exception as e:
                logger.warning(e)
                if cfg.MODEL.META_ARCHITECTURE == "RetinaNet":
                    num_categories = cfg.MODEL.RETINANET.NUM_CLASSES
                else:  # fasterrcnn/maskrcnn etc
                    num_categories = cfg.MODEL.ROI_HEADS.NUM_CLASSES
                self.category_names = [
                    str(category_id) for category_id in range(num_categories)
                ]
                self.category_mapping = {
                    str(ind): category_name
                    for ind, category_name in enumerate(self.category_names)
                }
        else:
            self.category_names = list(self.category_mapping.values())

    def perform_inference(self, image: np.ndarray):
        """
        Prediction is performed using self.model and the prediction result is set to self._original_predictions.
        """
        if self.model is None:
            raise RuntimeError("Model is not loaded, load it by calling .load_model()")

        if isinstance(image, np.ndarray) and self.model.input_format == "BGR":
            image = image[:, :, ::-1]

        prediction_result = self.model(image)
        self._original_predictions = prediction_result

    @property
    def num_categories(self):
        return len(self.category_mapping)

    def _create_object_prediction_list_from_original_predictions(
        self,
        shift_amount_list: Optional[List[List[int]]] = [[0, 0]],
        full_shape_list: Optional[List[List[int]]] = None,
    ):
        original_predictions = self._original_predictions

        if isinstance(shift_amount_list[0], int):
            shift_amount_list = [shift_amount_list]
        if full_shape_list is not None and isinstance(full_shape_list[0], int):
            full_shape_list = [full_shape_list]

        shift_amount = shift_amount_list[0]
        full_shape = None if full_shape_list is None else full_shape_list[0]

        instances = original_predictions["instances"]

        boxes = instances.pred_boxes.tensor.cpu().numpy()
        scores = instances.scores.cpu().numpy()
        category_ids = instances.pred_classes.cpu().numpy()

        try:
            masks = instances.pred_masks.cpu().numpy()
        except AttributeError:
            masks = None

        # try:
        #     keypoints = instances.pred_keypoints.cpu().numpy()  # shape: (N, K, 3)
        #     print(f"[INFO] Keypoints shape: {keypoints.shape}")
        # except AttributeError as e:
        #     print(f"[INFO] Keypoints not found in the prediction: {e}")
        #     keypoints = []

        keypoints = None
        try:
            keypoints = instances.pred_keypoints.cpu().numpy()  # shape: (N, K, 3)
            # print(f"[INFO] Keypoints shape: {keypoints.shape}")
        except AttributeError as e:
            print(f"[INFO] Keypoints not found in the prediction: {e}")
            keypoints = None

        high_conf_mask = scores >= self.confidence_threshold
        boxes = boxes[high_conf_mask]
        scores = scores[high_conf_mask]
        category_ids = category_ids[high_conf_mask]
        if masks is not None:
            masks = masks[high_conf_mask]

        # if len(keypoints) == len(high_conf_mask):
        #     keypoints = keypoints[high_conf_mask]
        #     print(f"[INFO] Keypoints shape after filtering: {keypoints.shape}")
        # elif len(keypoints) == len(scores):
        #     print(f"[INFO] Keypoints shape matches scores: {keypoints.shape}")
        #     keypoints = keypoints
        # else:
        #     print(
        #         f"[Warning] Keypoints and scores mismatch: keypoints={len(keypoints)}, scores={len(scores)}"
        #     )
        #     keypoints = []  #


            
        if keypoints is not None:
            if len(keypoints) == len(high_conf_mask):
                keypoints = keypoints[high_conf_mask]
                # print(f"[INFO] Keypoints shape after filtering: {keypoints.shape}")
            elif len(keypoints) == len(scores):
                print(f"[INFO] Keypoints shape matches scores: {keypoints.shape}")
            else:
                print(
                    f"[Warning] Keypoints and scores mismatch: keypoints={len(keypoints)}, scores={len(scores)}"
                )
                keypoints = None

        object_prediction_list = []

        for i in range(len(boxes)):
            keypoints_list = None

            if keypoints is not None and len(keypoints) > i:
                current_kps = keypoints[i]  # shape: (K, 3)
                # Each keypoint has format: [x, y, visibility_score]
                # where visibility_score indicates confidence in keypoint visibility

                # Primary filter: Select only keypoints with visibility > 0
                # This prioritizes keypoints that the model considers clearly visible
                visible_kps = [kp for kp in current_kps if kp[2] > 0]

                if visible_kps:
                    # If visible keypoints exist, include all of them
                    # Flatten the list: [x1, y1, v1, x2, y2, v2, ...]
                    keypoints_list = [coord for kp in visible_kps for coord in kp]
                else:
                    # Fallback: If no keypoints have visibility > 0, 
                    # select the keypoint with the highest visibility score
                    # This ensures at least one keypoint is shown even with low confidence
                    best_kp = max(current_kps, key=lambda kp: kp[2])
                    keypoints_list = list(best_kp)
                    # Set visibility score to 0 for fallback case
                    keypoints_list[2] = 0

            object_prediction = ObjectPrediction(
                bbox=boxes[i].tolist(),
                segmentation=(
                    get_coco_segmentation_from_bool_mask(masks[i])
                    if masks is not None
                    else None
                ),
                category_id=int(category_ids[i]),
                category_name=self.category_mapping[str(int(category_ids[i]))],
                score=float(scores[i]),
                shift_amount=shift_amount,
                full_shape=full_shape,
                keypoints=keypoints_list,
            )
            object_prediction_list.append(object_prediction)

        self._object_prediction_list_per_image = [object_prediction_list]
