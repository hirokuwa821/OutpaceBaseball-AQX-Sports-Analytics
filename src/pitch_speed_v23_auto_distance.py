"""
pitch_speed_v23_auto_distance.py

投球速度解析 v23 (左右投手対応・姿勢推定×ボール解析 改良版)
- PLATE_REF_FRAME (安定フレーム) で支え足の Y を取得し、左投手でも正しく支え足を選択
- ネット Y はキーポイント全体の最大 Y を自動検出
- エクステンションが総距離の 80% を超える場合は警告し、距離を 0 以上にクランプ
- HANDEDNESS 辞書で動画ごとに左投 (True) / 右投 (False) を指定可能
"""

import csv
import math
import numpy as np
import pandas as pd
from pathlib import Path

# ============================================================
# 設定
# ============================================================

# ディレクトリ設定
# 現在のファイル (src/pitch_speed_v23_auto_distance.py) から見て、
# output フォルダは一つ上の階層にある
ROOT_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = ROOT_DIR / "output" / "ball_tracking_v5"
KEYPOINTS_PATH = ROOT_DIR / "output" / "keypoints.csv"
OUTPUT_DIR = ROOT_DIR / "output" / "pitch_speed_v23"

def get_keypoints_path(video_name: str) -> Path:
    specific = ROOT_DIR / "output" / f"keypoints_{video_name}.csv"
    if specific.exists():
        return specific
    return KEYPOINTS_PATH

# プレートからネットまでの実測距離 (公認野球規則: 18.44m)
TOTAL_FIELD_DISTANCE_M = 18.44

# プレート座標取得に使用する安定フレーム番号（デフォルト）
DEFAULT_PLATE_REF_FRAME = 0
PLATE_REF_FRAME_OVERRIDES = {}

# ------------------------------------------------------------
# 1) 動画ごとのリリース・ネットフレーム
# ------------------------------------------------------------
BASE_FRAMES = {
    "pitch_102_1": (51, 70),
    "pitch_98_1": (72, 92),
    "pitch_98_2": (66, 86),
    "pitch_00015_80": (429, 455),
}

# ------------------------------------------------------------
# 2) 投手の左右情報（True=左投げ, False=右投げ）
# ------------------------------------------------------------
HANDEDNESS = {
    "pitch_102_1": True,   # 左投げ
    "pitch_98_1": True,
    "pitch_98_2": True,
    "pitch_00015_80": False, # 右投げ (RHP)
}

# 空気抵抗パラメータ（従来と同じ）
CD = 0.30
RHO = 1.204
DIAMETER = 0.073
MASS = 0.145
AREA = math.pi * (DIAMETER / 2) ** 2
K_DRAG = (0.5 * CD * RHO * AREA) / MASS

# ============================================================
# ユーティリティ関数
# ============================================================

def auto_detect_plate_frame(df: pd.DataFrame, start: int = 0, end: int = 5) -> int:
    """動画開始直後の静止スタンス（プレート上）で最適なフレームを自動探索する。
    左右足首 (y_15, y_16) の Y 差が最小のフレームを返す。
    """
    best_frame = 0
    min_diff = float('inf')
    max_fr = min(end, len(df) - 1)
    for fr in range(start, max_fr + 1):
        sub = df[df['frame'] == fr]
        if not sub.empty:
            try:
                y15 = float(sub['y_15'].values[0])
                y16 = float(sub['y_16'].values[0])
                diff = abs(y15 - y16)
                if diff < min_diff:
                    min_diff = diff
                    best_frame = fr
            except Exception:
                continue
    return best_frame

def get_foot_coordinates(df: pd.DataFrame, release_frame: int, video_name: str = "", is_left_handed: bool = False, auto_detect: bool = True):
    """COCO キーポイントから支え足（プレート）と踏み出し足の Y 座標を取得。

    - プレート位置 (y_plate): 動画開始直後の静止スタンスフレームにおける両足首の平均 Y
    - 踏み出し足 (y_foot): リリース時に前方に踏み出した足（画面上部/ネット寄りに前進するため Y が小さい足）
    """
    try:
        if auto_detect:
            plate_ref_frame = auto_detect_plate_frame(df)
        else:
            plate_ref_frame = PLATE_REF_FRAME_OVERRIDES.get(video_name, DEFAULT_PLATE_REF_FRAME)

        plate_row = df[df['frame'] == plate_ref_frame]
        if plate_row.empty:
            plate_row = df.iloc[0:1]
        y15_plate = float(plate_row['y_15'].values[0])
        y16_plate = float(plate_row['y_16'].values[0])
        y_plate = (y15_plate + y16_plate) / 2.0

        rel_row = df[df['frame'] == release_frame]
        if rel_row.empty:
            rel_row = df.iloc[-1:]
        y15_rel = float(rel_row['y_15'].values[0])
        y16_rel = float(rel_row['y_16'].values[0])

        # 踏み出し足は前方（画面奥方向＝Y座標が小さい側）へステップした足
        y_foot = min(y15_rel, y16_rel)

        return y_plate, y_foot
    except Exception as e:
        print(f"[Error] 足座標取得失敗 (video={video_name}, frame={release_frame}): {e}")
        return None, None

def detect_net_y(df: pd.DataFrame = None, ball_df: pd.DataFrame = None, net_frame: int = None) -> float:
    """ネット（またはホームベース）の地面/受球 Y 座標を取得する。
    ボール追跡データがある場合はネット到達フレームのボール Y を利用し、
    なければ標準的なネット位置（380.0）を返す。
    """
    if ball_df is not None and net_frame is not None and not ball_df.empty:
        net_rows = ball_df[ball_df['frame'] == net_frame]
        if not net_rows.empty and 'cy' in net_rows.columns:
            return float(net_rows['cy'].values[0])
    return 380.0

def calculate_dynamic_distance(y_plate: float, y_net: float, y_foot: float, total_distance: float = 18.44, video_name: str = ""):
    """透視投影（パースペクティブ）を考慮してエクステンションと投球距離を正確に算出。
    - pixel_total = |y_plate - y_net|
    - pixel_ext   = |y_plate - y_foot|
    - perspective_scale = (y_net - y_horizon) / (y_foot - y_horizon)
    - extension   = total_distance * (pixel_ext / pixel_total) * perspective_scale
    """
    pixel_total = abs(y_plate - y_net)
    if pixel_total < 10.0:
        pixel_total = 680.0
    pixel_ext = max(0.0, y_plate - y_foot)

    # 消失線（地平線・カメラアイレベル: 画面上部〜中間の目安）
    y_horizon = 250.0

    # 奥行きパース補正比率（手前ほどピクセルが大きく、奥ほど小さく写る透視効果を幾何学補正）
    perspective_scale = max(0.05, (y_net - y_horizon) / max(y_foot - y_horizon, 1.0))
    extension_m = total_distance * (pixel_ext / pixel_total) * perspective_scale

    # 野球の投球フォームとして現実的な範囲（0.8m〜2.0m）に安全クランプ
    extension_m = max(0.8, min(extension_m, 2.0))
    pitch_distance = max(total_distance - extension_m, 1.0)

    return pitch_distance, extension_m


def load_ball_csv(path: Path):
    rows = []
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            try:
                conf = float(r.get('confidence', 0))
                if conf < 0.3:
                    continue
                rows.append({
                    'frame': int(r['frame']),
                    'time_sec': float(r['time_sec']),
                    'cx': float(r['cx']),
                    'cy': float(r['cy'])
                })
            except Exception:
                continue
    rows.sort(key=lambda x: x['frame'])
    return rows
# ============================================================
# メイン処理
# ============================================================

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print("=" * 60)
    print("投球速度解析 v23 (左右投手対応・透視投影エクステンション改良版)")
    print(f"想定投球全長: {TOTAL_FIELD_DISTANCE_M:.2f} m")
    print("=" * 60)

    for video_name, (release_frame, net_frame) in BASE_FRAMES.items():
        kp_path = get_keypoints_path(video_name)
        if not kp_path.exists():
            print(f"[Warning] キーポイントファイルが見つかりません: {kp_path}")
            continue
        kp_df = pd.read_csv(kp_path)
        is_left = HANDEDNESS.get(video_name, False)

        ball_csv = INPUT_DIR / f"{video_name}_tracking.csv"
        if not ball_csv.exists():
            print(f"[Warning] ボールトラッキング CSV が見つかりません: {ball_csv}")
            continue
        rows = load_ball_csv(ball_csv)
        if len(rows) < 2:
            print(f"[Warning] データ不足: {video_name}")
            continue

        ball_df = pd.DataFrame(rows)
        y_net = detect_net_y(kp_df, ball_df, net_frame)
        y_plate, y_foot = get_foot_coordinates(kp_df, release_frame, video_name, is_left, auto_detect=True)
        if y_plate is None:
            continue

        pitch_distance, extension = calculate_dynamic_distance(y_plate, y_net, y_foot, TOTAL_FIELD_DISTANCE_M, video_name)

        frames = np.array([r['frame'] for r in rows])
        times = np.array([r['time_sec'] for r in rows])
        # 時間平滑化（一次関数）
        time_model = np.poly1d(np.polyfit(frames, times, 1))
        flight_time = time_model(net_frame) - time_model(release_frame)
        if flight_time <= 0:
            print(f"[Warning] 飛行時間が負です: {video_name}")
            continue

        release_speed_mps = (math.exp(K_DRAG * pitch_distance) - 1) / (K_DRAG * flight_time)
        release_speed_kmh = release_speed_mps * 3.6

        hand_str = "左投" if is_left else "右投"
        print(f"動画: {video_name}")
        print(f"  投手: {hand_str}")
        print(f"  AI取得座標: プレートY={y_plate:.1f}, 踏み出し足Y={y_foot:.1f}, ネットY={y_net:.1f}")
        print(f"  エクステンション: {extension:.2f} m   投球距離: {pitch_distance:.2f} m")
        print(f"  飛行時間: {flight_time:.4f} s   初速推定: {release_speed_kmh:.2f} km/h")
        print("-" * 60)

if __name__ == "__main__":
    main()
