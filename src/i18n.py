# -*- coding: utf-8 -*-
"""
Baseball Velocity & Biomechanics AI - Multilingual (i18n) Module
Supported Languages:
- ja: 日本語 (Japanese)
- en: English
- es: Español (Spanish)
- ko: 한국어 (Korean)
- zh: 繁體中文 (Traditional Chinese)
"""

LANGUAGES = {
    "ja": "🇯🇵 日本語",
    "en": "🇺🇸 English",
    "es": "🇩🇴 Español",
    "ko": "🇰🇷 한국어",
    "zh": "🇹🇼 繁體中文",
}

FONT_MAP = {
    "ja": "C:/Windows/Fonts/meiryo.ttc",
    "en": "C:/Windows/Fonts/arial.ttf",
    "es": "C:/Windows/Fonts/arial.ttf",
    "ko": "C:/Windows/Fonts/malgun.ttf",
    "zh": "C:/Windows/Fonts/msjh.ttc",
}

TRANSLATIONS = {
    "app_title": {
        "ja": "⚾ Outpace Baseball",
        "en": "⚾ Outpace Baseball",
        "es": "⚾ Outpace Baseball",
        "ko": "⚾ Outpace Baseball",
        "zh": "⚾ Outpace Baseball",
    },
    "app_subtitle": {
        "ja": "投球・バイオメカニクス解析ダッシュボード",
        "en": "Analytics & Biomechanics Dashboard",
        "es": "Panel de Análisis y Biomecánica",
        "ko": "투구 및 바이오메카닉스 분석 대시보드",
        "zh": "投球與生物力學分析儀表板",
    },
    "lang_select": {
        "ja": "🌐 言語 / Language",
        "en": "🌐 Language",
        "es": "🌐 Idioma / Language",
        "ko": "🌐 언어 / Language",
        "zh": "🌐 語言 / Language",
    },
    "unit_settings": {
        "ja": "📏 単位設定",
        "en": "📏 Unit Settings",
        "es": "📏 Unidades",
        "ko": "📏 단위 설정",
        "zh": "📏 單位設定",
    },
    "speed_unit_label": {
        "ja": "球速の単位",
        "en": "Velocity Unit",
        "es": "Unidad de Velocidad",
        "ko": "구속 단위",
        "zh": "球速單位",
    },
    "dist_unit_label": {
        "ja": "距離・エクステンション",
        "en": "Distance & Extension",
        "es": "Distancia y Extensión",
        "ko": "거리 및 익스텐션",
        "zh": "距離與延伸長度",
    },
    "height_settings": {
        "ja": "🧍 投手身長設定",
        "en": "🧍 Pitcher Height",
        "es": "🧍 Altura del Lanzador",
        "ko": "🧍 투수 신장 설정",
        "zh": "🧍 投手身高設定",
    },
    "ai_est_height": {
        "ja": "🤖 AI推定身長: {height}",
        "en": "🤖 AI Estimated Height: {height}",
        "es": "🤖 Altura Estimada por IA: {height}",
        "ko": "🤖 AI 추정 신장: {height}",
        "zh": "🤖 AI 推定身高: {height}",
    },
    "height_label": {
        "ja": "投手の身長 (Height)",
        "en": "Pitcher Height",
        "es": "Altura del Lanzador",
        "ko": "투수 신장 (Height)",
        "zh": "投手身高 (Height)",
    },
    "height_preset_hs": {
        "ja": "高校生/一般",
        "en": "High School",
        "es": "Escuela",
        "ko": "고교/일반",
        "zh": "高中/一般",
    },
    "height_preset_adult": {
        "ja": "一般成人",
        "en": "Standard Adult",
        "es": "Adulto Estándar",
        "ko": "일반 성인",
        "zh": "一般成人",
    },
    "height_preset_pro": {
        "ja": "プロ/大学",
        "en": "Pro/College",
        "es": "Pro/Univ",
        "ko": "프로/대학",
        "zh": "職棒/大學",
    },
    "height_preset_mlb": {
        "ja": "MLB大柄",
        "en": "MLB Pitcher",
        "es": "Grandes Ligas",
        "ko": "MLB 대형",
        "zh": "MLB長人",
    },
    "preset_title": {
        "ja": "クイックプリセット",
        "en": "Quick Presets",
        "es": "Ajustes Rápidos",
        "ko": "빠른 프리셋",
        "zh": "快速預設",
    },
    "btn_select": {
        "ja": "選択",
        "en": "Select",
        "es": "Elegir",
        "ko": "선택",
        "zh": "選擇",
    },
    "btn_selected": {
        "ja": "選択中",
        "en": "Active",
        "es": "Activo",
        "ko": "선택됨",
        "zh": "已選擇",
    },
    "btn_jump": {
        "ja": "移動",
        "en": "Jump",
        "es": "Ir",
        "ko": "이동",
        "zh": "跳轉",
    },


    "frame_settings": {
        "ja": "⏱️ 投球フレーム設定 (微調整)",
        "en": "⏱️ Pitch Timing Frames",
        "es": "⏱️ Cuadros de Lanzamiento",
        "ko": "⏱️ 투구 프레임 설정",
        "zh": "⏱️ 投球影格微調",
    },

    "sidebar_settings": {
        "ja": "⚙️ 設定・動画選択",
        "en": "⚙️ Settings & Video",
        "es": "⚙️ Ajustes y Selección de Video",
        "ko": "⚙️ 설정 및 영상 선택",
        "zh": "⚙️ 設定與影片選擇",
    },
    "select_video": {
        "ja": "解析動画",
        "en": "Select Pitch Video",
        "es": "Video de Lanzamiento",
        "ko": "분석 영상 선택",
        "zh": "解析投球影片",
    },
    "handedness": {
        "ja": "利き腕",
        "en": "Handedness",
        "es": "Brazo Dominante",
        "ko": "투구 손",
        "zh": "慣用手",
    },
    "right_pitcher": {
        "ja": "右投げ",
        "en": "Right-Handed (RHP)",
        "es": "Diestro (RHP)",
        "ko": "우투",
        "zh": "右投",
    },
    "left_pitcher": {
        "ja": "左投げ",
        "en": "Left-Handed (LHP)",
        "es": "Zurdo (LHP)",
        "ko": "좌투",
        "zh": "左投",
    },
    "run_analysis": {
        "ja": "🚀 解析実行",
        "en": "🚀 Run Analysis",
        "es": "🚀 Ejecutar Análisis",
        "ko": "🚀 분석 실행",
        "zh": "🚀 執行分析",
    },
    "upload_header": {
        "ja": "📤 新規動画アップロード",
        "en": "📤 Upload New Pitch Video",
        "es": "📤 Subir Nuevo Video",
        "ko": "📤 새 영상 업로드",
        "zh": "📤 上傳新影片",
    },
    "upload_label": {
        "ja": "スマホ撮影動画を解析",
        "en": "Analyze smartphone video",
        "es": "Analizar video de smartphone",
        "ko": "스마트폰 촬영 영상 분석",
        "zh": "分析手機拍攝影片",
    },
    "upload_btn": {
        "ja": "📥 アップロードして登録",
        "en": "📥 Upload & Register",
        "es": "📥 Subir y Registrar",
        "ko": "📥 업로드 및 등록",
        "zh": "📥 上傳並註冊",
    },
    "upload_success": {
        "ja": "動画 '{name}' を登録しました！選択ボックスから選べます。",
        "en": "Video '{name}' registered! You can select it from the dropdown.",
        "es": "¡Video '{name}' registrado! Puedes seleccionarlo en el menú.",
        "ko": "영상 '{name}'이(가) 등록되었습니다! 드롭다운에서 선택할 수 있습니다.",
        "zh": "影片 '{name}' 已註冊！您可以從選單中選取。",
    },
    "analyzing_spinner": {
        "ja": "投球速度・骨格・バイオメカニクス解析中...",
        "en": "Analyzing pitch velocity, pose keypoints, and biomechanics...",
        "es": "Analizando velocidad de lanzamiento, pose y biomecánica...",
        "ko": "구속, 투구 폼 및 바이오메카닉스 분석 중...",
        "zh": "正在分析投球速度、骨架與生物力學...",
    },
    "tab_single": {
        "ja": "📊 投球・バイオメカニクス解析",
        "en": "📊 Pitch & Biomechanics Analysis",
        "es": "📊 Análisis de Lanzamiento y Biomecánica",
        "ko": "📊 투구 및 바이오메카닉스 분석",
        "zh": "📊 投球與生物力學分析",
    },
    "tab_compare": {
        "ja": "🆚 2投球フォーム比較",
        "en": "🆚 2-Pitch Comparison",
        "es": "🆚 Comparación de 2 Lanzamientos",
        "ko": "🆚 2개 투구 폼 비교",
        "zh": "🆚 雙球比對模式",
    },
    "tab_history": {
        "ja": "📈 投球履歴・成長トラッカー",
        "en": "📈 History & Progress Tracker",
        "es": "📈 Historial y Seguimiento de Progreso",
        "ko": "📈 투구 기록 및 성장 추적",
        "zh": "📈 投球記錄與成長追蹤",
    },
    "velocity_score": {
        "ja": "📊 弾道・速度スコア",
        "en": "📊 Trajectory & Velocity Score",
        "es": "📊 Puntuación de Trayectoria y Velocidad",
        "ko": "📊 구속 및 궤적 점수",
        "zh": "📊 球速與軌跡得分",
    },
    "extension": {
        "ja": "エクステンション",
        "en": "Extension",
        "es": "Extensión",
        "ko": "익스텐션",
        "zh": "延伸長度 (Extension)",
    },
    "pitch_distance": {
        "ja": "到達距離",
        "en": "Pitch Dist",
        "es": "Dist. Efectiva",
        "ko": "투구 거리",
        "zh": "投球距離",
    },
    "flight_time": {
        "ja": "飛行時間",
        "en": "Flight Time",
        "es": "Tiempo Vuelo",
        "ko": "비행 시간",
        "zh": "飛行時間",
    },
    "biomechanics_header": {
        "ja": "🦾 バイオメカニクス指標",
        "en": "🦾 Biomechanics Metrics",
        "es": "🦾 Métricas Biomecánicas",
        "ko": "🦾 바이오메카닉스 지표",
        "zh": "🦾 生物力學指標",
    },
    "elbow_angle": {
        "ja": "肘の角度 (Release)",
        "en": "Elbow Angle (Release)",
        "es": "Ángulo del Codo (Soltada)",
        "ko": "팔꿈치 각도 (릴리스)",
        "zh": "手肘角度 (出手時)",
    },
    "knee_angle": {
        "ja": "前膝突っ張り角度",
        "en": "Lead Knee Blocking Angle",
        "es": "Ángulo de Bloqueo de Rodilla",
        "ko": "앞무릎 버팀 각도",
        "zh": "前膝支撐角度",
    },
    "arm_slot": {
        "ja": "アームスロット",
        "en": "Arm Slot",
        "es": "Ángulo de Brazo (Arm Slot)",
        "ko": "암 슬롯 (투구 각도)",
        "zh": "出手角度 (Arm Slot)",
    },
    "stride_ratio": {
        "ja": "歩幅比率 (対身長)",
        "en": "Stride % of Height",
        "es": "Zancada (% de Altura)",
        "ko": "보폭 비율 (키 대비)",
        "zh": "步伐比率 (對身高)",
    },
    "ai_diagnosis_header": {
        "ja": "🤖 AIフォーム診断＆指導アドバイス",
        "en": "🤖 AI Form Diagnosis & Coaching Feedback",
        "es": "🤖 Diagnóstico de IA y Consejos de Entrenamiento",
        "ko": "🤖 AI 투구 폼 진단 및 코칭 조언",
        "zh": "🤖 AI 姿勢診斷與指導建議",
    },
    "overall_score": {
        "ja": "総合フォーム判定",
        "en": "Overall Mechanics Score",
        "es": "Calificación General de Mecánica",
        "ko": "종합 투구 폼 판정",
        "zh": "整體姿勢評分",
    },
    "perceived_velocity": {
        "ja": "打者体感球速 (Extension補正)",
        "en": "Perceived Velocity (Batter's View)",
        "es": "Velocidad Percibida por el Bateador",
        "ko": "타자 체감 구속 (익스텐션 보정)",
        "zh": "打者體感球速 (延伸長度補正)",
    },
    "strengths_title": {
        "ja": "✅ 良好なポイント",
        "en": "✅ Key Strengths",
        "es": "✅ Puntos Fuertes",
        "ko": "✅ 우수한 포인트",
        "zh": "✅ 優良重點",
    },
    "improvements_title": {
        "ja": "💡 球速アップへの改善提案",
        "en": "💡 Velocity & Mechanics Recommendations",
        "es": "💡 Consejos para Aumentar la Velocidad",
        "ko": "💡 구속 향상을 위한 개선 제안",
        "zh": "💡 提升球速改善建議",
    },
    "no_improvements": {
        "ja": "現在、大きな課題は見当たりません。この好調なフォームを維持しましょう！",
        "en": "No major mechanical flaws detected. Maintain this great form!",
        "es": "¡No se detectaron fallas mecánicas importantes. Mantén esta gran forma!",
        "ko": "현재 큰 문제점이 발견되지 않았습니다. 이 훌륭한 폼을 유지하세요!",
        "zh": "目前未發現重大動作問題。請繼續維持此絕佳狀態！",
    },
    "download_report": {
        "ja": "📄 投球カルテ（PNG画像レポート）をダウンロード",
        "en": "📄 Download Pitching Report Card (PNG)",
        "es": "📄 Descargar Tarjeta de Informe de Pitcheo (PNG)",
        "ko": "📄 투구 리포트 카드 (PNG 이미지) 다운로드",
        "zh": "📄 下載投球分析診斷卡 (PNG)",
    },
    "layer_toggles": {
        "ja": "🎛️ 表示レイヤー切り替え:",
        "en": "🎛️ Display Layer Controls:",
        "es": "🎛️ Controles de Capas:",
        "ko": "🎛️ 표시 레이어 전환:",
        "zh": "🎛️ 顯示圖層切換:",
    },
    "show_skel": {
        "ja": "骨格線を表示",
        "en": "Show Skeleton",
        "es": "Mostrar Esqueleto",
        "ko": "골격선 표시",
        "zh": "顯示骨架線",
    },
    "show_labels": {
        "ja": "関節番号を表示",
        "en": "Show Joint IDs",
        "es": "Mostrar IDs de Articulaciones",
        "ko": "관절 번호 표시",
        "zh": "顯示關節編號",
    },
    "show_tracer": {
        "ja": "弾道トレーサーを表示",
        "en": "Show Ball Tracer",
        "es": "Mostrar Trayectoria",
        "ko": "궤적 트레이서 표시",
        "zh": "顯示彈道軌跡",
    },
    "subtab_video": {
        "ja": "🎬 骨格再生動画",
        "en": "🎬 Pose Video",
        "es": "🎬 Video de Pose",
        "ko": "🎬 골격 재생 영상",
        "zh": "🎬 骨架重播影片",
    },
    "subtab_still": {
        "ja": "📸 リリース瞬間",
        "en": "📸 Release Snapshot",
        "es": "📸 Momento de Soltada",
        "ko": "📸 릴리스 순간",
        "zh": "📸 出手瞬間",
    },
    "subtab_tracer": {
        "ja": "🌀 弾道トレーサー",
        "en": "🌀 Ball Tracer",
        "es": "🌀 Trazador de Pelota",
        "ko": "🌀 궤적 트레이서",
        "zh": "🌀 彈道軌跡",
    },
    "subtab_phases": {
        "ja": "🔍 コマ送り＆フェーズ",
        "en": "🔍 Frame Scrubber & Phases",
        "es": "🔍 Cuadro por Cuadro y Fases",
        "ko": "🔍 프레임 넘기기 및 페이즈",
        "zh": "🔍 逐幀檢視與階段",
    },
    "subtab_strike": {
        "ja": "🎯 捕球ゾーン",
        "en": "🎯 Strike Zone",
        "es": "🎯 Zona de Strike",
        "ko": "🎯 스트라이크 존",
        "zh": "🎯 進壘好球帶",
    },
    "playback_speed": {
        "ja": "再生速度 (Playback Speed)",
        "en": "Playback Speed",
        "es": "Velocidad de Reproducción",
        "ko": "재생 속도 (Playback Speed)",
        "zh": "播放速度 (Playback Speed)",
    },
    "speed_normal": {
        "ja": "1.0x (通常)",
        "en": "1.0x (Normal)",
        "es": "1.0x (Normal)",
        "ko": "1.0x (표준)",
        "zh": "1.0x (正常)",
    },
    "speed_slow": {
        "ja": "0.5x (スロー)",
        "en": "0.5x (Slow-Mo)",
        "es": "0.5x (Cámara Lenta)",
        "ko": "0.5x (슬로우)",
        "zh": "0.5x (慢動作)",
    },
    "speed_superslow": {
        "ja": "0.25x (スーパースロー)",
        "en": "0.25x (Super Slow)",
        "es": "0.25x (Súper Lenta)",
        "ko": "0.25x (슈퍼 슬로우)",
        "zh": "0.25x (超級慢動作)",
    },
    "phase_jump": {
        "ja": "📍 投球フェーズジャンプ:",
        "en": "📍 Pitch Phase Jump:",
        "es": "📍 Salto a Fase de Lanzamiento:",
        "ko": "📍 투구 페이즈 바로가기:",
        "zh": "📍 投球階段快速切換:",
    },
    "frame_scrub": {
        "ja": "ドラッグしてフレーム選択",
        "en": "Drag to Scrub Frame",
        "es": "Arrastra para Seleccionar Cuadro",
        "ko": "드래그하여 프레임 선택",
        "zh": "拖曳滑動條選擇影格",
    },
    "step_controls": {
        "ja": "🎞️ コマ送り（1コマ・5コマ送り/戻し）:",
        "en": "🎞️ Frame Step Controls:",
        "es": "🎞️ Controles de Cuadro:",
        "ko": "🎞️ 프레임 이동 (1프레임 / 5프레임):",
        "zh": "🎞️ 逐幀前進/後退 (1幀 / 5幀):",
    },
    "step_m5": {
        "ja": "⏪ -5コマ",
        "en": "⏪ -5 Frames",
        "es": "⏪ -5 Cuadros",
        "ko": "⏪ -5 프레임",
        "zh": "⏪ -5 幀",
    },
    "step_m1": {
        "ja": "◀ 1コマ戻る",
        "en": "◀ -1 Frame",
        "es": "◀ -1 Cuadro",
        "ko": "◀ 1 프레임 뒤로",
        "zh": "◀ 上 1 幀",
    },
    "step_p1": {
        "ja": "1コマ進む ▶",
        "en": "1 Frame ▶",
        "es": "1 Cuadro ▶",
        "ko": "1 프레임 앞으로 ▶",
        "zh": "下 1 幀 ▶",
    },
    "step_p5": {
        "ja": "+5コマ ⏩",
        "en": "+5 Frames ⏩",
        "es": "+5 Cuadros ⏩",
        "ko": "+5 프레임 ⏩",
        "zh": "+5 幀 ⏩",
    },
    "caption_release": {
        "ja": "フレーム {frame}: ボールリリース瞬間",
        "en": "Frame {frame}: Ball Release Snapshot",
        "es": "Cuadro {frame}: Momento de Soltada",
        "ko": "프레임 {frame}: 볼 릴리스 순간",
        "zh": "影格 {frame}: 出手瞬間快照",
    },
    "caption_tracer": {
        "ja": "投球弾道トレーサー (球速: {speed:.1f} {speed_unit}, エクステンション: {ext:.2f} {dist_unit})",
        "en": "Pitch Trajectory Tracer (Speed: {speed:.1f} {speed_unit}, Extension: {ext:.2f} {dist_unit})",
        "es": "Trazador de Trayectoria (Vel: {speed:.1f} {speed_unit}, Extensión: {ext:.2f} {dist_unit})",
        "ko": "투구 궤적 트레이서 (구속: {speed:.1f} {speed_unit}, 익스텐션: {ext:.2f} {dist_unit})",
        "zh": "投球彈道軌跡 (球速: {speed:.1f} {speed_unit}, 延伸長度: {ext:.2f} {dist_unit})",
    },
    "tracer_mode_label": {
        "ja": "弾道トレーサー表示形式",
        "en": "Tracer Visualization Mode",
        "es": "Modo de Rastreador de Trayectoria",
        "ko": "궤적 트레이서 표시 형식",
        "zh": "軌跡追蹤顯示形式",
    },
    "mode_statcast_3d": {
        "ja": "⚾ MLB スタットキャスト 3D弾道 (Statcast 3D)",
        "en": "⚾ MLB Statcast 3D Trajectory",
        "es": "⚾ Trayectoria 3D Statcast MLB",
        "ko": "⚾ MLB 스탯캐스트 3D 궤적",
        "zh": "⚾ MLB Statcast 3D 彈道",
    },
    "mode_real_2d": {
        "ja": "📺 実写2D弾道ライン (2D Video Overlay)",
        "en": "📺 2D Video Overlay",
        "es": "📺 Superposición de Video 2D",
        "ko": "📺 실사 2D 궤적 라인",
        "zh": "📺 實景 2D 彈道線條",
    },
    "camera_view_label": {
        "ja": "視点カメラ (Camera Angle)",
        "en": "Camera Angle",
        "es": "Ángulo de Cámara",
        "ko": "시점 카메라 (Camera Angle)",
        "zh": "視角攝影機 (Camera Angle)",
    },
    "cam_batter_rhb": {
        "ja": "⚾ 右打者視点 (RHB Batter's Eye)",
        "en": "⚾ Righty Batter's Eye",
        "es": "⚾ Bateador Derecho",
        "ko": "⚾ 우타자 시점 (RHB)",
        "zh": "⚾ 右打者視角 (RHB)",
    },
    "cam_batter_lhb": {
        "ja": "⚾ 左打者視点 (LHB Batter's Eye)",
        "en": "⚾ Lefty Batter's Eye",
        "es": "⚾ Bateador Zurdo",
        "ko": "⚾ 좌타자 시점 (LHB)",
        "zh": "⚾ 左打者視角 (LHB)",
    },
    "cam_catcher": {
        "ja": "🎯 捕手・審判視点 (Catcher / Umpire)",
        "en": "🎯 Catcher / Umpire View",
        "es": "🎯 Receptor / Árbitro",
        "ko": "🎯 포수·심판 시점",
        "zh": "🎯 捕手/主審 視角",
    },
    "cam_pitcher": {
        "ja": "🏟️ 投手視点 (Pitcher's Eye)",
        "en": "🏟️ Pitcher's Eye",
        "es": "🏟️ Ojo del Lanzador",
        "ko": "🏟️ 투수 시점",
        "zh": "🏟️ 投手視角",
    },
    "cam_side": {
        "ja": "📺 側面 3D アングル (Side View)",
        "en": "📺 Side 3D View",
        "es": "📺 Vista Lateral 3D",
        "ko": "📺 측면 3D 뷰",
        "zh": "📺 側面 3D 視角",
    },
    "overlay_pitches_label": {
        "ja": "➕ 重ね合わせ比較する投球を追加 (複数選択可)",
        "en": "➕ Add Pitches to Compare in 3D",
        "es": "➕ Agregar Lanzamientos para Comparar en 3D",
        "ko": "➕ 3D 중첩 비교할 투구 추가 (다중 선택)",
        "zh": "➕ 新增 3D 重疊比較的投球 (可複選)",
    },
    "pitch_color_legend": {
        "ja": "球種別 Statcast カラー凡例",
        "en": "Pitch Type Statcast Colors",
        "es": "Colores Statcast por Tipo",
        "ko": "구종별 스탯캐스트 색상 범례",
        "zh": "球種 Statcast 顏色圖例",
    },



    "compare_header": {
        "ja": "🆚 投球フォーム 左右比較 (Side-by-Side Comparison)",
        "en": "🆚 Pitch Mechanics Side-by-Side Comparison",
        "es": "🆚 Comparación Lado a Lado de Mecánica de Pitcheo",
        "ko": "🆚 투구 폼 양방향 비교 (Side-by-Side Comparison)",
        "zh": "🆚 投球動作雙分割比對 (Side-by-Side Comparison)",
    },
    "pitch_a": {
        "ja": "投球 A",
        "en": "Pitch A",
        "es": "Lanzamiento A",
        "ko": "투구 A",
        "zh": "投球 A",
    },
    "pitch_b": {
        "ja": "投球 B",
        "en": "Pitch B",
        "es": "Lanzamiento B",
        "ko": "투구 B",
        "zh": "投球 B",
    },
    "compare_view_mode": {
        "ja": "比較モード切り替え",
        "en": "Comparison View Mode",
        "es": "Modo de Comparación",
        "ko": "비교 모드 선택",
        "zh": "比較模式切換",
    },
    "view_ghost": {
        "ja": "👻 ゴースト重ね合わせ (Ghost Overlay)",
        "en": "👻 Ghost Overlay",
        "es": "👻 Superposición Fantasma",
        "ko": "👻 고스트 중첩 비교",
        "zh": "👻 重疊幽靈比較",
    },
    "view_side_by_side": {
        "ja": "↔️ 2画面並列表示 (Side-by-Side)",
        "en": "↔️ Side-by-Side",
        "es": "↔️ Lado a Lado",
        "ko": "↔️ 2화면 나란히 보기",
        "zh": "↔️ 雙畫面並排檢視",
    },
    "blend_slider": {
        "ja": "背景透過ブレンド (投球A ↔ 投球B)",
        "en": "Background Blend (Pitch A ↔ Pitch B)",
        "es": "Mezcla de Fondo (Lanzamiento A ↔ B)",
        "ko": "배경 투명도 블렌드 (투구 A ↔ 투구 B)",
        "zh": "背景透明度融合 (投球A ↔ 投球B)",
    },
    "show_vectors": {
        "ja": "手元・肘・膝のズレ矢印を表示 (Displacement Vectors)",
        "en": "Show Displacement Vectors (Hand/Elbow/Knee)",
        "es": "Mostrar Vectores de Desplazamiento",
        "ko": "손·팔꿈치·무릎 차이 벡터 표시",
        "zh": "顯示手部/手肘/膝蓋偏移向量",
    },
    "compare_phase_select": {
        "ja": "同期比較する投球フェーズ",
        "en": "Synchronized Pitch Phase",
        "es": "Fase Sincronizada a Comparar",
        "ko": "동기화 비교할 투구 페이즈",
        "zh": "同步比較的投球階段",
    },

    "diff_table_title": {
        "ja": "📊 投球指標・フォーム差異",
        "en": "📊 Metric & Mechanical Differences",
        "es": "📊 Diferencias Métricas y Mecánicas",
        "ko": "📊 투구 지표 및 폼 차이",
        "zh": "📊 投球指標與動作差異",
    },
    "difference": {
        "ja": "差分 (A - B)",
        "en": "Delta (A - B)",
        "es": "Diferencia (A - B)",
        "ko": "차이 (A - B)",
        "zh": "差異 (A - B)",
    },
    "metric_name": {
        "ja": "指標",
        "en": "Metric",
        "es": "Métrica",
        "ko": "지표",
        "zh": "指標",
    },
    "form_type": {
        "ja": "投球フォーム分類",
        "en": "Arm Slot Category",
        "es": "Tipo de Mecánica",
        "ko": "투구 폼 분류",
        "zh": "投球姿勢分類",
    },
    "spin_analytics_header": {
        "ja": "🌀 球質・回転アナリティクス",
        "en": "🌀 Spin & Movement Analytics",
        "es": "🌀 Analítica de Rotación y Quiebre",
        "ko": "🌀 구질·회전수 분석 (Spin & Break)",
        "zh": "🌀 球質·轉速進階分析 (Spin & Break)",
    },
    "spin_rate_label": {
        "ja": "推定回転数",
        "en": "Spin Rate",
        "es": "Velocidad de Rotación",
        "ko": "추정 회전수",
        "zh": "推定轉速",
    },
    "spin_eff_label": {
        "ja": "スピン効率",
        "en": "Spin Efficiency",
        "es": "Eficiencia de Rotación",
        "ko": "스핀 효율",
        "zh": "旋轉效率",
    },
    "gyro_angle_label": {
        "ja": "ジャイロ角度",
        "en": "Gyro Angle",
        "es": "Ángulo Giroscópico",
        "ko": "자이로 각도",
        "zh": "陀螺旋轉角",
    },
    "ivb_label": {
        "ja": "縦の変化量 (IVB)",
        "en": "Induced Vert Break (IVB)",
        "es": "Quiebre Vertical Inducido",
        "ko": "수직 무브먼트 (IVB)",
        "zh": "垂直位移量 (IVB)",
    },
    "hb_label": {
        "ja": "横の変化量 (HB)",
        "en": "Horizontal Break (HB)",
        "es": "Quiebre Horizontal (HB)",
        "ko": "수평 무브먼트 (HB)",
        "zh": "水平位移量 (HB)",
    },
    "spin_axis_label": {
        "ja": "推定回転軸",
        "en": "Spin Axis",
        "es": "Eje de Giro",
        "ko": "추정 회전축",
        "zh": "推定旋轉軸",
    },
    "bauer_unit_label": {
        "ja": "バウアーユニット",
        "en": "Bauer Units",
        "es": "Unidades Bauer",
        "ko": "바우어 유닛",
        "zh": "鮑爾單位 (Bauer Units)",
    },
    "spin_caption": {
        "ja": "💡 実際の飛行軌道と重力落下の差（マグヌス揚力）および球速・球種特性から、空気力学方程式（Nathan's Aerodynamic Equations）に基づき回転数・ジャイロ角度・変化量を逆算推計しています。",
        "en": "💡 Calculated from aerodynamic trajectory deflection (Magnus effect lift vs. pure gravity) using Nathan's baseball equations and empirical Statcast Bauer unit priors.",
        "es": "💡 Calculado a partir de la desviación aerodinámica de la trayectoria (efecto Magnus frente a gravedad pura) usando las ecuaciones de Nathan.",
        "ko": "💡 실제 비행 궤적과 순수 중력 낙하의 차이(마그누스 양력) 및 구속·구종 특성으로부터 공기역학 방정식(Nathan's Equations)에 기반해 역산 추정합니다.",
        "zh": "💡 根據實際飛行軌跡與純重力下墜的落差（馬格努斯力位移），結合空氣動力學方程逆向推算轉速、陀螺角與位移量。",
    },
    "spin_rate_help": {
        "ja": "【推定回転数】ボールが1分間に回転する回数(rpm)。\n【BU (バウアーユニット)】回転数(rpm)÷球速(mph)。球速の割に回転が多いか(25以上: ホップ型)少ないか(22以下: 沈む重い球)を表す指標です(MLB平均約23.8)。",
        "en": "【Spin Rate】Total revolutions per minute (rpm).\n【BU (Bauer Units)】Spin (rpm) ÷ Velocity (mph). Measures spin quality independent of speed (MLB avg ~23.8; >25 = ride/hop, <22 = sink/heavy).",
        "es": "【Velocidad de Giro】Revoluciones por minuto (rpm).\n【BU (Unidades Bauer)】Giro (rpm) ÷ Velocidad (mph). Mide la calidad de giro relativa (promedio MLB ~23.8).",
        "ko": "【추정 회전수】1분당 볼의 회전수(rpm).\n【BU (바우어 유닛)】회전수(rpm) ÷ 구속(mph). 구속 대비 회전이 많은지(25이상: 호프형) 적은지(22이하: 가라앉는 무거운 공)를 나타냅니다(MLB평균 약 23.8).",
        "zh": "【推定轉速】球體每分鐘轉速(rpm)。\n【BU (鮑爾單位)】轉速(rpm) ÷ 球速(mph)。衡量球速對應的純轉速質量(MLB平均約23.8；25以上為竄升型，22以下為下沉重球)。",
    },
    "spin_eff_help": {
        "ja": "【スピン効率】総回転のうち、ボールの揚力・変化（マグヌス効果）に実際に使われている回転の割合。100%に近いほど変化量が大きく、低いほどジャイロ回転（ライフル回転）が多くなります。",
        "en": "【Spin Efficiency】Percentage of spin contributing to movement (Magnus lift). Closer to 100% means more break; lower means more gyro/spiral spin.",
        "es": "【Eficiencia de Giro】Porcentaje de rotación que contribuye al movimiento (efecto Magnus).",
        "ko": "【스핀 효율】전체 회전 중 실제 무브먼트(마그누스 양력)에 기여하는 회전 비율입니다.",
        "zh": "【旋轉效率】總轉速中實際轉化為進壘位移（馬格努斯力）的比例。",
    },
    "gyro_angle_help": {
        "ja": "【ジャイロ角度】ボールの進行方向に対する回転軸の傾き(0°〜90°)。0°は完全なバックスピン/トップスピン（効率100%）、90°は銃弾のような純ジャイロ回転（効率0%）です。",
        "en": "【Gyro Angle】Angle between spin axis and flight path (0°-90°). 0° = pure transverse spin (100% eff), 90° = bullet/spiral gyro spin (0% eff).",
        "es": "【Ángulo Giroscópico】Inclinación del eje de giro respecto a la dirección de vuelo (0°-90°).",
        "ko": "【자이로 각도】공의 진행 방향에 대한 회전축의 기울기(0°~90°). 90°에 가까울수록 총알 스핀 형태입니다.",
        "zh": "【陀螺角度】旋轉軸相對於飛行方向的傾角(0°~90°)。90°為子彈螺旋旋轉。",
    },
    "ivb_help": {
        "ja": "【縦の変化量 (IVB)】重力のみで自然落下した場合と比べ、ボールが何cm浮き上がったか（または落ちたか）。ストレートでは＋40cm前後が優秀なホップ成分の目安です。",
        "en": "【Induced Vertical Break (IVB)】Vertical deflection in cm compared to a spinless ball under pure gravity. High positive IVB (+40cm+) indicates great fastball ride/hop.",
        "es": "【Quiebre Vertical Inducido (IVB)】Desviación vertical en cm en comparación con la caída libre por gravedad.",
        "ko": "【수직 무브먼트 (IVB)】순수 중력 낙하 궤적 대비 볼이 몇 cm 떠올랐는지(호프 성분)를 나타냅니다.",
        "zh": "【垂直位移量 (IVB)】相較於無旋轉純重力下墜，球體向上竄升（或下墜）的公分數。快速球通常在 +40cm 以上為極佳竄升量。",
    },
    "hb_help": {
        "ja": "【横の変化量 (HB)】直線軌道からの左右の曲がり幅。右腕のシュートや左腕のアームサイドラン、スライダーの横曲がり量を表します。",
        "en": "【Horizontal Break (HB)】Horizontal deflection from straight line. Measures arm-side run or glove-side sweep.",
        "es": "【Quiebre Horizontal (HB)】Desviación horizontal lateral respecto a la línea recta.",
        "ko": "【수평 무브먼트 (HB)】직선 궤적 대비 좌우 꺾임 폭(슈트 또는 슬라이더 무브먼트)을 나타냅니다.",
        "zh": "【水平位移量 (HB)】相較於直線軌跡的橫向偏轉公分數（伸卡內竄或滑球外掃）。",
    },
    "spin_clock_title": {
        "ja": "⚾ 3D回転ボール＆スピン軸 (3D Spin Visualizer)",
        "en": "⚾ 3D Spinning Ball & Spin Axis",
        "es": "⚾ Béisbol 3D en Rotación y Eje de Giro",
        "ko": "⚾ 3D 회전 야구공 & 스핀축",
        "zh": "⚾ 3D旋轉棒球與旋轉軸",
    },
    "view_2d_clock": {
        "ja": "⏰ 2D時計盤ビュー",
        "en": "⏰ 2D Clock View",
        "es": "⏰ Vista Reloj 2D",
        "ko": "⏰ 2D 시계판 보기",
        "zh": "⏰ 2D時鐘方向視圖",
    },
    "spin_3d_help": {
        "ja": "ドラッグで3D視点を自由に回転可能。右上のボタンで再生速度（0.1x〜1.0x/一時停止）を変更できます。",
        "en": "Click & drag to orbit 3D view. Use top-right button to adjust rotation speed (0.1x to 1.0x / Pause).",
        "es": "Arrastre para rotar la vista 3D. Cambie la velocidad con el botón superior derecho.",
        "ko": "드래그하여 3D 시점을 회전할 수 있습니다. 우측 상단 버튼으로 회전 속도를 변경하세요.",
        "zh": "可拖曳旋轉3D視角，右上角按鈕可切換旋轉速度與暫停。",
    },
    "movement_plot_title": {
        "ja": "🎯 球種別変化量マップ (Movement Plot: IVB vs HB)",
        "en": "🎯 Pitch Movement Plot (IVB vs HB)",
        "es": "🎯 Gráfico de Movimiento de Lanzamientos",
        "ko": "🎯 구종별 무브먼트 맵 (IVB vs HB)",
        "zh": "🎯 球種位移分佈圖 (IVB vs HB)",
    },
    "motion_trail_title": {
        "ja": "📸 連続フォーム残像ストロボ写真 (Motion Trail)",
        "en": "📸 Continuous Motion Trail (Strobe Photo)",
        "es": "📸 Foto Estroboscópica de Mecánica",
        "ko": "📸 투구 폼 연속 잔상 스트로보 사진",
        "zh": "📸 投球動作連續殘影疊圖 (Strobe Photo)",
    },
    "download_strobe": {
        "ja": "📸 連続ストロボ写真をダウンロード (PNG)",
        "en": "📸 Download Strobe Photo (PNG)",
        "es": "📸 Descargar Foto Estroboscópica (PNG)",
        "ko": "📸 연속 스트로보 사진 다운로드 (PNG)",
        "zh": "📸 下載連續動作殘影圖 (PNG)",
    },
    "what_if_title": {
        "ja": "🚀 球速・球質アップ・シミュレーター (What-If Sandbox)",
        "en": "🚀 Velocity & Stuff Simulator (What-If Sandbox)",
        "es": "🚀 Simulador de Mejora de Velocidad (What-If)",
        "ko": "🚀 구속·구질 향상 시뮬레이터 (What-If)",
        "zh": "🚀 球速與球質強化模擬器 (What-If)",
    },
    "sim_ext_label": {
        "ja": "エクステンションの延長",
        "en": "Add Extension",
        "es": "Aumentar Extensión",
        "ko": "익스텐션 연장",
        "zh": "增加延伸步幅",
    },
    "sim_knee_label": {
        "ja": "前膝ブロッキングの強化",
        "en": "Increase Knee Bracing",
        "es": "Fortalecer Bloqueo de Rodilla",
        "ko": "앞무릎 브레이킹 강화",
        "zh": "強化前膝煞車制動",
    },
    "sim_spin_label": {
        "ja": "回転数の増加",
        "en": "Boost Spin Rate",
        "es": "Aumentar Giro (rpm)",
        "ko": "회전수 증가",
        "zh": "提高旋轉數 (rpm)",
    },
    "sim_arm_label": {
        "ja": "腕の振り・しなりの加速",
        "en": "Arm Whip Acceleration",
        "es": "Aceleración del Latigazo",
        "ko": "팔 스윙 가속도 향상",
        "zh": "手臂鞭擊加速",
    },
    "projected_velo": {
        "ja": "予測初速",
        "en": "Projected Velo",
        "es": "Velocidad Proyectada",
        "ko": "예상 구속",
        "zh": "預測球速",
    },
    "projected_perceived": {
        "ja": "予測体感球速",
        "en": "Projected Perceived",
        "es": "Velocidad Percibida Proyectada",
        "ko": "예상 체감 구속",
        "zh": "預測體感球速",
    },
    "projected_ivb": {
        "ja": "予測ホップ量",
        "en": "Projected IVB",
        "es": "IVB Proyectado",
        "ko": "예상 수직 호프",
        "zh": "預測垂直竄升量",
    },
    "projected_whiff": {
        "ja": "推定空振り率 (Whiff%)",
        "en": "Projected Whiff%",
        "es": "Tasa de Abanicos Proyectada",
        "ko": "예상 헛스윙률",
        "zh": "預測揮空率 (Whiff%)",
    },
    "prescription_title": {
        "ja": "📋 本日のピッチング処方箋（改善ドリル・ToDoリスト）",
        "en": "📋 Pitching Prescription & Training Drills",
        "es": "📋 Prescripción de Pitcheo y Ejercicios Recomendados",
        "ko": "📋 오늘의 피칭 처방전 (개선 드릴 & ToDo 리스트)",
        "zh": "📋 今日投球處方箋 (強化訓練選單與 ToDo 清單)",
    },



    "history_header": {
        "ja": "📈 投球履歴・パフォーマンス推移",
        "en": "📈 Pitch History & Progression Tracker",
        "es": "📈 Historial de Pitcheo y Seguimiento de Rendimiento",
        "ko": "📈 투구 기록 및 퍼포먼스 추이",
        "zh": "📈 投球記錄與表現趨勢",
    },
    "total_pitches": {
        "ja": "総投球数",
        "en": "Total Pitches",
        "es": "Total de Lanzamientos",
        "ko": "총 투구 수",
        "zh": "總投球數",
    },
    "max_speed": {
        "ja": "最高球速",
        "en": "Max Velocity",
        "es": "Velocidad Máxima",
        "ko": "최고 구속",
        "zh": "最高球速",
    },
    "avg_speed": {
        "ja": "平均球速",
        "en": "Avg Velocity",
        "es": "Velocidad Promedio",
        "ko": "평균 구속",
        "zh": "平均球速",
    },
    "avg_extension": {
        "ja": "平均エクステンション",
        "en": "Avg Extension",
        "es": "Extensión Promedio",
        "ko": "평균 익스텐션",
        "zh": "平均延伸長度",
    },
    "chart_speed_title": {
        "ja": "球速の推移 (km/h)",
        "en": "Velocity Progression (km/h)",
        "es": "Evolución de la Velocidad (km/h)",
        "ko": "구속 변화 추이 (km/h)",
        "zh": "球速變化趨勢 (km/h)",
    },
    "chart_time_label": {
        "ja": "日時",
        "en": "Timestamp",
        "es": "Fecha y Hora",
        "ko": "일시",
        "zh": "時間",
    },
    "history_records": {
        "ja": "📜 全記録一覧",
        "en": "📜 Full Pitch Log",
        "es": "📜 Registro Completo de Lanzamientos",
        "ko": "📜 전체 투구 기록",
        "zh": "📜 完整投球紀錄",
    },
    "kinematic_header": {
        "ja": "📊 キネマティック・シーケンス (関節角度・速度推移)",
        "en": "📊 Kinematic Sequence (Joint Angles & Angular Velocity)",
        "es": "📊 Secuencia Cinemática (Ángulos y Velocidades Articulares)",
        "ko": "📊 키네마틱 시퀀스 (관절 각도 및 속도 추이)",
        "zh": "📊 運動學動力鏈 (關節角度與速度變化曲線)",
    },
    "kinematic_knee": {
        "ja": "前膝角度",
        "en": "Lead Knee Angle",
        "es": "Ángulo Rodilla Delantera",
        "ko": "앞무릎 각도",
        "zh": "前膝角度",
    },
    "kinematic_elbow": {
        "ja": "肘屈曲角度",
        "en": "Elbow Flexion",
        "es": "Flexión de Codo",
        "ko": "팔꿈치 굴곡 각도",
        "zh": "手肘屈曲角度",
    },
    "kinematic_shoulder_tilt": {
        "ja": "肩傾斜角",
        "en": "Shoulder Tilt",
        "es": "Inclinación de Hombros",
        "ko": "어깨 기울기",
        "zh": "肩膀傾斜角",
    },
    "kinematic_wrist_speed": {
        "ja": "手首速度 (px/s)",
        "en": "Wrist Speed (px/s)",
        "es": "Velocidad de Muñeca (px/s)",
        "ko": "손목 이동 속도 (px/s)",
        "zh": "手腕揮臂速度 (px/s)",
    },
    "kinematic_caption": {
        "ja": "💡 赤縦線は現在のコマ位置を示します。運動連鎖（骨盤/前膝の急減速 → 胸郭・肩回旋 → 肘伸展 → 手首加速）のエネルギー伝達を確認できます。",
        "en": "💡 Red dashed line shows current scrub frame. Observe proximal-to-distal kinetic chain (pelvis/lead-knee braking → torso → elbow → wrist peak velocity).",
        "es": "💡 La línea vertical roja indica el cuadro actual. Observa la cadena cinética (frenado de rodilla → torso → codo → aceleración máxima de muñeca).",
        "ko": "💡 붉은 점선은 현재 재생 프레임을 나타냅니다. 운동 사슬(앞무릎 감속 브레이크 → 몸통 회전 → 팔꿈치 → 손목 최고 가속)의 에너지 전달을 확인하세요.",
        "zh": "💡 紅色虛線代表當前格位。可觀察動力鏈傳遞順序（前膝制動煞車 → 軀幹加速 → 手肘甩臂 → 手腕極速釋放）。",
    },
    "pitch_type_label": {
        "ja": "⚾ 投球の球種 (Pitch Type)",
        "en": "⚾ Pitch Type",
        "es": "⚾ Tipo de Lanzamiento",
        "ko": "⚾ 구종 선택 (Pitch Type)",
        "zh": "⚾ 投球球種 (Pitch Type)",
    },
    "pitch_fastball": {
        "ja": "ストレート (4シーム)",
        "en": "4-Seam Fastball",
        "es": "Recta de 4 Costuras",
        "ko": "포심 패스트볼",
        "zh": "四縫線快速球",
    },
    "pitch_twoseam": {
        "ja": "ツーシーム / シンカー",
        "en": "2-Seam / Sinker",
        "es": "Recta de 2 Costuras / Sinker",
        "ko": "투심 / 싱커",
        "zh": "二縫線 / 伸卡球",
    },
    "pitch_slider": {
        "ja": "スライダー",
        "en": "Slider",
        "es": "Slider",
        "ko": "슬라이더",
        "zh": "滑球",
    },
    "pitch_curve": {
        "ja": "カーブ",
        "en": "Curveball",
        "es": "Curva",
        "ko": "커브",
        "zh": "曲球",
    },
    "pitch_changeup": {
        "ja": "チェンジアップ",
        "en": "Changeup",
        "es": "Cambio de Velocidad",
        "ko": "체인지업",
        "zh": "變速球",
    },
    "pitch_splitter": {
        "ja": "スプリット / フォーク",
        "en": "Splitter / Forkball",
        "es": "Splitter / Tenedor",
        "ko": "스플리터 / 포크볼",
        "zh": "指叉球 (Splitter)",
    },
    "pitch_cutter": {
        "ja": "カットボール (カッター)",
        "en": "Cutter",
        "es": "Cortadora",
        "ko": "커터",
        "zh": "卡特球 (Cutter)",
    },
    "benchmark_header": {
        "ja": "🏆 球種別ベンチマーク比較",
        "en": "🏆 Pitch Type Benchmarks",
        "es": "🏆 Comparación de Parámetros por Tipo",
        "ko": "🏆 구종별 벤치마크 비교",
        "zh": "🏆 球種基準水準比較",
    },
    "mlb_benchmark": {
        "ja": "🇺🇸 MLB平均",
        "en": "🇺🇸 MLB Avg",
        "es": "🇺🇸 Prom. MLB",
        "ko": "🇺🇸 MLB 평균",
        "zh": "🇺🇸 MLB 平均",
    },
    "npb_benchmark": {
        "ja": "⚾ NPB平均",
        "en": "⚾ NPB Avg",
        "es": "⚾ Prom. NPB",
        "ko": "⚾ NPB 평균",
        "zh": "⚾ NPB 平均",
    },
    "amateur_benchmark": {
        "ja": "🎓 高校/アマ",
        "en": "🎓 Amateur",
        "es": "🎓 Amateur",
        "ko": "🎓 고교/일반",
        "zh": "🎓 高校/業餘",
    },
    "perspective_label": {
        "ja": "👁️ 視点切り替え (Perspective)",
        "en": "👁️ Perspective View",
        "es": "👁️ Perspectiva",
        "ko": "👁️ 시점 전환 (Perspective)",
        "zh": "👁️ 視角切換 (Perspective)",
    },
    "catcher_view": {
        "ja": "捕手・正面視点",
        "en": "Catcher / Umpire View",
        "es": "Vista del Receptor",
        "ko": "포수·심판 정면 시점",
        "zh": "捕手/主審 正面視角",
    },
    "right_batter_view": {
        "ja": "右打席視点 (RHB Box)",
        "en": "Righty Batter's Eye",
        "es": "Bateador Derecho",
        "ko": "우타석 시점 (RHB Box)",
        "zh": "右打者打擊區視角",
    },
    "left_batter_view": {
        "ja": "左打席視点 (LHB Box)",
        "en": "Lefty Batter's Eye",
        "es": "Bateador Zurdo",
        "ko": "좌타석 시점 (LHB Box)",
        "zh": "左打者打擊區視角",
    },
    "export_csv": {
        "ja": "📥 履歴CSVダウンロード",
        "en": "📥 Export History (CSV)",
        "es": "📥 Exportar Historial (CSV)",
        "ko": "📥 기록 CSV 다운로드",
        "zh": "📥 匯出投球紀錄 (CSV)",
    },
    "export_excel": {
        "ja": "📊 履歴Excelダウンロード",
        "en": "📊 Export History (Excel)",
        "es": "📊 Exportar Historial (Excel)",
        "ko": "📊 기록 Excel 다운로드",
        "zh": "📊 匯出投球紀錄 (Excel)",
    },
    "clear_history": {
        "ja": "🗑️ 履歴全消去",
        "en": "🗑️ Clear History",
        "es": "🗑️ Borrar Historial",
        "ko": "🗑️ 기록 전체 삭제",
        "zh": "🗑️ 清空所有紀錄",
    },
    "auto_track_btn": {
        "ja": "⚡ AI自動弾道解析 (Auto-Tracker)",
        "en": "⚡ AI Auto Ball-Tracker",
        "es": "⚡ Auto-Rastreo de Pelota IA",
        "ko": "⚡ AI 자동 볼 트래킹 실행",
        "zh": "⚡ AI 自動彈道追蹤分析",
    },

    "strike_zone_title": {
        "ja": "🎯 捕球位置・ストライクゾーン",
        "en": "🎯 Ball Location & Strike Zone",
        "es": "🎯 Ubicación de la Pelota y Zona de Strike",
        "ko": "🎯 포구 위치 및 스트라이크 존",
        "zh": "🎯 進壘點與好球帶",
    },
    "impact_call": {
        "ja": "着弾判定",
        "en": "Call",
        "es": "Decisión",
        "ko": "판정",
        "zh": "好壞球判定",
    },
    "zone_call_unavailable": {
        "ja": "判定不可（捕球付近の実検出データが不足しています）",
        "en": "No call (insufficient real detections near the plate)",
        "es": "Sin decisión (faltan detecciones reales cerca del plato)",
        "ko": "판정 불가 (홈 플레이트 부근의 실제 검출 데이터 부족)",
        "zh": "無法判定（本壘附近的實際偵測資料不足）",
    },
    "zone_estimate_disclaimer": {
        "ja": "元版の基準動画と同じカメラ位置・画角として校正済みの動画だけを参考判定します。打者ごとのゾーン高・ボール全体の3D通過位置・カメラの遠近情報が不足するため、公式なストライク／ボール判定ではありません。切り抜きや異なる画角の動画は判定不可になります。",
        "en": "A reference estimate is shown only for videos calibrated to the reference camera and framing. Batter-specific zone height, the ball's full 3D passage, and camera depth are unavailable, so this is not an official call. Cropped or differently framed videos are not called.",
        "es": "Solo se muestra una estimación para videos calibrados con la cámara y el encuadre de referencia. Faltan la altura de la zona del bateador, el paso 3D completo y la profundidad de cámara; no es una decisión oficial. Los videos recortados o con otro encuadre no se deciden.",
        "ko": "기준 카메라와 구도로 보정된 영상에만 참고 추정을 표시합니다. 타자별 존 높이, 공의 전체 3D 통과 위치와 카메라 깊이 정보가 부족하여 공식 판정이 아닙니다. 잘라내거나 구도가 다른 영상은 판정하지 않습니다.",
        "zh": "僅對已按參考鏡頭位置與構圖校正的影片提供參考估計。缺少打者個別好球帶高度、球體完整3D通過位置及鏡頭深度資訊，因此不是正式判決；裁切或不同構圖的影片不予判定。",
    },
    "strike": {
        "ja": "ストライク",
        "en": "Strike",
        "es": "Strike",
        "ko": "스트라이크",
        "zh": "好球",
    },
    "ball": {
        "ja": "ボール",
        "en": "Ball",
        "es": "Bola",
        "ko": "볼",
        "zh": "壞球",
    },
    "high": {
        "ja": "高め",
        "en": "High",
        "es": "Alta",
        "ko": "높은 코스",
        "zh": "高球",
    },
    "low": {
        "ja": "低め",
        "en": "Low",
        "es": "Baja",
        "ko": "낮은 코스",
        "zh": "低球",
    },
    "middle_v": {
        "ja": "真ん中",
        "en": "Middle",
        "es": "Media",
        "ko": "한가운데",
        "zh": "中央",
    },
    "inside": {
        "ja": "右打者内角",
        "en": "Inside (vs RHB)",
        "es": "Pegada (vs BD)",
        "ko": "몸쪽 (우타자 기준)",
        "zh": "內角 (右打視角)",
    },
    "outside": {
        "ja": "右打者外角",
        "en": "Outside (vs RHB)",
        "es": "Afuera (vs BD)",
        "ko": "바깥쪽 (우타자 기준)",
        "zh": "外角 (右打視角)",
    },
    "center_h": {
        "ja": "中央",
        "en": "Center",
        "es": "Centro",
        "ko": "중앙",
        "zh": "正中",
    },

    "report_card_title": {
        "ja": "BASEBALL BIOMECHANICS REPORT",
        "en": "BASEBALL BIOMECHANICS REPORT",
        "es": "INFORME BIOMECÁNICO DE BÉISBOL",
        "ko": "야구 바이오메카닉스 분석 리포트",
        "zh": "棒球生物力學分析診斷書",
    },
    "stuff_plus_title": {
        "ja": "📊 Statcast風「Stuff+」球質レーダー評価",
        "en": "📊 Statcast Stuff+ Pitch Quality Radar",
        "es": "📊 Radar de Calidad de Lanzamiento Stuff+",
        "ko": "📊 스탯캐스트 Stuff+ 구질 레이더 평가",
        "zh": "📊 Statcast Stuff+ 球質五維雷達評估",
    },
    "stuff_plus_desc": {
        "ja": "プロ平均を100とした球速・ホップ量・変化幅・スピン効率・エクステンションの総合偏差値評価",
        "en": "Indexed rating (Pro Avg = 100) evaluating Velocity, Ride, Run, Efficiency, and Extension",
        "es": "Evaluación indexada (Promedio = 100) de velocidad, salto, movimiento, eficiencia y extensión",
        "ko": "프로 평균을 100으로 기준한 구속·호프·변화폭·효율·익스텐션 종합 편차치",
        "zh": "以職棒平均100為基準之球速、升力、位移、效率與延伸步幅綜合評分",
    },
    "stuff_plus_guide_html": {
        "ja": """<div style="background-color: #1a1e29; border: 1px solid #0284c7; border-radius: 10px; padding: 12px 16px; font-size: 11.5px; color: #38bdf8; line-height: 1.75; margin-top: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.25);">
<b style="color: #7dd3fc; font-size: 12.5px;">【5大球質指標の読み方 (基準: プロ平均=100)】</b><br>
• <b style="color:#38bdf8;">球速 (Velo+)</b>: 純粋な初速スピード。110超でMLB上位の快速球<br>
• <b style="color:#38bdf8;">ホップ (Ride+)</b>: 重力に逆らう垂直浮き上がり量 (IVB)。空振り・ファウル誘発力<br>
• <b style="color:#38bdf8;">横変化 (Run+)</b>: 芯を外す横の曲がり幅 (HB)。シュートやスライダーの切れ味<br>
• <b style="color:#38bdf8;">スピン効率 (Eff+)</b>: 変化量に変換される有効回転の比率（ジャイロ成分の少なさ）<br>
• <b style="color:#38bdf8;">前到達 (Ext+)</b>: 打者寄りで球を離す前への伸び。打者の体感速度を大幅UP
</div>""",
        "en": """<div style="background-color: #1a1e29; border: 1px solid #0284c7; border-radius: 10px; padding: 12px 16px; font-size: 11.5px; color: #38bdf8; line-height: 1.75; margin-top: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.25);">
<b style="color: #7dd3fc; font-size: 12.5px;">【5 Key Stuff+ Metrics (Baseline: Pro Avg = 100)】</b><br>
• <b style="color:#38bdf8;">Velo+ (Velocity)</b>: Pure release speed. 110+ represents elite MLB heat<br>
• <b style="color:#38bdf8;">Ride+ (IVB Hop)</b>: Induced vertical break above gravity. Whiff & popup generator<br>
• <b style="color:#38bdf8;">Run+ (HB Movement)</b>: Horizontal break. Arm-side tail or glove-side sweep<br>
• <b style="color:#38bdf8;">Eff+ (Spin Efficiency)</b>: Percentage of spin contributing to movement (active spin)<br>
• <b style="color:#38bdf8;">Ext+ (Extension)</b>: Distance released towards plate. Increases perceived velocity
</div>""",
        "es": """<div style="background-color: #1a1e29; border: 1px solid #0284c7; border-radius: 10px; padding: 12px 16px; font-size: 11.5px; color: #38bdf8; line-height: 1.75; margin-top: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.25);">
<b style="color: #7dd3fc; font-size: 12.5px;">【5 Métricas Clave de Stuff+ (Promedio = 100)】</b><br>
• <b style="color:#38bdf8;">Velo+ (Velocidad)</b>: Velocidad de salida. Más de 110 es élite MLB<br>
• <b style="color:#38bdf8;">Ride+ (Salto IVB)</b>: Movimiento vertical inducido contra la gravedad<br>
• <b style="color:#38bdf8;">Run+ (Movimiento HB)</b>: Quiebre lateral horizontal<br>
• <b style="color:#38bdf8;">Eff+ (Eficiencia de Giro)</b>: Giro activo que genera movimiento<br>
• <b style="color:#38bdf8;">Ext+ (Extensión)</b>: Distancia de soltada hacia el plato
</div>""",
        "ko": """<div style="background-color: #1a1e29; border: 1px solid #0284c7; border-radius: 10px; padding: 12px 16px; font-size: 11.5px; color: #38bdf8; line-height: 1.75; margin-top: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.25);">
<b style="color: #38bdf8; font-size: 12.5px;">【5대 구질 지표 분석법 (기준: 프로 평균 = 100)】</b><br>
• <b style="color:#ffffff;">구속 (Velo+)</b>: 순수 릴리스 스피드. 110 초과 시 프로 상위권 강속구<br>
• <b style="color:#ffffff;">호프 (Ride+)</b>: 중력 낙하를 이겨내는 수직 상승 성분 (IVB). 헛스윙 유도력<br>
• <b style="color:#ffffff;">가로변화 (Run+)</b>: 배트 중심을 빗맞히는 가로 꺾임 폭 (HB)<br>
• <b style="color:#ffffff;">스핀효율 (Eff+)</b>: 변화량으로 직결되는 유효 회전 비율 (액티브 스핀)<br>
• <b style="color:#ffffff;">앞도달 (Ext+)</b>: 타자 쪽으로 팔을 끌고 나와 던지는 릴리스 익스텐션
</div>""",
        "zh": """<div style="background-color: #1a1e29; border: 1px solid #0284c7; border-radius: 10px; padding: 12px 16px; font-size: 11.5px; color: #38bdf8; line-height: 1.75; margin-top: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.25);">
<b style="color: #38bdf8; font-size: 12.5px;">【五大球質指標解析 (基準: 職棒平均 = 100)】</b><br>
• <b style="color:#ffffff;">球速 (Velo+)</b>: 純初速速度。110以上為頂級火球<br>
• <b style="color:#ffffff;">升力 (Ride+)</b>: 對抗重力下墜的垂直竄升量 (IVB)。揮空率與擦棒球保證<br>
• <b style="color:#ffffff;">位移 (Run+)</b>: 錯開擊球甜蜜點的橫向偏折量 (HB)<br>
• <b style="color:#ffffff;">效率 (Eff+)</b>: 轉化為進壘位移的有效旋轉比例 (非子彈旋轉比率)<br>
• <b style="color:#ffffff;">步幅 (Ext+)</b>: 往前延伸釋放球的長度。大幅強化打者體感球速
</div>""",
    },
    "stuff_plus_score_label": {
        "ja": "総合 Stuff+ 指数",
        "en": "Overall Stuff+ Rating",
        "es": "Índice Stuff+ General",
        "ko": "종합 Stuff+ 지수",
        "zh": "綜合 Stuff+ 評分",
    },
    "ideal_slot_label": {
        "ja": "理想スロット",
        "en": "Ideal Arm Slot",
        "es": "Ángulo de Brazo Ideal",
        "ko": "이상적 암슬롯",
        "zh": "理想出手角度",
    },
    "vs_pro_avg": {
        "ja": "(プロ平均比)",
        "en": "(vs Pro Avg)",
        "es": "(vs Prom. Pro)",
        "ko": "(프로 평균 대비)",
        "zh": "(對職棒平均)",
    },
    "pitch_archetype_label": {
        "ja": "球質タイプ判定",
        "en": "Pitch Archetype",
        "es": "Tipo de Movimiento",
        "ko": "구질 타입 판정",
        "zh": "球質型態判定",
    },
    "movement_profile_label": {
        "ja": "変化特性",
        "en": "Movement Profile",
        "es": "Perfil de Movimiento",
        "ko": "무브먼트 특성",
        "zh": "位移特性診斷",
    },
    "actual_label": {
        "ja": "実測",
        "en": "Actual",
        "es": "Real",
        "ko": "실측",
        "zh": "實測",
    },
    "3d_mouse_hint": {
        "ja": "💡 3D画面はマウスのドラッグで360度自由回転、スクロールでズームイン/アウトが可能です。",
        "en": "💡 Click & drag to rotate 3D view 360°, scroll to zoom in/out.",
        "es": "💡 Arrastre el mouse para rotar en 360°, use la rueda para hacer zoom.",
        "ko": "💡 마우스 드래그로 3D 화면을 360도 자유 회전하고, 스크롤로 확대/축소할 수 있습니다.",
        "zh": "💡 可按住滑鼠拖曳360度自由旋轉3D畫面，滾動滾輪可放大/縮小。",
    },
    "3d_lift_btn": {
        "ja": "🎯 揚力",
        "en": "🎯 Lift",
        "es": "🎯 Sustentación",
        "ko": "🎯 양력",
        "zh": "🎯 升力",
    },
    "3d_grip_off_btn": {
        "ja": "✋ 握り OFF",
        "en": "✋ Grip OFF",
        "es": "✋ Agarre OFF",
        "ko": "✋ 그립 OFF",
        "zh": "✋ 握法 OFF",
    },
    "gravity_only": {
        "ja": "(0,0) 重力落下",
        "en": "(0,0) Gravity Only",
        "es": "(0,0) Caída Libre",
        "ko": "(0,0) 중력낙하",
        "zh": "(0,0) 純重力下墜",
    },
    "movement_plot_your_pitch": {
        "ja": "  ⚾ 今回の投球",
        "en": "  ⚾ Your Pitch",
        "es": "  ⚾ Tu Lanzamiento",
        "ko": "  ⚾ 이번 투구",
        "zh": "  ⚾ 本次投球",
    },
    "movement_plot_measured_loc": {
        "ja": "📍 実測ボール位置",
        "en": "📍 Measured Ball",
        "es": "📍 Bola Real",
        "ko": "📍 실측 볼 위치",
        "zh": "📍 實測進壘位置",
    },
    "legend_your_pitch": {
        "ja": "あなたの投球",
        "en": "Your Pitch",
        "es": "Tu Lanzamiento",
        "ko": "당신의 투구",
        "zh": "您的投球",
    },
    "pitch_velocity_badge": {
        "ja": "PITCH VELOCITY (初速)",
        "en": "PITCH VELOCITY (RELEASE)",
        "es": "VELOCIDAD DE LANZAMIENTO (SALIDA)",
        "ko": "PITCH VELOCITY (초속)",
        "zh": "PITCH VELOCITY (初速)",
    },
    "pitch_tunnel_header": {
        "ja": "🌀 3Dピッチトンネル＆打者コミットメント判定 (7.2m)",
        "en": "🌀 3D Pitch Tunneling & Commitment Point (7.2m)",
        "es": "🌀 Túnel de Lanzamiento 3D y Punto de Decisión",
        "ko": "🌀 3D 피치 터널 & 타자 판단 결정점 (7.2m)",
        "zh": "🌀 3D共軌投球隧道與打者決策點 (壘前7.2m)",
    },
    "commit_dist_label": {
        "ja": "打者判断点(7.2m手前) トンネル幅",
        "en": "Decision Point (7.2m) Tunnel Width",
        "es": "Ancho de Túnel en Decisión (7.2m)",
        "ko": "판단점(7.2m) 터널 간격",
        "zh": "決策點(前7.2m) 隧道軌跡差距",
    },
    "plate_dist_label": {
        "ja": "ホームプレート到達時 分離幅",
        "en": "Home Plate Final Separation",
        "es": "Separación Final en el Plato",
        "ko": "홈플레이트 최종 분리폭",
        "zh": "本壘板進壘最終位移差距",
    },
    "tunnel_ratio_label": {
        "ja": "トンネル変化倍率",
        "en": "Tunnel Expansion Ratio",
        "es": "Ratio de Expansión del Túnel",
        "ko": "터널 확장 배율",
        "zh": "共軌隧道放大擴散倍率",
    },
    "paywall_dialog_title": {
        "ja": "💎 料金プラン・サブスクリプション (Powered by RevenueCat)",
        "en": "💎 Plans & Subscriptions (Powered by RevenueCat)",
        "es": "💎 Planes y Suscripciones (Powered by RevenueCat)",
        "ko": "💎 요금제 및 구독 (Powered by RevenueCat)",
        "zh": "💎 訂閱方案與方案管理 (Powered by RevenueCat)",
    },
    "paywall_header_title": {
        "ja": "あなたのピッチングをネクストレベルへ",
        "en": "Take Your Pitching to the Next Level",
        "es": "Lleva Tu Lanzamiento al Siguiente Nivel",
        "ko": "당신의 피칭을 다음 레벨로",
        "zh": "將您的投球水準提升至全新境界",
    },
    "paywall_header_subtitle": {
        "ja": "プロ基準の3D弾道解析、Stuff+球質評価、フォーム同期比較を完全アンロック",
        "en": "Unlock Pro 3D Trajectory, Stuff+ Radar, and Synchronized Mechanics",
        "es": "Desbloquea Trayectoria 3D Pro, Radar Stuff+ y Comparación Sincronizada",
        "ko": "프로 기준 3D 궤적 분석, Stuff+ 구질 평가, 폼 동기화 비교 완전 잠금 해제",
        "zh": "全面解鎖職棒級 3D 彈道軌跡、Stuff+ 球質五維評估與動作同步比對",
    },
    "paywall_current_plan": {
        "ja": "✅ 現在のプラン",
        "en": "✅ Current Plan",
        "es": "✅ Plan Actual",
        "ko": "✅ 현재 플랜",
        "zh": "✅ 當前方案",
    },
    "paywall_test_purchase": {
        "ja": "🧪 {name}をテスト購入",
        "en": "🧪 Test Purchase {name}",
        "es": "🧪 Probar Compra {name}",
        "ko": "🧪 {name} 테스트 구매",
        "zh": "🧪 測試訂閱 {name}",
    },
    "paywall_purchase_success": {
        "ja": "🎉 [RevenueCat Sandbox] {name} の購入に成功！ (isSubscribed = True)",
        "en": "🎉 [RevenueCat Sandbox] Successfully purchased {name}! (isSubscribed = True)",
        "es": "🎉 [RevenueCat Sandbox] ¡Compra exitosa de {name}! (isSubscribed = True)",
        "ko": "🎉 [RevenueCat Sandbox] {name} 구매 성공! (isSubscribed = True)",
        "zh": "🎉 [RevenueCat Sandbox] {name} 訂閱成功！ (isSubscribed = True)",
    },
    "paywall_free_switched": {
        "ja": "🌱 Free プランに切り替えました。(isSubscribed = False)",
        "en": "🌱 Switched to Free Plan (isSubscribed = False)",
        "es": "🌱 Cambiado al Plan Gratis (isSubscribed = False)",
        "ko": "🌱 Free 플랜으로 전환되었습니다 (isSubscribed = False)",
        "zh": "🌱 已切換為 Free 免費方案 (isSubscribed = False)",
    },
    "paywall_footer_note": {
        "ja": "🔒 <b>課金インフラ: RevenueCat 連携</b>（App Store IAP / Google Play Billing / Stripe Web決済対応）<br>🧪 <b>Sandbox テスト環境</b>: 実際の課金は発生しません。Shipaton提出用デモ構成です。",
        "en": "🔒 <b>Billing Infrastructure: Powered by RevenueCat</b> (App Store IAP, Google Play, Stripe supported)<br>🧪 <b>Sandbox Test Environment</b>: No real charges will occur. Prototype configured for Shipaton demo.",
        "es": "🔒 <b>Infraestructura de Pagos: RevenueCat</b> (Compatible con App Store IAP, Google Play, Stripe)<br>🧪 <b>Entorno Sandbox de Prueba</b>: No se realizarán cargos reales. Prototipo para Shipaton.",
        "ko": "🔒 <b>결제 인프라: RevenueCat 연동</b> (App Store IAP / Google Play Billing / Stripe 지원)<br>🧪 <b>Sandbox 테스트 환경</b>: 실제 요금이 청구되지 않습니다. Shipaton 제출용 데모 구성입니다.",
        "zh": "🔒 <b>付費基建: RevenueCat 連線</b>（支援 App Store IAP / Google Play Billing / Stripe 線上支付）<br>🧪 <b>Sandbox 測試環境</b>: 不會產生實際扣款，為 Shipaton 審查演示架構。",
    },
    "plan_badge_btn": {
        "ja": "{badge} プラン (RevenueCat)",
        "en": "{badge} Plan (RevenueCat)",
        "es": "Plan {badge} (RevenueCat)",
        "ko": "{badge} 플랜 (RevenueCat)",
        "zh": "{badge} 方案 (RevenueCat)",
    },
    "sb_paywall_view_btn": {
        "ja": "💎 料金プラン確認 (Paywall)",
        "en": "💎 View Plans (Paywall)",
        "es": "💎 Ver Planes (Paywall)",
        "ko": "💎 요금제 확인 (Paywall)",
        "zh": "💎 查看方案 (Paywall)",
    },
    "demo_switch_plan_label": {
        "ja": "【デモ用】プラン切替",
        "en": "[Demo] Switch Plan",
        "es": "[Demo] Cambiar Plan",
        "ko": "[데모용] 플랜 전환",
        "zh": "[演示] 切換方案",
    },
    "demo_switch_plan_help": {
        "ja": "動画撮影用にプラン表示を即時切り替えられます",
        "en": "Instantly switch active plan for demonstration",
        "es": "Cambie el plan activo para la demostración",
        "ko": "영상 촬영용으로 플랜을 즉시 전환할 수 있습니다",
        "zh": "可即時切換當前方案以供影片拍攝演示",
    },
    "tunnel_view_catcher": {
        "ja": "🎯 捕手・打者視点 (Catcher)",
        "en": "🎯 Catcher / Batter View",
        "es": "🎯 Vista del Receptor",
        "ko": "🎯 포수·타자 시점",
        "zh": "🎯 捕手/打者 視角",
    },
    "tunnel_view_pitcher": {
        "ja": "🏟️ 投手視点 (Pitcher)",
        "en": "🏟️ Pitcher's Eye View",
        "es": "🏟️ Vista del Lanzador",
        "ko": "🏟️ 투수 시점",
        "zh": "🏟️ 投手視角",
    },
    "tunnel_view_side": {
        "ja": "📺 側面アングル (Side)",
        "en": "📺 Side 3D View",
        "es": "📺 Vista Lateral 3D",
        "ko": "📺 측면 3D 뷰",
        "zh": "📺 側面 3D 視角",
    },
    "tunnel_view_top": {
        "ja": "🪟 真上俯瞰 (Top-Down)",
        "en": "🪟 Top-Down View",
        "es": "🪟 Vista Superior",
        "ko": "🪟 상공 평면 뷰",
        "zh": "🪟 頂部俯瞰視角",
    },
    "tunnel_xaxis_title": {
        "ja": "水平 X (m)",
        "en": "Horizontal X (m)",
        "es": "Horizontal X (m)",
        "ko": "가로 X (m)",
        "zh": "水平 X (m)",
    },
    "tunnel_yaxis_title": {
        "ja": "距離 Y (m)",
        "en": "Distance Y (m)",
        "es": "Distancia Y (m)",
        "ko": "거리 Y (m)",
        "zh": "距離 Y (m)",
    },
    "tunnel_zaxis_title": {
        "ja": "高さ Z (m)",
        "en": "Height Z (m)",
        "es": "Altura Z (m)",
        "ko": "높이 Z (m)",
        "zh": "高度 Z (m)",
    },
    "strike_zone_name": {
        "ja": "ストライクゾーン",
        "en": "Strike Zone",
        "es": "Zona de Strike",
        "ko": "스트라이크 존",
        "zh": "好球帶",
    },
    "tunnel_zone_name": {
        "ja": "🌀 ピッチトンネル (Tunnel)",
        "en": "🌀 Pitch Tunnel Zone",
        "es": "🌀 Zona de Túnel",
        "ko": "🌀 피치 터널 영역",
        "zh": "🌀 投球共軌隧道區",
    },
    "commit_point_name": {
        "ja": "⚡ 打者判断決定点 (7.2m手前)",
        "en": "⚡ Commit Point (7.2m)",
        "es": "⚡ Punto de Decisión (7.2m)",
        "ko": "⚡ 타자 판단점 (7.2m)",
        "zh": "⚡ 打者決策點 (壘前7.2m)",
    },
    "sync_player_header": {
        "ja": "⏱ 2投球フォーム完全同期スプリット再生 (Sync Player)",
        "en": "⏱ Synchronized Dual-Pitch Form Player",
        "es": "⏱ Reproductor Sincronizado de Dos Lanzamientos",
        "ko": "⏱ 2구 폼 완전 동기화 스플릿 재생",
        "zh": "⏱ 雙投球動作完全同步雙分割播放器",
    },
    "sync_frame_label": {
        "ja": "リリース基準 同期コマ送り",
        "en": "Sync Frame (Relative to Release)",
        "es": "Cuadro Sincronizado (Relativo a la Soltada)",
        "ko": "릴리스 기준 동기화 프레임",
        "zh": "以出手點為基準之同步逐幀滑桿",
    },
    "broadcast_card_btn": {
        "ja": "📥 MLB中継風「投球スタッツカード (PNG)」を保存",
        "en": "📥 Download MLB Broadcast Stats Card (PNG)",
        "es": "📥 Descargar Tarjeta de Estadísticas Estilo MLB",
        "ko": "📥 MLB 중계 스타일 투구 스탯 카드 (PNG) 저장",
        "zh": "📥 下載大聯盟轉播級「投球數據卡 (PNG)」",
    },


}


def t(key: str, lang: str = "ja", **kwargs) -> str:
    """翻訳キーから指定言語のテキストを取得し、フォーマットして返す。"""
    entry = TRANSLATIONS.get(key, {})
    val = entry.get(lang, entry.get("ja", key))
    if kwargs:
        try:
            return val.format(**kwargs)
        except Exception:
            return val
    return val


def get_phase_label(phase_key: str, frame_num: int, lang: str = "ja") -> str:
    """フェーズキーからローカライズされたボタンラベルを返す。"""
    pk = phase_key
    if "足上げ" in pk or "Lift" in pk or pk == "leg_lift":
        code = "leg_lift"
    elif "着地" in pk or "Plant" in pk or pk == "foot_plant":
        code = "foot_plant"
    elif "外旋" in pk or "MER" in pk or pk == "mer":
        code = "mer"
    elif "リリース" in pk or "Release" in pk or pk == "release":
        code = "release"
    elif "フォロースルー" in pk or "Follow" in pk or pk == "follow_through":
        code = "follow_through"
    else:
        code = pk

    name_dict = {
        "leg_lift": {
            "ja": "① 足上げ",
            "en": "① Leg Lift",
            "es": "① Levantamiento",
            "ko": "① 다리 올리기",
            "zh": "① 抬腿",
        },
        "foot_plant": {
            "ja": "② 踏み出し着地",
            "en": "② Foot Plant",
            "es": "② Apoyo del Pie",
            "ko": "② 착지",
            "zh": "② 著地",
        },
        "mer": {
            "ja": "③ 最大外旋",
            "en": "③ MER / Top",
            "es": "③ MER / Tope",
            "ko": "③ 최대 외회전",
            "zh": "③ 最大外旋",
        },
        "release": {
            "ja": "④ リリース",
            "en": "④ Ball Release",
            "es": "④ Soltada",
            "ko": "④ 릴리스",
            "zh": "④ 出手點",
        },
        "follow_through": {
            "ja": "⑤ フォロースルー",
            "en": "⑤ Follow-Through",
            "es": "⑤ Terminación",
            "ko": "⑤ 팔로우스루",
            "zh": "⑤ 隨球動作",
        },
    }
    short_name = name_dict.get(code, {}).get(lang, phase_key)
    return f"{short_name} ({frame_num})"

def get_phase_components(phase_key: str, lang: str = "ja"):
    """フェーズの主タイトルと英語サブタイトルを返す（ボタン外側表示用）。"""
    pk = phase_key.lower()
    if "足上げ" in pk or "balance" in pk or "leg" in pk:
        code = "leg_lift"
    elif "踏み出し" in pk or "foot" in pk or "plant" in pk or "着地" in pk:
        code = "foot_plant"
    elif "外旋" in pk or "mer" in pk or "top" in pk:
        code = "mer"
    elif "リリース" in pk or "release" in pk:
        code = "release"
    elif "フォロー" in pk or "follow" in pk:
        code = "follow_through"
    else:
        code = pk

    titles = {
        "leg_lift": {"ja": "① 足上げ", "en": "① Leg Lift", "es": "① Levantamiento", "ko": "① 다리 올리기", "zh": "① 抬腿"},
        "foot_plant": {"ja": "② 踏み出し", "en": "② Foot Plant", "es": "② Apoyo Pie", "ko": "② 착지", "zh": "② 著地"},
        "mer": {"ja": "③ 最大外旋", "en": "③ MER (Top)", "es": "③ MER (Tope)", "ko": "③ 최대외회전", "zh": "③ 最大外旋"},
        "release": {"ja": "④ リリース", "en": "④ Release", "es": "④ Soltada", "ko": "④ 릴리스", "zh": "④ 出手點"},
        "follow_through": {"ja": "⑤ フォロー", "en": "⑤ Follow", "es": "⑤ Terminación", "ko": "⑤ 팔로우스루", "zh": "⑤ 隨球動作"},
    }
    subs = {
        "leg_lift": "Balance Point",
        "foot_plant": "Foot Plant",
        "mer": "MER / Cocking",
        "release": "Ball Release",
        "follow_through": "Follow-Through",
    }
    t = titles.get(code, {}).get(lang, phase_key)
    s = subs.get(code, "")
    return t, s




def get_slot_name(slot_key: str, lang: str = "ja") -> str:
    """アームスロット名を指定言語で取得。"""
    slots = {
        "オーバースロー": {
            "ja": "オーバースロー",
            "en": "Overhand",
            "es": "Sobre el Brazo",
            "ko": "오버핸드",
            "zh": "高壓式",
        },
        "スリークォーター": {
            "ja": "スリークォーター",
            "en": "Three-Quarters",
            "es": "Tres Cuartos",
            "ko": "스리쿼터",
            "zh": "四分之三",
        },
        "サイドスロー": {
            "ja": "サイドスロー",
            "en": "Sidearm",
            "es": "Por el Lado",
            "ko": "사이드암",
            "zh": "側投",
        },
        "アンダースロー": {
            "ja": "アンダースロー",
            "en": "Submarine",
            "es": "Submarino",
            "ko": "언더핸드",
            "zh": "下勾低肩",
        },
    }
    return slots.get(slot_key, {}).get(lang, slot_key)



def get_knee_feedback(knee: float, lang: str = "ja"):
    """前膝角度の評価とフィードバックテキストを返す。"""
    if knee >= 165:
        score_delta = 8
        txt = {
            "ja": f"前膝ブロッキング (角度: {knee:.1f}°): 踏み出し足の膝が強固に伸びてブロックできており、並進エネルギーが逃げずに上半身へ高効率に伝達されています。",
            "en": f"Lead Knee Blocking ({knee:.1f}°): Strong front-knee brace stops linear momentum, transferring lower-body energy cleanly into torso rotation.",
            "es": f"Bloqueo de Rodilla Delantera ({knee:.1f}°): El firme bloqueo de la pierna frena eficientemente la energía lineal y la transfiere al torso.",
            "ko": f"앞무릎 브로킹 (각도: {knee:.1f}°): 착지 다리가 단단하게 펴져 하체의 병진 에너지가 상체로 극히 효율적으로 전달되고 있습니다.",
            "zh": f"前膝支撐煞車 (角度: {knee:.1f}°): 跨步腳前膝強勢伸展支撐，下半身動能極高效率轉化為上半身旋轉力道。",
        }.get(lang)
        return score_delta, [txt], []
    elif knee >= 145:
        score_delta = 4
        st = {
            "ja": f"着地足の安定感 (角度: {knee:.1f}°): 踏み込みの安定性が保たれています。",
            "en": f"Landing Stability ({knee:.1f}°): Foot plant provides good balance and balance control.",
            "es": f"Estabilidad del Aterrizaje ({knee:.1f}°): El apoyo del pie proporciona buen equilibrio.",
            "ko": f"착지 안정성 (각도: {knee:.1f}°): 디딤발의 착지 밸런스가 안정적입니다.",
            "zh": f"著地穩定性 (角度: {knee:.1f}°): 跨步著地維持良好的下盤平衡度。",
        }.get(lang)
        imp = {
            "ja": "リリース直前に前膝をさらにピンと突っ張る意識（伸展動作）を持つと、骨盤の急減速から回転加速が促され、球速向上が期待できます。",
            "en": "Focus on firmly bracing the lead knee at release to accelerate pelvic decel and whip the torso faster.",
            "es": "Extiende firmemente la rodilla delantera justo antes de soltar para acelerar la rotación del tronco y ganar velocidad.",
            "ko": "릴리스 직전에 앞무릎을 단단히 펴며 버티면 골반 급감속을 통해 상체 회전 가속과 구속 상승을 이끌어낼 수 있습니다.",
            "zh": "出手前夕加強前膝打直煞車動作，能帶動骨盆急停與上半身爆發加速，顯著提升球速。",
        }.get(lang)
        return score_delta, [st], [imp]
    else:
        score_delta = -5
        imp = {
            "ja": f"前膝抜けの改善 (角度: {knee:.1f}°): 着地足の膝が曲がり気味（膝抜け）でエネルギーが逃げています。前足の壁を意識して突っ張ると球威が増します。",
            "en": f"Lead Knee Collapse ({knee:.1f}°): The front knee bends excessively, leaking momentum. Firm up the lead-leg brace to increase velocity.",
            "es": f"Colapso de Rodilla Delantera ({knee:.1f}°): La rodilla delantera se flexiona en exceso, perdiendo energía. Afirma el bloqueo de la pierna.",
            "ko": f"앞무릎 꺾임 개선 (각도: {knee:.1f}°): 착지 다리 무릎이 다소 굽혀져 에너지가 새어나가고 있습니다. 앞발의 벽을 단단히 버티면 구위가 향상됩니다.",
            "zh": f"前膝緩衝過度 (角度: {knee:.1f}°): 著地腳膝蓋彎曲過多導致衝力流失。建立前腳支撐牆能大幅增加球威。",
        }.get(lang)
        return score_delta, [], [imp]



def get_elbow_feedback(elbow: float, lang: str = "ja"):
    """肘角度の評価とフィードバックテキストを返す。"""
    if 85 <= elbow <= 125:
        score_delta = 7
        txt = {
            "ja": f"理想的な肘のしなり (角度: {elbow:.1f}°): リリース時の肘屈曲角が約90〜110°の適正範囲にあり、肩肘への負担を抑えつつムチのように加速する理想的なアームアクションです。",
            "en": f"Optimal Elbow Flexion ({elbow:.1f}°): Elbow angle is in the ideal 90–110° power pocket, maximizing whip acceleration while protecting the arm.",
            "es": f"Flexión de Codo Ideal ({elbow:.1f}°): Ángulo de 90–110° perfecto en la soltada, generando efecto de látigo y reduciendo el estrés en el brazo.",
            "ko": f"이상적인 팔꿈치 굴곡 (각도: {elbow:.1f}°): 릴리스 시 팔꿈치 각도가 90~110° 적정 범위로, 팔 부담을 줄이면서 채찍 같은 가속을 만듭니다.",
            "zh": f"理想手肘屈曲 (角度: {elbow:.1f}°): 出手手肘角度維持在 90~110° 黃金區間，兼具鞭擊加速效果並保護肩肘關節。",
        }.get(lang)
        return score_delta, [txt], []
    elif elbow > 125:
        score_delta = 0
        imp = {
            "ja": f"肘の伸展タイミング (角度: {elbow:.1f}°): 肘がやや早めに伸びてアーム投げ傾向があります。トップ〜胸郭回旋まで肘の90度前後の角度を保つとしなりが効きます。",
            "en": f"Arm Whip Timing ({elbow:.1f}°): Elbow extends slightly too early. Maintain elbow flexion until late trunk rotation for greater whip action.",
            "es": f"Tiempo de Extensión del Codo ({elbow:.1f}°): El codo se extiende antes de tiempo. Mantén la flexión hasta la rotación del tronco para más latigazo.",
            "ko": f"팔꿈치 신전 타이밍 ({elbow:.1f}°): 팔꿈치가 다소 일찍 펴집니다. 가슴 회전까지 팔꿈치 굴곡을 유지하면 회전 채찍 효과가 극대화됩니다.",
            "zh": f"手肘伸展時機 (角度: {elbow:.1f}°): 手肘伸展略早。軀幹加速旋轉前維持屈肘能發揮更佳的鞭擊威力。",
        }.get(lang)
        return score_delta, [], [imp]
    else:
        score_delta = 0
        imp = {
            "ja": f"肘の懐作り (角度: {elbow:.1f}°): 肘が過度に畳まれています。トップで適度な懐（ふところ）を作ることで遠心力を引き出せます。",
            "en": f"Elbow Spacing ({elbow:.1f}°): Elbow is tucked too close. Creating more space at the top generates greater rotational torque.",
            "es": f"Espacio del Codo ({elbow:.1f}°): El codo está demasiado recogido. Crear más espacio en el tope genera mayor torsión rotacional.",
            "ko": f"팔꿈치 여유 공간 ({elbow:.1f}°): 팔꿈치가 지나치게 좁혀져 있습니다. 탑 위치에서 충분한 공간을 확보하면 원심력을 더 살릴 수 있습니다.",
            "zh": f"出手胸前空間 (角度: {elbow:.1f}°): 手肘過度內縮。建議頂點蓄力時保留合適空間以帶出更大離心力。",
        }.get(lang)
        return score_delta, [], [imp]


def get_slot_feedback(slot_name: str, forearm_slot: float, lang: str = "ja"):
    """アームスロットの解説テキストを返す。"""
    loc_slot = get_slot_name(slot_name, lang)
    slot_desc = {
        "オーバースロー": {
            "ja": "高い打点から角度を活かして投げ下ろすフォームです。",
            "en": "Delivers downward plane with high release angle.",
            "es": "Lanza con gran plano descendente desde un punto alto.",
            "ko": "높은 타점에서 각도를 살려 꽂아 내리는 폼입니다.",
            "zh": "從高出手點發揮角度優勢向下重壓進壘。",
        },
        "スリークォーター": {
            "ja": "身体の回旋プレーンに最も自然に腕が乗り、球速・回転数・制球力のバランスが最高峰の王道スロットです。",
            "en": "Most natural arm slot aligned with shoulder rotation, maximizing velocity, spin, and command.",
            "es": "El ángulo más natural alineado con el torso, optimizando velocidad, rotación y control.",
            "ko": "상체 회전면에 가장 자연스럽게 실려 구속, 회전수, 제구의 밸런스가 뛰어난 정통 슬롯입니다.",
            "zh": "最契合軀幹旋轉平面的自然出手角度，兼備球速、轉速與控球的黃金比例。",
        },
        "サイドスロー": {
            "ja": "骨盤と体幹の横回転をフルに活かし、横の角度と強い変化球のキレで勝負できるフォームです。",
            "en": "Harnesses rotational torque with deceptive horizontal angle and sharp break.",
            "es": "Aprovecha la rotación lateral del cuerpo con gran quiebre horizontal engañoso.",
            "ko": "골반과 몸통의 횡회전을 극대화해 좌우 각도와 날카로운 변화구 각을 만드는 폼입니다.",
            "zh": "充分利用核心橫向轉體，產生極佳橫向進壘角度與位移銳利的變化球。",
        },
        "アンダースロー": {
            "ja": "地面スレスレの低いリリースから浮き上がる球筋を生み出すフォームです。",
            "en": "Rising pitch trajectory released close to the ground.",
            "es": "Trayectoria ascendente única soltada casi a ras del suelo.",
            "ko": "지면 가까운 낮은 릴리스에서 떠오르는 독특한 궤적을 만드는 폼입니다.",
            "zh": "緊貼地面的超低出手點，造就宛如向上竄升的特殊進壘軌跡。",
        },
    }.get(slot_name, {}).get(lang, "Balanced mechanics.")
    title = {"ja": "アームスロット", "en": "Arm Slot", "es": "Ángulo de Brazo", "ko": "암 슬롯", "zh": "出手角度"}.get(lang, "Arm Slot")
    return f"{title}: {loc_slot} ({forearm_slot:.1f}°): {slot_desc}"



def get_stride_feedback(stride_pct: float, lang: str = "ja"):
    """歩幅比率（対身長）の評価とフィードバックを返す。"""
    if stride_pct >= 95:
        txt = {
            "ja": f"メジャークラスの長大ストライド (歩幅比率: {stride_pct:.1f}%): 身長と同等以上の驚異的なステップ幅を誇り、打者との距離を極限まで縮めて強烈な体感速度を生み出しています。",
            "en": f"Elite Extension ({stride_pct:.1f}% of height): Stride matches or exceeds body height, drastically cutting down distance to the batter and maximizing perceived velocity.",
            "es": f"Extensión Élite de Grandes Ligas ({stride_pct:.1f}% de altura): Zancada igual o superior a la altura corporal, acortando al máximo la distancia al plato.",
            "ko": f"메이저리그급 최상위 익스텐션 (보폭 비율: {stride_pct:.1f}%): 신장과 맞먹는 긴 스트라이드로 타자와의 거리를 극단적으로 좁혀 엄청난 체감 구속을 만듭니다.",
            "zh": f"大聯盟級極限延伸 (步幅比: {stride_pct:.1f}%): 步幅達到或超越身高，將出手點極度前推，創造壓倒性的打者體感球速。",
        }.get(lang, f"Elite Extension ({stride_pct:.1f}%)")
        return 5, [txt], []
    elif stride_pct >= 75:
        txt = {
            "ja": f"ダイナミックなステップ (歩幅比率: {stride_pct:.1f}%): 身長の75%以上の大きなストライドが取れており、低く鋭いステップで球持ちが抜群です。",
            "en": f"Dynamic Stride Length ({stride_pct:.1f}% of height): Stride exceeds 75% of height, driving down the mound with great extension.",
            "es": f"Zancada Dinámica ({stride_pct:.1f}% de altura): Zancada de más del 75% de la altura, logrando gran extensión hacia el plato.",
            "ko": f"다이내믹한 스트라이드 (보폭 비율: {stride_pct:.1f}%): 신장의 75% 이상 큰 보폭으로 릴리스를 타자 쪽으로 깊게 끌고 나갑니다.",
            "zh": f"強勁跨步延伸 (步幅比: {stride_pct:.1f}%): 跨步達身高 75% 以上，充分利用投手丘傾斜度向前大幅延伸出手。",
        }.get(lang, f"Dynamic Stride Length ({stride_pct:.1f}%)")
        return 5, [txt], []
    elif stride_pct > 0:
        imp = {
            "ja": f"ステップ幅の活用 (歩幅比率: {stride_pct:.1f}%): 軸足の股関節でタメを作り、あと5〜10cm前へ踏み出せるとエクステンションが伸び、打者の手元での体感速度が向上します。",
            "en": f"Extension Potential ({stride_pct:.1f}% of height): Loading back-hip hinge to stride 2–4 inches further forward will significantly boost perceived velocity.",
            "es": f"Aprovechar la Extensión ({stride_pct:.1f}% de altura): Un paso 5-10 cm más largo hacia adelante aumentará la velocidad percibida por el bateador.",
            "ko": f"익스텐션 활용 ({stride_pct:.1f}%): 축발 고관절을 활용해 5~10cm만 더 앞쪽으로 내딛으면 타자 체감 구속이 2~3km/h 상승합니다.",
            "zh": f"延伸空間潛力 ({stride_pct:.1f}%): 後腳髖關節充分蓄力，若能再向前踏出 5-10 公分，打者體感球速將顯著提升。",
        }.get(lang, f"Extension Potential ({stride_pct:.1f}%)")
        return 0, [], [imp]
    return 0, [], []


def get_headline(grade: str, score: int, lang: str = "ja") -> str:
    """総合フォーム評価の見出し文字列を返す。"""
    headlines = {
        "ja": f"総合フォーム評価: {grade} ({score}点)",
        "en": f"Overall Mechanics Grade: {grade} ({score} pts)",
        "es": f"Calificación General: {grade} ({score} pts)",
        "ko": f"종합 투구 폼 판정: {grade} ({score}점)",
        "zh": f"整體姿勢評級: {grade} ({score}分)",
    }
    return headlines.get(lang, f"Grade {grade} ({score} pts)")


def get_subscription_plans(lang: str = "ja", current_plan: str = "Pro") -> list:
    """言語設定に応じたサブスクリプションプラン情報（USD/JPY、価格、多言語説明）を返す。
    日本語('ja')の場合はJPY（円）、英語等の場合はUSD（ドル）表記。
    """
    is_jpy = (lang == "ja")

    names = {
        "Free": {"ja": "Free (無料)", "en": "Free", "es": "Gratis", "ko": "Free (무료)", "zh": "Free (免費)"},
        "Pro": {"ja": "Pro (月額)", "en": "Pro Monthly", "es": "Pro Mensual", "ko": "Pro (월간)", "zh": "Pro (月繳)"},
        "Elite": {"ja": "Elite (年額)", "en": "Elite Annual", "es": "Elite Anual", "ko": "Elite (연간)", "zh": "Elite (年繳)"},
    }
    badges = {
        "Free": {"ja": "🌱 スタンダード", "en": "🌱 Standard", "es": "🌱 Estándar", "ko": "🌱 기본", "zh": "🌱 基本版"},
        "Pro": {"ja": "人気No.1 👑", "en": "Most Popular 👑", "es": "Más Popular 👑", "ko": "인기 No.1 👑", "zh": "最受歡迎 👑"},
        "Elite": {"ja": "約25%お得 ✨", "en": "Save ~25% ✨", "es": "Ahorra ~25% ✨", "ko": "약 25% 할인 ✨", "zh": "現省約 25% ✨"},
    }
    periods = {
        "Free": {"ja": "/ ずっと無料", "en": "/ forever free", "es": "/ gratis siempre", "ko": "/ 영구 무료", "zh": "/ 永久免費"},
        "Pro": {"ja": "/ 月 (いつでも解約可)", "en": "/ month (cancel anytime)", "es": "/ mes", "ko": "/ 월 (언제든 해지 가능)", "zh": "/ 月 (隨時可取消)"},
        "Elite": {"ja": "/ 年 (¥1,483/月)", "en": "/ year ($11.66/mo)", "es": "/ año ($11.66/mes)", "ko": "/ 년 (월 $11.66)", "zh": "/ 年 (月約 $11.66)"},
    }

    # 改定価格 (RevenueCat Billing設定準拠: JPY ¥1,980/月, ¥17,800/年 | USD $12.99/mo, $139.99/yr)
    prices = {
        "Free": "¥0" if is_jpy else "$0",
        "Pro": "¥1,980" if is_jpy else "$12.99",
        "Elite": "¥17,800" if is_jpy else "$139.99",
    }

    features_all = {
        "Free": {
            "ja": ["投球初速スピード計測 (km/h & mph)", "基本2D弾道・ストライクゾーン", "投球履歴の直近3件保存", "<s style='color:#94a3b8;'>Statcast 3D弾道＆ピッチトンネル</s>", "<s style='color:#94a3b8;'>Stuff+ 球質5軸レーダー評価</s>", "<s style='color:#94a3b8;'>2投球フォーム完全同期比較</s>"],
            "en": ["Pitch velocity tracking (km/h & mph)", "Basic 2D trajectory & strike zone", "Store up to 3 recent pitches", "<s style='color:#94a3b8;'>Statcast 3D Trajectory & Pitch Tunnel</s>", "<s style='color:#94a3b8;'>Stuff+ 5-Axis Radar Evaluation</s>", "<s style='color:#94a3b8;'>Synchronized Dual Mechanics Player</s>"],
        },
        "Pro": {
            "ja": ["<b>Freeの全機能</b>", "Statcast 3D弾道＆立体ゾーン", "3D回転球 (4シーム・握り方)", "Stuff+ 球質5軸レーダー評価", "2投球フォーム完全同期スプリット再生", "履歴 無制限保存＆CSVエクスポート"],
            "en": ["<b>All Free Features</b>", "Statcast 3D Trajectory & 3D Zone", "3D Spinning Ball (4-Seam & Grips)", "Stuff+ 5-Axis Quality Radar", "Synchronized Dual Form Player", "Unlimited History & CSV Export"],
        },
        "Elite": {
            "ja": ["<b>Proの全機能</b>", "MLB中継風「投球カード (PNG)」保存", "連続フォーム残像ストロボ写真生成", "What-If 球速・球質向上シミュレーター", "3Dピッチトンネル＆打者判断判定", "AI投球処方箋（改善ドリル・ToDo）"],
            "en": ["<b>All Pro Features</b>", "MLB Broadcast Stats Card (PNG) Export", "Motion Trail Strobe Photo Generator", "What-If Velocity & Stuff Sandbox", "3D Pitch Tunnel & Commitment Point", "AI Pitching Prescription Drills"],
        }
    }

    res = []
    for pid in ["Free", "Pro", "Elite"]:
        f_list = features_all[pid].get(lang) or features_all[pid]["en"]
        res.append({
            "id": pid,
            "name": names[pid].get(lang, names[pid]["en"]),
            "badge": badges[pid].get(lang, badges[pid]["en"]),
            "price": prices[pid],
            "period": periods[pid].get(lang, periods[pid]["en"]),
            "border": "#0284c7" if current_plan == pid and pid != "Elite" else ("#f59e0b" if pid == "Elite" else "#e2e8f0"),
            "bg": "#f0f9ff" if pid == "Pro" else ("#fffbeb" if pid == "Elite" else "#ffffff"),
            "features": f_list,
        })
    return res




def convert_speed(speed_kmh: float, unit: str = "km/h") -> float:
    """km/h から指定単位 (km/h または mph) に変換。"""
    if unit == "mph":
        return float(speed_kmh) * 0.621371
    return float(speed_kmh)


def convert_distance(dist_m: float, unit: str = "m") -> float:
    """m から指定単位 (m または ft) に変換。"""
    if unit == "ft":
        return float(dist_m) * 3.28084
    return float(dist_m)



def cm_to_feet_inches(cm: float) -> str:
    """cm を フィート・インチ表記 (例: 5'9\", 6'3\") に変換。"""
    total_inches = round(float(cm) / 2.54)
    feet = total_inches // 12
    inches = total_inches % 12
    return f"{feet}'{inches}\""


def format_height(cm: float, unit: str = "m") -> str:
    """単位系 (m または ft) に応じた身長表記を返す。"""
    ft_in = cm_to_feet_inches(cm)
    if unit == "ft":
        return f"{ft_in} ({int(round(cm))} cm)"
    return f"{int(round(cm))} cm ({ft_in})"


def get_benchmark_details(pitch_key: str, lang: str = "ja") -> dict:
    """球種ベンチマークの多言語解説と理想スロットを返す。"""
    descs = {
        "fastball": {
            "ja": "垂直ホップ成分を最大化し打者のバットの上を通す王道球種",
            "en": "Maximizes vertical hop to ride above batter's barrel",
            "es": "Maximiza el salto vertical para superar el bate del rival",
            "ko": "수직 호프를 극대화하여 타자의 배트 위를 통과하는 대표 구종",
            "zh": "極大化垂直位移以竄升越過打者球棒的經典球種",
        },
        "twoseam": {
            "ja": "シュート回転と沈む軌道でゴロを打たせる変形直球",
            "en": "Arm-side tailing and sinking action to induce weak ground balls",
            "es": "Cola al lado del brazo y hundimiento para inducir rodados",
            "ko": "슈트 회전과 가라앉는 궤적으로 땅볼을 유도하는 변형 패스트볼",
            "zh": "內竄帶下沉軌跡以誘發大量滾地球的變形快速球",
        },
        "slider": {
            "ja": "直球の軌道から打者の手元で鋭く横〜斜め下に逃げる変化球",
            "en": "Sharp late glove-side sweep and drop breaking away from barrel",
            "es": "Quiebre lateral pronunciado y tardío que escapa del bate",
            "ko": "직구 궤적에서 타자 앞에서 날카롭게 꺾여 도망가는 변화구",
            "zh": "自快速球軌跡於打者近身處外掃急墜的強烈位移球",
        },
        "curve": {
            "ja": "強いトップスピンによる大きなドロップと緩急差でタイミングを外す",
            "en": "Heavy topspin creating 12-6 drop and velocity gap to disrupt timing",
            "es": "Fuerte efecto de caída vertical 12-6 que rompe el ritmo del bateador",
            "ko": "강한 탑스핀으로 큰 낙차와 속도차를 만들어 타이밍을 빼앗는 구종",
            "zh": "極強前旋帶來垂直大落差與速差，破壞打者揮棒節奏",
        },
        "changeup": {
            "ja": "直球と同じ腕の振りからブレーキが効いて沈む球種",
            "en": "Identical arm speed with deceleration and late fading sink",
            "es": "Misma velocidad de brazo pero con desaceleración y caída tardía",
            "ko": "직구와 동일한 팔 스윙에서 감속되며 가라앉는 구종",
            "zh": "維持與快速球相同揮臂速度，於進壘時失速下沉變速",
        },
        "splitter": {
            "ja": "打者の手元で急激に垂直落下し空振りを奪うウイニングショット",
            "en": "Tumbles vertically off the table at the plate to generate whiffs",
            "es": "Cae en picada al llegar al plato para conseguir abanicos",
            "ko": "타자 앞에서 급격히 수직 낙하하여 헛스윙을 이끌어내는 결정구",
            "zh": "於進壘點垂直急遽陡墜以奪取揮空的致命決戰球",
        },
        "cutter": {
            "ja": "直球に近い球速で芯を外しバットをへし折る高速スライダー",
            "en": "Near-fastball velocity with late cut to saw off bats and avoid barrels",
            "es": "Velocidad cercana a la recta con corte tardío para romper bates",
            "ko": "직구에 가까운 구속으로 빗맞혀 배트를 부러뜨리는 고속 슬라이더",
            "zh": "逼近快速球極速並在進壘瞬間微幅竄切折棒的卡特球",
        },
    }

    slots = {
        "fastball": {
            "ja": "スリークォーター / オーバースロー",
            "en": "Three-Quarter / Overhand",
            "es": "Tres Cuartos / Sobre el Hombro",
            "ko": "쓰리쿼터 / 오버핸드",
            "zh": "四分之三 / 高壓出手",
        },
        "twoseam": {
            "ja": "スリークォーター / サイドスロー",
            "en": "Three-Quarter / Sidearm",
            "es": "Tres Cuartos / Lateral",
            "ko": "쓰리쿼터 / 사이드암",
            "zh": "四分之三 / 側投",
        },
        "slider": {
            "ja": "スリークォーター / サイドスロー",
            "en": "Three-Quarter / Sidearm",
            "es": "Tres Cuartos / Lateral",
            "ko": "쓰리쿼터 / 사이드암",
            "zh": "四分之三 / 側投",
        },
        "curve": {
            "ja": "オーバースロー / スリークォーター",
            "en": "Overhand / Three-Quarter",
            "es": "Sobre el Hombro / Tres Cuartos",
            "ko": "오버핸드 / 쓰리쿼터",
            "zh": "高壓出手 / 四分之三",
        },
        "changeup": {
            "ja": "スリークォーター",
            "en": "Three-Quarter",
            "es": "Tres Cuartos",
            "ko": "쓰리쿼터",
            "zh": "四分之三",
        },
        "splitter": {
            "ja": "オーバースロー / スリークォーター",
            "en": "Overhand / Three-Quarter",
            "es": "Sobre el Hombro / Tres Cuartos",
            "ko": "오버핸드 / 쓰리쿼터",
            "zh": "高壓出手 / 四分之三",
        },
        "cutter": {
            "ja": "スリークォーター / オーバースロー",
            "en": "Three-Quarter / Overhand",
            "es": "Tres Cuartos / Sobre el Hombro",
            "ko": "쓰리쿼터 / 오버핸드",
            "zh": "四分之三 / 高壓出手",
        },
    }

    pk = pitch_key.lower() if pitch_key else "fastball"
    desc_dict = descs.get(pk, descs["fastball"])
    slot_dict = slots.get(pk, slots["fastball"])
    return {
        "movement_desc": desc_dict.get(lang, desc_dict["en"]),
        "ideal_slot": slot_dict.get(lang, slot_dict["en"]),
    }

def get_movement_profile_tags(d_ivb: float, d_hb: float, is_left_handed: bool, lang: str = "ja") -> tuple:
    """変化量マップ直下の変化特性タグ（IVB & HB）を多言語で生成。"""
    if d_ivb >= 2.0:
        ivb_templates = {
            "ja": f"ホップ特化 (+{d_ivb:.1f}cm)",
            "en": f"Elite Hop (+{d_ivb:.1f}cm)",
            "es": f"Salto Destacado (+{d_ivb:.1f}cm)",
            "ko": f"호프 특화 (+{d_ivb:.1f}cm)",
            "zh": f"極致升力 (+{d_ivb:.1f}cm)",
        }
    elif d_ivb <= -2.0:
        ivb_templates = {
            "ja": f"沈み・落差大 ({d_ivb:.1f}cm)",
            "en": f"Heavy Drop ({d_ivb:.1f}cm)",
            "es": f"Gran Hundimiento ({d_ivb:.1f}cm)",
            "ko": f"가라앉음/낙차 대 ({d_ivb:.1f}cm)",
            "zh": f"下沉大落差 ({d_ivb:.1f}cm)",
        }
    else:
        ivb_templates = {
            "ja": "標準ホップ",
            "en": "Standard Hop",
            "es": "Salto Estándar",
            "ko": "표준 호프",
            "zh": "標準升力",
        }

    is_run = (d_hb > 2.0) if not is_left_handed else (d_hb < -2.0)
    is_cut = (d_hb < -2.0) if not is_left_handed else (d_hb > 2.0)
    if is_run:
        hb_templates = {
            "ja": f"鋭いアームラン (+{abs(d_hb):.1f}cm)",
            "en": f"Sharp Arm-Side Run (+{abs(d_hb):.1f}cm)",
            "es": f"Cola Afilada del Brazo (+{abs(d_hb):.1f}cm)",
            "ko": f"날카로운 암런 (+{abs(d_hb):.1f}cm)",
            "zh": f"銳利噴射內竄 (+{abs(d_hb):.1f}cm)",
        }
    elif is_cut:
        hb_templates = {
            "ja": "スライダー/カット成分寄り",
            "en": "Glove-Side Cut / Sweep",
            "es": "Tendencia Cut / Sweep",
            "ko": "슬라이더/커터 성분 경향",
            "zh": "滑球/卡特外掃偏折",
        }
    else:
        hb_templates = {
            "ja": "標準横変化",
            "en": "Standard Horiz Break",
            "es": "Quiebre Horiz. Estándar",
            "ko": "표준 가로변화",
            "zh": "標準橫向位移",
        }

    ivb_t = ivb_templates.get(lang, ivb_templates["en"])
    hb_t = hb_templates.get(lang, hb_templates["en"])
    return ivb_t, hb_t


def get_stuff_metrics_info(speed: float, spin: dict, ext: float, lang: str = "ja") -> dict:
    """Stuff+ 5大指標のタイトルおよびサブ説明文を多言語で生成。"""
    ivb_val = spin.get("ivb_cm", 35.0)
    hb_val = spin.get("hb_cm", 15.0)
    eff_val = spin.get("active_spin_pct", 85.0)

    titles = {
        "ride": {"ja": "⬆️ ホップ (Ride+)", "en": "⬆️ Hop (Ride+)", "es": "⬆️ Salto (Ride+)", "ko": "⬆️ 호프 (Ride+)", "zh": "⬆️ 縱向升力 (Ride+)"},
        "velo": {"ja": "🚀 球速 (Velo+)", "en": "🚀 Velocity (Velo+)", "es": "🚀 Velocidad (Velo+)", "ko": "🚀 구속 (Velo+)", "zh": "🚀 球速初速 (Velo+)"},
        "ext": {"ja": "📏 前到達 (Ext+)", "en": "📏 Extension (Ext+)", "es": "📏 Extensión (Ext+)", "ko": "📏 앞도달 (Ext+)", "zh": "📏 延伸步幅 (Ext+)"},
        "eff": {"ja": "🌀 スピン効率 (Eff+)", "en": "🌀 Spin Eff (Eff+)", "es": "🌀 Eficiencia (Eff+)", "ko": "🌀 스핀효율 (Eff+)", "zh": "🌀 旋轉效率 (Eff+)"},
        "run": {"ja": "↔️ 横変化 (Run+)", "en": "↔️ Movement (Run+)", "es": "↔️ Quiebre (Run+)", "ko": "↔️ 가로변화 (Run+)", "zh": "↔️ 橫向位移 (Run+)"},
    }

    sub_ride = {
        "ja": f"垂直変化: {ivb_val:+.1f} cm (100=平均38cm)",
        "en": f"Vert Break: {ivb_val:+.1f} cm (100=Avg 38cm)",
        "es": f"Quiebre Vert.: {ivb_val:+.1f} cm (100=Prom. 38cm)",
        "ko": f"수직 변화: {ivb_val:+.1f} cm (100=평균 38cm)",
        "zh": f"垂直位移: {ivb_val:+.1f} cm (100=平均38cm)",
    }.get(lang, f"Vert Break: {ivb_val:+.1f} cm")

    sub_velo = {
        "ja": f"初速: {speed:.1f} km/h (100=平均145km/h)",
        "en": f"Release: {speed:.1f} km/h (100=Avg 145km/h)",
        "es": f"Velocidad: {speed:.1f} km/h (100=Prom. 145km/h)",
        "ko": f"초속: {speed:.1f} km/h (100=평균 145km/h)",
        "zh": f"初速: {speed:.1f} km/h (100=平均145km/h)",
    }.get(lang, f"Release: {speed:.1f} km/h")

    sub_ext = {
        "ja": f"前伸長: {ext:.2f} m (100=平均1.82m)",
        "en": f"Extension: {ext:.2f} m (100=Avg 1.82m)",
        "es": f"Extensión: {ext:.2f} m (100=Prom. 1.82m)",
        "ko": f"앞 신장: {ext:.2f} m (100=평균 1.82m)",
        "zh": f"延伸步幅: {ext:.2f} m (100=平均1.82m)",
    }.get(lang, f"Extension: {ext:.2f} m")

    sub_eff = {
        "ja": f"有効回転: {eff_val:.1f} % (100=平均85%)",
        "en": f"Active Spin: {eff_val:.1f} % (100=Avg 85%)",
        "es": f"Giro Activo: {eff_val:.1f} % (100=Prom. 85%)",
        "ko": f"유효 회전: {eff_val:.1f} % (100=평균 85%)",
        "zh": f"有效旋轉: {eff_val:.1f} % (100=平均85%)",
    }.get(lang, f"Active Spin: {eff_val:.1f} %")

    sub_run = {
        "ja": f"横曲がり: {hb_val:+.1f} cm (100=平均20cm)",
        "en": f"Horiz Break: {hb_val:+.1f} cm (100=Avg 20cm)",
        "es": f"Quiebre Horiz.: {hb_val:+.1f} cm (100=Prom. 20cm)",
        "ko": f"가로 꺾임: {hb_val:+.1f} cm (100=평균 20cm)",
        "zh": f"橫向偏折: {hb_val:+.1f} cm (100=平均20cm)",
    }.get(lang, f"Horiz Break: {hb_val:+.1f} cm")

    return {
        "title_ride": titles["ride"].get(lang, titles["ride"]["en"]),
        "title_velo": titles["velo"].get(lang, titles["velo"]["en"]),
        "title_ext": titles["ext"].get(lang, titles["ext"]["en"]),
        "title_eff": titles["eff"].get(lang, titles["eff"]["en"]),
        "title_run": titles["run"].get(lang, titles["run"]["en"]),
        "sub_ride": sub_ride,
        "sub_velo": sub_velo,
        "sub_ext": sub_ext,
        "sub_eff": sub_eff,
        "sub_run": sub_run,
    }
