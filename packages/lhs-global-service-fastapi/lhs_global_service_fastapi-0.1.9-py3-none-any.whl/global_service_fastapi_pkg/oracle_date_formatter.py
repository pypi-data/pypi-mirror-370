from datetime import datetime

def format_oracle_datetime(dt_str):
    """
    Converts 'DD-MM-YYYY HH:MM:SS' to 'YYYY-MM-DD HH:MM:SS' for Oracle.
    Returns None if input is invalid or empty.
    """
    if not dt_str:
        return None
    try:
        dt = datetime.strptime(dt_str, "%d-%m-%Y %H:%M:%S")
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return None