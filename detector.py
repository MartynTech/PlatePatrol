from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import cv2
import numpy as np
from ultralytics import YOLO

from util import get_car, read_license_plate, write_csv

try:
    from sort.sort import Sort
except Exception as exc:  # pragma: no cover
    raise ImportError(
        "Could not import Sort tracker. Download the SORT repo and ensure 'sort/sort.py' exists."
    ) from exc


@dataclass
class PlateDetection:
    frame_number: int
    car_id: int
    plate_text: str
    text_score: float
    bbox_score: float


def detect_plates(
    video_path: str,
    vehicle_model_path: str = "yolov8n.pt",
    plate_model_path: str = "license_plate_detector.pt",
    output_csv_path: str | None = None,
) -> List[PlateDetection]:
    """Run plate detection pipeline and return best detection per tracked car."""
    video = Path(video_path)
    if not video.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")

    results: Dict[int, Dict[int, dict]] = {}
    mot_tracker = Sort()
    coco_model = YOLO(vehicle_model_path)
    license_plate_detector = YOLO(plate_model_path)

    cap = cv2.VideoCapture(str(video))
    if not cap.isOpened():
        raise RuntimeError(f"Unable to open video: {video_path}")

    vehicles = [2, 3, 5, 7]
    frame_nmr = -1
    ret = True

    while ret:
        frame_nmr += 1
        ret, frame = cap.read()
        if not ret:
            break

        results[frame_nmr] = {}

        detections = coco_model(frame, verbose=False)[0]
        detections_ = []
        for detection in detections.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = detection
            if int(class_id) in vehicles:
                detections_.append([x1, y1, x2, y2, score])

        track_ids = mot_tracker.update(np.asarray(detections_)) if detections_ else np.empty((0, 5))

        license_plates = license_plate_detector(frame, verbose=False)[0]
        for license_plate in license_plates.boxes.data.tolist():
            x1, y1, x2, y2, score, _ = license_plate

            xcar1, ycar1, xcar2, ycar2, car_id = get_car(license_plate, track_ids)
            if car_id == -1:
                continue

            license_plate_crop = frame[int(y1):int(y2), int(x1): int(x2), :]
            if license_plate_crop.size == 0:
                continue

            license_plate_crop_gray = cv2.cvtColor(license_plate_crop, cv2.COLOR_BGR2GRAY)
            _, license_plate_crop_thresh = cv2.threshold(
                license_plate_crop_gray, 64, 255, cv2.THRESH_BINARY_INV
            )

            license_plate_text, license_plate_text_score = read_license_plate(license_plate_crop_thresh)
            if license_plate_text is None:
                continue

            results[frame_nmr][int(car_id)] = {
                "car": {"bbox": [xcar1, ycar1, xcar2, ycar2]},
                "license_plate": {
                    "bbox": [x1, y1, x2, y2],
                    "text": license_plate_text,
                    "bbox_score": float(score),
                    "text_score": float(license_plate_text_score),
                },
            }

    cap.release()

    if output_csv_path:
        write_csv(results, output_csv_path)

    best_by_car: Dict[int, PlateDetection] = {}
    for frame_number, frame_result in results.items():
        for car_id, payload in frame_result.items():
            lp = payload["license_plate"]
            candidate = PlateDetection(
                frame_number=frame_number,
                car_id=car_id,
                plate_text=lp["text"],
                text_score=float(lp["text_score"]),
                bbox_score=float(lp["bbox_score"]),
            )
            previous = best_by_car.get(car_id)
            if previous is None or candidate.text_score > previous.text_score:
                best_by_car[car_id] = candidate

    return sorted(best_by_car.values(), key=lambda x: x.car_id)
