import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import alexa_experience
from aws_utils import AWSOperationResult


class AlexaExperienceTests(unittest.TestCase):
    def setUp(self):
        self.streamlit = MagicMock()
        self.streamlit.session_state = {}
        self.streamlit.columns.return_value = [Mock(), Mock(), Mock()]
        for column in self.streamlit.columns.return_value:
            column.button.return_value = False
        self.tab = MagicMock()

    def test_previous_pitch_uses_saved_metrics_without_video_identifier(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            history_file = Path(temp_dir) / "analysis_history.csv"
            history_file.write_text(
                "video,pitch_type,speed,extension,distance,spin_rate,gyro_angle,ivb_cm,hb_cm\n"
                "previous-video,fastball,115.2,1.8,16.6,2100,35,38,12\n"
                "current-video,slider,120.5,2.0,16.4,2200,30,40,10\n",
                encoding="utf-8",
            )

            context = alexa_experience.add_previous_pitch_from_history(
                {"current_pitch": {"speed_kmh": 120.5}},
                "current-video",
                history_file,
            )

        self.assertEqual(context["previous_pitch"]["speed_kmh"], 115.2)
        self.assertEqual(context["previous_pitch"]["pitch_type"], "fastball")
        self.assertEqual(context["previous_pitch"]["source"], "saved pitch history")
        self.assertNotIn("video", context["previous_pitch"])
        self.assertNotIn("current-video", str(context))

    def test_missing_history_does_not_create_a_previous_pitch(self):
        context = {"current_pitch": {"speed_kmh": 120.5}}
        with tempfile.TemporaryDirectory() as temp_dir:
            result = alexa_experience.add_previous_pitch_from_history(
                context,
                "current-video",
                Path(temp_dir) / "missing.csv",
            )

        self.assertIs(result, context)
        self.assertNotIn("previous_pitch", result)

    def test_no_analysis_renders_guidance_and_submits_without_metrics(self):
        self.streamlit.chat_input.return_value = "今回の投球で改善すべき点は？"
        bedrock_result = AWSOperationResult(
            success=True,
            message="ok",
            feedback={"response": "一般的な助言です。"},
        )
        with (
            patch.object(alexa_experience, "st", self.streamlit),
            patch.object(
                alexa_experience.aws_utils,
                "generate_bedrock_conversation_response",
                return_value=bedrock_result,
            ) as generate_response,
        ):
            alexa_experience.render_alexa_experience_tab(self.tab, None, "ja")

        self.streamlit.info.assert_called_once()
        self.assertIn("解析データはありません", self.streamlit.info.call_args.args[0])
        generate_response.assert_called_once_with(
            "今回の投球で改善すべき点は？",
            None,
            history=[],
            language="ja",
        )
        self.assertEqual(
            self.streamlit.session_state["alexa_chat_messages"],
            [
                {"role": "user", "content": "今回の投球で改善すべき点は？"},
                {"role": "assistant", "content": "一般的な助言です。"},
            ],
        )

    def test_saved_messages_are_rendered_on_the_next_run(self):
        context = {"current_pitch": {"speed_kmh": 120.5}}
        context_fingerprint = hashlib.sha256(
            json.dumps(context, ensure_ascii=False, sort_keys=True, allow_nan=False).encode("utf-8")
        ).hexdigest()
        self.streamlit.session_state.update(
            {
                "alexa_context_fingerprint": context_fingerprint,
                "alexa_chat_messages": [
                    {"role": "user", "content": "球速は？"},
                    {"role": "assistant", "content": "解析値を確認します。"},
                ],
            }
        )
        self.streamlit.chat_input.return_value = None

        with patch.object(alexa_experience, "st", self.streamlit):
            alexa_experience.render_alexa_experience_tab(
                self.tab,
                context,
                "ja",
            )

        rendered_roles = [call.args[0] for call in self.streamlit.chat_message.call_args_list]
        self.assertEqual(rendered_roles, ["user", "assistant"])
        self.assertEqual(
            self.streamlit.write.call_args_list,
            [unittest.mock.call("球速は？"), unittest.mock.call("解析値を確認します。")],
        )

    def test_bedrock_error_is_displayed_and_user_question_is_kept(self):
        self.streamlit.chat_input.return_value = "前回と今回の投球を比較して"
        bedrock_error = AWSOperationResult(
            success=False,
            message="Amazon Bedrock is unavailable. Local analysis is still available.",
        )
        with (
            patch.object(alexa_experience, "st", self.streamlit),
            patch.object(
                alexa_experience.aws_utils,
                "generate_bedrock_conversation_response",
                return_value=bedrock_error,
            ),
        ):
            alexa_experience.render_alexa_experience_tab(
                self.tab,
                {"current_pitch": {"speed_kmh": 120.5}},
                "ja",
            )

        self.streamlit.error.assert_called_once_with(bedrock_error.message)
        self.assertEqual(
            self.streamlit.session_state["alexa_chat_messages"],
            [{"role": "user", "content": "前回と今回の投球を比較して"}],
        )

    def test_changed_analysis_context_starts_a_fresh_conversation(self):
        self.streamlit.session_state.update(
            {
                "alexa_context_fingerprint": "old-context",
                "alexa_chat_messages": [{"role": "user", "content": "old question"}],
            }
        )
        self.streamlit.chat_input.return_value = None

        with patch.object(alexa_experience, "st", self.streamlit):
            alexa_experience.render_alexa_experience_tab(
                self.tab,
                {"current_pitch": {"speed_kmh": 120.5}},
                "ja",
            )

        self.assertEqual(self.streamlit.session_state["alexa_chat_messages"], [])


if __name__ == "__main__":
    unittest.main()
