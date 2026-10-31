# Outpace Baseball — AQX Sports Analytics Data Bowl 4.0

## Project Overview

Outpace Baseball is a video-based pitching analysis application built to turn a single pitching clip into understandable performance measurements and practical next steps. It combines computer vision, video-derived estimates, rule-based interpretation, and optional AI coaching to make useful pitching analysis more accessible to players and coaches.

This AQX project preserves the Amazon edition's analysis workflows and AWS integrations. Metrics are estimates from the available video, not laboratory measurements or official calls.

## Inspiration

High-quality motion analysis is often expensive or unavailable to amateur players. A phone video can still reveal useful patterns when its limitations are made clear. We wanted to help players review measurable aspects of a pitch, compare sessions, and translate observations into focused practice ideas.

## What It Does

Users can analyze a pitching video and review the measurements and visualizations the clip supports. The application estimates pitch speed and other available pitch or biomechanics metrics, visualizes detected body keypoints, and can track the baseball when the authorized ball-detection model is installed. A camera-calibrated strike-zone estimate is shown only when the required real detections and supported video conditions are available.

Analysis results can be reviewed alongside local pitch history. The rule-based diagnosis highlights possible areas to work on, while the optional Amazon Bedrock coach can turn available metrics and that diagnosis into personalized suggestions. The AI integration sends structured analysis context rather than raw video or pose-coordinate frames.

## How We Built It

- **Python and Streamlit** provide the interactive application.
- **OpenCV** reads and processes video frames and produces visual analysis output.
- **Ultralytics YOLO pose** detects body keypoints for pitching-mechanics analysis.
- **A project-specific YOLO ball detector** supports ball tracking and related estimates when an authorized weight file is available.
- **Pandas and Plotly** support history, metric review, and visualizations.
- Existing application logic derives video-based pitch metrics and rule-based coaching observations.
- **boto3** connects optional cloud features to Amazon Bedrock and Amazon S3.

## AWS Services

| Service | Use |
| --- | --- |
| Amazon Bedrock Runtime | Generates pitching feedback and conversational coaching from available structured metrics. |
| Amazon S3 | Optionally archives uploaded videos and structured analysis data in the user's configured bucket. |

AWS is optional. Local application startup and local analysis do not require AWS credentials. Bedrock and S3 actions require a configured AWS identity, Region, permissions, and (for Bedrock) model access. The application reports AWS errors rather than treating an unavailable service as a successful operation.

## Key Features

- Pitching-video processing with OpenCV and YOLO pose keypoints.
- Video-based pitch-speed and available biomechanics estimates.
- Ball detection, short-gap tracking, trajectory visualization, and a camera-calibrated strike-zone estimate when supported by real detections.
- Rule-based analysis and actionable improvement suggestions.
- Local pitch-analysis history and pitch-to-pitch comparisons.
- Optional Amazon Bedrock AI Pitching Coach and text-based conversational coaching.
- Optional Amazon S3 archiving of videos and structured analysis.
- English and Japanese user-facing text.
- Existing RevenueCat integration code is retained for projects that configure its optional purchase flow.

## Challenges

Video quality, camera position, lighting, and occlusion affect pose and ball detection. A 2D clip cannot provide the same evidence as calibrated multi-camera capture, and image-plane movement should not be mistaken for physical ball movement. The application therefore treats speed and biomechanics as estimates and avoids a strike-zone call when the required calibrated evidence is missing.

Cloud services add their own setup requirements: AWS credentials, Region, least-privilege permissions, S3 configuration, and Bedrock model access. The app keeps local workflows available when cloud configuration is absent. Model weights are not included because redistribution rights have not been established.

## Future Plans

- Evaluate estimates against appropriately collected reference measurements and a broader range of pitchers and camera setups.
- Improve confidence reporting and guidance for recording videos that produce useful analysis.
- Explore AQX-compatible data exports and aggregate analysis, subject to the event's data format and rules.
- Expand longitudinal comparisons and coaching recommendations while keeping uncertainty visible.
- Verify cloud behavior and model licensing in the intended deployment environment.

## Installation and Usage

### Requirements

- Python 3.12 is the development environment used for this project.
- Git (if cloning the AQX repository after it is created).
- Optional: an AWS account and configured permissions for Bedrock or S3.
- Authorized model weights for the YOLO workflows (see **Model Files and Licensing**).

### Set up locally

From the project directory, create and activate a virtual environment, then install the pinned dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Start the application:

```powershell
python -m streamlit run src/app.py
```

Open the local URL printed by Streamlit. The application creates its `videos/` and `output/` working directories as needed; generated clips, histories, and uploaded personal videos are not part of this source copy.

Run the automated tests with:

```powershell
python -m unittest discover -s tests -v
```

### Optional AWS setup

1. Copy `.env.example` to `.env` and set only the non-secret application settings you need, such as `AWS_REGION`, `S3_BUCKET`, and optionally `BEDROCK_MODEL_ID`.
2. Provide AWS credentials through a standard boto3 provider (for example, an AWS profile or an attached IAM role). Do not place AWS access keys in `.env`, Streamlit secrets, or source control.
3. Grant only the permissions needed for the configured S3 objects and Bedrock model invocation.

With no AWS credentials, the app still starts and local analysis remains available. Cloud actions require working AWS configuration and show an explicit error when they cannot be completed.

### Model Files and Licensing

Model weights are intentionally not included in this repository and are ignored by Git:

- The pose workflow looks for `yolo11n-pose.pt` in the project root. Obtain an authorized copy through the official [Ultralytics YOLO11 documentation](https://docs.ultralytics.com/models/yolo11/).
- Ball tracking looks for `models/ball_detector.pt`. This is a project-specific fine-tuned model; obtain it from its owner only after confirming permission to use it.

Ball tracking and associated strike-zone estimates require the ball-detector weight. Pose analysis requires its pose weight. Do not commit or redistribute weights without confirming the applicable rights. Review [Ultralytics licensing information](https://www.ultralytics.com/license) and all relevant model terms before public distribution. No project license has been selected.

## Limitations

Pitch speed and biomechanics are video-based estimates and vary with camera setup and detection quality. The strike-zone display is a 2D camera-calibrated estimate, not an official umpire call. AI-generated suggestions are informational and are not medical advice or guaranteed predictions of performance improvement. Live AWS behavior depends on the configured account, services, and permissions.
