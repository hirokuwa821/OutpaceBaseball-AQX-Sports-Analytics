import hashlib
import json
import math
from pathlib import Path

import pandas as pd
import streamlit as st

import aws_utils


def add_previous_pitch_from_history(context, current_video, history_file):
    history_path = Path(history_file)
    if not history_path.exists():
        return context

    pitch_history = pd.read_csv(history_path, on_bad_lines="skip")
    if pitch_history.empty or not {"video", "speed"}.issubset(pitch_history.columns):
        return context

    previous_pitches = pitch_history[pitch_history["video"] != current_video]
    if previous_pitches.empty:
        return context

    previous = previous_pitches.iloc[-1]

    def finite_history_value(key, decimals):
        try:
            number = float(previous.get(key))
        except (TypeError, ValueError):
            return None
        return round(number, decimals) if math.isfinite(number) else None

    previous_pitch = {
        "pitch_type": previous.get("pitch_type")
        if isinstance(previous.get("pitch_type"), str)
        else None,
        "speed_kmh": finite_history_value("speed", 2),
        "extension_m": finite_history_value("extension", 2),
        "pitch_distance_m": finite_history_value("distance", 2),
        "spin_rate_rpm": finite_history_value("spin_rate", 1),
        "gyro_angle_deg": finite_history_value("gyro_angle", 2),
        "ivb_cm": finite_history_value("ivb_cm", 2),
        "hb_cm": finite_history_value("hb_cm", 2),
        "source": "saved pitch history",
    }
    if previous_pitch["speed_kmh"] is not None:
        context["previous_pitch"] = previous_pitch
    return context


def render_alexa_experience_tab(tab, pitch_context, current_lang):
    with tab:
        st.subheader("Alexa+ Experience Simulation")
        st.caption(
            "Text-only conversation simulation. This does not use Alexa devices, "
            "speech recognition, or speech synthesis."
        )
        if pitch_context is None:
            st.info(
                "現在の投球解析データはありません。個別の投球について回答するには、"
                "左側から動画を選んで解析してください。Bedrockが利用できる場合は、"
                "一般的な助言であることを明示したうえで質問に回答します。"
                if current_lang == "ja"
                else "There is no current pitch analysis. Analyze a video from the sidebar "
                "for personalized feedback. If Bedrock is available, you can still ask "
                "questions and receive clearly labeled general advice."
            )
        else:
            st.caption(
                "解析済みの球速・投球指標とルール診断を必要な範囲で利用します。"
                "動画や姿勢座標は送信しません。"
                if current_lang == "ja"
                else "Answers use selected computed pitch metrics and rule-based feedback. "
                "Raw video and pose coordinates are not sent."
            )

        fingerprint_payload = (
            json.dumps(pitch_context, ensure_ascii=False, sort_keys=True, allow_nan=False)
            if pitch_context is not None
            else "no-current-analysis"
        )
        fingerprint = hashlib.sha256(fingerprint_payload.encode("utf-8")).hexdigest()
        if st.session_state.get("alexa_context_fingerprint") != fingerprint:
            st.session_state["alexa_context_fingerprint"] = fingerprint
            st.session_state["alexa_chat_messages"] = []
            st.session_state.pop("alexa_chat_error", None)

        st.markdown("**質問例**" if current_lang == "ja" else "**Try asking**")
        examples = (
            ["球速を上げるには？", "今回の投球で改善すべき点は？", "前回と今回の投球を比較して"]
            if current_lang == "ja"
            else [
                "How can I increase my velocity?",
                "What should I improve in this pitch?",
                "Compare my previous and current pitches.",
            ]
        )
        example_cols = st.columns(len(examples))
        selected_question = None
        for index, (column, example) in enumerate(zip(example_cols, examples)):
            if column.button(example, key=f"alexa_example_{index}"):
                selected_question = example

        for message in st.session_state["alexa_chat_messages"]:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        prior_error = st.session_state.pop("alexa_chat_error", None)
        if prior_error:
            st.error(prior_error)

        typed_question = st.chat_input(
            "投球について質問してください…" if current_lang == "ja" else "Ask about your pitching…",
            key="alexa_chat_input",
        )
        question = selected_question or typed_question
        if question:
            messages = st.session_state["alexa_chat_messages"]
            history = messages[-8:]
            messages.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.write(question)
            with st.chat_message("assistant"):
                with st.spinner("Amazon Bedrockに質問しています…"):
                    result = aws_utils.generate_bedrock_conversation_response(
                        question,
                        pitch_context,
                        history=history,
                        language=current_lang,
                    )
                if result.success and result.feedback:
                    answer = result.feedback["response"]
                    messages.append({"role": "assistant", "content": answer})
                    st.write(answer)
                else:
                    st.session_state["alexa_chat_error"] = result.message
                    st.error(result.message)
