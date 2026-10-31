import pandas as pd


REQUIRED_HISTORY_COLUMNS = {"timestamp", "speed", "extension"}


def prepare_pitch_history(history_df: pd.DataFrame) -> pd.DataFrame:
    missing_columns = REQUIRED_HISTORY_COLUMNS.difference(history_df.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"履歴CSVに必要な列がありません: {missing}")

    prepared = history_df.copy()
    prepared["timestamp"] = pd.to_datetime(prepared["timestamp"], errors="coerce")
    prepared["speed"] = pd.to_numeric(prepared["speed"], errors="coerce")
    prepared["extension"] = pd.to_numeric(prepared["extension"], errors="coerce")
    return prepared
