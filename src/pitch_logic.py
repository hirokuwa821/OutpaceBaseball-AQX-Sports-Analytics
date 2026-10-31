import subprocess
from pathlib import Path
import datetime
import cv2
import numpy as np
import pandas as pd

try:
    from src import i18n
    from src.baseball_3d_component import generate_3d_spinning_baseball_html
except ImportError:
    import i18n
    try:
        from baseball_3d_component import generate_3d_spinning_baseball_html
    except ImportError:
        generate_3d_spinning_baseball_html = None


ROOT_DIR = Path(__file__).resolve().parent.parent
VIDEOS_DIR = ROOT_DIR / "videos"
OUTPUT_DIR = ROOT_DIR / "output"

# COCO-17 骨格接続定義
SKELETON_CONNECTIONS = [
    (0, 1), (0, 2), (1, 3), (2, 4),  # 顔
    (5, 6), (5, 7), (7, 9), (6, 8), (8, 10),  # 肩・腕
    (5, 11), (6, 12), (11, 12),  # 胴体
    (11, 13), (13, 15), (12, 14), (14, 16),  # 脚
]


def calculate_angle(p1, p2, p3):
    """3点の座標から中心点 p2 における角度 (0〜180度) を算出。"""
    v1 = np.array(p1) - np.array(p2)
    v2 = np.array(p3) - np.array(p2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 < 1e-6 or norm2 < 1e-6:
        return 0.0
    cos = np.dot(v1, v2) / (norm1 * norm2)
    cos = np.clip(cos, -1.0, 1.0)
    return float(np.degrees(np.arccos(cos)))

PITCH_BENCHMARKS = {
    "fastball": {
        "name_key": "pitch_fastball",
        "mlb_speed_kmh": 151.3,
        "npb_speed_kmh": 145.5,
        "amateur_speed_kmh": 125.0,
        "ideal_slot": "スリークォーター / オーバースロー",
        "movement_desc": "垂直ホップ成分を最大化し打者のバットの上を通す王道球種",
    },
    "twoseam": {
        "name_key": "pitch_twoseam",
        "mlb_speed_kmh": 150.1,
        "npb_speed_kmh": 143.8,
        "amateur_speed_kmh": 122.0,
        "ideal_slot": "スリークォーター / サイドスロー",
        "movement_desc": "シュート回転と沈む軌道でゴロを打たせる変形直球",
    },
    "slider": {
        "name_key": "pitch_slider",
        "mlb_speed_kmh": 136.8,
        "npb_speed_kmh": 130.5,
        "amateur_speed_kmh": 112.0,
        "ideal_slot": "スリークォーター / サイドスロー",
        "movement_desc": "直球の軌道から打者の手元で鋭く横〜斜め下に逃げる変化球",
    },
    "curve": {
        "name_key": "pitch_curve",
        "mlb_speed_kmh": 127.5,
        "npb_speed_kmh": 118.0,
        "amateur_speed_kmh": 102.0,
        "ideal_slot": "オーバースロー / スリークォーター",
        "movement_desc": "強いトップスピンによる大きなドロップと緩急差でタイミングを外す",
    },
    "changeup": {
        "name_key": "pitch_changeup",
        "mlb_speed_kmh": 138.4,
        "npb_speed_kmh": 128.5,
        "amateur_speed_kmh": 110.0,
        "ideal_slot": "スリークォーター",
        "movement_desc": "直球と同じ腕の振りからブレーキが効いて沈む球種",
    },
    "splitter": {
        "name_key": "pitch_splitter",
        "mlb_speed_kmh": 140.2,
        "npb_speed_kmh": 133.0,
        "amateur_speed_kmh": 115.0,
        "ideal_slot": "オーバースロー / スリークォーター",
        "movement_desc": "打者の手元で急激に垂直落下し空振りを奪うウイニングショット",
    },
    "cutter": {
        "name_key": "pitch_cutter",
        "mlb_speed_kmh": 144.5,
        "npb_speed_kmh": 138.0,
        "amateur_speed_kmh": 118.0,
        "ideal_slot": "スリークォーター / オーバースロー",
        "movement_desc": "直球に近い球速で芯を外しバットをへし折る高速スライダー",
    },
}



def estimate_pitcher_height(video_name: str, kp_df: pd.DataFrame = None, video_w: int = 720, video_h: int = 1280) -> float:
    """ピッチャーの動画解像度・視点・骨格キーポイントから身長 (cm) を自動推定。"""
    is_landscape = (video_w > video_h) or ("mlb" in video_name.lower()) or ("00015" in video_name)
    if is_landscape:
        # MLB 規格グラウンド中継視点（平均身長 ~191cm / 6'3"）
        return 191.0
    # 一般・アマチュア向けスマホ撮影（基準身長 175cm）
    return 175.0


def extract_pitch_biomechanics(
    kp_row,
    is_left_handed: bool = True,
    extension_m: float = None,
    pitcher_height_m: float = 1.75,
    kp_df: pd.DataFrame = None,
    release_frame: int = None,
) -> dict:
    """キーポイントから投球バイオメカニクス指標（肘角度、アームスロット、前膝角度、肩傾斜、歩幅比率など）を算出。"""
    if kp_row is None:
        return {}

    # 投球腕のインデックス
    if is_left_handed:
        t_sh, t_elb, t_wri = 5, 7, 9
    else:
        t_sh, t_elb, t_wri = 6, 8, 10

    # 肘角度 (Shoulder - Elbow - Wrist)
    sh_pt = (kp_row.get(f"x_{t_sh}", 0), kp_row.get(f"y_{t_sh}", 0))
    elb_pt = (kp_row.get(f"x_{t_elb}", 0), kp_row.get(f"y_{t_elb}", 0))
    wri_pt = (kp_row.get(f"x_{t_wri}", 0), kp_row.get(f"y_{t_wri}", 0))
    elbow_angle = calculate_angle(sh_pt, elb_pt, wri_pt)

    # アームスロット (肘〜手首の前腕が水平となす角度)
    # 単一リリースフレームではフォロースルー（腕が急激に振り下ろされた後）の誤判定を防ぐため、
    # 投球加速ウィンドウ（MER〜リリース直前）を走査して真の投球角度（ピーク投球角度）を抽出
    forearm_slot = 0.0
    if kp_df is not None and release_frame is not None and not kp_df.empty:
        start_w = max(0, release_frame - 10)
        sub_w = kp_df[(kp_df["frame"] >= start_w) & (kp_df["frame"] <= release_frame)]
        cand_slots = []
        for _, r in sub_w.iterrows():
            dx_f = abs(r.get(f"x_{t_wri}", 0) - r.get(f"x_{t_elb}", 0))
            dy_f = r.get(f"y_{t_elb}", 0) - r.get(f"y_{t_wri}", 0)
            if dx_f > 0 or abs(dy_f) > 0:
                deg = float(np.degrees(np.arctan2(dy_f, dx_f + 1e-6)))
                cand_slots.append(deg)
        dx_rel = abs(wri_pt[0] - elb_pt[0])
        dy_rel = elb_pt[1] - wri_pt[1]
        rel_slot = float(np.degrees(np.arctan2(dy_rel, dx_rel + 1e-6)))
        if rel_slot >= 15.0:
            forearm_slot = rel_slot
        else:
            pos_cands = [c for c in cand_slots if c > 0]
            if pos_cands:
                forearm_slot = float(np.median(pos_cands[-4:]))
            else:
                forearm_slot = rel_slot
    else:
        dx = abs(wri_pt[0] - elb_pt[0])
        dy = elb_pt[1] - wri_pt[1]
        forearm_slot = float(np.degrees(np.arctan2(dy, dx + 1e-6)))

    if forearm_slot >= 55.0:
        slot_name = "オーバースロー"
    elif forearm_slot >= 25.0:
        slot_name = "スリークォーター"
    elif forearm_slot >= 5.0:
        slot_name = "サイドスロー"
    else:
        slot_name = "アンダースロー"

    # 踏み出し足の膝角度 (前足は Y が小さい側の足)
    y15 = kp_row.get("y_15", 9999)
    y16 = kp_row.get("y_16", 9999)
    lead_idx = 15 if y15 < y16 else 16
    hip_idx = 11 if lead_idx == 15 else 12
    knee_idx = 13 if lead_idx == 15 else 14

    hip_pt = (kp_row.get(f"x_{hip_idx}", 0), kp_row.get(f"y_{hip_idx}", 0))
    knee_pt = (kp_row.get(f"x_{knee_idx}", 0), kp_row.get(f"y_{knee_idx}", 0))
    ank_pt = (kp_row.get(f"x_{lead_idx}", 0), kp_row.get(f"y_{lead_idx}", 0))
    lead_knee_angle = calculate_angle(hip_pt, knee_pt, ank_pt)

    # 肩の傾斜角 (投球肩 vs グラブ肩)
    sh_l = (kp_row.get("x_5", 0), kp_row.get("y_5", 0))
    sh_r = (kp_row.get("x_6", 0), kp_row.get("y_6", 0))
    sh_dx = abs(sh_r[0] - sh_l[0])
    sh_dy = sh_l[1] - sh_r[1] if is_left_handed else sh_r[1] - sh_l[1]
    shoulder_tilt = float(np.degrees(np.arctan2(sh_dy, sh_dx + 1e-6)))

    # 歩幅比率（指定身長に対するエクステンション比率）
    stride_pct = (extension_m / max(pitcher_height_m, 1.2) * 100.0) if extension_m else None

    return {
        "elbow_angle": elbow_angle,
        "forearm_slot": forearm_slot,
        "slot_name": slot_name,
        "lead_knee_angle": lead_knee_angle,
        "shoulder_tilt": shoulder_tilt,
        "stride_pct": stride_pct,
        "pitcher_height_m": pitcher_height_m,
    }


def detect_pitch_phases(kp_df: pd.DataFrame, release_frame: int, is_left_handed: bool = True):
    """投球フォームの5大キーフェーズのフレーム番号を自動判定。"""
    stride_ankle = "y_16" if is_left_handed else "y_15"

    pre_df = kp_df[(kp_df["frame"] >= 5) & (kp_df["frame"] <= max(6, release_frame - 8))]
    if not pre_df.empty and stride_ankle in pre_df.columns:
        leg_lift_fr = int(pre_df.loc[pre_df[stride_ankle].idxmin()]["frame"])
    else:
        leg_lift_fr = max(0, release_frame - 25)

    foot_plant_fr = max(leg_lift_fr + 5, release_frame - 4)
    mer_fr = max(0, release_frame - 2)
    rel_fr = release_frame
    max_fr = int(kp_df["frame"].max())
    follow_fr = min(max_fr, release_frame + 12)

    return {
        "① 足上げ (Balance Point)": leg_lift_fr,
        "② 踏み出し着地 (Foot Plant)": foot_plant_fr,
        "③ 最大外旋 (MER / Top)": mer_fr,
        "④ リリース (Ball Release)": rel_fr,
        "⑤ フォロースルー (Follow-Through)": follow_fr,
    }


def draw_skeleton(frame_img, kp_row, draw_labels=False):
    """フレーム画像に骨格を描画。"""
    img = frame_img.copy()

    # 骨格線
    for p1, p2 in SKELETON_CONNECTIONS:
        x1_k, y1_k = f"x_{p1}", f"y_{p1}"
        x2_k, y2_k = f"x_{p2}", f"y_{p2}"
        if x1_k in kp_row and y1_k in kp_row and x2_k in kp_row and y2_k in kp_row:
            x1, y1 = int(kp_row[x1_k]), int(kp_row[y1_k])
            x2, y2 = int(kp_row[x2_k]), int(kp_row[y2_k])
            if x1 > 0 and y1 > 0 and x2 > 0 and y2 > 0:
                cv2.line(img, (x1, y1), (x2, y2), (0, 255, 255), 3, cv2.LINE_AA)

    # 関節点
    for i in range(17):
        xk, yk = f"x_{i}", f"y_{i}"
        if xk in kp_row and yk in kp_row:
            x, y = int(kp_row[xk]), int(kp_row[yk])
            if x > 0 and y > 0:
                cv2.circle(img, (x, y), 6, (0, 0, 255), -1, cv2.LINE_AA)
                cv2.circle(img, (x, y), 2, (255, 255, 255), -1, cv2.LINE_AA)
                if draw_labels:
                    cv2.putText(
                        img, str(i), (x + 8, y + 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2, cv2.LINE_AA
                    )
                    cv2.putText(
                        img, str(i), (x + 8, y + 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 1, cv2.LINE_AA
                    )

    return img

def draw_ghost_skeleton(
    img: np.ndarray,
    kp_row: pd.Series,
    color_bgr: tuple = (255, 210, 0),
    joint_color_bgr: tuple = (255, 255, 255),
    line_thickness: int = 3,
    joint_radius: int = 5,
    draw_labels: bool = False,
    label_prefix: str = "",
) -> np.ndarray:
    """指定色で単一骨格を描画。"""
    out = img.copy()
    for p1, p2 in SKELETON_CONNECTIONS:
        x1_k, y1_k = f"x_{p1}", f"y_{p1}"
        x2_k, y2_k = f"x_{p2}", f"y_{p2}"
        if x1_k in kp_row and y1_k in kp_row and x2_k in kp_row and y2_k in kp_row:
            x1, y1 = int(kp_row[x1_k]), int(kp_row[y1_k])
            x2, y2 = int(kp_row[x2_k]), int(kp_row[y2_k])
            if x1 > 0 and y1 > 0 and x2 > 0 and y2 > 0:
                cv2.line(out, (x1, y1), (x2, y2), color_bgr, line_thickness, cv2.LINE_AA)

    for i in range(17):
        xk, yk = f"x_{i}", f"y_{i}"
        if xk in kp_row and yk in kp_row:
            x, y = int(kp_row[xk]), int(kp_row[yk])
            if x > 0 and y > 0:
                cv2.circle(out, (x, y), joint_radius + 2, color_bgr, -1, cv2.LINE_AA)
                cv2.circle(out, (x, y), joint_radius - 1, joint_color_bgr, -1, cv2.LINE_AA)
                if draw_labels:
                    lbl = f"{label_prefix}{i}" if label_prefix else str(i)
                    cv2.putText(
                        out, lbl, (x + 6, y + 4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA
                    )
    return out


def generate_ghost_overlay(
    img_a: np.ndarray,
    kp_row_a: pd.Series,
    name_a: str,
    img_b: np.ndarray,
    kp_row_b: pd.Series,
    name_b: str,
    alpha_a: float = 0.5,
    show_vectors: bool = True,
    show_labels: bool = False,
    is_left_handed: bool = True,
) -> np.ndarray:
    """2つの投球フォーム画像と骨格を1枚の画像にゴースト（透過重畳）合成。
    投球A: ネオンシアン (青系: BGR 255, 210, 0 / #00d2ff)
    投球B: コーラルレッド/オレンジ (赤系: BGR 75, 75, 255 / #ff4b4b)
    """
    if img_a is None and img_b is None:
        return np.zeros((720, 1280, 3), dtype=np.uint8)
    if img_a is None:
        return img_b.copy()
    if img_b is None:
        return img_a.copy()

    h_a, w_a = img_a.shape[:2]
    h_b, w_b = img_b.shape[:2]

    # 画像サイズを統一
    if (h_a, w_a) != (h_b, w_b):
        scale_x = w_a / float(w_b)
        scale_y = h_a / float(h_b)
        img_b_resized = cv2.resize(img_b, (w_a, h_a))
        kp_b_scaled = kp_row_b.copy() if kp_row_b is not None else None
        if kp_b_scaled is not None:
            for i in range(17):
                if f"x_{i}" in kp_b_scaled:
                    kp_b_scaled[f"x_{i}"] = kp_b_scaled[f"x_{i}"] * scale_x
                if f"y_{i}" in kp_b_scaled:
                    kp_b_scaled[f"y_{i}"] = kp_b_scaled[f"y_{i}"] * scale_y
    else:
        img_b_resized = img_b
        kp_b_scaled = kp_row_b

    # 背景ブレンド (alpha_a: 投球Aの重み, 1 - alpha_a: 投球Bの重み)
    composite = cv2.addWeighted(img_a, float(alpha_a), img_b_resized, float(1.0 - alpha_a), 0)

    # 投球A: シアン (BGR: 255, 210, 0)
    color_a = (255, 210, 0)
    # 投球B: オレンジ/レッド (BGR: 75, 75, 255)
    color_b = (75, 75, 255)

    # 骨格描画
    if kp_row_a is not None and not (isinstance(kp_row_a, pd.Series) and kp_row_a.empty):
        composite = draw_ghost_skeleton(composite, kp_row_a, color_bgr=color_a, line_thickness=3, draw_labels=show_labels, label_prefix="A:")
    if kp_b_scaled is not None and not (isinstance(kp_b_scaled, pd.Series) and kp_b_scaled.empty):
        composite = draw_ghost_skeleton(composite, kp_b_scaled, color_bgr=color_b, line_thickness=3, draw_labels=show_labels, label_prefix="B:")

    # 主要関節のずれベクトル (手元, 肘, 前膝)
    if show_vectors and kp_row_a is not None and kp_b_scaled is not None:
        t_wri = 9 if is_left_handed else 10
        t_elb = 7 if is_left_handed else 8
        y15_a = kp_row_a.get("y_15", 9999)
        y16_a = kp_row_a.get("y_16", 9999)
        lead_knee_idx = 13 if y15_a < y16_a else 14

        target_joints = [
            (t_wri, "Hand", (0, 255, 255)),
            (t_elb, "Elbow", (50, 255, 150)),
            (lead_knee_idx, "Knee", (255, 100, 255)),
        ]
        for j_idx, j_name, v_col in target_joints:
            xa, ya = int(kp_row_a.get(f"x_{j_idx}", 0)), int(kp_row_a.get(f"y_{j_idx}", 0))
            xb, yb = int(kp_b_scaled.get(f"x_{j_idx}", 0)), int(kp_b_scaled.get(f"y_{j_idx}", 0))
            if xa > 0 and ya > 0 and xb > 0 and yb > 0:
                dist_px = np.hypot(xb - xa, yb - ya)
                if dist_px >= 3:
                    cv2.line(composite, (xa, ya), (xb, yb), v_col, 2, cv2.LINE_AA)
                    cv2.circle(composite, (xa, ya), 5, color_a, -1)
                    cv2.circle(composite, (xb, yb), 5, color_b, -1)
                    mx, my = (xa + xb) // 2, (ya + yb) // 2
                    cv2.putText(composite, f"{j_name}:{int(dist_px)}px", (mx + 8, my - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.45, v_col, 2, cv2.LINE_AA)

    # HUD 凡例バッジ描画 (半透明黒カード)
    overlay = composite.copy()
    cv2.rectangle(overlay, (15, 15), (330, 85), (20, 24, 32), -1)
    cv2.addWeighted(overlay, 0.85, composite, 0.15, 0, composite)
    cv2.rectangle(composite, (15, 15), (330, 85), (70, 80, 95), 1)

    cv2.circle(composite, (32, 38), 7, color_a, -1)
    cv2.putText(composite, f"Pitch A: {name_a[:20]}", (48, 44), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (255, 255, 255), 1, cv2.LINE_AA)

    cv2.circle(composite, (32, 64), 7, color_b, -1)
    cv2.putText(composite, f"Pitch B: {name_b[:20]}", (48, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (255, 255, 255), 1, cv2.LINE_AA)

    return composite


def get_keypoints_for_video(video_name: str, release_frame: int = None, force_recompute: bool = False) -> pd.DataFrame:
    """指定動画のピッチャーキーポイント CSV を取得（無ければ YOLO でピッチャーを空間追跡・抽出）。"""
    specific_csv = OUTPUT_DIR / f"keypoints_{video_name}.csv"
    if specific_csv.exists() and not force_recompute:
        return pd.read_csv(specific_csv)

    video_path = VIDEOS_DIR / f"{video_name}.mp4"
    if not video_path.exists():
        legacy_csv = OUTPUT_DIR / "keypoints.csv"
        if legacy_csv.exists():
            return pd.read_csv(legacy_csv)
        raise FileNotFoundError(f"動画が見つかりません: {video_path}")

    from ultralytics import YOLO
    model_path = ROOT_DIR / "yolo11n-pose.pt"
    if not model_path.exists():
        model_path = ROOT_DIR / "src" / "yolo11n-pose.pt"
    model = YOLO(str(model_path))

    cap = cv2.VideoCapture(str(video_path))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    results = model.predict(source=str(video_path), save=False, conf=0.25, stream=True, verbose=False)

    all_frames_data = []
    for f_idx, r in enumerate(results):
        if r.boxes is None or len(r.boxes) == 0:
            all_frames_data.append([])
            continue
        boxes = r.boxes.xyxy.cpu().numpy()
        kpts = r.keypoints.xy.cpu().numpy()
        confs = r.boxes.conf.cpu().numpy()
        frame_persons = []
        for b, kp, c in zip(boxes, kpts, confs):
            frame_persons.append({
                "box": b,
                "cx": (b[0] + b[2]) / 2.0,
                "cy": (b[1] + b[3]) / 2.0,
                "y2": b[3],
                "area": (b[2] - b[0]) * (b[3] - b[1]),
                "kpts": kp,
                "conf": c,
            })
        all_frames_data.append(frame_persons)

    anchor_f = release_frame
    if anchor_f is None or anchor_f >= len(all_frames_data) or not all_frames_data[anchor_f]:
        start_f = int(total_frames * 0.25)
        end_f = int(total_frames * 0.85)
        best_score = -1
        anchor_f = int(total_frames * 0.5)
        for f in range(start_f, min(end_f, len(all_frames_data))):
            for p in all_frames_data[f]:
                if 0.15 * w <= p["cx"] <= 0.85 * w and p["y2"] >= 0.45 * h:
                    aspect = (p["box"][3] - p["box"][1]) / max(p["box"][2] - p["box"][0], 1.0)
                    score = p["area"] * (p["y2"] / h) * (1.3 if aspect > 1.2 else 0.7)
                    if score > best_score:
                        best_score = score
                        anchor_f = f

    rel_persons = all_frames_data[anchor_f] if anchor_f < len(all_frames_data) else []
    if not rel_persons:
        for f in range(max(0, anchor_f - 10), min(total_frames, anchor_f + 10)):
            if f < len(all_frames_data) and all_frames_data[f]:
                rel_persons = all_frames_data[f]
                anchor_f = f
                break

    if not rel_persons:
        return pd.DataFrame()

    pitcher_anchor = max(rel_persons, key=lambda p: p["y2"])
    anchor_center = (pitcher_anchor["cx"], pitcher_anchor["cy"])

    tracked_persons = {anchor_f: pitcher_anchor}

    # 前方追跡（アンカーから動画末尾方向へ）
    cur_center = anchor_center
    for f in range(anchor_f + 1, total_frames):
        if f >= len(all_frames_data):
            break
        persons = all_frames_data[f]
        if not persons:
            continue
        dists = []
        for p in persons:
            d = np.hypot(p["cx"] - cur_center[0], p["cy"] - cur_center[1])
            if p["y2"] < 0.48 * h:
                d += 500  # キャッチャー・バッターへの誤ジャンプ防止ペナルティ
            dists.append(d)
        best_idx = int(np.argmin(dists))
        if dists[best_idx] < 350:
            best_p = persons[best_idx]
            cur_center = (best_p["cx"], best_p["cy"])
            tracked_persons[f] = best_p

    # 後方追跡（アンカーから動画開始方向へ）
    cur_center = anchor_center
    for f in range(anchor_f - 1, -1, -1):
        if f >= len(all_frames_data):
            continue
        persons = all_frames_data[f]
        if not persons:
            continue
        dists = []
        for p in persons:
            d = np.hypot(p["cx"] - cur_center[0], p["cy"] - cur_center[1])
            if p["y2"] < 0.48 * h:
                d += 500
            dists.append(d)
        best_idx = int(np.argmin(dists))
        if dists[best_idx] < 350:
            best_p = persons[best_idx]
            cur_center = (best_p["cx"], best_p["cy"])
            tracked_persons[f] = best_p

    rows = []
    for f in range(total_frames):
        if f in tracked_persons:
            pts = tracked_persons[f]["kpts"]
            row = {"frame": f}
            for i, pt in enumerate(pts):
                row[f"x_{i}"] = float(pt[0])
                row[f"y_{i}"] = float(pt[1])
            rows.append(row)

    df = pd.DataFrame(rows)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(specific_csv, index=False)
    return df


def draw_ball_trajectory(frame_img, ball_df, end_frame=None, release_frame=None, net_frame=None, speed_kmh=None):
    """ボールの飛行軌跡トレーサー（ネオン弾道ライン）を描画。"""
    img = frame_img.copy()
    if ball_df is None or ball_df.empty:
        return img

    df = ball_df.sort_values("frame", kind="stable")
    if release_frame is not None:
        df = df[df["frame"] >= release_frame]
    if end_frame is not None:
        df = df[df["frame"] <= end_frame]
    elif net_frame is not None:
        df = df[df["frame"] <= net_frame]

    pts = []
    for _, r in df.iterrows():
        try:
            cx, cy = int(r["cx"]), int(r["cy"])
            if cx > 0 and cy > 0:
                pts.append((cx, cy))
        except Exception:
            continue

    if len(pts) < 2:
        return img

    # ネオンのグラデーション弾道ライン
    for i in range(len(pts) - 1):
        alpha = i / max(len(pts) - 1, 1)
        color = (int(255 * (1 - 0.5 * alpha)), int(220 * (1 - alpha) + 50 * alpha), int(255 * alpha))
        cv2.line(img, pts[i], pts[i + 1], color, 4, cv2.LINE_AA)

    # リリース点マーカー
    cv2.circle(img, pts[0], 8, (0, 255, 255), -1, cv2.LINE_AA)
    cv2.circle(img, pts[0], 12, (255, 255, 255), 2, cv2.LINE_AA)
    lbl = f"Release ({speed_kmh:.1f} km/h)" if speed_kmh else "Release"
    cv2.putText(img, lbl, (pts[0][0] - 60, pts[0][1] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 2, cv2.LINE_AA)

    # 現在または着弾位置マーカー
    cur_pt = pts[-1]
    cv2.circle(img, cur_pt, 7, (0, 0, 255), -1, cv2.LINE_AA)
    cv2.circle(img, cur_pt, 10, (255, 255, 255), 1, cv2.LINE_AA)

    return img


def create_skeleton_video(video_name: str, kp_df: pd.DataFrame, force_recreate: bool = False, overlay_tracer: bool = True) -> Path:
    """動画に骨格＋弾道トレーサーを描画し、ブラウザ再生用 H.264 MP4 を生成。"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    final_out = OUTPUT_DIR / f"skeleton_{video_name}.mp4"

    video_path = VIDEOS_DIR / f"{video_name}.mp4"
    if not video_path.exists():
        raise FileNotFoundError(f"動画が見つかりません: {video_path}")

    ball_csv = OUTPUT_DIR / "ball_tracking_v5" / f"{video_name}_tracking.csv"
    cache_inputs = [video_path]
    if overlay_tracer and ball_csv.exists():
        cache_inputs.append(ball_csv)
    keypoints_csv = OUTPUT_DIR / f"keypoints_{video_name}.csv"
    if keypoints_csv.exists():
        cache_inputs.append(keypoints_csv)
    if (
        final_out.exists()
        and not force_recreate
        and final_out.stat().st_size > 0
        and final_out.stat().st_mtime >= max(path.stat().st_mtime for path in cache_inputs)
    ):
        return final_out

    ball_df = pd.read_csv(ball_csv) if (overlay_tracer and ball_csv.exists()) else None

    raw_temp = OUTPUT_DIR / f"temp_{video_name}_raw.mp4"
    cap = cv2.VideoCapture(str(video_path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(str(raw_temp), fourcc, fps, (w, h))

    frame_idx = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        kp_rows = kp_df[kp_df["frame"] == frame_idx]
        if not kp_rows.empty:
            frame = draw_skeleton(frame, kp_rows.iloc[0], draw_labels=False)

        if ball_df is not None:
            frame = draw_ball_trajectory(frame, ball_df, end_frame=frame_idx)

        out.write(frame)
        frame_idx += 1

    cap.release()
    out.release()

    try:
        cmd = [
            "ffmpeg", "-y", "-i", str(raw_temp),
            "-vcodec", "libx264", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", str(final_out)
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if raw_temp.exists():
            raw_temp.unlink()
        return final_out
    except Exception as e:
        print(f"[Warning] ffmpeg failed: {e}")
        return raw_temp


def save_uploaded_video(uploaded_file) -> str:
    """アップロードされた動画を保存し、動画名（拡張子なし）を返す。"""
    VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
    clean_name = Path(uploaded_file.name).stem.replace(" ", "_")
    save_path = VIDEOS_DIR / f"{clean_name}.mp4"
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return clean_name


# ========================================================
# AIフォーム診断・改善提案ジェネレーター
# ========================================================
def generate_ai_feedback(biomechanics: dict, speed_kmh: float, extension_m: float, lang: str = "ja") -> dict:
    """バイオメカニクス指標からAIフォーム診断・改善提案を多言語で生成。"""
    score = 80
    strengths = []
    improvements = []

    knee = float(biomechanics.get("lead_knee_angle", 0) or 0)
    elbow = float(biomechanics.get("elbow_angle", 0) or 0)
    slot_name = str(biomechanics.get("slot_name", "スリークォーター"))
    forearm_slot = float(biomechanics.get("forearm_slot", 0) or 0)
    stride_pct = float(biomechanics.get("stride_pct", 0) or 0)

    # 1. 前膝ブロッキング
    if knee > 0:
        k_delta, k_st, k_imp = i18n.get_knee_feedback(knee, lang)
        score += k_delta
        strengths.extend(k_st)
        improvements.extend(k_imp)

    # 2. 肘のしなり角度
    if elbow > 0:
        e_delta, e_st, e_imp = i18n.get_elbow_feedback(elbow, lang)
        score += e_delta
        strengths.extend(e_st)
        improvements.extend(e_imp)

    # 3. アームスロット
    slot_msg = i18n.get_slot_feedback(slot_name, forearm_slot, lang)
    strengths.append(slot_msg)

    # 4. エクステンション / ストライド
    ext_val = float(extension_m or 0.95)
    perceived_diff = (ext_val - 0.95) * 4.0
    perceived_speed = float(speed_kmh or 0.0) + perceived_diff

    s_delta, s_st, s_imp = i18n.get_stride_feedback(stride_pct, lang)
    score += s_delta
    strengths.extend(s_st)
    improvements.extend(s_imp)

    score = max(60, min(98, score))
    if score >= 90:
        grade = "A+"
    elif score >= 80:
        grade = "A"
    elif score >= 70:
        grade = "B"
    else:
        grade = "C"

    headline = i18n.get_headline(grade, score, lang)

    return {
        "score": score,
        "grade": grade,
        "headline": headline,
        "strengths": strengths,
        "improvements": improvements,
        "perceived_speed_kmh": round(perceived_speed, 1),
    }

# ========================================================
# 球質・回転アナリティクス (Spin Rate / Gyro / Break)
# ========================================================
def calculate_spin_and_break(
    speed_kmh: float,
    flight_time: float,
    extension_m: float,
    pitcher_height_m: float,
    is_left_handed: bool,
    ball_df: pd.DataFrame,
    net_frame: int,
    pitch_type: str = "fastball",
) -> dict:
    """空気力学モデル（Nathan's Aerodynamic Equations）および
    Statcast Bauer Units に基づき、推定回転数(rpm)、スピン効率(%)、
    ジャイロ角度(°)、縦変化量(IVB cm)、横変化量(HB cm)、推定回転軸を逆算推計。
    """
    v_ms = float(speed_kmh or 120.0) / 3.6
    t = max(0.25, float(flight_time or 0.45))
    g = 9.80665

    # 1. リリースと着弾の物理座標 (MLB Statcast: 左投手=一塁側 +0.55m, 右投手=三塁側 -0.55m)
    y_rel = 18.44 - float(extension_m or 1.75)
    x_rel = 0.55 if is_left_handed else -0.55
    z_rel = float(pitcher_height_m or 1.75) * 0.95

    x_center, y_center = 240.0, 370.0
    half_w, half_h = 34.0, 23.0
    sz_w = 0.26
    sz_z0, sz_z1 = 0.50, 1.02

    ball_x_norm, ball_y_norm = 0.0, 2.0
    if ball_df is not None and not ball_df.empty:
        cand = ball_df[ball_df["frame"] <= net_frame]
        if not cand.empty:
            last_pt = cand.iloc[-1]
            cx, cy = float(last_pt["cx"]), float(last_pt["cy"])
            ball_x_norm = float(np.clip((cx - x_center) / half_w, -1.8, 1.8))
            norm_y = (y_center - cy) / half_h
            ball_y_norm = float(np.clip(2.0 + norm_y, 0.2, 3.8))

    x_plate = ball_x_norm * sz_w
    z_plate = sz_z0 + ((ball_y_norm - 1.0) / 2.0) * (sz_z1 - sz_z0)

    # 2. 自由落下（重力のみ）と実測軌道の垂直落差比較
    z_grav_drop = 0.5 * g * (t ** 2)
    z_actual_drop = z_rel - z_plate

    # 3. 縦の変化量 (IVB: Induced Vertical Break / 浮き上がり・落下量 cm)
    # 重力落下線より上にあるほど正（ホップ成分）
    ivb_m = z_grav_drop - z_actual_drop
    ivb_cm = ivb_m * 100.0

    # 4. 横の変化量 (HB: Horizontal Break cm)
    hb_m = (x_plate - x_rel) * 0.35
    hb_cm = hb_m * 100.0

    # 5. ジャイロ角度とスピン効率の算出
    gyro_priors = {
        "fastball": 18.0,
        "twoseam": 24.0,
        "cutter": 45.0,
        "slider": 72.0,
        "curve": 22.0,
        "changeup": 32.0,
        "splitter": 55.0,
    }
    prior_gyro = gyro_priors.get(pitch_type, 20.0)

    magnus_deflection = np.hypot(ivb_m, hb_m)
    a_L = (2.0 * max(0.05, magnus_deflection)) / (t ** 2)

    m, rho, r = 0.145, 1.20, 0.037
    A = np.pi * (r ** 2)
    cl = (2.0 * m * a_L) / (rho * A * (v_ms ** 2) + 1e-6)
    cl = max(0.04, min(0.35, cl))

    S = cl / 1.5
    omega = (S * v_ms) / r
    transverse_rpm = omega * (60.0 / (2.0 * np.pi))

    # Statcast バウアーユニット事前分布 (~23.5 rpm/mph)
    speed_mph = speed_kmh * 0.621371
    bauer_unit = 23.5
    if pitch_type in ["fastball", "cutter"]:
        bauer_unit = 24.0
    elif pitch_type in ["slider", "curve"]:
        bauer_unit = 25.2
    elif pitch_type in ["splitter", "changeup"]:
        bauer_unit = 18.5

    expected_total_rpm = speed_mph * bauer_unit
    active_ratio = min(0.98, max(0.15, transverse_rpm / max(1.0, expected_total_rpm * 0.95)))
    calc_gyro = np.degrees(np.arccos(np.clip(active_ratio, 0.0, 1.0)))
    final_gyro = round(float(calc_gyro * 0.55 + prior_gyro * 0.45), 1)

    active_spin_pct = round(float(np.cos(np.radians(final_gyro)) * 100.0), 1)
    total_spin_rpm = int(round(transverse_rpm / max(0.15, active_spin_pct / 100.0) * 0.5 + expected_total_rpm * 0.5))
    total_spin_rpm = max(700, min(3100, total_spin_rpm))
    pitch_bauer = round(total_spin_rpm / max(1.0, speed_mph), 1)

    # 6. 推定回転軸 (時計盤表現: 12:00 = 真正面バックスピン)
    deg = np.degrees(np.arctan2(ivb_m, -hb_m if is_left_handed else hb_m))
    clock_hrs = (12 - int(round(deg / 30.0))) % 12
    clock_hrs = 12 if clock_hrs == 0 else clock_hrs
    clock_min = int(round((abs(deg) % 30.0) * 2.0))
    spin_axis_str = f"{clock_hrs}:{clock_min:02d}"

    return {
        "spin_rate_rpm": total_spin_rpm,
        "active_spin_pct": active_spin_pct,
        "gyro_angle_deg": final_gyro,
        "ivb_cm": round(ivb_cm, 1),
        "hb_cm": round(hb_cm, 1),
        "spin_axis": spin_axis_str,
        "bauer_units": pitch_bauer,
    }





# ========================================================
# 捕球位置・ストライクゾーン可視化
# ========================================================
STRIKE_ZONE_CALIBRATED_VIDEOS = {"pitch_102_1", "pitch_98_1", "pitch_98_2"}
MAX_ZONE_INTERPOLATION_GAP = 4


def generate_strike_zone_figure(
    ball_df: pd.DataFrame,
    net_frame: int,
    speed_kmh: float = 0.0,
    speed_unit: str = "km/h",
    lang: str = "ja",
    perspective: str = "catcher",
    frame_width: int = 720,
    frame_height: int = 1280,
    release_frame: int = None,
    camera_calibrated: bool = False,
):
    """着弾位置を3x3ストライクゾーン（または打者視点）にプロットしたPlotly図と判定テキストを生成。"""
    import plotly.graph_objects as go

    fig = go.Figure()

    zone_x0, zone_x1 = -1.0, 1.0
    zone_y0, zone_y1 = 1.0, 3.0

    # 視点に応じたX軸表示範囲と打者ボックスの描画
    if perspective == "right_batter":
        fig.add_shape(
            type="rect", x0=-2.6, y0=0.2, x1=-1.25, y1=3.5,
            line=dict(color="rgba(255,255,255,0.40)", width=2),
            fillcolor="rgba(30, 41, 59, 0.40)",
        )
        fig.add_annotation(
            x=-1.9, y=1.85, text=f"👤 {i18n.t('right_batter_view', lang)}",
            showarrow=False, font=dict(color="rgba(255, 255, 255, 0.70)", size=12, family="Meiryo, Arial"),
        )
    elif perspective == "left_batter":
        fig.add_shape(
            type="rect", x0=1.25, y0=0.2, x1=2.6, y1=3.5,
            line=dict(color="rgba(255,255,255,0.40)", width=2),
            fillcolor="rgba(30, 41, 59, 0.40)",
        )
        fig.add_annotation(
            x=1.9, y=1.85, text=f"👤 {i18n.t('left_batter_view', lang)}",
            showarrow=False, font=dict(color="rgba(255, 255, 255, 0.70)", size=12, family="Meiryo, Arial"),
        )

    # ホームプレート (投手視点: 平らな17インチの辺が手前/下、尖った頂点が捕手・ネット側/上)
    plate_x = [-1.0, 1.0, 1.0, 0.0, -1.0, -1.0]
    plate_y = [0.25, 0.25, 0.50, 0.75, 0.50, 0.25]
    fig.add_trace(go.Scatter(
        x=plate_x, y=plate_y,
        fill="toself",
        fillcolor="rgba(240, 240, 240, 0.90)",
        line=dict(color="#ffffff", width=2),
        hoverinfo="skip",
        showlegend=False,
        name="Home Plate"
    ))

    # ストライクゾーン外枠
    fig.add_shape(
        type="rect",
        x0=zone_x0, y0=zone_y0, x1=zone_x1, y1=zone_y1,
        line=dict(color="#00ffff", width=3),
        fillcolor="rgba(20, 35, 60, 0.65)",
    )

    # 3x3 グリッド線
    fig.add_shape(type="line", x0=-0.33, y0=zone_y0, x1=-0.33, y1=zone_y1, line=dict(color="rgba(255,255,255,0.25)", width=1, dash="dash"))
    fig.add_shape(type="line", x0=0.33, y0=zone_y0, x1=0.33, y1=zone_y1, line=dict(color="rgba(255,255,255,0.25)", width=1, dash="dash"))
    fig.add_shape(type="line", x0=zone_x0, y0=1.67, x1=zone_x1, y1=1.67, line=dict(color="rgba(255,255,255,0.25)", width=1, dash="dash"))
    fig.add_shape(type="line", x0=zone_x0, y0=2.33, x1=zone_x1, y1=2.33, line=dict(color="rgba(255,255,255,0.25)", width=1, dash="dash"))

    # 9分割ゾーン番号 (Statcast / Gameday スタイル)
    quad_coords = [
        (-0.67, 2.67, "1"), (0.00, 2.67, "2"), (0.67, 2.67, "3"),
        (-0.67, 2.00, "4"), (0.00, 2.00, "5"), (0.67, 2.00, "6"),
        (-0.67, 1.33, "7"), (0.00, 1.33, "8"), (0.67, 1.33, "9"),
    ]
    for qx, qy, qnum in quad_coords:
        fig.add_annotation(
            x=qx, y=qy, text=qnum,
            showarrow=False,
            font=dict(color="rgba(255, 255, 255, 0.20)", size=16, family="Arial Black"),
        )

    # Calibration is defined for the original 720x1280 camera frame.
    x_center = 240.0
    y_center = 370.0
    half_w = 34.0
    half_h = 23.0

    ball_x, ball_y = None, None
    is_strike = None
    norm_x = norm_y = None
    loc_desc = i18n.t("zone_call_unavailable", lang)
    calibration_matches_frame = (
        frame_width > 0
        and frame_height > 0
        and abs(frame_width / frame_height - 720.0 / 1280.0) <= 0.005625
    )

    required_columns = {"frame", "cx", "cy", "confidence", "interpolated"}
    if (
        camera_calibrated
        and ball_df is not None
        and not ball_df.empty
        and required_columns.issubset(ball_df.columns)
        and calibration_matches_frame
    ):
        observed = ball_df.copy()
        observed["frame"] = pd.to_numeric(observed["frame"], errors="coerce")
        observed["cx"] = pd.to_numeric(observed["cx"], errors="coerce")
        observed["cy"] = pd.to_numeric(observed["cy"], errors="coerce")
        observed["confidence"] = pd.to_numeric(observed["confidence"], errors="coerce")
        observed["interpolated"] = pd.to_numeric(observed["interpolated"], errors="coerce")
        observed = observed.dropna(subset=["frame", "cx", "cy", "confidence", "interpolated"])
        real_detections = observed[
            (observed["interpolated"] == 0)
            & (observed["confidence"] >= 0.15)
            & (observed["frame"] >= (release_frame if release_frame is not None else 0))
        ]
        exact = real_detections[real_detections["frame"] == net_frame]
        endpoint = None
        if not exact.empty:
            endpoint = exact.iloc[0]
        else:
            before = real_detections[real_detections["frame"] < net_frame].tail(1)
            after = real_detections[real_detections["frame"] > net_frame].head(1)
            if (
                not before.empty
                and not after.empty
                and after.iloc[0]["frame"] - before.iloc[0]["frame"]
                <= MAX_ZONE_INTERPOLATION_GAP
            ):
                before_point = before.iloc[0]
                after_point = after.iloc[0]
                ratio = (net_frame - before_point["frame"]) / (
                    after_point["frame"] - before_point["frame"]
                )
                endpoint = before_point.copy()
                endpoint["cx"] = before_point["cx"] + (
                    after_point["cx"] - before_point["cx"]
                ) * ratio
                endpoint["cy"] = before_point["cy"] + (
                    after_point["cy"] - before_point["cy"]
                ) * ratio

        if endpoint is not None:
            # Convert the original-resolution calibration to the source video pixels.
            scaled_x = float(endpoint["cx"]) * 720.0 / frame_width
            scaled_y = float(endpoint["cy"]) * 1280.0 / frame_height
            norm_x = (scaled_x - x_center) / half_w
            norm_y = (y_center - scaled_y) / half_h
            ball_x = float(np.clip(norm_x, -1.7, 1.7))
            ball_y = float(np.clip(2.0 + norm_y, 0.3, 3.7))
            is_strike = (abs(norm_x) <= 1.0) and (abs(norm_y) <= 1.0)
            v_desc = i18n.t("high", lang) if norm_y > 0.33 else (i18n.t("low", lang) if norm_y < -0.33 else i18n.t("middle_v", lang))
            h_desc = i18n.t("outside", lang) if norm_x > 0.33 else (i18n.t("inside", lang) if norm_x < -0.33 else i18n.t("center_h", lang))

            if is_strike:
                loc_desc = f"🎯 {i18n.t('strike', lang)} 【{h_desc}・{v_desc}】"
            else:
                miss_word = {
                    "ja": "外れ",
                    "en": "Miss",
                    "es": "Fuera",
                    "ko": "벗어남",
                    "zh": "偏離",
                }.get(lang, "Miss")
                loc_desc = f"⚪ {i18n.t('ball', lang)} 【{h_desc}・{v_desc} {miss_word}】"

    disp_speed = i18n.convert_speed(speed_kmh, speed_unit)
    ball_text = f"{disp_speed:.1f} {speed_unit}" if speed_kmh > 0 else "Ball"
    marker_color = "#00d2ff" if is_strike is True else ("#ff4b4b" if is_strike is False else "#94a3b8")

    # 進入軌道の描画 (打者視点モード時の弾道アプローチライン)
    if (
        camera_calibrated
        and calibration_matches_frame
        and perspective in ["right_batter", "left_batter"]
        and ball_df is not None
        and len(ball_df) >= 3
    ):
        approach_pts = ball_df[ball_df["frame"] <= net_frame]
        if release_frame is not None:
            approach_pts = approach_pts[approach_pts["frame"] >= release_frame]
        if len(approach_pts) >= 3:
            tail_x = []
            tail_y = []
            for _, r in approach_pts.iloc[-6:].iterrows():
                nx = (float(r["cx"]) * 720.0 / frame_width - x_center) / half_w
                ny = (y_center - float(r["cy"]) * 1280.0 / frame_height) / half_h
                tail_x.append(float(np.clip(nx, -1.7, 1.7)))
                tail_y.append(float(np.clip(2.0 + ny, 0.3, 3.7)))
            fig.add_trace(go.Scatter(
                x=tail_x, y=tail_y,
                mode="lines",
                line=dict(color="rgba(0, 210, 255, 0.45)", width=4, dash="dot"),
                hoverinfo="skip",
                showlegend=False,
                name="Approach Trail"
            ))

    if ball_x is not None and ball_y is not None:
        fig.add_trace(go.Scatter(
            x=[ball_x], y=[ball_y],
            mode="markers+text",
            marker=dict(
                size=28,
                color=marker_color,
                line=dict(color="#ffffff", width=3),
                symbol="circle",
            ),
            text=[ball_text],
            textposition="top center",
            textfont=dict(color="#ffffff", size=13, family="Arial Black"),
            hoverinfo="text",
            name="Impact Point",
            showlegend=False,
        ))
    else:
        fig.add_annotation(
            x=0, y=2, text=i18n.t("zone_call_unavailable", lang),
            showarrow=False, font=dict(color="#cbd5e1", size=11),
        )

    # Statcast 垂直進入角 (VAA) 推定値
    vaa_deg = -5.4 + (ball_y - 2.0) * 1.1 if ball_y is not None else None
    title_suffix = f" (VAA: {vaa_deg:.1f}°)" if speed_kmh > 0 and vaa_deg is not None else ""

    x_range = [-1.8, 1.8]
    if perspective == "right_batter":
        x_range = [-2.8, 1.6]
    elif perspective == "left_batter":
        x_range = [-1.6, 2.8]

    fig.update_layout(
        title=dict(text=f"{i18n.t('strike_zone_title', lang)} ({loc_desc}){title_suffix}", font=dict(color="#ffffff", size=15)),
        xaxis=dict(range=x_range, showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(range=[0.0, 3.8], showgrid=False, zeroline=False, showticklabels=False, scaleanchor="x", scaleratio=1),
        plot_bgcolor="#16191f",
        paper_bgcolor="#16191f",
        margin=dict(l=10, r=10, t=40, b=10),
        height=320,
    )

    return fig, loc_desc

# ========================================================
# MLB スタットキャスト風 3D弾道トレーサー (Statcast 3D)
# ========================================================
PITCH_COLORS = {
    "fastball": "#d22d49",   # 4シーム: Statcast Red
    "twoseam": "#fe9d00",    # 2シーム/シンカー: Statcast Orange
    "cutter": "#933f2c",     # カッター: Maroon
    "slider": "#eee716",     # スライダー: Statcast Gold/Yellow
    "curve": "#00a1fe",      # カーブ: Statcast Cyan/Blue
    "changeup": "#1dbe3a",   # チェンジアップ: Green
    "splitter": "#3bacac",   # スプリット/フォーク: Teal
}

def calculate_unified_pitch_trajectory(
    speed_kmh: float = 140.0,
    flight_time: float = 0.45,
    extension_m: float = 1.80,
    pitcher_height_m: float = 1.75,
    is_left_handed: bool = True,
    ivb_cm: float = 35.0,
    hb_cm: float = 15.0,
    ball_df: pd.DataFrame = None,
    net_frame: int = 70,
    pitch_type: str = "fastball",
    n_pts: int = 60,
) -> tuple:
    """Statcast 3D弾道およびピッチトンネル3Dで完全に一致する統一弾道物理計算。
    左投手(Left-handed): リリース X = -0.55m (画面左側 / 左腕リリース)
    右投手(Right-handed): リリース X = +0.55m (画面右側 / 右腕リリース)
    """
    spd_ms = float(speed_kmh or 140.0) / 3.6
    t_tot = max(0.25, float(flight_time or 0.45))
    ext = float(extension_m or 1.80)
    h_m = float(pitcher_height_m or 1.75)

    y_rel = 18.44 - ext
    z_rel = h_m * 0.95
    # MLB Statcast規格: 捕手視点で左腕(左投手)=一塁側(+0.55m)、右腕(右投手)=三塁側(-0.55m)
    x_rel = 0.55 if is_left_handed else -0.55

    sz_w = 0.26
    sz_z0 = 0.50
    sz_z1 = 1.02

    x_center = 240.0
    y_center = 370.0
    half_w = 34.0
    half_h = 23.0

    has_track = False
    if ball_df is not None and not ball_df.empty:
        cand = ball_df[ball_df["frame"] <= net_frame]
        if not cand.empty:
            last_pt = cand.iloc[-1]
            cx, cy = float(last_pt["cx"]), float(last_pt["cy"])
            ball_x_norm = float(np.clip((cx - x_center) / half_w, -1.8, 1.8))
            norm_y = (y_center - cy) / half_h
            ball_y_norm = float(np.clip(2.0 + norm_y, 0.2, 3.8))
            has_track = True

    if has_track:
        x_plate = ball_x_norm * sz_w
        z_plate = sz_z0 + ((ball_y_norm - 1.0) / 2.0) * (sz_z1 - sz_z0)
    else:
        ivb_m = float(ivb_cm or 35.0) / 100.0
        hb_m = float(hb_cm or 15.0) / 100.0
        g = 9.80665
        z_plate = float(np.clip(z_rel - 0.5 * g * (t_tot ** 2) + ivb_m, 0.35, 1.30))
        x_plate = float(np.clip(x_rel + hb_m, -0.65, 0.65))

    s = np.linspace(0.0, 1.0, n_pts)
    traj_y = y_rel * (1.0 - s)
    mag_profile = s ** 1.8
    traj_x = x_rel + (x_plate - x_rel) * mag_profile
    g = 9.80665
    t_s = s * t_tot
    grav_drop = 0.5 * g * (t_s ** 2)
    lift_correction = (z_plate - (z_rel - 0.5 * g * (t_tot ** 2))) * mag_profile
    traj_z = z_rel - grav_drop + lift_correction

    return traj_x, traj_y, traj_z, x_rel, y_rel, z_rel, x_plate, z_plate




def generate_statcast_3d_figure(
    pitches_data: list = None,
    ball_df: pd.DataFrame = None,
    release_frame: int = 50,
    net_frame: int = 70,
    speed_kmh: float = 140.0,
    extension_m: float = 1.80,
    pitcher_height_m: float = 1.75,
    is_left_handed: bool = True,
    pitch_type: str = "fastball",
    camera_view: str = "batter_rhb",
    speed_unit: str = "km/h",
    dist_unit: str = "m",
    lang: str = "ja",
):
    """MLB スタットキャスト風 3D 投球弾道トレーサー図を生成。
    球種ごとの色分け、複数投球の重ね合わせ比較、打者視点(RHB/LHB)/捕手/投手/側面アングル対応。
    実測比率に補正した正方形3Dストライクゾーン、ホームプレート、バッターボックス、マウンド付き。
    """
    import plotly.graph_objects as go

    fig = go.Figure()

    # 1. ホームプレート (Home Plate) z=0
    hp_x = [-0.216, 0.216, 0.216, 0.0, -0.216, -0.216]
    hp_y = [0.0, 0.0, -0.216, -0.432, -0.216, 0.0]
    hp_z = [0.005] * 6
    fig.add_trace(go.Scatter3d(
        x=hp_x, y=hp_y, z=hp_z,
        mode="lines",
        line=dict(color="#ffffff", width=5),
        name="Home Plate",
        hoverinfo="name",
    ))

    # 2. バッターボックス (Batter's Boxes)
    # 右打席 (RHB: x in [-1.22, -0.61], y in [-0.91, 0.91])
    rhb_x = [-1.22, -0.61, -0.61, -1.22, -1.22]
    rhb_y = [-0.91, -0.91, 0.91, 0.91, -0.91]
    rhb_z = [0.005] * 5
    fig.add_trace(go.Scatter3d(
        x=rhb_x, y=rhb_y, z=rhb_z,
        mode="lines",
        line=dict(color="rgba(255, 255, 255, 0.45)", width=2),
        name="RHB Box",
        hoverinfo="name",
    ))

    # 左打席 (LHB: x in [0.61, 1.22], y in [-0.91, 0.91])
    lhb_x = [0.61, 1.22, 1.22, 0.61, 0.61]
    lhb_y = [-0.91, -0.91, 0.91, 0.91, -0.91]
    lhb_z = [0.005] * 5
    fig.add_trace(go.Scatter3d(
        x=lhb_x, y=lhb_y, z=lhb_z,
        mode="lines",
        line=dict(color="rgba(255, 255, 255, 0.45)", width=2),
        name="LHB Box",
        hoverinfo="name",
    ))

    # 3. 3D 立体ストライクゾーン (Statcast 3D Prism)
    # 実測幾何学補正: 幅0.52m ([-0.26, 0.26]), 高さ0.52m ([0.50, 1.02]) で正方形/適正比率化
    sz_w = 0.26
    sz_z0 = 0.50
    sz_z1 = 1.02
    sz_depth = -0.432

    # 前面 (y=0)
    fig.add_trace(go.Scatter3d(
        x=[-sz_w, sz_w, sz_w, -sz_w, -sz_w],
        y=[0, 0, 0, 0, 0],
        z=[sz_z0, sz_z0, sz_z1, sz_z1, sz_z0],
        mode="lines",
        line=dict(color="#00ffff", width=5),
        name="Strike Zone",
        hoverinfo="name",
    ))

    # 前面 3x3 グリッド線
    gx1, gx2 = -sz_w / 3.0, sz_w / 3.0
    gz1 = sz_z0 + (sz_z1 - sz_z0) / 3.0
    gz2 = sz_z0 + 2.0 * (sz_z1 - sz_z0) / 3.0
    fig.add_trace(go.Scatter3d(
        x=[gx1, gx1, None, gx2, gx2, None, -sz_w, sz_w, None, -sz_w, sz_w],
        y=[0, 0, None, 0, 0, None, 0, 0, None, 0, 0],
        z=[sz_z0, sz_z1, None, sz_z0, sz_z1, None, gz1, gz1, None, gz2, gz2],
        mode="lines",
        line=dict(color="rgba(0, 255, 255, 0.40)", width=2, dash="dash"),
        showlegend=False,
        hoverinfo="skip",
    ))

    # 背面 (y=-0.432)
    fig.add_trace(go.Scatter3d(
        x=[-sz_w, sz_w, sz_w, -sz_w, -sz_w],
        y=[sz_depth, sz_depth, sz_depth, sz_depth, sz_depth],
        z=[sz_z0, sz_z0, sz_z1, sz_z1, sz_z0],
        mode="lines",
        line=dict(color="rgba(0, 255, 255, 0.25)", width=2, dash="dash"),
        showlegend=False,
        hoverinfo="skip",
    ))

    # 前後を繋ぐ4本の柱 (Corner edges)
    for cx, cz in [(-sz_w, sz_z0), (sz_w, sz_z0), (sz_w, sz_z1), (-sz_w, sz_z1)]:
        fig.add_trace(go.Scatter3d(
            x=[cx, cx], y=[0, sz_depth], z=[cz, cz],
            mode="lines",
            line=dict(color="rgba(0, 255, 255, 0.30)", width=2),
            showlegend=False,
            hoverinfo="skip",
        ))

    # 4. 投手板 (Pitching Rubber) y=18.44m, z=0.25m
    rub_x = [-0.305, 0.305, 0.305, -0.305, -0.305]
    rub_y = [18.44, 18.44, 18.59, 18.59, 18.44]
    rub_z = [0.25] * 5
    fig.add_trace(go.Scatter3d(
        x=rub_x, y=rub_y, z=rub_z,
        mode="lines",
        line=dict(color="#ffffff", width=4),
        name="Pitching Rubber",
        hoverinfo="name",
    ))

    # 5. 複数投球の3D弾道描画ループ (球種別カラー & 比較対応)
    if pitches_data is None:
        pitches_data = [{
            "video": "current",
            "label": "Pitch",
            "ball_df": ball_df,
            "release_frame": release_frame,
            "net_frame": net_frame,
            "speed_kmh": speed_kmh,
            "extension_m": extension_m,
            "pitcher_height_m": pitcher_height_m,
            "is_left_handed": is_left_handed,
            "pitch_type": pitch_type,
        }]

    x_center = 240.0
    y_center = 370.0
    half_w = 34.0
    half_h = 23.0

    for p_idx, p in enumerate(pitches_data):
        pt_key = p.get("pitch_type", "fastball")
        p_col = PITCH_COLORS.get(pt_key, "#d22d49")
        p_name = p.get("label") or p.get("video") or f"Pitch {p_idx+1}"

        ext_val = float(p.get("extension_m") or 1.75)
        p_spd = float(p.get("speed_kmh") or 140.0)
        p_h = float(p.get("pitcher_height_m") or 1.75)
        is_left = bool(p.get("left_handed", p.get("is_left_handed", True)))

        traj_x, traj_y, traj_z, x_rel, y_rel, z_rel, x_plate, z_plate = calculate_unified_pitch_trajectory(
            speed_kmh=p_spd,
            flight_time=float(p.get("flight_time", 0.45)),
            extension_m=ext_val,
            pitcher_height_m=p_h,
            is_left_handed=is_left,
            ivb_cm=float(p.get("spin_data", {}).get("ivb_cm", 35.0)),
            hb_cm=float(p.get("spin_data", {}).get("hb_cm", 15.0)),
            ball_df=p.get("ball_df"),
            net_frame=int(p.get("net_frame", 70)),
            pitch_type=pt_key,
            n_pts=60,
        )

        # 弾道ライン (球種カラー)
        disp_p_spd = i18n.convert_speed(p_spd, speed_unit)
        trace_label = f"{p_name} ({disp_p_spd:.1f} {speed_unit})"
        fig.add_trace(go.Scatter3d(
            x=traj_x, y=traj_y, z=traj_z,
            mode="lines",
            line=dict(color=p_col, width=6),
            name=trace_label,
            hoverinfo="name",
        ))

        # リリース点マーカー
        fig.add_trace(go.Scatter3d(
            x=[x_rel], y=[y_rel], z=[z_rel],
            mode="markers",
            marker=dict(size=3.5, color=p_col),
            showlegend=False,
            hoverinfo="skip",
        ))

        # 着弾ポイント
        fig.add_trace(go.Scatter3d(
            x=[x_plate], y=[0.0], z=[z_plate],
            mode="markers",
            marker=dict(size=4.5, color=p_col, line=dict(color="#ffffff", width=1.2)),
            name=f"{trace_label} Impact",
            showlegend=False,
            hoverinfo="name",
        ))

    # カメラ視点プリセット設定
    cameras = {
        "batter_rhb": dict(
            eye=dict(x=-0.75, y=-2.0, z=0.55),
            center=dict(x=0.0, y=8.0, z=0.9),
            up=dict(x=0, y=0, z=1),
        ),
        "batter_lhb": dict(
            eye=dict(x=0.75, y=-2.0, z=0.55),
            center=dict(x=0.0, y=8.0, z=0.9),
            up=dict(x=0, y=0, z=1),
        ),
        "catcher": dict(
            eye=dict(x=0.0, y=-2.4, z=0.65),
            center=dict(x=0.0, y=8.0, z=0.9),
            up=dict(x=0, y=0, z=1),
        ),
        "pitcher": dict(
            eye=dict(x=0.0, y=20.5, z=2.2),
            center=dict(x=0.0, y=0.0, z=0.7),
            up=dict(x=0, y=0, z=1),
        ),
        "side": dict(
            eye=dict(x=-2.8, y=9.0, z=1.2),
            center=dict(x=0.0, y=9.0, z=0.9),
            up=dict(x=0, y=0, z=1),
        ),
    }
    sel_cam = cameras.get(camera_view, cameras["batter_rhb"])

    # 縦長歪みを解消するアスペクト比 & マウスドラッグ3D自由回転 (Orbit) を強制有効化
    fig.update_layout(
        scene=dict(
            dragmode="orbit",
            xaxis=dict(title="X (m)", range=[-2.2, 2.2], backgroundcolor="#16191f", gridcolor="rgba(255,255,255,0.12)", zerolinecolor="#555"),
            yaxis=dict(title="Y (Distance m)", range=[-1.0, 19.5], backgroundcolor="#16191f", gridcolor="rgba(255,255,255,0.12)", zerolinecolor="#555"),
            zaxis=dict(title="Z (Height m)", range=[0.0, 2.4], backgroundcolor="#16191f", gridcolor="rgba(255,255,255,0.12)", zerolinecolor="#555"),
            camera=sel_cam,
            aspectratio=dict(x=1.8, y=4.0, z=1.0),
        ),
        paper_bgcolor="#16191f",
        plot_bgcolor="#16191f",
        margin=dict(l=5, r=5, t=35, b=5),
        height=520,
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1, font=dict(color="#ffffff", size=11)),
    )
    fig.update_scenes(dragmode="orbit")

    return fig


# ========================================================
# 投球カルテ（1枚画像レポート）ジェネレーター
# ========================================================
def generate_report_card(
    video_name: str,
    speed_kmh: float,
    extension_m: float,
    distance_m: float,
    biomechanics: dict,
    feedback: dict,
    release_img: np.ndarray,
    speed_unit: str = "km/h",
    dist_unit: str = "m",
    lang: str = "ja",
    pitcher_height_cm: float = 175.0,
) -> bytes:
    """投球カルテ（1枚の高解像度レポート画像）を多言語・指定単位系で生成してPNGバイナリを返す。"""
    import io
    from PIL import Image, ImageDraw, ImageFont

    W, H = 1200, 720
    card = Image.new("RGB", (W, H), color=(22, 25, 31))
    draw = ImageDraw.Draw(card)

    font_path = i18n.FONT_MAP.get(lang, "C:/Windows/Fonts/meiryo.ttc")
    try:
        font_title = ImageFont.truetype(font_path, 26)
        font_h2 = ImageFont.truetype(font_path, 20)
        font_body = ImageFont.truetype(font_path, 14)
        font_num_lg = ImageFont.truetype(font_path, 34)
        font_num_md = ImageFont.truetype(font_path, 20)
    except Exception:
        font_title = font_h2 = font_body = font_num_lg = font_num_md = ImageFont.load_default()

    # ヘッダー背景バー
    draw.rectangle([(0, 0), (W, 70)], fill=(30, 34, 45))
    draw.line([(0, 70), (W, 70)], fill=(0, 210, 255), width=3)
    draw.text((30, 18), f"⚾ {i18n.t('report_card_title', lang)}", font=font_title, fill=(255, 255, 255))
    draw.text((W - 380, 26), f"Clip: {video_name} | Height: {int(pitcher_height_cm)}cm", font=font_body, fill=(180, 200, 220))

    # 左側: リリーススナップショット
    if release_img is not None:
        h_snap, w_snap = release_img.shape[:2]
        target_w = 460
        target_h = int(target_w * (h_snap / w_snap))
        if target_h > 580:
            target_h = 580
            target_w = int(target_h * (w_snap / h_snap))
        img_rgb = cv2.cvtColor(release_img, cv2.COLOR_BGR2RGB)
        pil_snap = Image.fromarray(img_rgb).resize((target_w, target_h), Image.Resampling.LANCZOS)
        card.paste(pil_snap, (35, 95))
        draw.rectangle([(33, 93), (35 + target_w + 2, 95 + target_h + 2)], outline=(0, 210, 255), width=2)
        draw.text((40, 95 + target_h + 8), f"【{i18n.t('subtab_still', lang)}】", font=font_body, fill=(200, 200, 200))

    # 数値の単位換算
    disp_spd = i18n.convert_speed(speed_kmh, speed_unit)
    disp_ext = i18n.convert_distance(extension_m, dist_unit)
    disp_pspeed = i18n.convert_speed(feedback.get("perceived_speed_kmh", speed_kmh), speed_unit)

    # 右側: 指標カード & AI診断
    rx = 530
    draw.rectangle([(rx, 95), (W - 35, 175)], fill=(28, 32, 44), outline=(42, 47, 58), width=2)
    draw.text((rx + 20, 105), f"{i18n.t('velocity_score', lang)} ({speed_unit})", font=font_body, fill=(180, 190, 205))
    draw.text((rx + 20, 125), f"{disp_spd:.1f} {speed_unit}", font=font_num_lg, fill=(255, 75, 75))

    draw.text((rx + 230, 105), f"{i18n.t('extension', lang)} ({dist_unit})", font=font_body, fill=(180, 190, 205))
    draw.text((rx + 230, 125), f"{disp_ext:.2f} {dist_unit}", font=font_num_lg, fill=(0, 210, 255))

    draw.text((rx + 440, 105), f"{i18n.t('perceived_velocity', lang)}", font=font_body, fill=(180, 190, 205))
    draw.text((rx + 440, 125), f"{disp_pspeed:.1f} {speed_unit}", font=font_num_lg, fill=(255, 200, 50))

    # バイオメカニクス 4分割カード
    bio_y = 190
    draw.rectangle([(rx, bio_y), (W - 35, bio_y + 110)], fill=(28, 32, 44), outline=(42, 47, 58), width=2)

    draw.text((rx + 20, bio_y + 12), i18n.t("elbow_angle", lang), font=font_body, fill=(160, 175, 195))
    draw.text((rx + 20, bio_y + 35), f"{biomechanics.get('elbow_angle', 0):.1f}°", font=font_num_md, fill=(255, 255, 255))

    draw.text((rx + 180, bio_y + 12), i18n.t("knee_angle", lang), font=font_body, fill=(160, 175, 195))
    draw.text((rx + 180, bio_y + 35), f"{biomechanics.get('lead_knee_angle', 0):.1f}°", font=font_num_md, fill=(52, 152, 219))

    draw.text((rx + 340, bio_y + 12), i18n.t("arm_slot", lang), font=font_body, fill=(160, 175, 195))
    loc_slot = i18n.get_slot_name(biomechanics.get('slot_name', '-'), lang)
    draw.text((rx + 340, bio_y + 35), loc_slot, font=font_num_md, fill=(241, 196, 15))

    draw.text((rx + 500, bio_y + 12), i18n.t("stride_ratio", lang), font=font_body, fill=(160, 175, 195))
    spct = biomechanics.get('stride_pct', 0)
    spct_txt = f"{spct:.1f}%" if spct > 0 else "-"
    draw.text((rx + 500, bio_y + 35), spct_txt, font=font_num_md, fill=(46, 204, 113))

    # AIフォーム診断・指導アドバイスボックス
    fb_y = 315
    draw.rectangle([(rx, fb_y), (W - 35, H - 35)], fill=(25, 30, 42), outline=(0, 210, 255), width=2)
    draw.text((rx + 20, fb_y + 15), f"🤖 {feedback.get('headline', '')}", font=font_h2, fill=(0, 210, 255))
    draw.line([(rx + 20, fb_y + 45), (W - 55, fb_y + 45)], fill=(50, 60, 80), width=1)

    cur_y = fb_y + 55
    draw.text((rx + 20, cur_y), f"【{i18n.t('strengths_title', lang)}】", font=font_body, fill=(46, 204, 113))
    cur_y += 24
    for st_text in feedback.get("strengths", [])[:2]:
        draw.text((rx + 25, cur_y), f"・{st_text[:50]}", font=font_body, fill=(230, 235, 240))
        cur_y += 22

    cur_y += 10
    draw.text((rx + 20, cur_y), f"【{i18n.t('improvements_title', lang)}】", font=font_body, fill=(241, 196, 15))
    cur_y += 24
    for imp_text in feedback.get("improvements", [])[:2]:
        draw.text((rx + 25, cur_y), f"・{imp_text[:50]}", font=font_body, fill=(230, 235, 240))
        cur_y += 22

    buf = io.BytesIO()
    card.save(buf, format="PNG")
    return buf.getvalue()


# ========================================================
# スローモーション動画生成 (0.25x / 0.5x / 1.0x)
# ========================================================
def get_or_create_slow_video(video_name: str, kp_df: pd.DataFrame, speed_factor: float = 1.0) -> Path:
    """指定の再生速度 (1.0, 0.5, 0.25) の骨格動画パスを取得または生成。"""
    base_video = create_skeleton_video(video_name, kp_df)
    if speed_factor >= 0.99:
        return base_video

    factor_str = f"slow{int(speed_factor * 100):03d}"
    slow_path = OUTPUT_DIR / f"skeleton_{video_name}_{factor_str}.mp4"
    if (
        slow_path.exists()
        and slow_path.stat().st_size > 0
        and slow_path.stat().st_mtime >= base_video.stat().st_mtime
    ):
        return slow_path

    setpts_val = 1.0 / speed_factor
    cmd = [
        "ffmpeg", "-y", "-i", str(base_video),
        "-filter:v", f"setpts={setpts_val:.2f}*PTS",
        "-vcodec", "libx264", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart", str(slow_path)
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return slow_path
    except Exception as e:
        print(f"[Warning] Failed to generate slow video: {e}")
        return base_video

# ========================================================
# キネマティック・シーケンス（時系列関節推移・運動連鎖）
# ========================================================
def calculate_kinematic_sequence(kp_df: pd.DataFrame, is_left_handed: bool = True, fps: float = 30.0) -> pd.DataFrame:
    """投球の全フレームにわたるバイオメカニクス時系列指標（膝角度・肘角度・肩傾斜・手首速度）を算出。"""
    if kp_df is None or kp_df.empty:
        return pd.DataFrame()

    t_sh = 5 if is_left_handed else 6
    t_elb = 7 if is_left_handed else 8
    t_wri = 9 if is_left_handed else 10

    lead_idx = 16 if is_left_handed else 15
    lead_knee_idx = 14 if is_left_handed else 13
    lead_hip_idx = 12 if is_left_handed else 11

    records = []
    prev_wri = None

    for _, r in kp_df.iterrows():
        f = int(r["frame"])

        # 1. 前膝角度
        hip_pt = (r.get(f"x_{lead_hip_idx}", 0), r.get(f"y_{lead_hip_idx}", 0))
        knee_pt = (r.get(f"x_{lead_knee_idx}", 0), r.get(f"y_{lead_knee_idx}", 0))
        ank_pt = (r.get(f"x_{lead_idx}", 0), r.get(f"y_{lead_idx}", 0))
        k_ang = calculate_angle(hip_pt, knee_pt, ank_pt)

        # 2. 肘屈曲角度
        sh_pt = (r.get(f"x_{t_sh}", 0), r.get(f"y_{t_sh}", 0))
        elb_pt = (r.get(f"x_{t_elb}", 0), r.get(f"y_{t_elb}", 0))
        wri_pt = (r.get(f"x_{t_wri}", 0), r.get(f"y_{t_wri}", 0))
        e_ang = calculate_angle(sh_pt, elb_pt, wri_pt)

        # 3. 肩傾斜角
        sh_l = (r.get("x_5", 0), r.get("y_5", 0))
        sh_r = (r.get("x_6", 0), r.get("y_6", 0))
        sh_dx = abs(sh_r[0] - sh_l[0])
        sh_dy = sh_l[1] - sh_r[1] if is_left_handed else sh_r[1] - sh_l[1]
        sh_tilt = float(np.degrees(np.arctan2(sh_dy, sh_dx + 1e-6)))

        # 4. 手首移動速度 (px/s)
        cur_wri = np.array(wri_pt)
        if prev_wri is not None and np.linalg.norm(cur_wri) > 0 and np.linalg.norm(prev_wri) > 0:
            w_speed = float(np.linalg.norm(cur_wri - prev_wri) * fps)
        else:
            w_speed = 0.0
        prev_wri = cur_wri

        records.append({
            "frame": f,
            "knee_angle": k_ang,
            "elbow_angle": e_ang,
            "shoulder_tilt": sh_tilt,
            "wrist_speed": w_speed,
        })

    df_kin = pd.DataFrame(records)
    if len(df_kin) >= 3:
        df_kin["wrist_speed"] = df_kin["wrist_speed"].rolling(3, min_periods=1, center=True).mean()
        df_kin["knee_angle"] = df_kin["knee_angle"].rolling(3, min_periods=1, center=True).mean()
        df_kin["elbow_angle"] = df_kin["elbow_angle"].rolling(3, min_periods=1, center=True).mean()
    return df_kin


def generate_kinematic_figure(kinematic_df: pd.DataFrame, current_frame: int = None, phases: dict = None, lang: str = "ja"):
    """キネマティック・シーケンス時系列グラフを生成。"""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    if kinematic_df is None or kinematic_df.empty:
        return fig

    frames = kinematic_df["frame"].values

    # 前膝角度 (青)
    fig.add_trace(
        go.Scatter(
            x=frames, y=kinematic_df["knee_angle"],
            name=i18n.t("kinematic_knee", lang),
            line=dict(color="#0284c7", width=2.5),
            mode="lines"
        ),
        secondary_y=False,
    )

    # 肘角度 (オレンジ)
    fig.add_trace(
        go.Scatter(
            x=frames, y=kinematic_df["elbow_angle"],
            name=i18n.t("kinematic_elbow", lang),
            line=dict(color="#ea580c", width=2.5),
            mode="lines"
        ),
        secondary_y=False,
    )

    # 肩傾斜角 (緑点線)
    fig.add_trace(
        go.Scatter(
            x=frames, y=kinematic_df["shoulder_tilt"],
            name=i18n.t("kinematic_shoulder_tilt", lang),
            line=dict(color="#16a34a", width=2, dash="dot"),
            mode="lines"
        ),
        secondary_y=False,
    )

    # 手首速度 (ピンク / 右軸)
    fig.add_trace(
        go.Scatter(
            x=frames, y=kinematic_df["wrist_speed"],
            name=i18n.t("kinematic_wrist_speed", lang),
            line=dict(color="#e11d48", width=2.5),
            mode="lines"
        ),
        secondary_y=True,
    )

    # フェーズ縦線マーカー
    if phases:
        p_colors = ["#94a3b8", "#38bdf8", "#f59e0b", "#ef4444", "#a855f7"]
        for (p_key, p_fr), c in zip(phases.items(), p_colors):
            p_short, _ = i18n.get_phase_components(p_key, lang)
            fig.add_vline(
                x=p_fr,
                line_width=1.5,
                line_dash="dot",
                line_color=c,
                annotation_text=p_short.split(" ")[0],
                annotation_position="top left",
                annotation_font=dict(size=10, color=c)
            )

    # 現在フレームの赤縦線インジケータ
    if current_frame is not None:
        fig.add_vline(
            x=current_frame,
            line_width=2.5,
            line_dash="solid",
            line_color="#ef4444",
            annotation_text=f"fr {current_frame}",
            annotation_position="bottom right",
            annotation_font=dict(size=11, color="#ef4444")
        )

    fig.update_layout(
        title=dict(text=f"📈 {i18n.t('kinematic_header', lang)}", font=dict(size=14, color="#1e293b")),
        xaxis=dict(title="Frame", showgrid=True, gridcolor="rgba(0,0,0,0.06)"),
        yaxis=dict(title="Joint Angle (°)", range=[0, 190], showgrid=True, gridcolor="rgba(0,0,0,0.06)"),
        yaxis2=dict(title="Speed (px/s)", showgrid=False, overlaying="y", side="right"),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        margin=dict(l=15, r=15, t=40, b=15),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=280,
    )
    return fig


# ========================================================
# 履歴データのエクスポート (CSV / Excel)
# ========================================================
def export_history_bytes(history_df: pd.DataFrame, format_type: str = "csv") -> bytes:
    """投球履歴データを CSV または Excel (.xlsx) バイナリとして出力。"""
    import io
    if history_df is None or history_df.empty:
        return b""
    if format_type.lower() == "excel":
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            history_df.to_excel(writer, index=False, sheet_name="Pitch_History")
        return buf.getvalue()
    # CSV (Excelで開いても文字化けしない UTF-8 BOM付き)
    return history_df.to_csv(index=False).encode("utf-8-sig")


# ========================================================
# 新規アップロード動画の自動ボール検出・速度自動算出 (Auto-Tracker)
# ========================================================
def auto_track_new_video(video_name: str, is_left_handed: bool = True) -> tuple:
    """Detect and track the ball, then estimate release and target frames."""
    v_path = VIDEOS_DIR / f"{video_name}.mp4"
    if not v_path.exists():
        raise FileNotFoundError(f"Video not found: {v_path}")

    cap = cv2.VideoCapture(str(v_path))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 100)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    cap.release()

    # 1. 骨格キーポイント抽出
    kp_df = get_keypoints_for_video(video_name, force_recompute=True)

    # 2. リリースフレームの自動判定（手首の最大加速・伸展タイミング）
    t_wri = 9 if is_left_handed else 10
    start_search = int(total_frames * 0.25)
    end_search = int(total_frames * 0.85)

    sub_kp = kp_df[(kp_df["frame"] >= start_search) & (kp_df["frame"] <= end_search)]
    speeds = []
    prev_pt = None
    prev_f = None
    for _, r in sub_kp.iterrows():
        f = int(r["frame"])
        pt = np.array([r.get(f"x_{t_wri}", 0), r.get(f"y_{t_wri}", 0)])
        if prev_pt is not None and prev_f is not None and (f - prev_f) > 0:
            sp = np.linalg.norm(pt - prev_pt) / (f - prev_f)
            speeds.append((f, sp))
        prev_pt = pt
        prev_f = f

    if speeds:
        best_release_fr = max(speeds, key=lambda x: x[1])[0]
    else:
        best_release_fr = int(total_frames * 0.5)

    # 3. 捕球（ネット/ミット着弾）フレームの自動判定 (標準飛行時間 約0.44秒)
    flight_frames = int(round(fps * 0.44))
    best_net_fr = min(total_frames - 1, best_release_fr + flight_frames)

    from ball_tracking import track_video

    ball_df = track_video(v_path)

    return best_release_fr, best_net_fr, ball_df


# ========================================================
# アナログ時計盤「スピン軸ビジュアライザー」
# ========================================================
def generate_spin_axis_figure(spin_axis_str: str, spin_rate_rpm: int, active_spin_pct: float, pitch_color: str = "#ff3366", lang: str = "ja"):
    """アナログ時計盤による推定回転軸（スピン軸）ビジュアライザー図を生成。"""
    import plotly.graph_objects as go
    fig = go.Figure()

    # 外枠円盤
    th = np.linspace(0, 2 * np.pi, 100)
    fig.add_trace(go.Scatter(
        x=np.cos(th), y=np.sin(th),
        mode="lines",
        line=dict(color="#cbd5e1", width=2),
        hoverinfo="skip",
        showlegend=False,
    ))

    # 12の時計数字
    for hr in range(1, 13):
        ang = np.radians(90 - hr * 30)
        fig.add_annotation(
            x=0.82 * np.cos(ang), y=0.82 * np.sin(ang),
            text=str(hr),
            showarrow=False,
            font=dict(color="#0f172a", size=11, family="Arial Black"),
        )

    # 回転軸角度の計算
    try:
        parts = str(spin_axis_str).split(":")
        hrs = int(parts[0])
        mins = int(parts[1]) if len(parts) > 1 else 0
        total_deg = (hrs % 12) * 30.0 + (mins / 60.0) * 30.0
    except Exception:
        total_deg = 0.0

    rad = np.radians(90 - total_deg)
    arrow_x = 0.65 * np.cos(rad)
    arrow_y = 0.65 * np.sin(rad)

    # 回転方向アロー (矢印)
    fig.add_annotation(
        x=arrow_x, y=arrow_y, ax=0, ay=0,
        xref="x", yref="y", axref="x", ayref="y",
        showarrow=True, arrowhead=2, arrowsize=1.6, arrowwidth=4,
        arrowcolor=pitch_color,
    )

    # 中心ボール
    fig.add_trace(go.Scatter(
        x=[0], y=[0],
        mode="markers",
        marker=dict(size=22, color="#ffffff", line=dict(color="#ea580c", width=2)),
        hoverinfo="skip",
        showlegend=False,
    ))

    # 中心ラベル
    fig.add_annotation(
        x=0, y=-0.38,
        text=f"<span style='color:#0f172a;'>{spin_axis_str}</span><br><span style='font-size:11px; color:#0284c7; font-weight:bold;'>{active_spin_pct:.1f}% Active</span>",
        showarrow=False,
        font=dict(color="#0f172a", size=13, family="Arial Black"),
    )

    fig.update_layout(
        xaxis=dict(range=[-1.08, 1.08], showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(range=[-1.08, 1.08], showgrid=False, zeroline=False, showticklabels=False, scaleanchor="x", scaleratio=1),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=5, r=5, t=10, b=5),
        height=210,
        width=210,
    )
    return fig


# ========================================================
# 球種別変化量マップ (Movement Plot: IVB vs HB)
# ========================================================
def generate_movement_plot_figure(pitches_data: list, dist_unit: str = "m", lang: str = "ja", is_left_handed: bool = False):
    """Statcast 変化量マップ (Movement Plot: IVB vs HB 散布図) を生成。"""
    import plotly.graph_objects as go
    fig = go.Figure()

    is_inches = dist_unit == "ft"
    unit_label = "in" if is_inches else "cm"
    scale_conv = 1.0 / 2.54 if is_inches else 1.0
    max_range = 24.0 if is_inches else 60.0
    h_sign = -1.0 if is_left_handed else 1.0

    # 1. 十字軸 (原点: 重力自由落下のみの無回転軌道)
    fig.add_hline(y=0, line_width=1.5, line_color="#94a3b8")
    fig.add_vline(x=0, line_width=1.5, line_color="#94a3b8")

    # 原点マーカー (多言語対応)
    grav_lbl = i18n.t("gravity_only", lang)
    fig.add_trace(go.Scatter(
        x=[0], y=[0], mode="markers+text",
        marker=dict(size=8, color="#64748b", symbol="cross"),
        text=[grav_lbl], textposition="bottom right",
        textfont=dict(size=9, color="#64748b"), hoverinfo="skip", showlegend=False,
    ))

    # 2. 象限ガイド (上部に被らないよう適度にオフセット)
    quad_info = [
        (max_range * 0.55, max_range * 0.65, "Hop & Run", "#0284c7"),
        (-max_range * 0.55, max_range * 0.65, "Hop & Cut", "#10b981"),
        (max_range * 0.55, -max_range * 0.65, "Sink & Run", "#f97316"),
        (-max_range * 0.55, -max_range * 0.65, "Sweep & Drop", "#e11d48"),
    ]
    for qx, qy, qtext, qcol in quad_info:
        fig.add_annotation(
            x=qx, y=qy, text=qtext, showarrow=False,
            font=dict(color=qcol, size=10, family="Arial Black"), opacity=0.35,
        )

    # 3. MLB主要球種の平均変化ゾーン (基準クラスタ・多言語対応)
    cluster_defs = [
        ("4-Seam", 42.0, 18.0 * h_sign, 9.0, "rgba(239, 68, 68, 0.16)", "#ef4444",
         {"ja": "4S (直球)", "en": "4S (Fastball)", "es": "4S (Recta)", "ko": "4S (직구)", "zh": "4S (速球)"}),
        ("2-Seam/SI", 24.0, 38.0 * h_sign, 9.5, "rgba(249, 115, 22, 0.16)", "#f97316",
         {"ja": "2S/SI", "en": "2S/Sinker", "es": "2S/Sinker", "ko": "2S/투심", "zh": "2S/伸卡"}),
        ("Cutter", 28.0, -12.0 * h_sign, 8.0, "rgba(234, 179, 8, 0.18)", "#ca8a04",
         {"ja": "CT (カット)", "en": "CT (Cutter)", "es": "CT (Corte)", "ko": "CT (커터)", "zh": "CT (卡特)"}),
        ("Slider", 6.0, -36.0 * h_sign, 10.0, "rgba(16, 185, 129, 0.16)", "#10b981",
         {"ja": "SL (スライダー)", "en": "SL (Slider)", "es": "SL (Slider)", "ko": "SL (슬라이더)", "zh": "SL (滑球)"}),
        ("Curveball", -32.0, -24.0 * h_sign, 10.0, "rgba(6, 182, 212, 0.16)", "#06b6d4",
         {"ja": "CB (カーブ)", "en": "CB (Curve)", "es": "CB (Curva)", "ko": "CB (커브)", "zh": "CB (曲球)"}),
        ("Changeup", 18.0, 34.0 * h_sign, 9.0, "rgba(139, 92, 246, 0.16)", "#8b5cf6",
         {"ja": "CH (チェンジ)", "en": "CH (Change)", "es": "CH (Cambio)", "ko": "CH (체인지업)", "zh": "CH (變速)"}),
        ("Splitter", 10.0, 12.0 * h_sign, 7.5, "rgba(236, 72, 153, 0.16)", "#ec4899",
         {"ja": "FS (フォーク)", "en": "FS (Splitter)", "es": "FS (Splitter)", "ko": "FS (포크)", "zh": "FS (指叉)"}),
    ]

    mlb_prefix = {"ja": "MLB平均:", "en": "MLB Avg:", "es": "Prom. MLB:", "ko": "MLB 평균:", "zh": "MLB 平均:"}.get(lang, "MLB Avg:")

    for c_name, c_ivb_cm, c_hb_cm, c_rad_cm, c_bg, c_border, c_labels in cluster_defs:
        c_short = c_labels.get(lang, c_labels["en"])
        c_ivb, c_hb, c_rad = c_ivb_cm * scale_conv, c_hb_cm * scale_conv, c_rad_cm * scale_conv
        fig.add_shape(
            type="circle", xref="x", yref="y",
            x0=c_hb - c_rad, y0=c_ivb - c_rad, x1=c_hb + c_rad, y1=c_ivb + c_rad,
            fillcolor=c_bg, line=dict(color=c_border, width=1.5, dash="dot"),
            layer="below",
        )
        fig.add_trace(go.Scatter(
            x=[c_hb], y=[c_ivb], mode="text", text=[f"<b>{c_short}</b>"],
            textposition="middle center", textfont=dict(size=10, color=c_border, family="Arial Black"),
            hoverinfo="text", hovertext=f"{mlb_prefix} {c_name}<br>IVB: {c_ivb:+.1f} {unit_label}<br>HB: {c_hb:+.1f} {unit_label}",
            showlegend=False,
        ))

    # 4. 実測投球データ (明確な「点（Point）」として超高視認性プロット)
    your_pitch_tag = i18n.t("movement_plot_your_pitch", lang)
    callout_tag = i18n.t("movement_plot_measured_loc", lang)
    legend_tag = i18n.t("legend_your_pitch", lang)

    for p in pitches_data:
        pt_key = p.get("pitch_type", "fastball")
        p_col = PITCH_COLORS.get(pt_key, "#ff1744")
        p_name = p.get("label") or p.get("video") or "Pitch"
        ivb = float(p.get("ivb_cm", 35.0)) * scale_conv
        hb = float(p.get("hb_cm", 15.0)) * scale_conv

        # 外側発光パルスリング (大径 32px)
        fig.add_trace(go.Scatter(
            x=[hb], y=[ivb], mode="markers",
            marker=dict(size=32, color=p_col, opacity=0.35),
            hoverinfo="none", showlegend=False,
        ))

        # 実測ボールの「点」プロット本体 (鮮烈大径 22px + 白太枠 3.5px)
        text_pos = "bottom right" if (hb <= 0 and ivb >= 10) else ("bottom left" if ivb >= 10 else ("top right" if hb <= 0 else "top left"))
        fig.add_trace(go.Scatter(
            x=[hb], y=[ivb], mode="markers+text",
            marker=dict(size=22, color=p_col, line=dict(color="#ffffff", width=3.5), symbol="circle"),
            text=[f"  {your_pitch_tag}"],
            textposition=text_pos,
            textfont=dict(size=12, color="#0f172a", family="Arial Black"),
            name=legend_tag,
            hoverinfo="text",
            hovertext=f"<b>● {legend_tag}</b><br>IVB: {ivb:+.1f} {unit_label}<br>HB: {hb:+.1f} {unit_label}",
            showlegend=True,
        ))

        # ボールから適度に離れた位置からのポインタ吹き出し（上端の文字と絶対に被らないよう下側/横側へオフセット）
        callout_ax = -55 if hb >= 0 else 55
        callout_ay = 45 if ivb >= 10 else -45
        fig.add_annotation(
            x=hb, y=ivb,
            ax=callout_ax, ay=callout_ay,
            text=f"<b>{callout_tag}</b><br>IVB: {ivb:+.1f} {unit_label} | HB: {hb:+.1f} {unit_label}",
            showarrow=True, arrowhead=2, arrowsize=1.2, arrowwidth=2.5,
            arrowcolor="#0f172a",
            bgcolor="#0f172a", bordercolor="#38bdf8", borderwidth=2, borderpad=5,
            font=dict(size=11, color="#ffffff", family="Arial Black"), opacity=0.98,
        )

    # 多言語軸タイトル
    if is_left_handed:
        x_sub_dict = {
            "ja": "← シュート側 (三塁) | 水平変化 HB | スライダー側 (一塁) →",
            "en": "← Arm-Side (Run) | Horiz Break HB | Glove-Side (Cut/Sweep) →",
            "es": "← Lado Brazo (Run) | Quiebre Horiz. HB | Lado Guante (Sweep) →",
            "ko": "← 암사이드 (슈트) | 가로변화 HB | 글러브사이드 (슬라이더) →",
            "zh": "← 揮臂側 (內竄) | 水平位移 HB | 手套側 (外掃/卡特) →",
        }
    else:
        x_sub_dict = {
            "ja": "← スライダー側 (三塁) | 水平変化 HB | シュート側 (一塁) →",
            "en": "← Glove-Side (Cut/Sweep) | Horiz Break HB | Arm-Side (Run) →",
            "es": "← Lado Guante (Sweep) | Quiebre Horiz. HB | Lado Brazo (Run) →",
            "ko": "← 글러브사이드 (슬라이더) | 가로변화 HB | 암사이드 (슈트) →",
            "zh": "← 手套側 (外掃/卡特) | 水平位移 HB | 揮臂側 (內竄) →",
        }
    x_sub = x_sub_dict.get(lang, x_sub_dict["en"])

    y_sub_dict = {
        "ja": "↑ ホップ / 落下 ↓ 垂直変化 IVB",
        "en": "↑ Hop / Drop ↓ Induced Vert Break IVB",
        "es": "↑ Salto / Caída ↓ Quiebre Vertical IVB",
        "ko": "↑ 호프 / 낙하 ↓ 수직변화 IVB",
        "zh": "↑ 縱向升力 / 下墜 ↓ 垂直位移 IVB",
    }
    y_sub = y_sub_dict.get(lang, y_sub_dict["en"])

    fig.update_layout(
        title=dict(
            text=f"🎯 {i18n.t('movement_plot_title', lang)} (Statcast IVB vs HB)",
            font=dict(size=13, color="#0f172a", family="Arial Black"),
            y=0.96,
        ),
        xaxis=dict(
            title=dict(text=f"{x_sub} ({unit_label})", font=dict(size=10.5, color="#334155")),
            range=[-max_range, max_range],
            showgrid=True, gridcolor="rgba(0,0,0,0.06)", zeroline=False,
            tickfont=dict(size=10, color="#64748b"),
        ),
        yaxis=dict(
            title=dict(text=f"{y_sub} ({unit_label})", font=dict(size=10.5, color="#334155")),
            range=[-max_range, max_range],
            showgrid=True, gridcolor="rgba(0,0,0,0.06)", zeroline=False,
            tickfont=dict(size=10, color="#64748b"),
        ),
        plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
        margin=dict(l=25, r=25, t=75, b=25), height=410,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.04,
            xanchor="right",
            x=1,
            font=dict(size=11, color="#0f172a", family="Arial Black"),
        ),
    )
    return fig


# ========================================================
# 連続フォーム残像ストロボ写真 (Motion Trail)
# ========================================================
def generate_motion_trail_photo(video_name: str, kp_df: pd.DataFrame, phases: dict, release_frame: int, is_left_handed: bool = True) -> np.ndarray:
    """投球の主要5フェーズ骨格を1枚の静止画に残像（ストロボ写真）として合成。"""
    v_file = VIDEOS_DIR / f"{video_name}.mp4"
    if not v_file.exists():
        return np.zeros((720, 1280, 3), dtype=np.uint8)

    cap = cv2.VideoCapture(str(v_file))
    cap.set(cv2.CAP_PROP_POS_FRAMES, release_frame)
    ret, base_img = cap.read()
    cap.release()
    if not ret or base_img is None:
        base_img = np.zeros((720, 1280, 3), dtype=np.uint8)

    phase_styles = [
        ("① 足上げ", (255, 230, 200), 2, 0.45),
        ("② 踏み出し着地", (255, 210, 0), 2, 0.55),
        ("③ 最大外旋", (100, 255, 100), 3, 0.70),
        ("④ リリース", (0, 120, 255), 4, 1.00),
        ("⑤ フォロースルー", (255, 100, 200), 2, 0.60),
    ]

    t_wri = 9 if is_left_handed else 10
    wrist_pts = []
    out = base_img.copy()

    for (p_key, p_col, p_thick, p_alpha) in phase_styles:
        fr = phases.get(p_key)
        if fr is None:
            for k, f_val in phases.items():
                if p_key.split(" ")[1] in k:
                    fr = f_val
                    break
        if fr is None:
            continue

        sub = kp_df[kp_df["frame"] == fr]
        if sub.empty:
            continue
        row = sub.iloc[0]

        skel_layer = out.copy()
        for p1, p2 in SKELETON_CONNECTIONS:
            x1_k, y1_k = f"x_{p1}", f"y_{p1}"
            x2_k, y2_k = f"x_{p2}", f"y_{p2}"
            if x1_k in row and y1_k in row and x2_k in row and y2_k in row:
                x1, y1 = int(row[x1_k]), int(row[y1_k])
                x2, y2 = int(row[x2_k]), int(row[y2_k])
                if x1 > 0 and y1 > 0 and x2 > 0 and y2 > 0:
                    cv2.line(skel_layer, (x1, y1), (x2, y2), p_col, p_thick, cv2.LINE_AA)

        for i in range(17):
            xk, yk = f"x_{i}", f"y_{i}"
            if xk in row and yk in row:
                x, y = int(row[xk]), int(row[yk])
                if x > 0 and y > 0:
                    cv2.circle(skel_layer, (x, y), p_thick + 2, p_col, -1, cv2.LINE_AA)
                    cv2.circle(skel_layer, (x, y), max(1, p_thick - 1), (255, 255, 255), -1, cv2.LINE_AA)

        out = cv2.addWeighted(skel_layer, p_alpha, out, 1.0 - p_alpha, 0)
        wx, wy = int(row.get(f"x_{t_wri}", 0)), int(row.get(f"y_{t_wri}", 0))
        if wx > 0 and wy > 0:
            wrist_pts.append((wx, wy))

    if len(wrist_pts) >= 2:
        for i in range(len(wrist_pts) - 1):
            cv2.line(out, wrist_pts[i], wrist_pts[i+1], (0, 255, 255), 2, cv2.LINE_AA)
            cv2.circle(out, wrist_pts[i], 4, (0, 255, 255), -1)
        cv2.circle(out, wrist_pts[-1], 4, (0, 255, 255), -1)

    return out


# ========================================================
# What-If シミュレーター計算
# ========================================================
def calculate_what_if_simulation(
    current_speed_kmh: float,
    current_ext_m: float,
    current_knee_deg: float,
    current_spin_rpm: int,
    delta_ext_cm: float,
    delta_knee_deg: float,
    delta_spin_rpm: int,
    delta_arm_pct: float,
) -> dict:
    """What-If シミュレーション（球速・体感球速・ホップ量・空振り率）のリアルタイム試算。"""
    v0 = float(current_speed_kmh or 120.0)
    ext0 = float(current_ext_m or 1.5)

    d_velo = (delta_ext_cm * 0.08) + (delta_knee_deg * 0.12) + (delta_arm_pct * 0.35)
    proj_velo = v0 + d_velo

    new_ext = ext0 + (delta_ext_cm / 100.0)
    perceived_diff = (new_ext - 0.95) * 4.0
    proj_perceived = proj_velo + perceived_diff

    d_ivb = (delta_spin_rpm * 0.018) + (d_velo * 0.15)
    base_whiff = 18.0
    proj_whiff = max(10.0, min(45.0, base_whiff + (d_velo * 0.45) + (d_ivb * 0.25)))

    return {
        "proj_velo": round(proj_velo, 1),
        "delta_velo": round(d_velo, 1),
        "proj_perceived": round(proj_perceived, 1),
        "delta_perceived": round(proj_perceived - (v0 + (ext0 - 0.95) * 4.0), 1),
        "delta_ivb": round(d_ivb, 1),
        "proj_whiff": round(proj_whiff, 1),
        "delta_whiff": round(proj_whiff - base_whiff, 1),
    }


# ========================================================
# 本日のピッチング処方箋（練習ドリル推薦）
# ========================================================
def get_pitching_prescription_drills(biomechanics: dict, spin_data: dict = None, lang: str = "ja") -> list:
    """診断結果に基づき、個人に最適化された練習ドリル処方箋リストを生成。"""
    drills = []
    knee = float(biomechanics.get("lead_knee_angle", 0) or 0)
    elbow = float(biomechanics.get("elbow_angle", 0) or 0)
    stride_pct = float(biomechanics.get("stride_pct", 0) or 0)
    gyro = float(spin_data.get("gyro_angle_deg", 0) if spin_data else 0)

    if knee > 0 and knee < 165:
        drills.append({
            "title": {"ja": "ステップストップ・ボックススロー", "en": "Step-Stop Box Drop Throw", "es": "Lanzamiento con Parada en Caja", "ko": "스텝 스톱 박스 드롭 스로우", "zh": "前膝煞車木箱跨步投擲"}.get(lang, "Step-Stop Box Throw"),
            "target": {"ja": "前膝の突っ張り・骨盤急減速による回転加速", "en": "Lead knee bracing & rotational kinetic braking", "es": "Bloqueo de rodilla para aceleración", "ko": "앞무릎 브레이킹 및 골반 감속 가속", "zh": "前膝強效煞車帶動骨盆加速"}.get(lang, "Knee Bracing"),
            "desc": {"ja": "低めの台から前足を踏み込み、着地瞬間に前膝をピンと伸ばして骨盤を急停止させ、上半身を一気に振り抜く感覚を掴みます。", "en": "Step down from a low box and lock lead knee upon landing to translate linear momentum into violent torso rotation.", "es": "Baja de una caja bloqueando la rodilla para transferir energía.", "ko": "낮은 박스에서 착지하며 앞무릎을 곧게 펴 골반을 순간 정지시키는 연습입니다.", "zh": "從踏板向下著地瞬間前膝強力伸展鎖定，將衝力轉化為猛烈轉體速度。"}.get(lang, "Perform step-stop throw drill."),
        })

    if stride_pct > 0 and stride_pct < 85:
        drills.append({
            "title": {"ja": "メディシンボール・ダウンヒルドスロー", "en": "Downhill Med-Ball Drive Throw", "es": "Lanzamiento con Balón Cuesta Abajo", "ko": "메디신볼 다운힐 드라이브 스로우", "zh": "下坡藥球強推延伸投擲"}.get(lang, "Downhill Drive Throw"),
            "target": {"ja": "軸足ヒップヒンジのタメと前への大きなストライド", "en": "Back-hip hinge load & dynamic lower-half extension", "es": "Carga de cadera trasera y zancada más larga", "ko": "축발 힙힌지 장전 및 앞쪽 스트라이드 확장", "zh": "後腳髖關節充分蓄力與前向極致延伸"}.get(lang, "Hip Hinge Load"),
            "desc": {"ja": "2〜3kgのメディシンボールを持ち、マウンドの傾斜を使って軸足股関節を深く折り込み、限界まで前へ身体を運んでから投擲します。", "en": "Hold 4-6 lb med ball, load back hip deeply on slope, and drive far forward before releasing.", "es": "Usa un balón medicinal cargando la cadera y empujando hacia adelante.", "ko": "2~3kg 메디신볼로 축발 고관절을 깊게 접은 채 앞으로 길게 밀고 나가며 던집니다.", "zh": "雙手持 2-3kg 藥球，利用投手丘斜坡深度折疊後髖，大幅前進延伸後爆發投出。"}.get(lang, "Perform med ball downhill throw."),
        })

    if elbow > 0 and elbow > 120:
        drills.append({
            "title": {"ja": "タオルシャドー・トップの間作りドリル", "en": "Towel Whip & Top Spacing Pause", "es": "Ejercicio de Toalla y Pausa en el Tope", "ko": "수건 섀도우 탑 정지 드릴", "zh": "毛巾甩臂頂點蓄力定型訓練"}.get(lang, "Towel Whip Drill"),
            "target": {"ja": "トップでの肘90度保持としなり動作の習得", "en": "Maintain 90-degree elbow flexion at top for greater whip", "es": "Mantener flexión de codo a 90 grados para latigazo", "ko": "탑 위치 90도 팔꿈치 유지 및 채찍 효과 체득", "zh": "頂點維持90度屈肘以創造最大鞭打しなり"}.get(lang, "Elbow Whip Spacing"),
            "desc": {"ja": "タオルを持ち、トップの位置で一瞬静止（肘が90度前後の懐を作る）してから胸郭の回転とともに一気に振り下ろします。", "en": "Hold a towel, pause at top with elbow bent ~90 deg, then rotate torso to whip towel smoothly.", "es": "Pausa breve en el tope con codo a 90 grados y gira el torso.", "ko": "수건을 쥐고 탑에서 1초 멈춘 뒤 가슴 회전과 함께 채찍처럼 가속합니다.", "zh": "手持毛巾在頂點暫停定型（保持手肘約90度），隨後利用核心轉動將毛巾如鞭子般甩出。"}.get(lang, "Perform towel shadow drill."),
        })

    if gyro > 35:
        drills.append({
            "title": {"ja": "シームプレッシャー・スピン感覚ドリル", "en": "Seam Pressure & Pure Backspin Drill", "es": "Ejercicio de Presión en Costuras para Giro Puro", "ko": "솔기 압력 및 순수 백스핀 드릴", "zh": "縫線施力純純倒旋 (Backspin) 感知訓練"}.get(lang, "Seam Pressure Drill"),
            "target": {"ja": "ジャイロ成分を抑えてバックスピン効率（ホップ量）を最大化", "en": "Reduce gyro component to maximize pure backspin ride", "es": "Reducir giro giroscópico para maximizar efecto de subida", "ko": "자이로 성분을 줄이고 수직 호프 효율 극대화", "zh": "抑制子彈旋轉，將能量全數轉化為垂直進壘位移"}.get(lang, "Backspin Efficiency"),
            "desc": {"ja": "中指と人差し指で縫い目の角を均等に真後ろから押し込む意識を持ち、ネットに向けて近距離から純粋なスピンをかける反復練習を行います。", "en": "Focus on applying equal pressure on seams from directly behind ball, throwing short distance into net.", "es": "Presiona las costuras directamente desde atrás lanzando a corta distancia.", "ko": "검지와 중지로 솔기 뒷면を 균등하게 강하게 찍어 누르며 근거리에서 던집니다.", "zh": "食指與中指平均施力於縫線正後方，近距離向護網反覆投出純淨縱向倒旋球。"}.get(lang, "Perform seam pressure spin drill."),
        })

    if not drills:
        drills.append({
            "title": {"ja": "バランスピッチング・再現性ドリル", "en": "Full-Body Maintenance Throw", "es": "Mantenimiento General", "ko": "풀바디 밸런스 피칭 유지", "zh": "全身平衡動力鏈維持投擲"}.get(lang, "Maintenance Throw"),
            "target": {"ja": "現在の高効率な投球フォームの再現性向上", "en": "Repeatability of balanced mechanics", "es": "Consistencia de la mecánica actual", "ko": "현재 훌륭한 폼의 재현성 유지", "zh": "維持當前高效率投球動作的穩定性"}.get(lang, "Repeatability"),
            "desc": {"ja": "現状のフォームバランスが非常に良好です。70〜80%の力感で同じリリース位置を繰り返すピッチングで再現性を高めましょう。", "en": "Mechanics are exceptionally well-balanced. Practice repeating release point at 70-80% intensity.", "es": "Tus mecánicas son excelentes. Practica repetir el punto de soltada al 80%.", "ko": "현재 밸런스가 매우 우수합니다. 80% 힘으로 일관된 릴리스를 반복하세요.", "zh": "目前動力鏈效率極高。建議以七至八成力道反覆強化相同出手點的再現度。"}.get(lang, "Practice repeatable mechanics."),
        })

    return drills




# ========================================================
# 5. Statcast風「Stuff+」球質レーダーチャート
# ========================================================
def calculate_stuff_plus(
    speed_kmh: float,
    spin_data: dict,
    extension_m: float,
    pitch_type: str = "fastball",
) -> dict:
    """プロ基準（MLB / NPB 平均 = 100）に基づき球質指数 Stuff+ を総合算出。"""
    v = float(speed_kmh or 140.0)
    sp = spin_data or {}
    ivb = float(sp.get("ivb_cm", 35.0))
    hb = float(sp.get("hb_cm", 15.0))
    eff = float(sp.get("active_spin_pct", 85.0))
    ext = float(extension_m or 1.80)

    # 基準平均値 (Fastball baseline: 145km/h, 38cm IVB, 20cm HB, 85% Eff, 1.82m Ext)
    velo_plus = round(100.0 + (v - 145.0) * 1.6, 1)
    ivb_plus = round(100.0 + (ivb - 38.0) * 1.3, 1)
    hb_plus = round(100.0 + (abs(hb) - 20.0) * 1.1, 1)
    eff_plus = round(100.0 + (eff - 85.0) * 1.2, 1)
    ext_plus = round(100.0 + (ext - 1.82) * 55.0, 1)

    # 球種別ウェイト
    if pitch_type in ["slider", "sweeper"]:
        overall = 0.20 * velo_plus + 0.15 * ivb_plus + 0.40 * hb_plus + 0.15 * eff_plus + 0.10 * ext_plus
    elif pitch_type in ["curve", "splitter"]:
        overall = 0.20 * velo_plus + 0.40 * ivb_plus + 0.15 * hb_plus + 0.15 * eff_plus + 0.10 * ext_plus
    else:
        overall = 0.35 * velo_plus + 0.28 * ivb_plus + 0.14 * hb_plus + 0.13 * eff_plus + 0.10 * ext_plus

    overall_score = int(round(np.clip(overall, 60.0, 150.0)))

    # 球質アーキタイプ（タイプ判定）
    if ivb > 44.0 and eff > 90.0:
        archetype = {"ja": "🔥 ライジング・ホップ型 (High-Ride)", "en": "🔥 High-Ride Hop", "es": "🔥 Bola Alta con Salto", "ko": "🔥 하이라이드 호프형", "zh": "🔥 高轉升力衝穹型"}
    elif abs(hb) > 35.0:
        archetype = {"ja": "⚡ スイーパー・メガラン型 (Sweeper Run)", "en": "⚡ Mega-Sweeper Run", "es": "⚡ Gran Deslizador", "ko": "⚡ 스위퍼 메가런형", "zh": "⚡ 巨幅橫移外掃型"}
    elif ivb < 15.0 and v > 140.0:
        archetype = {"ja": "🪨 ヘビーシンカー・ボーリング型 (Bowling Sinker)", "en": "🪨 Heavy Bowling Sinker", "es": "🪨 Bola Pesada Hundida", "ko": "🪨 헤비 볼링 싱커형", "zh": "🪨 重砲滾地重沉球型"}
    elif eff > 92.0:
        archetype = {"ja": "🎯 高純度スピン型 (Pure Spin)", "en": "🎯 Pure Active Spin", "es": "🎯 Giro Puro Activo", "ko": "🎯 고순도 스핀형", "zh": "🎯 高純度有效轉速型"}
    else:
        archetype = {"ja": "⚖️ バランス型 (Well-Balanced)", "en": "⚖️ Well-Balanced Pitch", "es": "⚖️ Lanzamiento Equilibrado", "ko": "⚖️ 균형 밸런스형", "zh": "⚖️ 均衡標準型"}

    return {
        "overall": overall_score,
        "velo_plus": float(np.clip(velo_plus, 50, 160)),
        "ivb_plus": float(np.clip(ivb_plus, 50, 160)),
        "hb_plus": float(np.clip(hb_plus, 50, 160)),
        "eff_plus": float(np.clip(eff_plus, 50, 160)),
        "ext_plus": float(np.clip(ext_plus, 50, 160)),
        "archetype": archetype,
    }


def generate_stuff_plus_radar(stuff_dict: dict, pitch_color: str = "#00d2ff", lang: str = "ja"):
    r"""Statcast風 5軸 Stuff+ 球質レーダーチャート（基準100）を生成。
    レイアウト:
                    ホップ (Ride+)
                         ↑
        横変化 (Run+)          球速 (Velo+)
              ↖             ↗
                \         /
                 \       /
                  \     /
              ↙             ↘
      スピン効率 (Eff+)      前到達 (Ext+)
    外側の軸ラベル自体に各項目のスコア数値を明記。
    """
    import plotly.graph_objects as go

    # ユーザー指定の順序 (上から時計回り):
    # 0: ホップ (Ride+) [Top / North]
    # 1: 球速 (Velo+)   [Top-Right / NE]
    # 2: 前到達 (Ext+)  [Bottom-Right / SE]
    # 3: スピン効率 (Eff+) [Bottom-Left / SW]
    # 4: 横変化 (Run+)  [Top-Left / NW]

    cat_names = [
        {"ja": "ホップ (Ride+)", "en": "Ride+ (Hop)", "es": "Salto (Ride+)", "ko": "호프 (Ride+)", "zh": "縱向升力 (Ride+)"}.get(lang, "Ride+"),
        {"ja": "球速 (Velo+)", "en": "Velo+ (Speed)", "es": "Velocidad (Velo+)", "ko": "구속 (Velo+)", "zh": "球速初速 (Velo+)"}.get(lang, "Velo+"),
        {"ja": "前到達 (Ext+)", "en": "Ext+ (Extension)", "es": "Extensión (Ext+)", "ko": "익스텐션 (Ext+)", "zh": "前伸步幅 (Ext+)"}.get(lang, "Ext+"),
        {"ja": "スピン効率 (Eff+)", "en": "Eff+ (Spin Eff)", "es": "Eficiencia (Eff+)", "ko": "스핀효율 (Eff+)", "zh": "旋轉效率 (Eff+)"}.get(lang, "Eff+"),
        {"ja": "横変化 (Run+)", "en": "Run+ (Movement)", "es": "Quiebre (Run+)", "ko": "가로변화 (Run+)", "zh": "橫向位移 (Run+)"}.get(lang, "Run+"),
    ]

    values = [
        stuff_dict.get("ivb_plus", 100),
        stuff_dict.get("velo_plus", 100),
        stuff_dict.get("ext_plus", 100),
        stuff_dict.get("eff_plus", 100),
        stuff_dict.get("hb_plus", 100),
    ]

    # 外側の軸ラベルに項目名をクッキリ黒文字、数値を鮮烈ブルーで明記！
    categories = [
        f"<span style='color:#0f172a; font-weight:900; font-size:12px;'>{name}</span><br><b style='color:#0284c7; font-size:15px; font-family:Arial Black;'>【{val:.0f}】</b>"
        for name, val in zip(cat_names, values)
    ]

    cats_closed = categories + [categories[0]]
    vals_closed = values + [values[0]]
    bench_closed = [100, 100, 100, 100, 100, 100]

    fig = go.Figure()

    # プロ平均基準ライン (100)
    fig.add_trace(go.Scatterpolar(
        r=bench_closed,
        theta=cats_closed,
        mode="lines",
        line=dict(color="#64748b", dash="dot", width=2.0),
        name={"ja": "プロ平均 (100)", "en": "Pro Avg (100)", "es": "Promedio Pro (100)", "ko": "프로 평균 (100)", "zh": "職棒平均 (100)"}.get(lang, "Pro Avg"),
        hoverinfo="name",
    ))

    # 投手の Stuff+ ポリゴン
    fig.add_trace(go.Scatterpolar(
        r=vals_closed,
        theta=cats_closed,
        mode="lines+markers",
        fill="toself",
        fillcolor="rgba(2, 132, 199, 0.25)",
        line=dict(color=pitch_color, width=3.5),
        marker=dict(size=9, color="#0284c7", line=dict(color="#ffffff", width=2.0)),
        name="Stuff+",
        hovertemplate="%{theta}: %{r:.1f}<extra></extra>",
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[50, 145],
                tickvals=[70, 85, 100, 115, 130],
                tickfont=dict(size=10, color="#0f172a", family="Arial Black"),
                gridcolor="#cbd5e1",
            ),
            angularaxis=dict(
                direction="clockwise",
                rotation=90,  # 0番目(ホップ Ride+)が真上(90度)に来るように時計回り配置！
                tickfont=dict(size=12, color="#0f172a", family="Arial Black"),
                gridcolor="#cbd5e1",
            ),
            bgcolor="rgba(241, 245, 249, 0.65)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=75, r=75, t=55, b=45),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.22,
            xanchor="center",
            x=0.5,
            font=dict(size=11, color="#0f172a", family="Arial Black"),
        ),
        height=345,
    )
    return fig



# ========================================================
# 2. ピッチトンネル＆コミットポイント3D可視化
# ========================================================
def generate_pitch_tunnel_figure(
    res_a: dict,
    res_b: dict,
    dist_unit: str = "m",
    lang: str = "ja",
    camera_view: str = "catcher",
) -> tuple:
    """投球Aと投球Bの3D軌道を重ね合わせ、打者判断点(7.2m手前)のトンネル幅を算出・可視化。"""
    import plotly.graph_objects as go

    left_a = bool(res_a.get("left_handed", res_a.get("is_left_handed", True)))
    left_b = bool(res_b.get("left_handed", res_b.get("is_left_handed", True)))

    xa, ya, za, x0_a, y0_a, z0_a, xp_a, zp_a = calculate_unified_pitch_trajectory(
        speed_kmh=res_a.get("speed_kmh", 140.0),
        flight_time=float(res_a.get("flight_time", 0.45)),
        extension_m=float(res_a.get("extension", 1.80)),
        pitcher_height_m=float(res_a.get("biomechanics", {}).get("pitcher_height_m", 1.80)),
        is_left_handed=left_a,
        ivb_cm=float(res_a.get("spin_data", {}).get("ivb_cm", 35.0)),
        hb_cm=float(res_a.get("spin_data", {}).get("hb_cm", 15.0)),
        ball_df=res_a.get("ball_df"),
        net_frame=int(res_a.get("net_frame", 70)),
        pitch_type=res_a.get("pitch_type", "fastball"),
        n_pts=60,
    )
    xb, yb, zb, x0_b, y0_b, z0_b, xp_b, zp_b = calculate_unified_pitch_trajectory(
        speed_kmh=res_b.get("speed_kmh", 140.0),
        flight_time=float(res_b.get("flight_time", 0.45)),
        extension_m=float(res_b.get("extension", 1.80)),
        pitcher_height_m=float(res_b.get("biomechanics", {}).get("pitcher_height_m", 1.80)),
        is_left_handed=left_b,
        ivb_cm=float(res_b.get("spin_data", {}).get("ivb_cm", 35.0)),
        hb_cm=float(res_b.get("spin_data", {}).get("hb_cm", 15.0)),
        ball_df=res_b.get("ball_df"),
        net_frame=int(res_b.get("net_frame", 70)),
        pitch_type=res_b.get("pitch_type", "fastball"),
        n_pts=60,
    )

    idx_a = np.argmin(np.abs(ya - 7.2))
    idx_b = np.argmin(np.abs(yb - 7.2))
    pt_commit_a = np.array([xa[idx_a], ya[idx_a], za[idx_a]])
    pt_commit_b = np.array([xb[idx_b], yb[idx_b], zb[idx_b]])
    dist_commit_cm = np.linalg.norm(pt_commit_a - pt_commit_b) * 100.0
    dist_plate_cm = np.linalg.norm([xa[-1] - xb[-1], za[-1] - zb[-1]]) * 100.0

    ratio = dist_plate_cm / max(1.0, dist_commit_cm)
    if dist_commit_cm <= 15.0:
        tunnel_rating = {"ja": "⭐⭐⭐ 神ピッチトンネル (Elite Deception)", "en": "⭐⭐⭐ Elite Tunneling", "es": "⭐⭐⭐ Túnel Élite", "ko": "⭐⭐⭐ 엘리트 피치 터널", "zh": "⭐⭐⭐ 神級共軌隧道 (極致欺騙性)"}.get(lang, "Elite Tunnel")
    elif dist_commit_cm <= 25.0:
        tunnel_rating = {"ja": "⭐⭐ 優秀ピッチトンネル (Great)", "en": "⭐⭐ Great Tunneling", "es": "⭐⭐ Gran Túnel", "ko": "⭐⭐ 우수 피치 터널", "zh": "⭐⭐ 優秀共軌隧道"}.get(lang, "Great Tunnel")
    else:
        tunnel_rating = {"ja": "⭐ 通常トンネル (Standard)", "en": "⭐ Standard Separation", "es": "⭐ Separación Estándar", "ko": "⭐ 일반 분리", "zh": "⭐ 一般軌跡分離"}.get(lang, "Standard")

    metrics = {
        "commit_cm": round(dist_commit_cm, 1),
        "plate_cm": round(dist_plate_cm, 1),
        "ratio": round(ratio, 1),
        "rating": tunnel_rating,
    }

    # 多言語ラベルの取得
    pitch_a_lbl = i18n.t("pitch_a", lang)
    pitch_b_lbl = i18n.t("pitch_b", lang)
    tunnel_zone_lbl = i18n.t("tunnel_zone_name", lang)
    commit_pt_lbl = i18n.t("commit_point_name", lang)
    sz_lbl = i18n.t("strike_zone_name", lang)

    fig = go.Figure()
    fig.add_trace(go.Scatter3d(
        x=xa, y=ya, z=za, mode="lines",
        line=dict(color="#ef4444", width=5.5),
        name=f"🔴 {pitch_a_lbl} ({res_a.get('video', 'Pitch A')})",
    ))
    fig.add_trace(go.Scatter3d(
        x=xb, y=yb, z=zb, mode="lines",
        line=dict(color="#3b82f6", width=5.5),
        name=f"🔵 {pitch_b_lbl} ({res_b.get('video', 'Pitch B')})",
    ))

    # トンネル円筒（y >= 7.2m）
    tunnel_mask = ya >= 7.2
    fig.add_trace(go.Scatter3d(
        x=xa[tunnel_mask], y=ya[tunnel_mask], z=za[tunnel_mask],
        mode="lines",
        line=dict(color="rgba(0, 229, 255, 0.45)", width=14),
        name=tunnel_zone_lbl,
    ))

    # コミットメントポイントリング
    th = np.linspace(0, 2 * np.pi, 24)
    r_ring = 0.20
    fig.add_trace(go.Scatter3d(
        x=pt_commit_a[0] + r_ring * np.cos(th),
        y=np.full_like(th, 7.2),
        z=pt_commit_a[2] + r_ring * np.sin(th),
        mode="lines",
        line=dict(color="#f59e0b", width=4),
        name=commit_pt_lbl,
    ))

    # ストライクゾーン
    sz_x = [-0.26, 0.26, 0.26, -0.26, -0.26]
    sz_y = [0, 0, 0, 0, 0]
    sz_z = [0.50, 0.50, 1.02, 1.02, 0.50]
    fig.add_trace(go.Scatter3d(
        x=sz_x, y=sz_y, z=sz_z, mode="lines",
        line=dict(color="#ffffff", width=4), name=sz_lbl, hoverinfo="name",
    ))

    # 多言語軸タイトル
    x_axis_lbl = i18n.t("tunnel_xaxis_title", lang)
    y_axis_lbl = i18n.t("tunnel_yaxis_title", lang)
    z_axis_lbl = i18n.t("tunnel_zaxis_title", lang)

    # 視点プリセット（捕手視点、投手視点、側面、真上）
    # center を (0,0,0) に固定することで、ドラッグ時にジャンプやカクつきなく滑らかに360度オービット回転可能！
    cameras = {
        "catcher": dict(eye=dict(x=-0.08, y=-2.1, z=0.60), center=dict(x=0, y=0, z=0), up=dict(x=0, y=0, z=1)),
        "pitcher": dict(eye=dict(x=0.08, y=2.2, z=0.70), center=dict(x=0, y=0, z=0), up=dict(x=0, y=0, z=1)),
        "side": dict(eye=dict(x=-2.4, y=0.0, z=0.75), center=dict(x=0, y=0, z=0), up=dict(x=0, y=0, z=1)),
        "top": dict(eye=dict(x=0.0, y=0.01, z=2.7), center=dict(x=0, y=0, z=0), up=dict(x=0, y=1, z=0)),
    }
    sel_cam = cameras.get(camera_view, cameras["catcher"])

    fig.update_layout(
        scene=dict(
            dragmode="orbit",
            xaxis=dict(title=dict(text=x_axis_lbl, font=dict(color="#f8fafc", size=11)), range=[-1.8, 1.8], backgroundcolor="#0f172a", gridcolor="#334155"),
            yaxis=dict(title=dict(text=y_axis_lbl, font=dict(color="#f8fafc", size=11)), range=[-1.0, 19.5], backgroundcolor="#0f172a", gridcolor="#334155"),
            zaxis=dict(title=dict(text=z_axis_lbl, font=dict(color="#f8fafc", size=11)), range=[0, 2.5], backgroundcolor="#0f172a", gridcolor="#334155"),
            camera=sel_cam,
            aspectratio=dict(x=1.3, y=2.8, z=1.0),
        ),
        paper_bgcolor="#0b0f19",
        plot_bgcolor="#0b0f19",
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=0.01, xanchor="center", x=0.5, font=dict(size=10.5, color="#f8fafc")),
        height=420,
    )
    fig.update_scenes(dragmode="orbit")
    return fig, metrics



# ========================================================
# 4. 2投球フォーム完全同期スプリット再生ヘルパー
# ========================================================
def get_synced_compare_frames(
    video_a: str,
    video_b: str,
    rel_a: int,
    rel_b: int,
    offset_frame: int = 0,
    kp_df_a: pd.DataFrame = None,
    kp_df_b: pd.DataFrame = None,
) -> tuple:
    """リリースフレームを基準に完全同期した投球A・Bの2画面フレーム（骨格付き）を取得。"""
    fa = max(0, int(rel_a + offset_frame))
    fb = max(0, int(rel_b + offset_frame))

    v_a = VIDEOS_DIR / f"{video_a}.mp4"
    v_b = VIDEOS_DIR / f"{video_b}.mp4"

    def read_annotated_frame(v_path, target_frame, kp_df):
        cap = cv2.VideoCapture(str(v_path))
        cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
        ret, frame = cap.read()
        cap.release()
        if not ret or frame is None:
            return np.zeros((480, 640, 3), dtype=np.uint8)

        if kp_df is not None and not kp_df.empty:
            cand = kp_df[kp_df["frame"] == target_frame]
            if not cand.empty:
                frame = draw_skeleton(frame, cand.iloc[0], draw_labels=False)

        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    img_a = read_annotated_frame(v_a, fa, kp_df_a)
    img_b = read_annotated_frame(v_b, fb, kp_df_b)
    return img_a, img_b



# ========================================================
# 6. MLB中継風「投球スタッツカード (Broadcast Card)」PNG生成
# ========================================================
def generate_broadcast_card(
    video_name: str,
    speed_kmh: float,
    extension_m: float,
    spin_data: dict,
    stuff_data: dict,
    release_frame: int,
    kp_df: pd.DataFrame,
    pitch_type: str = "fastball",
    speed_unit: str = "km/h",
    dist_unit: str = "m",
    lang: str = "ja",
) -> bytes:
    """MLB中継 / Statcast風のスタイリッシュな投球リザルトカード（1200x675 PNG）を生成。"""
    from PIL import Image, ImageDraw, ImageFont
    import io

    W, H = 1200, 675
    # ベース画像（ダークネイビーグラデーション）
    card = Image.new("RGB", (W, H), color=(11, 15, 25))
    draw = ImageDraw.Draw(card)

    # 上部アクセントバー
    draw.rectangle([0, 0, W, 8], fill=(0, 210, 255))

    # 背景グリッド線
    for y in range(50, H, 60):
        draw.line([(0, y), (W, y)], fill=(20, 28, 48), width=1)
    for x in range(50, W, 80):
        draw.line([(x, 0), (x, H)], fill=(20, 28, 48), width=1)

    # 1. 左側: リリース写真（骨格付き）の埋め込み
    v_file = VIDEOS_DIR / f"{video_name}.mp4"
    frame_rgb = None
    if v_file.exists():
        cap = cv2.VideoCapture(str(v_file))
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(release_frame or 0))
        ret, f_bgr = cap.read()
        cap.release()
        if ret and f_bgr is not None:
            if kp_df is not None and not kp_df.empty:
                cand = kp_df[kp_df["frame"] == release_frame]
                if not cand.empty:
                    f_bgr = draw_skeleton(f_bgr, cand.iloc[0], draw_labels=False)
            frame_rgb = cv2.cvtColor(f_bgr, cv2.COLOR_BGR2RGB)

    if frame_rgb is not None:
        pil_frame = Image.fromarray(frame_rgb)
        # アスペクト比維持で 520x570 内にリサイズ
        pil_frame.thumbnail((520, 570), Image.Resampling.LANCZOS)
        # カードへ貼り付け
        card.paste(pil_frame, (40, 50))
        # 枠線
        fw, fh = pil_frame.size
        draw.rectangle([39, 49, 41 + fw, 51 + fh], outline=(0, 210, 255), width=2)
    else:
        draw.rectangle([40, 50, 560, 620], fill=(22, 30, 46), outline=(51, 65, 85), width=2)
        draw.text((180, 320), "RELEASE FRAME", fill=(148, 163, 184))

    # 2. 右側: スタッツパネル描画
    px0 = 600

    # フォント準備
    try:
        font_lg = ImageFont.truetype("arial.ttf", 64)
        font_md = ImageFont.truetype("arial.ttf", 28)
        font_sm = ImageFont.truetype("arial.ttf", 18)
        font_bold = ImageFont.truetype("arialbd.ttf", 26)
    except Exception:
        font_lg = ImageFont.load_default()
        font_md = ImageFont.load_default()
        font_sm = ImageFont.load_default()
        font_bold = ImageFont.load_default()

    # ヘッダー
    draw.text((px0, 45), "⚾ STATCAST PITCH ANALYSIS  |  OUTPACE BASEBALL", fill=(0, 210, 255), font=font_sm)
    draw.text((px0, 75), f"{video_name.upper()} • {pitch_type.upper()}", fill=(248, 250, 252), font=font_bold)

    # 区切り線
    draw.line([(px0, 115), (W - 40, 115)], fill=(51, 65, 85), width=2)

    # メイン球速
    sp_mph = speed_kmh * 0.621371
    velo_text = f"{speed_kmh:.1f} km/h" if speed_unit == "km/h" else f"{sp_mph:.1f} mph"
    sub_velo = f"({sp_mph:.1f} mph)" if speed_unit == "km/h" else f"({speed_kmh:.1f} km/h)"
    draw.text((px0, 130), velo_text, fill=(255, 255, 255), font=font_lg)
    draw.text((px0 + 360, 165), sub_velo, fill=(148, 163, 184), font=font_sm)

    # Stuff+ バッジ
    st_val = stuff_data.get("overall", 100)
    badge_col = (16, 185, 129) if st_val >= 110 else ((0, 210, 255) if st_val >= 100 else (245, 158, 11))
    draw.rectangle([px0, 220, px0 + 170, 260], fill=badge_col)
    draw.text((px0 + 15, 228), f"STUFF+ {st_val}", fill=(15, 23, 42), font=font_bold)

    # アーキタイプ判定
    arch = stuff_data.get("archetype", {}).get(lang, "Standard Pitch")
    draw.text((px0 + 185, 232), str(arch), fill=(226, 232, 240), font=font_sm)

    # メトリクスグリッド (2列 x 3行)
    sp_data = spin_data or {}
    metrics_list = [
        ("SPIN RATE", f"{sp_data.get('spin_rate_rpm', 0):,} rpm"),
        ("SPIN AXIS", f"{sp_data.get('spin_axis', '12:00')}"),
        ("ACTIVE SPIN", f"{sp_data.get('active_spin_pct', 85):.1f} %"),
        ("IVB (RIDE)", f"{sp_data.get('ivb_cm', 35):+.1f} cm"),
        ("HB (RUN)", f"{sp_data.get('hb_cm', 15):+.1f} cm"),
        ("EXTENSION", f"{extension_m:.2f} m"),
    ]

    for idx, (label, val) in enumerate(metrics_list):
        row = idx // 2
        col = idx % 2
        bx = px0 + col * 270
        by = 295 + row * 95

        # ミニボックス
        draw.rectangle([bx, by, bx + 250, by + 75], fill=(22, 30, 46), outline=(39, 53, 76), width=1)
        draw.text((bx + 14, by + 10), label, fill=(148, 163, 184), font=font_sm)
        draw.text((bx + 14, by + 34), val, fill=(0, 210, 255), font=font_bold)

    # フッターウォーターマーク
    draw.line([(px0, H - 55), (W - 40, H - 55)], fill=(39, 53, 76), width=1)
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    draw.text((px0, H - 42), f"VERIFIED BY OUTPACE BASEBALL • {now_str}", fill=(100, 116, 139), font=font_sm)

    buf = io.BytesIO()
    card.save(buf, format="PNG")
    return buf.getvalue()
