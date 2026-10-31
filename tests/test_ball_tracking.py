import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ball_tracking import build_track, interpolate_track
import pitch_logic


class BallTrackingTests(unittest.TestCase):
    def test_track_connects_detections_and_interpolates_short_gaps_in_frame_order(self):
        detections_by_frame = {
            frame: [{"cx": 100.0 + frame, "cy": 200.0 + frame, "confidence": 0.8}]
            for frame in range(10, 19)
            if frame != 13
        }

        track = build_track(detections_by_frame)
        points = interpolate_track(track)

        self.assertEqual([point["frame"] for point in points], list(range(10, 19)))
        self.assertEqual(points[3]["interpolated"], 1)
        self.assertEqual(points[2]["interpolated"], 0)
        self.assertEqual(points[4]["interpolated"], 0)

    def test_short_or_missing_detections_do_not_create_a_track(self):
        detections_by_frame = {
            frame: [{"cx": frame * 2.0, "cy": frame * 2.0, "confidence": 0.9}]
            for frame in range(5)
        }

        self.assertEqual(build_track({}), [])
        self.assertEqual(build_track(detections_by_frame), [])


class StrikeZoneTests(unittest.TestCase):
    def _call(self, cx, cy, frame=70, **kwargs):
        import pandas as pd

        camera_calibrated = kwargs.pop("camera_calibrated", True)
        ball_df = pd.DataFrame(
            [
                {
                    "frame": frame,
                    "cx": cx,
                    "cy": cy,
                    "confidence": 0.9,
                    "interpolated": 0,
                }
            ]
        )
        return pitch_logic.generate_strike_zone_figure(
            ball_df,
            net_frame=70,
            release_frame=50,
            camera_calibrated=camera_calibrated,
            **kwargs,
        )

    def test_strike_zone_boundaries_are_inclusive(self):
        for cx, cy in ((206, 370), (274, 370), (240, 347), (240, 393)):
            with self.subTest(cx=cx, cy=cy):
                _, call = self._call(cx, cy)
                self.assertIn("ストライク", call)

    def test_point_just_outside_zone_is_a_ball(self):
        _, call = self._call(274.01, 370)
        self.assertIn("ボール", call)

    def test_short_real_detection_gap_is_interpolated_at_net_frame(self):
        import pandas as pd

        ball_df = pd.DataFrame(
            [
                {"frame": 68, "cx": 259.494, "cy": 393.211, "confidence": 0.45, "interpolated": 0},
                {"frame": 72, "cx": 256.343, "cy": 380.743, "confidence": 0.17, "interpolated": 0},
            ]
        )
        fig, call = pitch_logic.generate_strike_zone_figure(
            ball_df,
            net_frame=70,
            release_frame=50,
            camera_calibrated=True,
        )

        self.assertIn("ストライク", call)
        point = next(trace for trace in fig.data if trace.name == "Impact Point")
        self.assertAlmostEqual(float(point.x[0]), (257.9185 - 240) / 34, places=4)
        self.assertAlmostEqual(float(point.y[0]), 2 + (370 - 386.977) / 23, places=4)

    def test_scaled_video_coordinates_use_the_same_calibration(self):
        _, call = self._call(
            548,
            740,
            frame_width=1440,
            frame_height=2560,
        )
        self.assertIn("ストライク", call)

    def test_uncalibrated_or_differently_framed_video_is_not_called(self):
        _, uncalibrated_call = self._call(240, 370, camera_calibrated=False)
        _, cropped_call = self._call(
            240,
            370,
            frame_width=1280,
            frame_height=720,
        )

        self.assertIn("判定不可", uncalibrated_call)
        self.assertIn("判定不可", cropped_call)

    def test_missing_interpolated_or_distant_detection_is_not_called(self):
        cases = [
            (None, 70),
            (
                {
                    "frame": 70,
                    "cx": 240,
                    "cy": 370,
                    "confidence": 0,
                    "interpolated": 1,
                },
                70,
            ),
            (
                {
                    "frame": 66,
                    "cx": 240,
                    "cy": 370,
                    "confidence": 0.9,
                    "interpolated": 0,
                },
                66,
            ),
        ]
        import pandas as pd

        for row, frame in cases:
            with self.subTest(row=row):
                ball_df = pd.DataFrame([row]) if row else None
                fig, call = pitch_logic.generate_strike_zone_figure(
                    ball_df,
                    net_frame=70,
                    release_frame=50,
                    camera_calibrated=True,
                )
                self.assertIn("判定不可", call)
                self.assertFalse(
                    any(trace.name == "Impact Point" for trace in fig.data)
                )


if __name__ == "__main__":
    unittest.main()
