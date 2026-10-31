import streamlit as st
st.set_page_config(page_title="Outpace Baseball", page_icon="⚾", layout="wide")

import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import cv2
import os
import sys
from pathlib import Path
import datetime
import secrets
import hashlib
import json
import uuid

# --- パス設定とインポート ---
sys.path.append(str(Path(__file__).parent))
import streamlit.components.v1 as components
import pitch_speed_v23_auto_distance as pitch_mod
import pitch_logic
import aws_utils
import alexa_experience
import baseball_3d_component
import i18n
import revenuecat_sdk as rc
from history_tracker import prepare_pitch_history

# ディレクトリとファイル
ROOT_DIR = Path(__file__).resolve().parent.parent
VIDEOS_DIR = ROOT_DIR / "videos"
OUTPUT_DIR = ROOT_DIR / "output"
HISTORY_FILE = OUTPUT_DIR / "analysis_history.csv"
CONFIG_FILE = ROOT_DIR / "config.yaml"

# 言語の初期化
if "lang" not in st.session_state:
    st.session_state["lang"] = "ja"
lang = st.session_state["lang"]

# --- App User ID の解決 & localStorage 永続化同期 ---
url_uid = st.query_params.get("rc_uid")
if url_uid and url_uid.startswith("rc_user_"):
    app_user_id = url_uid
    st.session_state["app_user_id"] = app_user_id
elif "app_user_id" in st.session_state:
    app_user_id = st.session_state["app_user_id"]
else:
    app_user_id = rc.generate_anonymous_app_user_id()
    st.session_state["app_user_id"] = app_user_id

# ブラウザの localStorage ("outpace_rc_uid") と Python を自動同期 (F5・再起動後も同じIDを復元)
components.html(rc.generate_user_id_sync_script(app_user_id), height=0)

# --- RevenueCat SDK 初期化 (Purchases.configure / 永続化 App User ID) ---
rc_purchases = rc.Purchases.configure(app_user_id=app_user_id)

# --- RevenueCat Web SDK からの購入完了トリガー検証 (URLパラメータ単体改ざん防止) ---
if "rc_token" in st.query_params:
    expected_nonce = st.session_state.pop("rc_checkout_nonce", None)
    if expected_nonce and rc_purchases.verify_purchase_trigger(
        st.query_params, expected_nonce=expected_nonce, expected_user_id=app_user_id
    ):
        st.session_state["user_plan"] = "Pro"
        st.session_state["isSubscribed"] = True
        st.session_state["is_premium"] = True
        st.toast(i18n.t("paywall_purchase_success", lang, name="Pro"), icon="💎")
    for param_key in ["rc_token", "rc_nonce", "rc_trigger", "rc_action"]:
        st.query_params.pop(param_key, None)

# --- ユーザー・サブスクリプション状態管理（F5・再起動時の自動復元） ---
if "user_plan" not in st.session_state:
    st.session_state["user_plan"] = "Free"
if "isSubscribed" not in st.session_state:
    st.session_state["isSubscribed"] = False
if "is_premium" not in st.session_state:
    st.session_state["is_premium"] = False
if "show_paywall" not in st.session_state:
    st.session_state["show_paywall"] = False

# F5・再起動時: RevenueCat サーバー側 REST API で実購入状態を確認して自動復元
if not st.session_state["isSubscribed"]:
    srv_check = rc_purchases.check_server_entitlement(app_user_id)
    if srv_check.get("is_active"):
        st.session_state["user_plan"] = "Pro"
        st.session_state["isSubscribed"] = True
        st.session_state["is_premium"] = True

st.session_state["demo_user_id"] = app_user_id


# --- RevenueCat Paywall (公式 Web SDK @revenuecat/purchases-js 決済ダイアログ) ---
@st.dialog("Outpace Baseball - Pro Subscription", width="large")
def _revenuecat_paywall_dialog(app_uid: str, current_lang: str):
    header_title = i18n.t("paywall_header_title", current_lang)
    header_subtitle = i18n.t("paywall_header_subtitle", current_lang)

    # 暗号論的安全なワンタイム Nonce を発行してセッションに保持
    checkout_nonce = secrets.token_urlsafe(16)
    st.session_state["rc_checkout_nonce"] = checkout_nonce

    # RevenueCat Billing 公式 Web SDK 決済コンポーネント (iframe)
    components.html(rc_purchases.generate_web_billing_checkout_html(nonce=checkout_nonce, app_user_id=app_uid, lang=current_lang), height=240)

    # RevenueCat Web Purchase Link (ホスト型決済ページへの直接遷移ボタン)
    purchase_link_url = os.getenv("REVENUECAT_PURCHASE_LINK_URL", "https://app.revenuecat.com")
    st.link_button(
        "🌐 RevenueCat 公式決済ページを開く (Hosted Web Checkout)",
        url=purchase_link_url,
        type="secondary",
        use_container_width=True,
        help="RevenueCat がホストする公式 Web 決済ページを別タブで開きます。"
    )

    # Sandbox ステータスバッジ
    st.markdown(
        f"""<div style="background-color: #f0fdf4; border: 1px solid #86efac; border-radius: 8px; padding: 6px 12px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 4px;">
            <div style="font-size: 11px; color: #166534; font-weight: 700;">
                🧪 <b>RevenueCat Billing Sandbox</b> (Shipaton 2026 Demo)
            </div>
            <div style="font-size: 10.5px; color: #15803d; font-weight: 600;">
                Key: <code>{rc_purchases.get_masked_api_key()}</code> | Entitlement: <code>{rc_purchases.entitlement_id}</code> | isSubscribed: <b style="color: {'#16a34a' if st.session_state.get('isSubscribed') else '#dc2626'};">{st.session_state.get('isSubscribed', False)}</b>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""<div style="text-align: center; margin-bottom: 16px;">
        <span style="background: linear-gradient(135deg, #0284c7, #0ea5e9); color: white; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: bold;">REVENUECAT IN-APP PURCHASE & SUBSCRIPTION</span>
        <h3 style="margin-top: 8px; margin-bottom: 4px; color: #0f172a;">{header_title}</h3>
        <p style="color: #64748b; font-size: 13px; margin: 0;">{header_subtitle}</p>
        </div>""",
        unsafe_allow_html=True,
    )

    current_plan = st.session_state.get("user_plan", "Free")
    plans = i18n.get_subscription_plans(lang=current_lang, current_plan=current_plan)

    cols = st.columns(3)
    for col, p in zip(cols, plans):
        with col:
            items_html = "".join([f"<li>{f}</li>" for f in p["features"]])
            st.markdown(
                f"""<div style="border: 2px solid {p['border']}; border-radius: 12px; padding: 14px 12px; background: {p['bg']}; height: 320px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); margin-bottom: 10px;">
                <div style="font-size: 11px; font-weight: bold; color: #0284c7;">{p['badge']}</div>
                <h4 style="margin: 4px 0 0 0; color: #0f172a;">{p['name']}</h4>
                <div style="font-size: 22px; font-weight: 900; color: #0f172a; margin: 8px 0;">{p['price']} <span style="font-size: 11px; font-weight: normal; color: #64748b;">{p['period']}</span></div>
                <ul style="font-size: 11.5px; color: #334155; padding-left: 16px; line-height: 1.7; margin-bottom: 0;">{items_html}</ul>
                </div>""",
                unsafe_allow_html=True,
            )
            if current_plan == p["id"]:
                btn_curr_lbl = i18n.t("paywall_current_plan", current_lang)
                st.button(btn_curr_lbl, key=f"pw_btn_{p['id']}", disabled=True, use_container_width=True)
            else:
                if p["id"] == "Free":
                    btn_select_lbl = i18n.t("paywall_test_purchase", current_lang, name=p['name'])
                    if st.button(btn_select_lbl, key=f"pw_btn_{p['id']}", type="secondary", use_container_width=True):
                        st.session_state["user_plan"] = "Free"
                        st.session_state["isSubscribed"] = False
                        st.session_state["is_premium"] = False
                        st.session_state["show_paywall"] = False
                        st.toast(i18n.t("paywall_free_switched", current_lang), icon="🌱")
                        st.rerun()
                else:
                    btn_select_lbl = f"💳 {p['name']} を購入 (Sandbox)"
                    if st.button(btn_select_lbl, key=f"pw_btn_{p['id']}", type="primary", use_container_width=True):
                        st.session_state["user_plan"] = p["id"]
                        st.session_state["isSubscribed"] = True
                        st.session_state["is_premium"] = True
                        st.session_state["show_paywall"] = False
                        st.toast(i18n.t("paywall_purchase_success", current_lang, name=p['name']), icon="💎")
                        st.rerun()

    footer_note = i18n.t("paywall_footer_note", current_lang)
    st.markdown(
        f"""<div style="text-align: center; margin-top: 14px; padding-top: 10px; border-top: 1px solid #e2e8f0; font-size: 11px; color: #64748b;">
        {footer_note}
        </div>""",
        unsafe_allow_html=True,
    )


_dialog_opened_in_run = False

def show_revenuecat_paywall():
    global _dialog_opened_in_run
    if _dialog_opened_in_run:
        return
    _dialog_opened_in_run = True
    cur_lang = st.session_state.get("lang", "ja")
    cur_uid = st.session_state.get("app_user_id", app_user_id)
    _revenuecat_paywall_dialog(cur_uid, cur_lang)


# セッションステートによる Paywall ダイアログ表示制御
if st.session_state.get("show_paywall", False):
    show_revenuecat_paywall()


# カスタムCSS
st.markdown(
    """
<style>
    /* 1. 通常の白い背景上の文字はくっきりした黒文字 (#0f172a) で視認性最大化 */
    h1, h2, h3, h4, h5, h6 {
        color: #0f172a !important;
        font-weight: 800 !important;
    }
    .stApp, p, label, .stMarkdown p {
        color: #0f172a;
    }
    /* タブ・チェックボックス・キャプションの黒文字化 */
    .stTabs [data-baseweb="tab"] {
        color: #334155 !important;
        font-weight: 700 !important;
    }
    .stTabs [aria-selected="true"] {
        color: #0284c7 !important;
        font-weight: 800 !important;
    }
    .stCheckbox label span, .stRadio label span {
        color: #0f172a !important;
        font-weight: 600 !important;
    }
    .stCaption, [data-testid="stCaptionContainer"] p {
        color: #475569 !important;
        font-weight: 500 !important;
    }

    /* 2. 黒いカード（メトリクス・バイオメカニクス・ベンチマーク・アナリティクス・レーダー評価）の中はすべて鮮やかな青色文字 (#38bdf8) に強制統一 */
    .card, .card *,
    .bio-box, .bio-box *,
    div[data-testid="stMetric"], div[data-testid="stMetric"] *,
    div[data-testid="stMetricLabel"], div[data-testid="stMetricLabel"] *,
    div[data-testid="stMetricValue"], div[data-testid="stMetricValue"] *,
    div[data-testid="stMetricDelta"], div[data-testid="stMetricDelta"] * {
        color: #38bdf8 !important;
    }
    .card h1, .card h2, .card h3, .card h4, .card h5, .card h6,
    .bio-box h1, .bio-box h2, .bio-box h3, .bio-box h4 {
        color: #38bdf8 !important;
    }
    .metric-badge { background: linear-gradient(135deg, #1e3c72, #2a5298); color: #38bdf8 !important; padding: 4px 10px; border-radius: 6px; font-size: 13px; font-weight: bold; }
    .bio-box { background-color: #1e222d; padding: 14px; border-radius: 8px; border-left: 5px solid #0284c7; margin-bottom: 12px; }
    .bio-title { color: #38bdf8 !important; font-size: 13px; font-weight: 700; display: block; margin-bottom: 6px; }
    .bio-val { color: #38bdf8 !important; font-size: 22px; font-weight: bold; }
    .bio-sub { color: #38bdf8 !important; font-size: 13px; font-weight: 600; margin-left: 6px; }
    .phase-btn { margin: 2px; }

    /* Streamlit st.metric（黒いカード）の中だけ鮮やかな青色テキスト */
    div[data-testid="stMetric"] {
        background-color: #1a1e29 !important;
        padding: 8px 10px !important;
        border-radius: 8px !important;
        border: 1px solid #0284c7 !important;
        min-width: 0 !important;
        overflow: hidden !important;
    }
    div[data-testid="stMetricLabel"], div[data-testid="stMetricLabel"] * {
        white-space: normal !important;
        word-break: break-word !important;
        overflow-wrap: break-word !important;
        text-overflow: clip !important;
        font-size: clamp(10.5px, 0.9vw, 13px) !important;
        line-height: 1.25 !important;
        color: #38bdf8 !important;
        font-weight: 700 !important;
    }
    div[data-testid="stMetricValue"], div[data-testid="stMetricValue"] * {
        white-space: nowrap !important;
        overflow: visible !important;
        text-overflow: clip !important;
        font-size: clamp(15px, 1.3vw, 22px) !important;
        font-weight: 900 !important;
        color: #38bdf8 !important;
        line-height: 1.15 !important;
    }
    div[data-testid="stMetricDelta"], div[data-testid="stMetricDelta"] * {
        font-size: clamp(10px, 0.85vw, 12px) !important;
        font-weight: 700 !important;
        white-space: nowrap !important;
        color: #38bdf8 !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

col_head_t, col_head_sub = st.columns([3.5, 1.3])
with col_head_t:
    st.markdown(f"<h1 style='margin-bottom: 0px; padding-bottom: 0px; font-size: 32px; color: #0f172a !important;'>{i18n.t('app_title', lang)}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: #334155 !important; font-size: 14.5px; margin-top: 2px; font-weight: 600; letter-spacing: 0.3px;'>{i18n.t('app_subtitle', lang)}</p>", unsafe_allow_html=True)
with col_head_sub:
    cur_p = st.session_state.get("user_plan", "Free")
    p_badge = "👑 Elite" if cur_p == "Elite" else ("💎 Pro" if cur_p == "Pro" else "🌱 Free")
    st.write("")
    plan_btn_title = i18n.t("plan_badge_btn", lang, badge=p_badge)
    if st.button(plan_btn_title, key="head_paywall_btn", use_container_width=True):
        st.session_state["show_paywall"] = True
        st.rerun()


# --- 解析関数 ---
def run_analysis(video, left_handed, release_frame=None, net_frame=None, pitcher_height_m=1.75, pitch_type="fastball"):
    video_file = VIDEOS_DIR / f"{video}.mp4"
    cap_info = cv2.VideoCapture(str(video_file))
    video_fps = cap_info.get(cv2.CAP_PROP_FPS) or 30.0
    video_w = int(cap_info.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_h = int(cap_info.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap_info.release()

    if release_frame is None or net_frame is None:
        auto_frames = st.session_state.get(f"auto_track_frames_{video}")
        if auto_frames is not None:
            release_frame, net_frame = auto_frames
        elif video in pitch_mod.BASE_FRAMES:
            release_frame, net_frame = pitch_mod.BASE_FRAMES[video]
        else:
            release_frame = 50
            net_frame = 70

    kp_df = pitch_logic.get_keypoints_for_video(video, release_frame=release_frame)

    ball_csv = pitch_mod.INPUT_DIR / f"{video}_tracking.csv"
    if ball_csv.exists():
        raw_ball_df = pd.read_csv(ball_csv)
        rows = pitch_mod.load_ball_csv(ball_csv)
    else:
        raw_ball_df = None
        rows = []

    ball_df = raw_ball_df if raw_ball_df is not None and not raw_ball_df.empty else (pd.DataFrame(rows) if len(rows) > 0 else None)

    if ball_df is not None and len(ball_df) >= 2 and len(rows) >= 2:
        frames = np.array([r["frame"] for r in rows])
        times = np.array([r["time_sec"] for r in rows])
        time_model = np.poly1d(np.polyfit(frames, times, 1))
        flight_time = max(0.01, float(time_model(net_frame) - time_model(release_frame)))
    else:
        flight_time = max(0.01, (net_frame - release_frame) / video_fps)

    # 映像画角に応じた距離計算（横長 MLB 中継画角 vs 縦長 スマホブルペン画角）
    is_landscape_broadcast = video_w > video_h
    if is_landscape_broadcast:
        # MLB 規格グラウンド中継視点（本塁間 18.44m, 平均エクステンション 1.95m）
        extension = 1.95
        pitch_distance = max(10.0, pitch_mod.TOTAL_FIELD_DISTANCE_M - extension)
    else:
        # スマホ撮影ブルペンネット視点（透視投影幾何学補正）
        y_net = pitch_mod.detect_net_y(kp_df, ball_df, net_frame)
        y_plate, y_foot = pitch_mod.get_foot_coordinates(
            kp_df, release_frame, video, is_left_handed=left_handed, auto_detect=True
        )
        pitch_distance, extension = pitch_mod.calculate_dynamic_distance(
            y_plate, y_net, y_foot, pitch_mod.TOTAL_FIELD_DISTANCE_M, video
        )

    speed_kmh = (
        (np.exp(pitch_mod.K_DRAG * pitch_distance) - 1)
        / (pitch_mod.K_DRAG * flight_time)
    ) * 3.6

    rel_row = kp_df[kp_df["frame"] == release_frame]
    rel_kp = rel_row.iloc[0] if not rel_row.empty else kp_df.iloc[-1]
    biomechanics = pitch_logic.extract_pitch_biomechanics(
        rel_kp,
        is_left_handed=left_handed,
        extension_m=extension,
        pitcher_height_m=pitcher_height_m,
        kp_df=kp_df,
        release_frame=release_frame,
    )
    phases = pitch_logic.detect_pitch_phases(
        kp_df, release_frame, is_left_handed=left_handed
    )

    # 空気力学モデルによる回転数・ジャイロ角度・変化量（IVB / HB）逆算推計
    spin_data = pitch_logic.calculate_spin_and_break(
        speed_kmh=speed_kmh,
        flight_time=flight_time,
        extension_m=extension,
        pitcher_height_m=pitcher_height_m,
        is_left_handed=left_handed,
        ball_df=ball_df,
        net_frame=net_frame,
        pitch_type=pitch_type,
    )

    return {
        "speed_kmh": speed_kmh,
        "extension": extension,
        "pitch_distance": pitch_distance,
        "flight_time": flight_time,
        "kp_df": kp_df,
        "ball_df": ball_df,
        "biomechanics": biomechanics,
        "phases": phases,
        "release_frame": release_frame,
        "net_frame": net_frame,
        "video": video,
        "video_width": video_w,
        "video_height": video_h,
        "left_handed": left_handed,
        "is_left_handed": left_handed,
        "video_fps": video_fps,
        "pitcher_height_m": pitcher_height_m,
        "spin_data": spin_data,
        "pitch_type": pitch_type,
    }


def build_coach_metrics(res, diagnosis):
    """Create a compact, identifying-data-free payload from computed pitch results."""
    def finite_number(value, decimals):
        if value is None:
            return None
        try:
            number = float(value)
        except (TypeError, ValueError):
            return None
        return round(number, decimals) if np.isfinite(number) else None

    biomechanics = res.get("biomechanics") or {}
    spin_data = res.get("spin_data") or {}
    ball_df = res.get("ball_df")
    trajectory_summary = {"tracked_observations": 0}
    if (
        isinstance(ball_df, pd.DataFrame)
        and not ball_df.empty
        and {"frame", "cx", "cy"}.issubset(ball_df.columns)
    ):
        track = (
            ball_df[["frame", "cx", "cy"]]
            .apply(pd.to_numeric, errors="coerce")
            .dropna()
            .sort_values("frame")
        )
        trajectory_summary["tracked_observations"] = int(len(track))
        if not track.empty:
            first = track.iloc[0]
            last = track.iloc[-1]
            trajectory_summary.update(
                {
                    "first_frame": int(first["frame"]),
                    "last_frame": int(last["frame"]),
                    "image_plane_displacement_px": {
                        "x": finite_number(last["cx"] - first["cx"], 2),
                        "y": finite_number(last["cy"] - first["cy"], 2),
                    },
                }
            )
    return {
        "pitch": {
            "pitch_type": res.get("pitch_type"),
            "handedness": "left" if res.get("left_handed") else "right",
            "speed_kmh": finite_number(res["speed_kmh"], 2),
            "flight_time_s": finite_number(res["flight_time"], 4),
            "extension_m": finite_number(res["extension"], 2),
            "pitch_distance_m": finite_number(res["pitch_distance"], 2),
        },
        "biomechanics": {
            key: (
                finite_number(value, 2)
                if isinstance(value, (int, float, np.number))
                else value
            )
            for key, value in biomechanics.items()
            if value is not None
        },
        "spin_and_break_estimates": {
            key: (
                finite_number(value, 2)
                if isinstance(value, (int, float, np.number))
                else value
            )
            for key, value in spin_data.items()
            if value is not None
        },
        "release_and_tracking": {
            "release_frame": int(res["release_frame"]),
            "net_frame": int(res["net_frame"]),
            "trajectory_summary": trajectory_summary,
        },
        "existing_rule_based_diagnosis": {
            "grade": diagnosis.get("grade"),
            "score": diagnosis.get("score"),
            "strengths": list(diagnosis.get("strengths", [])),
            "improvements": list(diagnosis.get("improvements", [])),
            "perceived_speed_kmh": finite_number(
                diagnosis.get("perceived_speed_kmh"), 2
            ),
        },
    }


def build_alexa_pitch_context(res, diagnosis):
    """Build a small, video-free context for the Alexa+ text experience simulation."""
    coach_metrics = build_coach_metrics(res, diagnosis)
    context = {
        "current_pitch": coach_metrics["pitch"],
        "current_biomechanics": {
            key: coach_metrics["biomechanics"].get(key)
            for key in ("elbow_angle", "forearm_slot", "lead_knee_angle", "stride_pct")
            if coach_metrics["biomechanics"].get(key) is not None
        },
        "current_spin_estimates": {
            key: coach_metrics["spin_and_break_estimates"].get(key)
            for key in ("spin_rate_rpm", "gyro_angle_deg", "ivb_cm", "hb_cm")
            if coach_metrics["spin_and_break_estimates"].get(key) is not None
        },
        "current_rule_based_diagnosis": coach_metrics["existing_rule_based_diagnosis"],
    }
    return alexa_experience.add_previous_pitch_from_history(
        context, res.get("video"), HISTORY_FILE
    )


def render_pitch_history(tab_history, current_lang, current_speed_unit, current_dist_unit):
    with tab_history:
        st.subheader(i18n.t("history_header", current_lang))

        if not HISTORY_FILE.exists():
            st.info("No pitch history yet. Run an analysis and save it to start tracking progress.")
            return

        try:
            history = pd.read_csv(HISTORY_FILE, on_bad_lines="skip")
            history = prepare_pitch_history(history)
        except (OSError, UnicodeError, pd.errors.ParserError, ValueError) as error:
            st.error(f"Could not load pitch history: {error}")
            return

        if history.empty:
            st.info("No history records yet.")
            return

        speed_values = history["speed"].dropna().map(
            lambda value: i18n.convert_speed(value, current_speed_unit)
        )
        extension_values = history["extension"].dropna().map(
            lambda value: i18n.convert_distance(value, current_dist_unit)
        )

        k1, k2, k3, k4 = st.columns(4)
        k1.metric(i18n.t("total_pitches", current_lang), f"{len(history)}")
        k2.metric(
            i18n.t("max_speed", current_lang),
            f"{speed_values.max():.1f} {current_speed_unit}" if not speed_values.empty else "—",
        )
        k3.metric(
            i18n.t("avg_speed", current_lang),
            f"{speed_values.mean():.1f} {current_speed_unit}" if not speed_values.empty else "—",
        )
        k4.metric(
            i18n.t("avg_extension", current_lang),
            f"{extension_values.mean():.2f} {current_dist_unit}" if not extension_values.empty else "—",
        )

        plot_history = history.dropna(subset=["timestamp", "speed"]).sort_values("timestamp")
        if not plot_history.empty:
            df_plot = plot_history.copy()
            df_plot["plot_speed"] = df_plot["speed"].map(
                lambda value: i18n.convert_speed(value, current_speed_unit)
            )
            st.plotly_chart(
                px.line(
                    df_plot,
                    x="timestamp",
                    y="plot_speed",
                    markers=True,
                    title=f"{i18n.t('chart_speed_title', current_lang)} ({current_speed_unit})",
                    labels={
                        "timestamp": i18n.t("chart_time_label", current_lang),
                        "plot_speed": f"Speed ({current_speed_unit})",
                    },
                ),
                width="stretch",
                key="history_speed_progression_chart",
            )
        else:
            st.info("No valid timestamps and pitch speeds are available to draw the progression chart.")

        st.markdown(f"#### {i18n.t('history_records', current_lang)}")
        df_display = history.copy()
        df_display[f"speed ({current_speed_unit})"] = history["speed"].map(
            lambda value: i18n.convert_speed(value, current_speed_unit)
            if pd.notna(value)
            else None
        ).round(1)
        df_display[f"extension ({current_dist_unit})"] = history["extension"].map(
            lambda value: i18n.convert_distance(value, current_dist_unit)
            if pd.notna(value)
            else None
        ).round(2)
        st.dataframe(df_display.iloc[::-1], width="stretch", hide_index=True)

        st.markdown("---")
        exp_c1, exp_c2, exp_c3 = st.columns([1.5, 1.5, 1.2])
        with exp_c1:
            csv_bytes = pitch_logic.export_history_bytes(history, "csv")
            st.download_button(
                i18n.t("export_csv", current_lang),
                data=csv_bytes,
                file_name=f"pitch_history_{datetime.date.today()}.csv",
                mime="text/csv",
                width="stretch",
            )
        with exp_c2:
            xlsx_bytes = pitch_logic.export_history_bytes(history, "excel")
            st.download_button(
                i18n.t("export_excel", current_lang),
                data=xlsx_bytes,
                file_name=f"pitch_history_{datetime.date.today()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                width="stretch",
            )
        with exp_c3:
            if st.button(i18n.t("clear_history", current_lang), width="stretch"):
                HISTORY_FILE.unlink(missing_ok=True)
                st.rerun()


# --- 動画リスト取得 ---
# 実在する mp4 ファイルのみをリストアップ (ローカルの既存動画はそのまま含まれる)
available_videos = [
    k for k in pitch_mod.BASE_FRAMES.keys()
    if (VIDEOS_DIR / f"{k}.mp4").exists()
]
for p in VIDEOS_DIR.glob("*.mp4"):
    if p.stem not in available_videos and not p.stem.startswith("temp_") and not p.stem.startswith("skeleton_"):
        available_videos.append(p.stem)

# --- UI サイドバー ---
with st.sidebar:
    # 💎 サブスクリプションプラン (RevenueCat)
    sb_plan_title = "💎 プラン管理 (RevenueCat)" if lang == "ja" else "💎 Subscription (RevenueCat)"
    st.subheader(sb_plan_title)
    cur_p = st.session_state.get("user_plan", "Free")
    badge_bg = "#f59e0b" if cur_p == "Elite" else ("#0284c7" if cur_p == "Pro" else "#64748b")
    cur_lbl = "現在のプラン" if lang == "ja" else "Current Plan"
    is_sub = st.session_state.get("isSubscribed", False)
    sub_badge = "✅ isSubscribed = True" if is_sub else "⚪ isSubscribed = False"
    sub_color = "#16a34a" if is_sub else "#dc2626"
    st.markdown(
        f"""<div style="background-color: #ffffff; border: 2px solid {badge_bg}; border-radius: 10px; padding: 10px 12px; margin-bottom: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.05);">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 12px; color: #0f172a; font-weight: 800;">{cur_lbl}</span>
            <span style="background: {badge_bg}; color: white; padding: 2px 10px; border-radius: 12px; font-size: 11px; font-weight: bold;">{cur_p} Plan</span>
        </div>
        <div style="font-size: 11px; color: {sub_color}; font-weight: 700; margin-top: 4px;">{sub_badge}</div>
        <div style="font-size: 10.5px; color: #334155; margin-top: 3px;">RC User: <code style="color: #0f172a; background: #f1f5f9; padding: 1px 5px; border-radius: 4px; font-weight: bold;">{st.session_state.get('demo_user_id', 'rc_anon_user')}</code></div>
        </div>""",
        unsafe_allow_html=True,
    )

    btn_paywall_lbl = i18n.t("sb_paywall_view_btn", lang)
    if st.button(btn_paywall_lbl, use_container_width=True, key="sb_paywall_btn"):
        st.session_state["show_paywall"] = True
        st.rerun()

    # 価格表記の通貨切り替え (JPY: ¥ / Other: $)
    is_jpy = (lang == "ja")
    pro_opt_lbl = "Pro (¥1,980/月)" if is_jpy else "Pro ($14.99/mo)"
    elite_opt_lbl = "Elite (¥17,800/年)" if is_jpy else "Elite ($139.99/yr)"
    demo_plan_opts = ["Free", pro_opt_lbl, elite_opt_lbl]
    if "prev_demo_plan" not in st.session_state:
        st.session_state["prev_demo_plan"] = cur_p

    cur_idx = 0 if cur_p == "Free" else (1 if cur_p == "Pro" else 2)
    demo_select_lbl = i18n.t("demo_switch_plan_label", lang)
    new_demo_sel = st.selectbox(
        demo_select_lbl,
        options=demo_plan_opts,
        index=cur_idx,
        help=i18n.t("demo_switch_plan_help", lang),
        key="sidebar_demo_plan_select",
    )
    new_plan_key = "Free" if "Free" in new_demo_sel else ("Pro" if "Pro" in new_demo_sel else "Elite")

    # ユーザーがセレクトボックスを手動で変更した場合のみ切り替え処理を実行
    if new_plan_key != st.session_state.get("prev_demo_plan"):
        st.session_state["prev_demo_plan"] = new_plan_key
        if new_plan_key == "Free":
            st.session_state["user_plan"] = "Free"
            st.session_state["isSubscribed"] = False
            st.session_state["is_premium"] = False
            st.session_state["show_paywall"] = False
            st.toast(i18n.t("paywall_free_switched", lang), icon="🌱")
            st.rerun()
        else:
            st.session_state["show_paywall"] = True
            st.rerun()
    else:
        st.session_state["prev_demo_plan"] = cur_p

    st.markdown("---")
    st.subheader(i18n.t("lang_select", lang))
    lang_codes = list(i18n.LANGUAGES.keys())
    selected_lang = st.selectbox(
        "Language",
        options=lang_codes,
        index=lang_codes.index(st.session_state["lang"]),
        format_func=lambda c: i18n.LANGUAGES[c],
        label_visibility="collapsed",
        key="selected_lang_widget",
    )
    if selected_lang != st.session_state["lang"]:
        st.session_state["lang"] = selected_lang
        st.rerun()
    lang = st.session_state["lang"]

    st.markdown("---")
    st.subheader(i18n.t("unit_settings", lang))
    u_c1, u_c2 = st.columns(2)
    speed_unit = u_c1.radio(
        i18n.t("speed_unit_label", lang),
        ["km/h", "mph"],
        index=0,
        horizontal=True,
        key="unit_speed",
    )
    dist_unit = u_c2.radio(
        i18n.t("dist_unit_label", lang),
        ["m", "ft"],
        index=0,
        horizontal=True,
        key="unit_dist",
    )

    st.markdown("---")
    st.header(i18n.t("sidebar_settings", lang))
    if available_videos:
        selected_video = st.selectbox(i18n.t("select_video", lang), available_videos)
    else:
        selected_video = None

    is_left_default = pitch_mod.HANDEDNESS.get(selected_video, True) if selected_video else True
    handed_labels = [i18n.t("right_pitcher", lang), i18n.t("left_pitcher", lang)]
    left_handed = (
        st.radio(i18n.t("handedness", lang), handed_labels, index=1 if is_left_default else 0)
        == handed_labels[1]
    )

    # 投手の身長設定 & AI自動推定 (フィート/メートル連動)
    st.markdown("---")
    st.subheader(i18n.t("height_settings", lang))

    # 動画解像度を取得してAI推定身長を計算
    v_path = (VIDEOS_DIR / f"{selected_video}.mp4") if selected_video else None
    vw, vh = 720, 1280
    if v_path and v_path.exists():
        cap_chk = cv2.VideoCapture(str(v_path))
        vw = int(cap_chk.get(cv2.CAP_PROP_FRAME_WIDTH) or 720)
        vh = int(cap_chk.get(cv2.CAP_PROP_FRAME_HEIGHT) or 1280)
        cap_chk.release()

    ai_h = pitch_logic.estimate_pitcher_height(selected_video or "pitch", video_w=vw, video_h=vh)
    height_key = f"pitcher_height_{selected_video or 'default'}"
    if height_key not in st.session_state:
        st.session_state[height_key] = int(ai_h)

    # AI推定身長の表示（単位系に応じたフィート・インチ/cm両表記）
    formatted_ai_h = i18n.format_height(ai_h, dist_unit)
    st.caption(i18n.t("ai_est_height", lang, height=formatted_ai_h))

    st.write(f"**📌 {i18n.t('preset_title', lang)}**")

    # 文字をボタンの外側に配置（文字の途切れを完全に防ぐレイアウト）
    presets = [
        (170, "height_preset_hs", "🎓"),
        (175, "height_preset_adult", "👤"),
        (182, "height_preset_pro", "⚾"),
        (191, "height_preset_mlb", "🇺🇸"),
    ]
    cur_val = st.session_state.get(height_key, int(ai_h))

    for h_val, role_key, icon in presets:
        c_txt, c_btn = st.columns([2.6, 1.4])
        is_active = (cur_val == h_val)
        with c_txt:
            h_str = i18n.format_height(h_val, dist_unit)
            active_color = "#0284c7" if is_active else "#0f172a"
            st.markdown(
                f"<div style='font-size: 13px; line-height: 1.35; padding: 3px 0; color: #0f172a;'>"
                f"{icon} <b>{i18n.t(role_key, lang)}</b><br/>"
                f"<span style='color: {active_color}; font-weight: bold;'>{h_str}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )
        with c_btn:
            btn_txt = i18n.t("btn_selected", lang) if is_active else i18n.t("btn_select", lang)
            btn_type = "primary" if is_active else "secondary"
            if st.button(btn_txt, key=f"btn_{h_val}_{selected_video}", width="stretch", type=btn_type):
                st.session_state[height_key] = h_val
                st.rerun()

    # スライダー見出しに現在のフィート・インチ/cm両表記をリアルタイム表示
    formatted_cur = i18n.format_height(cur_val, dist_unit)
    st.markdown(
        f"<div style='margin-top: 10px; margin-bottom: 2px; font-size: 13px; font-weight: bold; color: #0f172a;'>"
        f"{i18n.t('height_label', lang)}: <span style='color: #0284c7;'>{formatted_cur}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )

    pitcher_height_cm = st.slider(
        i18n.t("height_label", lang),
        min_value=150,
        max_value=215,
        value=st.session_state[height_key],
        step=1,
        key=f"slider_h_{selected_video}",
        label_visibility="collapsed",
    )
    st.session_state[height_key] = pitcher_height_cm
    pitcher_height_m = max(1.2, pitcher_height_cm / 100.0)

    # 球種（ピッチタイプ）選択
    st.markdown("---")
    pitch_type_keys = list(pitch_logic.PITCH_BENCHMARKS.keys())
    selected_pitch_type = st.selectbox(
        i18n.t("pitch_type_label", lang),
        pitch_type_keys,
        index=0,
        format_func=lambda k: i18n.t(pitch_logic.PITCH_BENCHMARKS[k]["name_key"], lang),
        key=f"pitch_type_select_{selected_video}",
    )

    run_btn = st.button(i18n.t("run_analysis", lang), type="primary", width="stretch", disabled=(not selected_video))

    # AI自動弾道解析ボタン
    auto_track_btn = st.button(i18n.t("auto_track_btn", lang), type="secondary", width="stretch", key=f"auto_btn_{selected_video}", disabled=(not selected_video))
    if auto_track_btn:
        with st.spinner(i18n.t("analyzing_spinner", lang)):
            try:
                rel_f, net_f, b_df = pitch_logic.auto_track_new_video(selected_video, is_left_handed=left_handed)
                st.session_state[f"auto_track_frames_{selected_video}"] = (rel_f, net_f)
                st.success("✅ AI自動トラッキングが完了しました！")
                st.session_state.pop("analyzed_result", None)
                st.rerun()
            except Exception as e:
                st.error(f"Auto-tracking error: {e}")

    st.markdown("---")
    st.subheader(i18n.t("upload_header", lang))
    st.caption("📥 **Sample Videos**: [Sample 1 (102km/h)](https://github.com/hirokuwa821/Outpose-Baseball/releases/download/sample-videos/pitch_102_1.mp4) | [Sample 2 (98km/h)](https://github.com/hirokuwa821/Outpose-Baseball/releases/download/sample-videos/pitch_98_1.mp4) | [📦 Release Page](https://github.com/hirokuwa821/Outpose-Baseball/releases/tag/sample-videos)")
    uploaded_file = st.file_uploader(i18n.t("upload_label", lang), type=["mp4", "mov"])
    if not aws_utils.is_s3_configured():
        st.info("Amazon S3 is not configured. Uploaded videos remain available locally.")
    if uploaded_file is not None:
        if st.button(i18n.t("upload_btn", lang), width="stretch"):
            with st.spinner("Saving video..."):
                new_name = pitch_logic.save_uploaded_video(uploaded_file)
                s3_upload_result = aws_utils.upload_file_to_s3(
                    VIDEOS_DIR / f"{new_name}.mp4",
                    f"videos/{new_name}.mp4",
                )
                st.session_state["last_video_s3_upload"] = {
                    "success": s3_upload_result.success,
                    "message": s3_upload_result.message,
                    "object_key": s3_upload_result.object_key,
                }
                st.success(i18n.t("upload_success", lang, name=new_name))
                # 自動トラッキングをバックグラウンド実行
                try:
                    rel_f, net_f, _ = pitch_logic.auto_track_new_video(
                        new_name, is_left_handed=left_handed
                    )
                    st.session_state[f"auto_track_frames_{new_name}"] = (rel_f, net_f)
                    st.session_state.pop("upload_tracking_error", None)
                except Exception as e:
                    st.session_state["upload_tracking_error"] = (
                        f"Ball tracking/automatic analysis failed for '{new_name}'. "
                        f"The uploaded video was saved locally and remains in the video list. "
                        f"Reason: {e}"
                    )
                st.session_state.pop("analyzed_result", None)
                st.rerun()

    tracking_error = st.session_state.pop("upload_tracking_error", None)
    if tracking_error:
        st.error(tracking_error)

    upload_status = st.session_state.get("last_video_s3_upload")
    if upload_status:
        if upload_status["success"]:
            bucket = aws_utils.get_s3_bucket()
            st.success(f"Private S3 object: s3://{bucket}/{upload_status['object_key']}")
        else:
            st.info(upload_status["message"])

# 初回またはボタン押下または動画切り替えで解析
has_valid_video = bool(selected_video and (VIDEOS_DIR / f"{selected_video}.mp4").exists())
should_run = (
    has_valid_video
    and (
        run_btn
        or "analyzed_result" not in st.session_state
        or st.session_state.get("analyzed_result") is None
        or st.session_state["analyzed_result"].get("video") != selected_video
        or st.session_state["analyzed_result"].get("left_handed") != left_handed
        or st.session_state["analyzed_result"].get("pitch_type") != selected_pitch_type
    )
)
if should_run:
    with st.spinner(i18n.t("analyzing_spinner", lang)):
        res = run_analysis(selected_video, left_handed, pitcher_height_m=pitcher_height_m, pitch_type=selected_pitch_type)
        skel_video_path = pitch_logic.create_skeleton_video(selected_video, res["kp_df"])
        res["skel_video_path"] = skel_video_path
        st.session_state["analyzed_result"] = res

        # 履歴保存
        if run_btn:
            sp_res = res.get("spin_data", {})
            data = {
                "timestamp": [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                "video": [selected_video],
                "pitch_type": [selected_pitch_type],
                "speed": [res["speed_kmh"]],
                "extension": [res["extension"]],
                "distance": [res["pitch_distance"]],
                "spin_rate": [sp_res.get("spin_rate_rpm", 0)],
                "gyro_angle": [sp_res.get("gyro_angle_deg", 0.0)],
                "ivb_cm": [sp_res.get("ivb_cm", 0.0)],
                "hb_cm": [sp_res.get("hb_cm", 0.0)],
            }
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            pd.DataFrame(data).to_csv(
                HISTORY_FILE, mode="a", header=not HISTORY_FILE.exists(), index=False
            )

# --- メインタブ構成 ---
tab_main, tab_compare, tab_history, tab_alexa = st.tabs([
    i18n.t("tab_single", lang),
    i18n.t("tab_compare", lang),
    i18n.t("tab_history", lang),
    "Alexa+ Experience Simulation",
])


if "analyzed_result" in st.session_state and st.session_state["analyzed_result"]:
    res = st.session_state["analyzed_result"]
    video = res["video"]
    speed = res["speed_kmh"]
    ext = res["extension"]
    dist = res["pitch_distance"]
    ftime = res["flight_time"]
    kp_df = res["kp_df"]
    ball_df = res["ball_df"]
    bio = res["biomechanics"]
    phases = res["phases"]
    release_frame = res["release_frame"]
    net_frame = res["net_frame"]
    skel_video_path = res.get("skel_video_path")
    video_fps = res.get("video_fps", 30.0)


    # 身長設定の動的反映（スライダー操作時に即時再計算）
    pitcher_height_m = max(1.2, pitcher_height_cm / 100.0)
    bio["stride_pct"] = (ext / pitcher_height_m * 100.0)
    bio["pitcher_height_m"] = pitcher_height_m

    # 単位換算
    disp_speed = i18n.convert_speed(speed, speed_unit)
    disp_ext = i18n.convert_distance(ext, dist_unit)
    disp_dist = i18n.convert_distance(dist, dist_unit)

    with tab_main:
        col_left, col_right = st.columns([1.1, 1.6])

        with col_left:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader(f"{i18n.t('velocity_score', lang)} ({speed_unit})")

            # --- ウインドウサイズ伸縮でも絶対に横にズレない MLB Statcast風 球速バッジ ---
            velo_badge_txt = i18n.t("pitch_velocity_badge", lang)
            st.markdown(
                f"""<div style="background: linear-gradient(180deg, #1e2430 0%, #151821 100%); border-radius: 10px; padding: 12px 16px; text-align: center; border: 1px solid #334155; margin-bottom: 4px; box-shadow: inset 0 1px 0 rgba(255,255,255,0.06);">
                    <div style="font-size: 11px; font-weight: 800; color: #ffffff; letter-spacing: 1.2px; text-transform: uppercase;">{velo_badge_txt}</div>
                    <div style="font-size: clamp(36px, 3.8vw, 50px); font-weight: 900; color: #ff4b4b; line-height: 1.1; font-family: 'Arial Black', -apple-system, sans-serif;">
                        {disp_speed:.1f} <span style="font-size: clamp(16px, 1.6vw, 22px); color: #ffffff; font-weight: 700;">{speed_unit}</span>
                    </div>
                </div>""",
                unsafe_allow_html=True,
            )

            if speed_unit == "mph":
                gauge_range = [40, 85] if disp_speed < 80 else [40, 105]
                gauge_steps = [
                    {"range": [40, 55], "color": "#2c3e50"},
                    {"range": [55, 70], "color": "#34495e"},
                    {"range": [70, 85], "color": "#1abc9c"},
                ]
            else:
                gauge_range = [70, 130] if disp_speed < 125 else [70, 165]
                gauge_steps = [
                    {"range": [70, 90], "color": "#2c3e50"},
                    {"range": [90, 110], "color": "#34495e"},
                    {"range": [110, 130], "color": "#1abc9c"},
                ]

            # mode="gauge" にすることで数値の横ズレを物理的に完全排除し、美しい円弧スケールを同期
            fig = go.Figure(
                go.Indicator(
                    mode="gauge",
                    value=disp_speed,
                    domain={"x": [0.05, 0.95], "y": [0.05, 0.95]},
                    gauge={
                        "axis": {"range": gauge_range, "tickcolor": "#ffffff", "tickfont": {"size": 10, "color": "#ffffff"}},
                        "bar": {"color": "#ff4b4b", "thickness": 0.28},
                        "bgcolor": "#1e222d",
                        "steps": gauge_steps,
                    },
                )
            )
            fig.update_layout(height=125, margin=dict(l=15, r=15, t=10, b=8), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, width="stretch", key="gauge_velocity_chart")

            m1, m2, m3 = st.columns(3)
            m1.metric(f"{i18n.t('extension', lang)} ({dist_unit})", f"{disp_ext:.2f} {dist_unit}")
            m2.metric(f"{i18n.t('pitch_distance', lang)} ({dist_unit})", f"{disp_dist:.2f} {dist_unit}")
            m3.metric(i18n.t("flight_time", lang), f"{ftime:.3f} s")

            # --- 球種別ベンチマーク比較カード ---
            st.markdown("---")
            st.subheader(i18n.t("benchmark_header", lang))
            bench = pitch_logic.PITCH_BENCHMARKS.get(selected_pitch_type, pitch_logic.PITCH_BENCHMARKS["fastball"])
            mlb_s = i18n.convert_speed(bench["mlb_speed_kmh"], speed_unit)
            npb_s = i18n.convert_speed(bench["npb_speed_kmh"], speed_unit)
            amat_s = i18n.convert_speed(bench["amateur_speed_kmh"], speed_unit)

            diff_mlb = disp_speed - mlb_s
            diff_amat = disp_speed - amat_s

            bc1, bc2, bc3 = st.columns(3)
            bc1.metric(i18n.t("mlb_benchmark", lang), f"{mlb_s:.1f} {speed_unit}", f"{diff_mlb:+.1f} {speed_unit}")
            bc2.metric(i18n.t("npb_benchmark", lang), f"{npb_s:.1f} {speed_unit}")
            bc3.metric(i18n.t("amateur_benchmark", lang), f"{amat_s:.1f} {speed_unit}", f"{diff_amat:+.1f} {speed_unit}")

            pt_name = i18n.t(bench["name_key"], lang)
            b_detail = i18n.get_benchmark_details(selected_pitch_type, lang)
            ideal_slot_lbl = i18n.t("ideal_slot_label", lang)
            st.markdown(
                f"""<div style="background-color: #1a1e29; border-radius: 8px; padding: 10px 12px; border-left: 3px solid #0284c7; border-top: 1px solid #0284c7; border-right: 1px solid #0284c7; border-bottom: 1px solid #0284c7; margin-top: 10px; font-size: 12px; color: #38bdf8; line-height: 1.5;">
                📌 <b>{pt_name}</b>: {b_detail['movement_desc']}<br><span style="color: #38bdf8;">{ideal_slot_lbl}: <code style="color: #38bdf8; background: #0f172a; padding: 2px 6px; border-radius: 4px; font-weight: bold;">{b_detail['ideal_slot']}</code></span>
                </div>""",
                unsafe_allow_html=True,
            )

            st.markdown("---")
            st.subheader(i18n.t("biomechanics_header", lang))

            b1, b2 = st.columns(2)
            with b1:
                st.markdown(
                    f"""<div class="bio-box">
                    <span class="bio-title">{i18n.t('elbow_angle', lang)}</span>
                    <span class="bio-val">{bio.get('elbow_angle', 0):.1f}°</span>
                    </div>""",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"""<div class="bio-box" style="border-left-color: #3498db;">
                    <span class="bio-title">{i18n.t('knee_angle', lang)}</span>
                    <span class="bio-val">{bio.get('lead_knee_angle', 0):.1f}°</span>
                    </div>""",
                    unsafe_allow_html=True,
                )
            with b2:
                loc_slot = i18n.get_slot_name(bio.get('slot_name', '-'), lang)
                st.markdown(
                    f"""<div class="bio-box" style="border-left-color: #f1c40f;">
                    <span class="bio-title">{i18n.t('arm_slot', lang)}</span>
                    <span class="bio-val">{bio.get('forearm_slot', 0):.1f}°</span>
                    <span class="bio-sub">({loc_slot})</span>
                    </div>""",
                    unsafe_allow_html=True,
                )
                stride_txt = f"{bio.get('stride_pct', 0):.1f}%" if bio.get('stride_pct') else "-"
                st.markdown(
                    f"""<div class="bio-box" style="border-left-color: #2ecc71;">
                    <span class="bio-title">{i18n.t('stride_ratio', lang)}</span>
                    <span class="bio-val">{stride_txt}</span>
                    </div>""",
                    unsafe_allow_html=True,
                )
            # --- 🌀 球質・回転アナリティクス (Spin Rate / Gyro / Break) ---
            st.markdown("---")
            st.subheader(i18n.t("spin_analytics_header", lang))

            spin = res.get("spin_data") or pitch_logic.calculate_spin_and_break(
                speed, ftime, ext, pitcher_height_m, left_handed, ball_df, net_frame, pitch_type=selected_pitch_type
            )

            # 単位換算: 変化量 (cm または in)
            if dist_unit == "ft":
                disp_ivb = spin["ivb_cm"] / 2.54
                disp_hb = spin["hb_cm"] / 2.54
                break_unit = "in"
            else:
                disp_ivb = spin["ivb_cm"]
                disp_hb = spin["hb_cm"]
                break_unit = "cm"

            # 1. 上段: 6大メトリクスをゆったり3列×2行で配置（文字途切れを完全防止）
            m_c1, m_c2, m_c3 = st.columns(3)
            bu_desc = f"{spin['bauer_units']:.1f} BU (球速比)" if lang == "ja" else f"{spin['bauer_units']:.1f} BU"
            m_c1.metric(
                i18n.t("spin_rate_label", lang),
                f"{spin['spin_rate_rpm']:,} rpm",
                delta=bu_desc,
                delta_color="off",
                help=i18n.t("spin_rate_help", lang),
            )
            m_c2.metric(
                i18n.t("spin_eff_label", lang),
                f"{spin['active_spin_pct']:.1f} %",
                help=i18n.t("spin_eff_help", lang),
            )
            m_c3.metric(
                i18n.t("gyro_angle_label", lang),
                f"{spin['gyro_angle_deg']:.1f}°",
                help=i18n.t("gyro_angle_help", lang),
            )

            m_c4, m_c5, m_c6 = st.columns(3)
            m_c4.metric(
                i18n.t("spin_axis_label", lang),
                f"{spin['spin_axis']}",
            )
            m_c5.metric(
                i18n.t("ivb_label", lang),
                f"{disp_ivb:+.1f} {break_unit}",
                help=i18n.t("ivb_help", lang),
            )
            m_c6.metric(
                i18n.t("hb_label", lang),
                f"{disp_hb:+.1f} {break_unit}",
                help=i18n.t("hb_help", lang),
            )

            st.markdown("---")

            # 2. 下段: 左側に「3D回転野球ボール」、右側に「球種別変化量マップ (Movement Plot)」を配置！
            vis_c1, vis_c2 = st.columns(2)
            with vis_c1:
                st.caption(f"**{i18n.t('spin_clock_title', lang)}**")
                spin_3d_html = baseball_3d_component.generate_3d_spinning_baseball_html(
                    spin_axis_str=spin["spin_axis"],
                    spin_rate_rpm=spin["spin_rate_rpm"],
                    active_spin_pct=spin["active_spin_pct"],
                    gyro_angle_deg=spin["gyro_angle_deg"],
                    pitch_type=selected_pitch_type,
                    lang=lang,
                    ivb_cm=spin["ivb_cm"],
                    hb_cm=spin["hb_cm"],
                )
                components.html(spin_3d_html, height=310)
                st.caption(f"<small style='color:#334155; font-weight:600;'>{i18n.t('spin_3d_help', lang)}</small>", unsafe_allow_html=True)

                with st.expander(i18n.t("view_2d_clock", lang), expanded=False):
                    pt_col = pitch_logic.PITCH_COLORS.get(selected_pitch_type, "#ff3366")
                    clock_fig = pitch_logic.generate_spin_axis_figure(
                        spin["spin_axis"], spin["spin_rate_rpm"], spin["active_spin_pct"],
                        pitch_color=pt_col, lang=lang
                    )
                    st.plotly_chart(clock_fig, width="stretch", key="spin_clock_chart")

            with vis_c2:
                st.caption(f"**🎯 {i18n.t('movement_plot_title', lang)}**")
                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                mov_pitches = [{
                    "video": video,
                    "label": f"{video} ({i18n.t(pitch_logic.PITCH_BENCHMARKS.get(selected_pitch_type, {}).get('name_key', 'pitch_fastball'), lang)})",
                    "ivb_cm": spin["ivb_cm"],
                    "hb_cm": spin["hb_cm"],
                    "speed_kmh": speed,
                    "pitch_type": selected_pitch_type,
                }]
                mov_fig = pitch_logic.generate_movement_plot_figure(mov_pitches, dist_unit=dist_unit, lang=lang, is_left_handed=left_handed)
                st.plotly_chart(mov_fig, width="stretch", key="main_movement_plot_chart")

                # 球質の変化特性診断カード（どんな変化だったのか一目で分かるサマリー・多言語対応）
                b_ivb = bench.get("ivb_cm", 40.0)
                b_hb = bench.get("hb_cm", 15.0) if not left_handed else -bench.get("hb_cm", 15.0)
                d_ivb = spin["ivb_cm"] - b_ivb
                d_hb = spin["hb_cm"] - b_hb
                ivb_tag, hb_tag = i18n.get_movement_profile_tags(d_ivb, d_hb, left_handed, lang)
                mov_prof_lbl = i18n.t("movement_profile_label", lang)
                act_lbl = i18n.t("actual_label", lang)

                st.markdown(
                    f"""<div style="background-color: #1a1e29; border: 1px solid #0284c7; border-radius: 8px; padding: 10px 14px; margin-top: 6px; font-size: 12px; color: #38bdf8; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 6px;">
                        <div><b>⚾ {mov_prof_lbl}:</b> <span style="color: #38bdf8; font-weight: 800;">{ivb_tag}</span> × <span style="color: #34d399; font-weight: 800;">{hb_tag}</span></div>
                        <div style="color: #38bdf8;">{act_lbl}: IVB <b style="color: {'#ff4b4b' if spin['ivb_cm']>=0 else '#38bdf8'};">{disp_ivb:+.1f}{break_unit}</b> | HB <b style="color: #facc15;">{disp_hb:+.1f}{break_unit}</b></div>
                    </div>""",
                    unsafe_allow_html=True,
                )

            st.caption(i18n.t("spin_caption", lang))

            # --- 5. Statcast風「Stuff+」球質レーダー評価 ---
            stuff = pitch_logic.calculate_stuff_plus(speed, spin, ext, pitch_type=selected_pitch_type)
            st.markdown("---")
            st.markdown(f"#### {i18n.t('stuff_plus_title', lang)}")
            st.caption(i18n.t("stuff_plus_desc", lang))

            stf_col1, stf_col2 = st.columns([1.1, 1.9])
            with stf_col1:
                st_ovr = stuff["overall"]
                vs_avg_txt = i18n.t("vs_pro_avg", lang)
                delta_str = f"+{st_ovr - 100} {vs_avg_txt}" if st_ovr >= 100 else f"{st_ovr - 100} {vs_avg_txt}"
                st.metric(
                    i18n.t("stuff_plus_score_label", lang),
                    f"{st_ovr}",
                    delta=delta_str,
                )
                arch_text = stuff["archetype"].get(lang, "Standard")
                arch_lbl = i18n.t("pitch_archetype_label", lang)
                stf_info = i18n.get_stuff_metrics_info(speed, spin, ext, lang)
                st.html(
                    f"""<div style="background-color: #1a1e29; border-left: 4px solid #38bdf8; border-top: 1px solid #0284c7; border-right: 1px solid #0284c7; border-bottom: 1px solid #0284c7; border-radius: 8px; padding: 8px 12px; margin: 8px 0;">
<span style="font-size: 11px; color: #7dd3fc; font-weight: bold;">{arch_lbl}</span><br>
<b style="font-size: 14px; color: #38bdf8; font-weight: 900;">{arch_text}</b>
</div>
<div style="background-color: #1a1e29; border: 1px solid #0284c7; border-radius: 10px; padding: 12px 14px; margin-top: 6px; box-shadow: 0 4px 12px rgba(0,0,0,0.25);">
<div style="display:flex; justify-content:space-between; align-items:center; border-bottom: 1px solid #1e293b; padding-bottom:5px; margin-bottom:5px;">
<span style="color:#7dd3fc; font-weight:800; font-size:12px;">{stf_info['title_ride']}</span>
<b style="font-size:15px; color:#38bdf8; font-weight:900;">{stuff['ivb_plus']:.0f}</b>
</div>
<div style="font-size:10.5px; color:#38bdf8; font-weight:600; margin-top:-2px; margin-bottom:8px;">{stf_info['sub_ride']}</div>
<div style="display:flex; justify-content:space-between; align-items:center; border-bottom: 1px solid #1e293b; padding-bottom:5px; margin-bottom:5px;">
<span style="color:#7dd3fc; font-weight:800; font-size:12px;">{stf_info['title_velo']}</span>
<b style="font-size:15px; color:#38bdf8; font-weight:900;">{stuff['velo_plus']:.0f}</b>
</div>
<div style="font-size:10.5px; color:#38bdf8; font-weight:600; margin-top:-2px; margin-bottom:8px;">{stf_info['sub_velo']}</div>
<div style="display:flex; justify-content:space-between; align-items:center; border-bottom: 1px solid #1e293b; padding-bottom:5px; margin-bottom:5px;">
<span style="color:#7dd3fc; font-weight:800; font-size:12px;">{stf_info['title_ext']}</span>
<b style="font-size:15px; color:#38bdf8; font-weight:900;">{stuff['ext_plus']:.0f}</b>
</div>
<div style="font-size:10.5px; color:#38bdf8; font-weight:600; margin-top:-2px; margin-bottom:8px;">{stf_info['sub_ext']}</div>
<div style="display:flex; justify-content:space-between; align-items:center; border-bottom: 1px solid #1e293b; padding-bottom:5px; margin-bottom:5px;">
<span style="color:#7dd3fc; font-weight:800; font-size:12px;">{stf_info['title_eff']}</span>
<b style="font-size:15px; color:#38bdf8; font-weight:900;">{stuff['eff_plus']:.0f}</b>
</div>
<div style="font-size:10.5px; color:#38bdf8; font-weight:600; margin-top:-2px; margin-bottom:8px;">{stf_info['sub_eff']}</div>
<div style="display:flex; justify-content:space-between; align-items:center; padding-bottom:4px;">
<span style="color:#7dd3fc; font-weight:800; font-size:12px;">{stf_info['title_run']}</span>
<b style="font-size:15px; color:#38bdf8; font-weight:900;">{stuff['hb_plus']:.0f}</b>
</div>
<div style="font-size:10.5px; color:#38bdf8; font-weight:600; margin-top:-2px;">{stf_info['sub_run']}</div>
</div>"""
                )

            with stf_col2:
                pt_col = pitch_logic.PITCH_COLORS.get(selected_pitch_type, "#00d2ff")
                radar_fig = pitch_logic.generate_stuff_plus_radar(stuff, pitch_color=pt_col, lang=lang)
                st.plotly_chart(radar_fig, width="stretch", key="stuff_plus_radar_chart")

            st.html(i18n.t("stuff_plus_guide_html", lang))


            # --- 1. AIフォーム診断＆コーチングフィードバック ---
            feedback = pitch_logic.generate_ai_feedback(bio, speed, ext, lang=lang)

            st.markdown("---")
            st.subheader(i18n.t("ai_diagnosis_header", lang))

            f_col1, f_col2 = st.columns(2)
            with f_col1:
                st.markdown(
                    f"""<div class="bio-box" style="border-left-color: #00d2ff; background-color: #1e222d;">
                    <span class="bio-title" style="color: #ffffff !important;">{i18n.t('overall_score', lang)}</span>
                    <span class="bio-val" style="color: #00d2ff !important;">{feedback['grade']} ({feedback['score']})</span>
                    </div>""",
                    unsafe_allow_html=True,
                )
            with f_col2:
                disp_pspeed = i18n.convert_speed(feedback['perceived_speed_kmh'], speed_unit)
                st.markdown(
                    f"""<div class="bio-box" style="border-left-color: #e67e22; background-color: #1e222d;">
                    <span class="bio-title" style="color: #ffffff !important;">{i18n.t('perceived_velocity', lang)}</span>
                    <span class="bio-val" style="color: #f39c12 !important;">{disp_pspeed:.1f} {speed_unit}</span>
                    </div>""",
                    unsafe_allow_html=True,
                )

            # 良好なポイントと改善提案の描画
            card_items = []

            # 良好なポイントヘッダー
            card_items.append(
                f'<div style="background: linear-gradient(90deg, #1b3828, #182230); color: #2ecc71; font-weight: bold; font-size: 15px; padding: 8px 12px; border-radius: 6px; margin: 12px 0 8px 0; border: 1px solid #2ecc7166;">'
                f'{i18n.t("strengths_title", lang)}'
                f'</div>'
            )
            for st_msg in feedback.get("strengths", []):
                parts = st_msg.split(": ", 1)
                t_txt = parts[0] if len(parts) > 1 else i18n.t("strengths_title", lang)
                d_txt = parts[1] if len(parts) > 1 else st_msg
                card_items.append(
                    f'<div style="background-color: #1b2838; border-left: 4px solid #2ecc71; border-radius: 6px; padding: 10px 14px; margin-bottom: 8px;">'
                    f'<span style="color: #2ecc71; font-weight: bold; font-size: 14px;">✅ {t_txt}</span><br/>'
                    f'<span style="color: #f0f4f8; font-size: 13px; line-height: 1.5; display: block; margin-top: 3px;">{d_txt}</span>'
                    f'</div>'
                )

            # 球速アップへの改善提案ヘッダー
            card_items.append(
                f'<div style="background: linear-gradient(90deg, #3d2b14, #182230); color: #f39c12; font-weight: bold; font-size: 15px; padding: 8px 12px; border-radius: 6px; margin: 16px 0 8px 0; border: 1px solid #f39c1266;">'
                f'{i18n.t("improvements_title", lang)}'
                f'</div>'
            )
            improvements = feedback.get("improvements", [])
            if improvements:
                for imp_msg in improvements:
                    parts = imp_msg.split(": ", 1)
                    t_txt = parts[0] if len(parts) > 1 else i18n.t("improvements_title", lang)
                    d_txt = parts[1] if len(parts) > 1 else imp_msg
                    card_items.append(
                        f'<div style="background-color: #2c221a; border-left: 4px solid #f39c12; border-radius: 6px; padding: 10px 14px; margin-bottom: 8px;">'
                        f'<span style="color: #f39c12; font-weight: bold; font-size: 14px;">💡 {t_txt}</span><br/>'
                        f'<span style="color: #f0f4f8; font-size: 13px; line-height: 1.5; display: block; margin-top: 3px;">{d_txt}</span>'
                        f'</div>'
                    )
            else:
                card_items.append(
                    f'<div style="background-color: #2c221a; border-left: 4px solid #f39c12; border-radius: 6px; padding: 10px 14px; margin-bottom: 8px;">'
                    f'<span style="color: #f0f4f8; font-size: 13px;">{i18n.t("no_improvements", lang)}</span>'
                    f'</div>'
                )

            st.markdown("\n".join(card_items), unsafe_allow_html=True)

            st.markdown("---")
            st.subheader("AWS AI Pitching Coach (Amazon Bedrock)")
            st.caption(
                "Uses this pitch's computed velocity, biomechanics, spin estimates, "
                "tracking summary, and existing diagnosis. No raw video or pose coordinates are sent."
            )
            if not aws_utils.get_aws_region():
                st.info(
                    "AWS services are not configured. Set AWS_REGION and AWS credentials to use "
                    "S3 or Bedrock; local analysis is still available."
                )
            if not aws_utils.is_s3_configured():
                st.info("S3_BUCKET is not configured. Analysis remains available locally.")

            coach_metrics = build_coach_metrics(res, feedback)
            coach_payload = json.dumps(
                coach_metrics, ensure_ascii=False, sort_keys=True, allow_nan=False
            )
            coach_fingerprint = hashlib.sha256(coach_payload.encode("utf-8")).hexdigest()
            coach_state = st.session_state.get("bedrock_coach_result")
            if coach_state and coach_state.get("fingerprint") != coach_fingerprint:
                st.session_state.pop("bedrock_coach_result", None)

            if st.button(
                "Generate personalized pitching feedback",
                key=f"bedrock_coach_{video}",
                type="primary",
                disabled=not aws_utils.get_aws_region(),
            ):
                with st.spinner("Saving pitch metrics and asking Amazon Bedrock..."):
                    metrics_key = f"analysis/{uuid.uuid4().hex}.json"
                    archive_result = aws_utils.upload_json_to_s3(coach_metrics, metrics_key)
                    coach_result = aws_utils.generate_bedrock_coach_feedback(
                        coach_metrics, language=lang
                    )
                    st.session_state["bedrock_coach_result"] = {
                        "fingerprint": coach_fingerprint,
                        "archive_success": archive_result.success,
                        "archive_message": archive_result.message,
                        "archive_key": archive_result.object_key,
                        "success": coach_result.success,
                        "message": coach_result.message,
                        "feedback": coach_result.feedback,
                    }
                st.rerun()

            coach_state = st.session_state.get("bedrock_coach_result")
            if coach_state and coach_state.get("fingerprint") == coach_fingerprint:
                if coach_state["archive_success"]:
                    st.success(
                        "Pitch metrics archived in private S3 object "
                        f"s3://{aws_utils.get_s3_bucket()}/{coach_state['archive_key']}"
                    )
                else:
                    st.info(coach_state["archive_message"])

                if coach_state["success"]:
                    coach_feedback = coach_state["feedback"]
                    st.markdown("**Overall Assessment**")
                    st.write(coach_feedback["overall_assessment"])
                    st.markdown("**Strengths**")
                    for item in coach_feedback["strengths"]:
                        st.markdown(f"- {item}")
                    st.markdown("**Priority Improvements**")
                    for index, item in enumerate(coach_feedback["priority_improvements"], 1):
                        st.markdown(f"{index}. {item}")
                    st.markdown("**Recommended Practice**")
                    for item in coach_feedback["recommended_practice"]:
                        st.markdown(f"- {item}")
                    st.markdown("**Velocity Improvement Advice**")
                    st.write(coach_feedback["velocity_improvement_advice"])
                else:
                    st.warning(coach_state["message"])

            # --- 4. 球速・球質アップ・シミュレーター (What-If Sandbox) ---
            st.markdown("---")
            with st.expander(i18n.t("what_if_title", lang), expanded=False):
                sim_c1, sim_c2 = st.columns(2)
                sim_d_ext = sim_c1.slider(i18n.t("sim_ext_label", lang), 0, 25, 10, step=2, format="+%d cm", key=f"sim_ext_{video}")
                sim_d_knee = sim_c2.slider(i18n.t("sim_knee_label", lang), 0, 30, 10, step=2, format="+%d°", key=f"sim_knee_{video}")
                sim_c3, sim_c4 = st.columns(2)
                sim_d_spin = sim_c3.slider(i18n.t("sim_spin_label", lang), 0, 500, 150, step=25, format="+%d rpm", key=f"sim_spin_{video}")
                sim_d_arm = sim_c4.slider(i18n.t("sim_arm_label", lang), 0, 25, 10, step=2, format="+%d%%", key=f"sim_arm_{video}")

                sim_res = pitch_logic.calculate_what_if_simulation(
                    speed, ext, bio.get("lead_knee_angle", 150.0), spin["spin_rate_rpm"],
                    sim_d_ext, sim_d_knee, sim_d_spin, sim_d_arm
                )
                disp_proj_v = i18n.convert_speed(sim_res["proj_velo"], speed_unit)
                disp_delta_v = i18n.convert_speed(sim_res["delta_velo"], speed_unit)
                disp_proj_pv = i18n.convert_speed(sim_res["proj_perceived"], speed_unit)
                disp_delta_pv = i18n.convert_speed(sim_res["delta_perceived"], speed_unit)

                sm1, sm2 = st.columns(2)
                sm1.metric(i18n.t("projected_velo", lang), f"{disp_proj_v:.1f} {speed_unit}", f"+{disp_delta_v:.1f} {speed_unit}")
                sm2.metric(i18n.t("projected_perceived", lang), f"{disp_proj_pv:.1f} {speed_unit}", f"+{disp_delta_pv:.1f} {speed_unit}")

                sm3, sm4 = st.columns(2)
                disp_d_ivb = sim_res["delta_ivb"] / 2.54 if dist_unit == "ft" else sim_res["delta_ivb"]
                b_unit = "in" if dist_unit == "ft" else "cm"
                sm3.metric(i18n.t("projected_ivb", lang), f"+{disp_d_ivb:.1f} {b_unit}", f"+{disp_d_ivb:.1f} {b_unit}")
                sm4.metric(i18n.t("projected_whiff", lang), f"{sim_res['proj_whiff']:.1f} %", f"+{sim_res['delta_whiff']:.1f} %")

            # --- 5. 本日のピッチング処方箋（改善ドリル・ToDoリスト） ---
            st.markdown("---")
            st.subheader(i18n.t("prescription_title", lang))
            drills = pitch_logic.get_pitching_prescription_drills(bio, spin, lang=lang)
            for d_idx, drill in enumerate(drills):
                st.markdown(f"**🎯 {drill['title']}** (`{drill['target']}`)")
                st.caption(drill["desc"])


            # --- 3. 投球カルテ画像（ワンクリック出力） ---
            st.markdown("---")
            v_file = VIDEOS_DIR / f"{video}.mp4"
            cap_rep = cv2.VideoCapture(str(v_file))
            cap_rep.set(cv2.CAP_PROP_POS_FRAMES, release_frame)
            ret_rep, frame_rep = cap_rep.read()
            cap_rep.release()

            if ret_rep:
                r_kp = kp_df[kp_df["frame"] == release_frame]
                if not r_kp.empty:
                    frame_rep = pitch_logic.draw_skeleton(frame_rep, r_kp.iloc[0], draw_labels=False)
                frame_rep = pitch_logic.draw_ball_trajectory(
                    frame_rep, ball_df, end_frame=net_frame, release_frame=release_frame, net_frame=net_frame, speed_kmh=speed
                )

            report_png = pitch_logic.generate_report_card(
                video, speed, ext, dist, bio, feedback, frame_rep if ret_rep else None,
                speed_unit=speed_unit, dist_unit=dist_unit, lang=lang, pitcher_height_cm=pitcher_height_cm
            )

            dl_col1, dl_col2 = st.columns(2)
            with dl_col1:
                st.download_button(
                    label=i18n.t("download_report", lang),
                    data=report_png,
                    file_name=f"pitch_report_{video}.png",
                    mime="image/png",
                    width="stretch",
                    type="secondary",
                )
            with dl_col2:
                bcard_png = pitch_logic.generate_broadcast_card(
                    video, speed, ext, spin, stuff, release_frame, kp_df,
                    pitch_type=selected_pitch_type, speed_unit=speed_unit, dist_unit=dist_unit, lang=lang
                )
                st.download_button(
                    label=i18n.t("broadcast_card_btn", lang),
                    data=bcard_png,
                    file_name=f"statcast_card_{video}.png",
                    mime="image/png",
                    width="stretch",
                    type="primary",
                )

            st.markdown("</div>", unsafe_allow_html=True)

        with col_right:
            st.markdown('<div class="card">', unsafe_allow_html=True)

            # --- 4. 表示レイヤートグル ---
            st.write(f"**{i18n.t('layer_toggles', lang)}**")
            l_c1, l_c2, l_c3 = st.columns(3)
            show_skel = l_c1.checkbox(i18n.t("show_skel", lang), value=True, key=f"show_skel_{video}")
            show_labels = l_c2.checkbox(i18n.t("show_labels", lang), value=False, key=f"show_labels_{video}")
            show_tracer = l_c3.checkbox(i18n.t("show_tracer", lang), value=True, key=f"show_tracer_{video}")

            subtab_video, subtab_still, subtab_tracer, subtab_phases, subtab_strike = st.tabs([
                i18n.t("subtab_video", lang),
                i18n.t("subtab_still", lang),
                i18n.t("subtab_tracer", lang),
                i18n.t("subtab_phases", lang),
                i18n.t("subtab_strike", lang),
            ])

            with subtab_video:
                # --- 5. スローモーション再生速度切替 ---
                speed_opts = [
                    i18n.t("speed_normal", lang),
                    i18n.t("speed_slow", lang),
                    i18n.t("speed_superslow", lang),
                ]
                speed_label = st.radio(
                    i18n.t("playback_speed", lang),
                    speed_opts,
                    index=0,
                    horizontal=True,
                    key=f"video_speed_radio_{video}",
                )
                speed_factor = 1.0 if "1.0x" in speed_label else (0.5 if "0.5x" in speed_label else 0.25)
                active_video_path = pitch_logic.get_or_create_slow_video(video, kp_df, speed_factor=speed_factor)
                if active_video_path and Path(active_video_path).exists():
                    st.video(str(active_video_path))
                else:
                    st.warning("Video not found or processing.")

            with subtab_still:
                still_mode = st.radio(
                    "表示形式",
                    ["release_snap", "motion_trail"],
                    index=0,
                    format_func=lambda k: i18n.t("caption_release", lang, frame=release_frame) if k == "release_snap" else i18n.t("motion_trail_title", lang),
                    horizontal=True,
                    key=f"still_mode_radio_{video}",
                )

                if still_mode == "motion_trail":
                    trail_img = pitch_logic.generate_motion_trail_photo(video, kp_df, phases, release_frame, is_left_handed=left_handed)
                    st.image(cv2.cvtColor(trail_img, cv2.COLOR_BGR2RGB), caption=f"📸 {i18n.t('motion_trail_title', lang)} ({video})", width="stretch")
                    _, t_buf = cv2.imencode(".png", trail_img)
                    st.download_button(
                        label=i18n.t("download_strobe", lang),
                        data=t_buf.tobytes(),
                        file_name=f"motion_trail_{video}.png",
                        mime="image/png",
                        width="stretch",
                    )
                else:
                    video_file = VIDEOS_DIR / f"{video}.mp4"
                    cap = cv2.VideoCapture(str(video_file))
                    cap.set(cv2.CAP_PROP_POS_FRAMES, release_frame)
                    ret, frame = cap.read()
                    cap.release()

                    if ret:
                        rel_row = kp_df[kp_df["frame"] == release_frame]
                        if show_skel and not rel_row.empty:
                            frame = pitch_logic.draw_skeleton(frame, rel_row.iloc[0], draw_labels=show_labels)
                        if show_tracer and ball_df is not None:
                            frame = pitch_logic.draw_ball_trajectory(
                                frame, ball_df, end_frame=release_frame, release_frame=release_frame, net_frame=net_frame, speed_kmh=speed
                            )
                        st.image(
                            cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
                            caption=i18n.t("caption_release", lang, frame=release_frame),
                            width="stretch",
                        )

            with subtab_tracer:
                # 弾道トレーサー表示形式（3D Statcast vs 2D実写オーバーレイ）
                tracer_view_mode = st.radio(
                    i18n.t("tracer_mode_label", lang),
                    ["statcast_3d", "real_2d"],
                    index=0,
                    format_func=lambda k: i18n.t("mode_statcast_3d", lang) if k == "statcast_3d" else i18n.t("mode_real_2d", lang),
                    horizontal=True,
                    key=f"tracer_mode_radio_{video}",
                )

                if tracer_view_mode == "statcast_3d":
                    # カメラ視点選択（打者側からの視点をデフォルトに！）
                    cam_keys = ["batter_rhb", "batter_lhb", "catcher", "pitcher", "side"]
                    cam_labels = {
                        "batter_rhb": i18n.t("cam_batter_rhb", lang),
                        "batter_lhb": i18n.t("cam_batter_lhb", lang),
                        "catcher": i18n.t("cam_catcher", lang),
                        "pitcher": i18n.t("cam_pitcher", lang),
                        "side": i18n.t("cam_side", lang),
                    }
                    sel_cam = st.radio(
                        i18n.t("camera_view_label", lang),
                        cam_keys,
                        index=0,  # 打者側からの視点をデフォルトに！
                        format_func=lambda k: cam_labels[k],
                        horizontal=True,
                        key=f"cam_view_radio_{video}",
                    )

                    # 複数投球の重ね合わせ選択
                    sel_compare_pitches = st.multiselect(
                        i18n.t("overlay_pitches_label", lang),
                        options=available_videos,
                        default=[video],
                        key=f"statcast_multi_{video}",
                    )
                    if not sel_compare_pitches:
                        sel_compare_pitches = [video]

                    # 選択された全投球の3D弾道データを構築
                    pitches_data = []
                    default_pitch_types = {
                        "pitch_102_1": "fastball",
                        "pitch_98_1": "slider",
                        "pitch_98_2": "curve",
                        "pitch_00015_80": "twoseam",
                    }
                    for v_name in sel_compare_pitches:
                        if v_name == video:
                            p_bdf = ball_df
                            p_rel = release_frame
                            p_net = net_frame
                            p_spd = speed
                            p_ext = ext
                            p_h = pitcher_height_m
                            p_left = left_handed
                            p_pt = selected_pitch_type
                        else:
                            b_csv = pitch_mod.INPUT_DIR / f"{v_name}_tracking.csv"
                            p_bdf = pd.read_csv(b_csv) if b_csv.exists() else None
                            p_rel, p_net = pitch_mod.BASE_FRAMES.get(v_name, (50, 70))
                            p_h = pitch_logic.estimate_pitcher_height(v_name) / 100.0
                            p_left = pitch_mod.HANDEDNESS.get(v_name, True)
                            p_pt = default_pitch_types.get(v_name, "fastball")
                            if v_name == "pitch_00015_80":
                                p_spd = 142.9
                                p_ext = 1.95
                            elif "102" in v_name:
                                p_spd = 102.1
                                p_ext = 1.14
                            elif "98_1" in v_name:
                                p_spd = 98.1
                                p_ext = 1.10
                            elif "98_2" in v_name:
                                p_spd = 97.8
                                p_ext = 1.12
                            else:
                                p_spd = 120.0
                                p_ext = 1.20

                        pt_label = i18n.t(pitch_logic.PITCH_BENCHMARKS.get(p_pt, {}).get("name_key", "pitch_fastball"), lang)
                        pitches_data.append({
                            "video": v_name,
                            "label": f"{v_name}: {pt_label}",
                            "ball_df": p_bdf,
                            "release_frame": p_rel,
                            "net_frame": p_net,
                            "speed_kmh": p_spd,
                            "extension_m": p_ext,
                            "pitcher_height_m": p_h,
                            "is_left_handed": p_left,
                            "pitch_type": p_pt,
                        })

                    # 球種カラー凡例バッジ
                    legend_html = ["<div style='display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 8px;'>"]
                    for p_item in pitches_data:
                        col = pitch_logic.PITCH_COLORS.get(p_item["pitch_type"], "#d22d49")
                        disp_s = i18n.convert_speed(p_item["speed_kmh"], speed_unit)
                        legend_html.append(
                            f"<span style='background: {col}22; border: 1.5px solid {col}; border-radius: 6px; padding: 3px 8px; font-size: 12px; color: #ffffff; font-weight: bold;'>"
                            f"<span style='display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: {col}; margin-right: 5px;'></span>"
                            f"{p_item['label']} ({disp_s:.1f} {speed_unit})"
                            f"</span>"
                        )
                    legend_html.append("</div>")
                    st.markdown("".join(legend_html), unsafe_allow_html=True)

                    fig_3d = pitch_logic.generate_statcast_3d_figure(
                        pitches_data=pitches_data,
                        camera_view=sel_cam,
                        speed_unit=speed_unit,
                        dist_unit=dist_unit,
                        lang=lang,
                    )
                    st.plotly_chart(fig_3d, width="stretch", key="statcast_3d_trajectory_chart")
                    st.caption(i18n.t("3d_mouse_hint", lang))
                else:
                    video_file = VIDEOS_DIR / f"{video}.mp4"
                    cap = cv2.VideoCapture(str(video_file))
                    cap.set(cv2.CAP_PROP_POS_FRAMES, release_frame)
                    ret, frame = cap.read()
                    cap.release()

                    if ret:
                        rel_row = kp_df[kp_df["frame"] == release_frame]
                        if show_skel and not rel_row.empty:
                            frame = pitch_logic.draw_skeleton(frame, rel_row.iloc[0], draw_labels=show_labels)
                        if show_tracer:
                            frame = pitch_logic.draw_ball_trajectory(
                                frame, ball_df, end_frame=net_frame, release_frame=release_frame, net_frame=net_frame, speed_kmh=speed
                            )
                        st.image(
                            cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
                            caption=i18n.t("caption_tracer", lang, speed=disp_speed, speed_unit=speed_unit, ext=disp_ext, dist_unit=dist_unit),
                            width="stretch",
                        )

            with subtab_phases:
                max_frame_idx = int(kp_df["frame"].max())

                # 動画切り替え時の同期
                if "current_video" not in st.session_state or st.session_state["current_video"] != video:
                    st.session_state["current_video"] = video
                    st.session_state["scrub_slider"] = release_frame
                elif "scrub_slider" not in st.session_state:
                    st.session_state["scrub_slider"] = release_frame

                # クランプ
                st.session_state["scrub_slider"] = max(0, min(max_frame_idx, st.session_state["scrub_slider"]))

                # コールバック関数（スライダーを直接更新）
                def set_frame(target_fr):
                    st.session_state["scrub_slider"] = max(0, min(max_frame_idx, int(target_fr)))

                def step_frame(delta):
                    cur = st.session_state.get("scrub_slider", release_frame)
                    st.session_state["scrub_slider"] = max(0, min(max_frame_idx, int(cur + delta)))

                st.write(f"**{i18n.t('phase_jump', lang)}**")
                
                # フェーズジャンプ（文字をボタン外側に配置して途切れを完全に解消）
                cur_scrub = st.session_state.get("scrub_slider", release_frame)
                phase_cols = st.columns(len(phases))
                for idx, (p_name, p_fr) in enumerate(phases.items()):
                    is_active = (cur_scrub == p_fr)
                    p_title, p_sub = i18n.get_phase_components(p_name, lang)
                    with phase_cols[idx]:
                        if is_active:
                            t_color = "#0284c7"
                            sub_color = "#0369a1"
                            fr_color = "#0284c7"
                            bg_style = "background: #e0f2fe; border: 2px solid #0284c7;"
                        else:
                            t_color = "#0f172a"   # 視認性の高いくっきりした黒
                            sub_color = "#334155"  # 濃いダークグレー
                            fr_color = "#0f172a"   # くっきりした黒
                            bg_style = "background: #f8fafc; border: 1px solid #cbd5e1;"

                        st.markdown(
                            f"<div style='{bg_style} border-radius: 6px; padding: 6px 2px; text-align: center; margin-bottom: 6px; min-height: 66px; display: flex; flex-direction: column; justify-content: center;'>"
                            f"<div style='font-size: 13px; font-weight: 700; color: {t_color}; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;'>{p_title}</div>"
                            f"<div style='font-size: 11px; font-weight: 500; color: {sub_color}; white-space: nowrap;'>{p_sub}</div>"
                            f"<div style='font-size: 11px; font-weight: 700; color: {fr_color}; margin-top: 2px;'>fr {p_fr}</div>"
                            f"</div>",
                            unsafe_allow_html=True,
                        )
                        btn_txt = i18n.t("btn_selected", lang) if is_active else i18n.t("btn_jump", lang)
                        btn_type = "primary" if is_active else "secondary"
                        phase_cols[idx].button(
                            btn_txt,
                            key=f"phase_btn_{idx}_{video}",
                            on_click=set_frame,
                            args=(p_fr,),
                            width="stretch",
                            type=btn_type,
                        )

                st.write(f"**{i18n.t('step_controls', lang)}**")
                btn_c1, btn_c2, btn_c3, btn_c4 = st.columns([1, 1.2, 1.2, 1])
                btn_c1.button(i18n.t("step_m5", lang), on_click=step_frame, args=(-5,), width="stretch", key=f"btn_m5_{video}")
                btn_c2.button(i18n.t("step_m1", lang), on_click=step_frame, args=(-1,), width="stretch", key=f"btn_m1_{video}")
                btn_c3.button(i18n.t("step_p1", lang), on_click=step_frame, args=(1,), width="stretch", key=f"btn_p1_{video}")
                btn_c4.button(i18n.t("step_p5", lang), on_click=step_frame, args=(5,), width="stretch", key=f"btn_p5_{video}")

                selected_frame = st.slider(
                    i18n.t("frame_scrub", lang),
                    min_value=0,
                    max_value=max_frame_idx,
                    step=1,
                    key="scrub_slider",
                )

                # 現在のフェーズ名判定
                current_phase_label = ""
                for p_name, p_fr in phases.items():
                    if selected_frame == p_fr:
                        current_phase_label = f" 【{i18n.get_phase_label(p_name, p_fr, lang)}】"
                        break

                video_file = VIDEOS_DIR / f"{video}.mp4"
                cap = cv2.VideoCapture(str(video_file))
                cap.set(cv2.CAP_PROP_POS_FRAMES, selected_frame)
                ret, s_frame = cap.read()
                cap.release()

                if ret:
                    sub_row = kp_df[kp_df["frame"] == selected_frame]
                    if show_skel and not sub_row.empty:
                        s_frame = pitch_logic.draw_skeleton(s_frame, sub_row.iloc[0], draw_labels=show_labels)
                    if show_tracer and ball_df is not None:
                        s_frame = pitch_logic.draw_ball_trajectory(
                            s_frame, ball_df, end_frame=selected_frame, release_frame=release_frame, net_frame=net_frame, speed_kmh=speed
                        )
                    st.image(
                        cv2.cvtColor(s_frame, cv2.COLOR_BGR2RGB),
                        caption=f"Frame {selected_frame} / {max_frame_idx}{current_phase_label}",
                        width="stretch",
                    )

                    # --- ② キネマティック・シーケンス時系列推移グラフ ---
                    st.markdown("---")
                    kin_df = pitch_logic.calculate_kinematic_sequence(kp_df, is_left_handed=left_handed, fps=video_fps)
                    kin_fig = pitch_logic.generate_kinematic_figure(kin_df, current_frame=selected_frame, phases=phases, lang=lang)
                    st.plotly_chart(kin_fig, width="stretch", key="kinematic_sequence_chart")
                    st.caption(i18n.t("kinematic_caption", lang))

            # --- ④ 捕球位置・ストライクゾーン可視化 (打者視点シミュレーション対応) ---
            with subtab_strike:
                persp_keys = ["catcher", "right_batter", "left_batter"]
                persp_labels = {
                    "catcher": i18n.t("catcher_view", lang),
                    "right_batter": i18n.t("right_batter_view", lang),
                    "left_batter": i18n.t("left_batter_view", lang),
                }
                sel_persp = st.radio(
                    i18n.t("perspective_label", lang),
                    persp_keys,
                    index=0,
                    format_func=lambda k: persp_labels[k],
                    horizontal=True,
                    key=f"persp_radio_{video}",
                )
                zone_fig, zone_desc = pitch_logic.generate_strike_zone_figure(
                    ball_df,
                    net_frame,
                    speed,
                    speed_unit=speed_unit,
                    lang=lang,
                    perspective=sel_persp,
                    frame_width=res["video_width"],
                    frame_height=res["video_height"],
                    release_frame=release_frame,
                    camera_calibrated=video in pitch_logic.STRIKE_ZONE_CALIBRATED_VIDEOS,
                )
                st.plotly_chart(zone_fig, width="stretch", key="strike_zone_chart")
                st.info(f"📍 **{i18n.t('impact_call', lang)}**: {zone_desc}")
                st.caption(i18n.t("zone_estimate_disclaimer", lang))

                # --- 🎯 球種別変化量マップ (Movement Plot: IVB vs HB) ---
                st.markdown("---")
                mov_pitches = [{
                    "video": video,
                    "label": f"{video}: {i18n.t(pitch_logic.PITCH_BENCHMARKS.get(selected_pitch_type, {}).get('name_key', 'pitch_fastball'), lang)}",
                    "ivb_cm": spin["ivb_cm"],
                    "hb_cm": spin["hb_cm"],
                    "speed_kmh": speed,
                    "pitch_type": selected_pitch_type,
                }]
                mov_fig = pitch_logic.generate_movement_plot_figure(mov_pitches, dist_unit=dist_unit, lang=lang, is_left_handed=left_handed)
                st.plotly_chart(mov_fig, width="stretch", key="tab2d_movement_plot_chart")

            st.markdown("</div>", unsafe_allow_html=True)

    # ========================================================
    # TAB 2: 2投球フォーム比較モード
    # ========================================================
    with tab_compare:
        st.subheader(i18n.t("compare_header", lang))
        c_sel1, c_sel2 = st.columns(2)
        with c_sel1:
            vid_a = st.selectbox(i18n.t("pitch_a", lang), available_videos, index=0, key="cmp_vid_a")
        with c_sel2:
            default_b_idx = 1 if len(available_videos) > 1 else 0
            vid_b = st.selectbox(i18n.t("pitch_b", lang), available_videos, index=default_b_idx, key="cmp_vid_b")

        if vid_a and vid_b:
            h_a = pitch_logic.estimate_pitcher_height(vid_a) / 100.0
            h_b = pitch_logic.estimate_pitcher_height(vid_b) / 100.0
            hand_a = left_handed if vid_a == selected_video else pitch_mod.HANDEDNESS.get(vid_a, True)
            hand_b = left_handed if vid_b == selected_video else pitch_mod.HANDEDNESS.get(vid_b, True)
            res_a = run_analysis(vid_a, hand_a, pitcher_height_m=h_a)
            res_b = run_analysis(vid_b, hand_b, pitcher_height_m=h_b)

            fb_a = pitch_logic.generate_ai_feedback(res_a['biomechanics'], res_a['speed_kmh'], res_a['extension'], lang=lang)
            fb_b = pitch_logic.generate_ai_feedback(res_b['biomechanics'], res_b['speed_kmh'], res_b['extension'], lang=lang)

            spd_a = i18n.convert_speed(res_a['speed_kmh'], speed_unit)
            spd_b = i18n.convert_speed(res_b['speed_kmh'], speed_unit)
            diff_speed = spd_a - spd_b

            pspd_a = i18n.convert_speed(fb_a['perceived_speed_kmh'], speed_unit)
            pspd_b = i18n.convert_speed(fb_b['perceived_speed_kmh'], speed_unit)
            diff_pspeed = pspd_a - pspd_b

            ext_a = i18n.convert_distance(res_a['extension'], dist_unit)
            ext_b = i18n.convert_distance(res_b['extension'], dist_unit)
            diff_ext = ext_a - ext_b

            dst_a = i18n.convert_distance(res_a['pitch_distance'], dist_unit)
            dst_b = i18n.convert_distance(res_b['pitch_distance'], dist_unit)
            diff_dist = dst_a - dst_b

            diff_elb = res_a['biomechanics'].get('elbow_angle', 0) - res_b['biomechanics'].get('elbow_angle', 0)
            diff_knee = res_a['biomechanics'].get('lead_knee_angle', 0) - res_b['biomechanics'].get('lead_knee_angle', 0)
            diff_slot = res_a['biomechanics'].get('forearm_slot', 0) - res_b['biomechanics'].get('forearm_slot', 0)
            diff_score = fb_a['score'] - fb_b['score']

            # 比較モード切り替え (ゴースト重ね合わせ vs 2画面並列)
            cmp_mode = st.radio(
                i18n.t("compare_view_mode", lang),
                [i18n.t("view_ghost", lang), i18n.t("view_side_by_side", lang)],
                horizontal=True,
                key=f"cmp_mode_{vid_a}_{vid_b}",
            )

            if cmp_mode == i18n.t("view_ghost", lang):
                st.markdown("---")
                # 同期フェーズ選択 & コントロール
                ctrl_c1, ctrl_c2 = st.columns([1.8, 2.2])
                with ctrl_c1:
                    phase_keys = list(res_a["phases"].keys())
                    sel_p_idx = st.selectbox(
                        i18n.t("compare_phase_select", lang),
                        range(len(phase_keys)),
                        index=3,  # リリースがデフォルト
                        format_func=lambda i: i18n.get_phase_components(phase_keys[i], lang)[0],
                        key=f"ghost_phase_{vid_a}_{vid_b}",
                    )
                with ctrl_c2:
                    blend_pct = st.slider(
                        i18n.t("blend_slider", lang),
                        min_value=0,
                        max_value=100,
                        value=50,
                        step=5,
                        format="%d%%",
                        key=f"ghost_blend_{vid_a}_{vid_b}",
                    )

                opt_c1, opt_c2 = st.columns(2)
                show_vecs = opt_c1.checkbox(i18n.t("show_vectors", lang), value=True, key=f"vecs_{vid_a}_{vid_b}")
                show_kpts = opt_c2.checkbox(i18n.t("show_labels", lang), value=False, key=f"kpts_{vid_a}_{vid_b}")

                target_p_name = phase_keys[sel_p_idx]
                fr_a = res_a["phases"].get(target_p_name, res_a["release_frame"])
                phase_keys_b = list(res_b["phases"].keys())
                fr_b = res_b["phases"].get(target_p_name, res_b["phases"][phase_keys_b[sel_p_idx]]) if sel_p_idx < len(phase_keys_b) else res_b["release_frame"]

                cap_a = cv2.VideoCapture(str(VIDEOS_DIR / f"{vid_a}.mp4"))
                cap_a.set(cv2.CAP_PROP_POS_FRAMES, fr_a)
                ret_a, f_a = cap_a.read()
                cap_a.release()

                cap_b = cv2.VideoCapture(str(VIDEOS_DIR / f"{vid_b}.mp4"))
                cap_b.set(cv2.CAP_PROP_POS_FRAMES, fr_b)
                ret_b, f_b = cap_b.read()
                cap_b.release()

                if ret_a and ret_b:
                    r_a = res_a["kp_df"][res_a["kp_df"]["frame"] == fr_a]
                    r_b = res_b["kp_df"][res_b["kp_df"]["frame"] == fr_b]
                    kp_row_a = r_a.iloc[0] if not r_a.empty else None
                    kp_row_b = r_b.iloc[0] if not r_b.empty else None

                    ghost_img = pitch_logic.generate_ghost_overlay(
                        f_a, kp_row_a, f"{vid_a} ({spd_a:.1f}{speed_unit})",
                        f_b, kp_row_b, f"{vid_b} ({spd_b:.1f}{speed_unit})",
                        alpha_a=blend_pct / 100.0,
                        show_vectors=show_vecs,
                        show_labels=show_kpts,
                        is_left_handed=pitch_mod.HANDEDNESS.get(vid_a, True),
                    )
                    p_disp_name, _ = i18n.get_phase_components(target_p_name, lang)
                    st.image(
                        cv2.cvtColor(ghost_img, cv2.COLOR_BGR2RGB),
                        caption=f"👻 Ghost Overlay | {p_disp_name} (A: fr {fr_a} vs B: fr {fr_b})",
                        width="stretch",
                    )
            else:
                img_col1, img_col2 = st.columns(2)
                with img_col1:
                    st.markdown(f"**{i18n.t('pitch_a', lang)}: `{vid_a}` ({spd_a:.1f} {speed_unit})**")
                    cap_a = cv2.VideoCapture(str(VIDEOS_DIR / f"{vid_a}.mp4"))
                    cap_a.set(cv2.CAP_PROP_POS_FRAMES, res_a["release_frame"])
                    ret_a, f_a = cap_a.read()
                    cap_a.release()
                    if ret_a:
                        r_a = res_a["kp_df"][res_a["kp_df"]["frame"] == res_a["release_frame"]]
                        if not r_a.empty:
                            f_a = pitch_logic.draw_skeleton(f_a, r_a.iloc[0], draw_labels=False)
                        st.image(cv2.cvtColor(f_a, cv2.COLOR_BGR2RGB), width="stretch")

                with img_col2:
                    st.markdown(f"**{i18n.t('pitch_b', lang)}: `{vid_b}` ({spd_b:.1f} {speed_unit})**")
                    cap_b = cv2.VideoCapture(str(VIDEOS_DIR / f"{vid_b}.mp4"))
                    cap_b.set(cv2.CAP_PROP_POS_FRAMES, res_b["release_frame"])
                    ret_b, f_b = cap_b.read()
                    cap_b.release()
                    if ret_b:
                        r_b = res_b["kp_df"][res_b["kp_df"]["frame"] == res_b["release_frame"]]
                        if not r_b.empty:
                            f_b = pitch_logic.draw_skeleton(f_b, r_b.iloc[0], draw_labels=False)
                        st.image(cv2.cvtColor(f_b, cv2.COLOR_BGR2RGB), width="stretch")

            # 指標比較テーブル
            st.markdown(f"#### {i18n.t('diff_table_title', lang)}")

            sp_a = res_a.get("spin_data", {})
            sp_b = res_b.get("spin_data", {})
            diff_rpm = sp_a.get("spin_rate_rpm", 0) - sp_b.get("spin_rate_rpm", 0)
            diff_eff = sp_a.get("active_spin_pct", 0.0) - sp_b.get("active_spin_pct", 0.0)
            diff_gyro = sp_a.get("gyro_angle_deg", 0.0) - sp_b.get("gyro_angle_deg", 0.0)
            diff_ivb = sp_a.get("ivb_cm", 0.0) - sp_b.get("ivb_cm", 0.0)
            diff_hb = sp_a.get("hb_cm", 0.0) - sp_b.get("hb_cm", 0.0)

            cmp_df = pd.DataFrame({
                i18n.t("metric_name", lang): [
                    f"{i18n.t('velocity_score', lang)} ({speed_unit})",
                    f"{i18n.t('perceived_velocity', lang)} ({speed_unit})",
                    i18n.t("overall_score", lang),
                    f"{i18n.t('spin_rate_label', lang)} (rpm)",
                    f"{i18n.t('spin_eff_label', lang)} (%)",
                    f"{i18n.t('gyro_angle_label', lang)} (°)",
                    f"{i18n.t('ivb_label', lang)} (cm)",
                    f"{i18n.t('hb_label', lang)} (cm)",
                    f"{i18n.t('extension', lang)} ({dist_unit})",
                    f"{i18n.t('pitch_distance', lang)} ({dist_unit})",
                    f"{i18n.t('stride_ratio', lang)} (%)",
                    f"{i18n.t('elbow_angle', lang)} (°)",
                    f"{i18n.t('knee_angle', lang)} (°)",
                    f"{i18n.t('arm_slot', lang)} (°)",
                    i18n.t("form_type", lang),
                ],
                f"{i18n.t('pitch_a', lang)} ({vid_a})": [
                    f"{spd_a:.1f}",
                    f"{pspd_a:.1f}",
                    f"{fb_a['grade']} ({fb_a['score']})",
                    f"{sp_a.get('spin_rate_rpm', 0):,} rpm",
                    f"{sp_a.get('active_spin_pct', 0.0):.1f}%",
                    f"{sp_a.get('gyro_angle_deg', 0.0):.1f}°",
                    f"{sp_a.get('ivb_cm', 0.0):+.1f} cm",
                    f"{sp_a.get('hb_cm', 0.0):+.1f} cm",
                    f"{ext_a:.2f}",
                    f"{dst_a:.2f}",
                    f"{res_a['biomechanics'].get('stride_pct', 0):.1f}%",
                    f"{res_a['biomechanics'].get('elbow_angle', 0):.1f}",
                    f"{res_a['biomechanics'].get('lead_knee_angle', 0):.1f}",
                    f"{res_a['biomechanics'].get('forearm_slot', 0):.1f}",
                    i18n.get_slot_name(res_a['biomechanics'].get('slot_name', '-'), lang),
                ],
                f"{i18n.t('pitch_b', lang)} ({vid_b})": [
                    f"{spd_b:.1f}",
                    f"{pspd_b:.1f}",
                    f"{fb_b['grade']} ({fb_b['score']})",
                    f"{sp_b.get('spin_rate_rpm', 0):,} rpm",
                    f"{sp_b.get('active_spin_pct', 0.0):.1f}%",
                    f"{sp_b.get('gyro_angle_deg', 0.0):.1f}°",
                    f"{sp_b.get('ivb_cm', 0.0):+.1f} cm",
                    f"{sp_b.get('hb_cm', 0.0):+.1f} cm",
                    f"{ext_b:.2f}",
                    f"{dst_b:.2f}",
                    f"{res_b['biomechanics'].get('stride_pct', 0):.1f}%",
                    f"{res_b['biomechanics'].get('elbow_angle', 0):.1f}",
                    f"{res_b['biomechanics'].get('lead_knee_angle', 0):.1f}",
                    f"{res_b['biomechanics'].get('forearm_slot', 0):.1f}",
                    i18n.get_slot_name(res_b['biomechanics'].get('slot_name', '-'), lang),
                ],
                i18n.t("difference", lang): [
                    f"{diff_speed:+.1f}",
                    f"{diff_pspeed:+.1f}",
                    f"{diff_score:+d}",
                    f"{diff_rpm:+d} rpm",
                    f"{diff_eff:+.1f}%",
                    f"{diff_gyro:+.1f}°",
                    f"{diff_ivb:+.1f} cm",
                    f"{diff_hb:+.1f} cm",
                    f"{diff_ext:+.2f}",
                    f"{diff_dist:+.2f}",
                    f"{(res_a['biomechanics'].get('stride_pct', 0) - res_b['biomechanics'].get('stride_pct', 0)):+.1f}%",
                    f"{diff_elb:+.1f}",
                    f"{diff_knee:+.1f}",
                    f"{diff_slot:+.1f}",
                    "-",
                ],
            })
            st.dataframe(cmp_df, width="stretch", hide_index=True)
            # --- 3D回転ボール比較 (Side-by-Side 3D Spinning Balls) ---
            st.markdown(f"##### {i18n.t('spin_clock_title', lang)}")
            c3d_a, c3d_b = st.columns(2)
            with c3d_a:
                lbl_a = f"{res_a.get('video', 'Pitch A')} ({sp_a.get('spin_axis', '12:00')}, {sp_a.get('spin_rate_rpm', 0):,} rpm)"
                st.caption(f"**🔴 {lbl_a}**")
                html_a = baseball_3d_component.generate_3d_spinning_baseball_html(
                    spin_axis_str=sp_a.get("spin_axis", "12:00"),
                    spin_rate_rpm=sp_a.get("spin_rate_rpm", 1800),
                    active_spin_pct=sp_a.get("active_spin_pct", 85.0),
                    gyro_angle_deg=sp_a.get("gyro_angle_deg", 25.0),
                    lang=lang,
                    ivb_cm=sp_a.get("ivb_cm", 35.0),
                    hb_cm=sp_a.get("hb_cm", 15.0),
                )
                components.html(html_a, height=310)
            with c3d_b:
                lbl_b = f"{res_b.get('video', 'Pitch B')} ({sp_b.get('spin_axis', '12:00')}, {sp_b.get('spin_rate_rpm', 0):,} rpm)"
                st.caption(f"**🔵 {lbl_b}**")
                html_b = baseball_3d_component.generate_3d_spinning_baseball_html(
                    spin_axis_str=sp_b.get("spin_axis", "12:00"),
                    spin_rate_rpm=sp_b.get("spin_rate_rpm", 1800),
                    active_spin_pct=sp_b.get("active_spin_pct", 85.0),
                    gyro_angle_deg=sp_b.get("gyro_angle_deg", 25.0),
                    lang=lang,
                    ivb_cm=sp_b.get("ivb_cm", 35.0),
                    hb_cm=sp_b.get("hb_cm", 15.0),
                )
                components.html(html_b, height=310)

            # --- 2. ピッチトンネル＆コミットポイント3D可視化 ---
            st.markdown("---")
            st.markdown(f"#### {i18n.t('pitch_tunnel_header', lang)}")

            # 3Dピッチトンネル視点切り替えラジオ（捕手視点、投手視点、側面、真上）
            tunnel_cam_keys = ["catcher", "pitcher", "side", "top"]
            tunnel_cam_labels = {
                "catcher": i18n.t("tunnel_view_catcher", lang),
                "pitcher": i18n.t("tunnel_view_pitcher", lang),
                "side": i18n.t("tunnel_view_side", lang),
                "top": i18n.t("tunnel_view_top", lang),
            }
            sel_tunnel_cam = st.radio(
                i18n.t("camera_view_label", lang),
                tunnel_cam_keys,
                index=0,
                format_func=lambda k: tunnel_cam_labels[k],
                horizontal=True,
                key=f"tunnel_cam_radio_{vid_a}_{vid_b}",
            )

            tunnel_fig, tunnel_met = pitch_logic.generate_pitch_tunnel_figure(
                res_a, res_b, dist_unit=dist_unit, lang=lang, camera_view=sel_tunnel_cam
            )
            t_m1, t_m2, t_m3 = st.columns(3)
            t_m1.metric(i18n.t("commit_dist_label", lang), f"{tunnel_met['commit_cm']} cm")
            t_m2.metric(i18n.t("plate_dist_label", lang), f"{tunnel_met['plate_cm']} cm")
            t_m3.metric(i18n.t("tunnel_ratio_label", lang), f"{tunnel_met['ratio']}x", delta=tunnel_met['rating'], delta_color="off")
            st.plotly_chart(tunnel_fig, width="stretch", key="pitch_tunnel_chart")
            st.caption(i18n.t("3d_mouse_hint", lang))

            # --- 4. 2投球フォーム完全同期スプリット再生 (Sync Player) ---
            st.markdown("---")
            st.markdown(f"#### {i18n.t('sync_player_header', lang)}")
            sync_off = st.slider(
                i18n.t("sync_frame_label", lang),
                min_value=-15, max_value=15, value=0, step=1,
                format="%+d frame", key="compare_sync_frame_slider"
            )
            img_a, img_b = pitch_logic.get_synced_compare_frames(
                res_a.get("video", ""), res_b.get("video", ""),
                res_a.get("release_frame", 0), res_b.get("release_frame", 0),
                offset_frame=sync_off, kp_df_a=res_a.get("kp_df"), kp_df_b=res_b.get("kp_df")
            )
            sync_col1, sync_col2 = st.columns(2)
            with sync_col1:
                lbl_a_sync = f"🔴 {res_a.get('video', 'Pitch A')} (Frame {res_a.get('release_frame', 0) + sync_off})"
                st.image(img_a, caption=lbl_a_sync, width="stretch")
            with sync_col2:
                lbl_b_sync = f"🔵 {res_b.get('video', 'Pitch B')} (Frame {res_b.get('release_frame', 0) + sync_off})"
                st.image(img_b, caption=lbl_b_sync, width="stretch")


    alexa_experience.render_alexa_experience_tab(
        tab_alexa,
        build_alexa_pitch_context(res, feedback),
        lang,
    )

else:
    with tab_main:
        st.markdown('<div class="card" style="text-align: center; padding: 35px 20px;">', unsafe_allow_html=True)
        st.markdown("### ⚾ Outpace Baseball")
        st.info("👈 左側のサイドバーにある「動画アップロード」から投球動画（MP4/MOV）をアップロードして解析を開始してください。" if lang == "ja" else "👈 Please upload a pitch video (MP4/MOV) from the sidebar to begin analysis.")
        
        sample_title = "📥 審査・デモ用サンプル動画（クリックしてダウンロード）" if lang == "ja" else "📥 Demo Sample Videos (Click to download)"
        st.markdown(f"<div style='margin-top: 18px; font-weight: bold; font-size: 14px;'>{sample_title}</div>", unsafe_allow_html=True)
        st.markdown(
            """<div style="display: flex; justify-content: center; gap: 12px; margin-top: 10px; flex-wrap: wrap;">
                <a href="https://github.com/hirokuwa821/Outpose-Baseball/releases/download/sample-videos/pitch_102_1.mp4" target="_blank" style="text-decoration: none; background: #ff4b4b; color: white; padding: 8px 16px; border-radius: 6px; font-weight: bold; font-size: 13px;">📥 Sample 1: 102 km/h (1.2MB)</a>
                <a href="https://github.com/hirokuwa821/Outpose-Baseball/releases/download/sample-videos/pitch_98_1.mp4" target="_blank" style="text-decoration: none; background: #1e293b; border: 1px solid #475569; color: white; padding: 8px 16px; border-radius: 6px; font-weight: bold; font-size: 13px;">📥 Sample 2: 98 km/h (1.8MB)</a>
                <a href="https://github.com/hirokuwa821/Outpose-Baseball/releases/tag/sample-videos" target="_blank" style="text-decoration: none; background: #0284c7; color: white; padding: 8px 16px; border-radius: 6px; font-weight: bold; font-size: 13px;">📦 GitHub Release ページ</a>
            </div>""",
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_compare:
        st.info("動画を解析すると、ここで2球のフォーム・軌道比較が行えます。" if lang == "ja" else "Analyze videos to compare 2 pitches here.")
    alexa_experience.render_alexa_experience_tab(tab_alexa, None, lang)

# Render history regardless of whether an analysis result is loaded.
render_pitch_history(tab_history, lang, speed_unit, dist_unit)
