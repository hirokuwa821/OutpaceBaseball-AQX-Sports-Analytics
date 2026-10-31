import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from history_tracker import prepare_pitch_history


class PitchHistoryTests(unittest.TestCase):
    def test_converts_metrics_and_timestamps_for_charting(self):
        history = pd.DataFrame(
            {
                "timestamp": ["2026-10-20 12:00:00", "invalid"],
                "speed": ["120.5", "not-a-number"],
                "extension": ["1.8", "2.0"],
                "video": ["pitch-a", "pitch-b"],
            }
        )

        prepared = prepare_pitch_history(history)

        self.assertEqual(prepared.loc[0, "speed"], 120.5)
        self.assertEqual(prepared.loc[0, "extension"], 1.8)
        self.assertTrue(pd.isna(prepared.loc[1, "timestamp"]))
        self.assertTrue(pd.isna(prepared.loc[1, "speed"]))
        self.assertEqual(prepared.loc[0, "video"], "pitch-a")

    def test_reports_missing_required_history_columns(self):
        with self.assertRaisesRegex(ValueError, "extension"):
            prepare_pitch_history(
                pd.DataFrame({"timestamp": [], "speed": []})
            )

    def test_header_only_history_is_valid_and_empty(self):
        prepared = prepare_pitch_history(
            pd.DataFrame(columns=["timestamp", "speed", "extension"])
        )

        self.assertTrue(prepared.empty)
        self.assertEqual(
            list(prepared.columns),
            ["timestamp", "speed", "extension"],
        )


if __name__ == "__main__":
    unittest.main()
