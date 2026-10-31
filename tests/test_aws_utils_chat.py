import unittest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

from botocore.exceptions import ClientError, NoCredentialsError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import aws_utils


class BedrockConversationTests(unittest.TestCase):
    def setUp(self):
        self.session = Mock()
        self.session.get_credentials.return_value = object()
        self.client = Mock()
        self.session.client.return_value = self.client
        self.client.converse.return_value = {
            "output": {
                "message": {
                    "content": [{"text": "解析データでは球速が計測されています。"}]
                }
            }
        }
        self.session.region_name = "ap-northeast-1"

    @patch("aws_utils.boto3.Session")
    def test_japanese_question_uses_compact_pitch_context(self, session_factory):
        session_factory.return_value = self.session
        context = {
            "current_pitch": {"speed_kmh": 120.5},
            "current_rule_based_diagnosis": {"improvements": ["踏み出し"]},
        }

        result = aws_utils.generate_bedrock_conversation_response(
            "球速を上げるには？",
            context,
            language="ja",
        )

        self.assertTrue(result.success)
        self.assertEqual(
            result.feedback["response"],
            "解析データでは球速が計測されています。",
        )
        request = self.client.converse.call_args.kwargs
        self.assertEqual(request["modelId"], aws_utils.DEFAULT_BEDROCK_MODEL_ID)
        self.assertEqual(request["messages"][-1]["role"], "user")
        request_text = request["messages"][-1]["content"][0]["text"]
        self.assertIn("球速を上げるには？", request_text)
        self.assertIn('"speed_kmh": 120.5', request_text)
        self.assertNotIn("video", request_text)
        self.assertNotIn("pose", request_text)
        self.assertIn("Japanese", request["system"][0]["text"])

    @patch("aws_utils.boto3.Session")
    def test_no_analysis_is_explicitly_marked_as_general_guidance(self, session_factory):
        session_factory.return_value = self.session

        result = aws_utils.generate_bedrock_conversation_response(
            "今回の投球で改善すべき点は？",
            None,
            language="ja",
        )

        self.assertTrue(result.success)
        request = self.client.converse.call_args.kwargs
        prompt = request["messages"][-1]["content"][0]["text"]
        system_prompt = request["system"][0]["text"]
        self.assertIn("No current pitch analysis is available.", prompt)
        self.assertIn("general advice explicitly labeled as general", system_prompt)
        self.assertIn("analyze a video", system_prompt)

    @patch("aws_utils.boto3.Session")
    def test_conversation_history_is_sent_in_order(self, session_factory):
        session_factory.return_value = self.session
        history = [
            {"role": "user", "content": "球速は何キロでしたか？"},
            {"role": "assistant", "content": "解析値は120.5 km/hです。"},
        ]

        result = aws_utils.generate_bedrock_conversation_response(
            "どの練習がよいですか？",
            {"current_pitch": {"speed_kmh": 120.5}},
            history=history,
            language="ja",
        )

        self.assertTrue(result.success)
        messages = self.client.converse.call_args.kwargs["messages"]
        self.assertEqual([message["role"] for message in messages], ["user", "assistant", "user"])
        self.assertIn("120.5", messages[1]["content"][0]["text"])

    @patch("aws_utils.boto3.Session")
    def test_incomplete_failed_turn_is_not_replayed_as_history(self, session_factory):
        session_factory.return_value = self.session
        history = [
            {"role": "user", "content": "前の質問"},
            {"role": "assistant", "content": "前の回答"},
            {"role": "user", "content": "Bedrockで失敗した質問"},
        ]

        result = aws_utils.generate_bedrock_conversation_response(
            "次の質問",
            None,
            history=history,
            language="ja",
        )

        self.assertTrue(result.success)
        messages = self.client.converse.call_args.kwargs["messages"]
        self.assertEqual([message["role"] for message in messages], ["user", "assistant", "user"])
        self.assertNotIn("Bedrockで失敗した質問", str(messages))
        self.assertIn("次の質問", messages[-1]["content"][0]["text"])

    @patch("aws_utils.boto3.Session")
    def test_missing_credentials_returns_clear_error(self, session_factory):
        self.session.get_credentials.return_value = None
        session_factory.return_value = self.session

        result = aws_utils.generate_bedrock_conversation_response(
            "球速を上げるには？",
            None,
            language="ja",
        )

        self.assertFalse(result.success)
        self.assertIn("AWS credentials are not configured", result.message)

    @patch("aws_utils.boto3.Session")
    def test_bedrock_service_error_returns_clear_error(self, session_factory):
        session_factory.return_value = self.session
        self.client.converse.side_effect = ClientError(
            {"Error": {"Code": "AccessDeniedException"}},
            "Converse",
        )

        result = aws_utils.generate_bedrock_conversation_response(
            "前回と今回の投球を比較して",
            {"current_pitch": {"speed_kmh": 120.5}},
            language="ja",
        )

        self.assertFalse(result.success)
        self.assertIn("AccessDeniedException", result.message)

    def test_invalid_question_is_rejected_before_calling_aws(self):
        with patch("aws_utils.boto3.Session") as session_factory:
            result = aws_utils.generate_bedrock_conversation_response(
                "   ",
                None,
                language="ja",
            )

        self.assertFalse(result.success)
        self.assertIn("enter a question", result.message)
        session_factory.assert_not_called()

    @patch("aws_utils.boto3.Session")
    def test_empty_bedrock_response_is_reported(self, session_factory):
        session_factory.return_value = self.session
        self.client.converse.return_value = {"output": {"message": {"content": []}}}

        result = aws_utils.generate_bedrock_conversation_response(
            "球速を上げるには？",
            None,
            language="ja",
        )

        self.assertFalse(result.success)
        self.assertIn("empty response", result.message)


if __name__ == "__main__":
    unittest.main()
