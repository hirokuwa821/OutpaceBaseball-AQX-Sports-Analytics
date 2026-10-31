from functools import lru_cache
from pathlib import Path
import math

import cv2
import pandas as pd


ROOT_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT_DIR / "models" / "ball_detector.pt"
TRACKING_DIR = ROOT_DIR / "output" / "ball_tracking_v5"

CONF_THRESHOLD = 0.15
MAX_MOVE_PER_FRAME = 80.0
MAX_GAP = 3
MIN_REAL_POINTS = 5
MIN_TRACK_LENGTH = 8


@lru_cache(maxsize=1)
def _load_model(model_path: str):
    from ultralytics import YOLO

    return YOLO(model_path)


def _get_detections(model, frame):
    results = model.predict(frame, conf=CONF_THRESHOLD, verbose=False)
    if not results or results[0].boxes is None:
        return []

    detections = []
    for box in results[0].boxes:
        confidence = float(box.conf[0])
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        detections.append(
            {
                "cx": (x1 + x2) / 2.0,
                "cy": (y1 + y2) / 2.0,
                "confidence": confidence,
            }
        )
    return detections


def _distance(first, second):
    return math.hypot(second[0] - first[0], second[1] - first[1])


def build_track(detections_by_frame):
    """Connect nearby detections, allowing only brief gaps as in the reference tracker."""
    if not detections_by_frame:
        return []

    tracks = []
    last_frame = max(detections_by_frame)
    for start_frame in sorted(detections_by_frame):
        for start_detection in detections_by_frame[start_frame]:
            track = [
                {
                    "frame": start_frame,
                    "cx": start_detection["cx"],
                    "cy": start_detection["cy"],
                    "confidence": start_detection["confidence"],
                    "interpolated": 0,
                }
            ]
            current_x = start_detection["cx"]
            current_y = start_detection["cy"]
            gap = 0

            for next_frame in range(start_frame + 1, last_frame + 1):
                candidates = detections_by_frame.get(next_frame, [])
                closest = None
                closest_distance = float("inf")
                for candidate in candidates:
                    distance = _distance(
                        (current_x, current_y), (candidate["cx"], candidate["cy"])
                    )
                    if distance <= MAX_MOVE_PER_FRAME and distance < closest_distance:
                        closest = candidate
                        closest_distance = distance

                if closest is None:
                    gap += 1
                    if gap > MAX_GAP:
                        break
                    continue

                track.append(
                    {
                        "frame": next_frame,
                        "cx": closest["cx"],
                        "cy": closest["cy"],
                        "confidence": closest["confidence"],
                        "interpolated": 0,
                    }
                )
                current_x = closest["cx"]
                current_y = closest["cy"]
                gap = 0

            if len(track) >= MIN_TRACK_LENGTH and len(track) >= MIN_REAL_POINTS:
                tracks.append(track)

    if not tracks:
        return []

    return max(
        tracks,
        key=lambda track: (
            len(track),
            sum(point["confidence"] for point in track) / len(track),
        ),
    )


def interpolate_track(track):
    if not track:
        return []

    result = []
    for current, following in zip(track, track[1:]):
        result.append(current)
        frame_gap = following["frame"] - current["frame"]
        if 1 < frame_gap <= MAX_GAP + 1:
            for offset in range(1, frame_gap):
                ratio = offset / frame_gap
                result.append(
                    {
                        "frame": current["frame"] + offset,
                        "cx": current["cx"] + (following["cx"] - current["cx"]) * ratio,
                        "cy": current["cy"] + (following["cy"] - current["cy"]) * ratio,
                        "confidence": 0.0,
                        "interpolated": 1,
                    }
                )
    result.append(track[-1])
    return sorted(result, key=lambda point: point["frame"])


def track_video(video_path, model_path=MODEL_PATH, tracking_dir=TRACKING_DIR):
    video_path = Path(video_path)
    model_path = Path(model_path)
    if not video_path.is_file():
        raise FileNotFoundError(f"Video not found: {video_path}")
    if not model_path.is_file():
        raise FileNotFoundError(f"Ball detector model not found: {model_path}")

    model = _load_model(str(model_path.resolve()))
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        cap.release()
        raise ValueError(f"Could not open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    if not math.isfinite(fps) or fps <= 0:
        cap.release()
        raise ValueError(f"Video has an invalid frame rate: {video_path}")

    detections_by_frame = {}
    frame_index = 0
    try:
        while True:
            success, frame = cap.read()
            if not success:
                break
            detections = _get_detections(model, frame)
            if detections:
                detections_by_frame[frame_index] = detections
            frame_index += 1
    finally:
        cap.release()

    track = build_track(detections_by_frame)
    if not track:
        raise ValueError(
            "No reliable ball track was found (at least 8 connected detections are required)."
        )

    points = interpolate_track(track)
    tracking_dir = Path(tracking_dir)
    tracking_dir.mkdir(parents=True, exist_ok=True)
    ball_df = pd.DataFrame(
        [
            {
                **point,
                "time_sec": point["frame"] / fps,
            }
            for point in points
        ],
        columns=["frame", "time_sec", "cx", "cy", "confidence", "interpolated"],
    )
    ball_df.to_csv(tracking_dir / f"{video_path.stem}_tracking.csv", index=False)
    return ball_df
