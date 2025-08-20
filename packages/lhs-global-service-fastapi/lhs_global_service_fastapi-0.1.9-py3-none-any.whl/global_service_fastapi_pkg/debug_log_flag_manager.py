import threading
# Shared event to interrupt TTL thread
_ttl_interrupt_event = threading.Event()
import time
import logging
import re
from datetime import datetime, timedelta
import cx_Oracle
from .global_service_fastapi_pkg import config
from .oracle_date_formatter import format_oracle_datetime

def get_debug_log_ttl_from_db():
    try:
        connection = cx_Oracle.connect(user=config.ORACLE_USER, password=config.ORACLE_PASS, dsn=config.ORACLE_DSN)
        cursor = connection.cursor()
        cursor.execute("""
            SELECT PARAMETER_VALUE FROM LHSSYS_PY_PARAMETERS
            WHERE PARAMETER_NAME = 'GLOBAL_SERVICE_DEBUG_LOG_TIMER'
        """)
        result = cursor.fetchone()
        logging.debug(f"[DEBUG LOG FLAG][DIAG] Fetched TTL from DB: {result}")
        return int(result[0]) if result else 5  # Default to 5 if not found
    except Exception as e:
        logging.error(f"Failed to fetch TTL from DB: {e}")
        return 5
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

def enable_debug_logs(debug_active_by):
    config.SAVE_DEBUG_LOGS = True
    config.debug_active_by = debug_active_by
    config.debug_end_by = None
    now = datetime.now()
    config.start_time = now.strftime('%Y-%m-%d %H:%M:%S')
    config.end_time = None
    logging.info(f"[DEBUG LOG FLAG] Enabling debug logs for user: {debug_active_by}")
    logging.debug(f"[DEBUG LOG FLAG] Debug logs enabled at {config.start_time}, will expire in 2 minutes")
    try:
        connection = cx_Oracle.connect(user=config.ORACLE_USER, password=config.ORACLE_PASS, dsn=config.ORACLE_DSN)
        cursor = connection.cursor()
        update_sql = """
        UPDATE LHSWMA_PY_API_DEBUG_LOGS
        SET DEBUG_FLAG = 'T', DEBUG_END_MODE_FLAG = NULL
        WHERE START_BY = :start_by AND START_TIME = TO_DATE(:start_time, 'YYYY-MM-DD HH24:MI:SS')
        """
        cursor.execute(update_sql, {
            "start_by": config.debug_active_by,
            "start_time": config.start_time
        })
        connection.commit()
        logging.info(f"[DEBUG LOG FLAG] DEBUG_FLAG set to 'T', DEBUG_END_MODE_FLAG set to NULL for user: {debug_active_by}")
    except Exception as e:
        logging.error(f"Failed to set DEBUG_FLAG/DEBUG_END_MODE_FLAG on enable: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
            
    def expire_debug_logs(start_by, start_time):
        ttl_minutes = get_debug_log_ttl_from_db()
        expiry_time = (datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S') + timedelta(minutes=ttl_minutes)).strftime('%Y-%m-%d %H:%M:%S')
        logging.info(f"[DEBUG LOG FLAG] TTL thread started for debug logs, will expire at {expiry_time}")
        # Wait for TTL duration or until interrupted
        interrupted = _ttl_interrupt_event.wait(timeout=ttl_minutes * 60)
        if interrupted:
            logging.info(f"[DEBUG LOG FLAG] TTL thread interrupted by manual disable for user: {start_by}. Exiting TTL thread immediately.")
            # Confirm exit and log current config state
            logging.info(f"[DEBUG LOG FLAG] TTL thread exit confirmation: SAVE_DEBUG_LOGS={config.SAVE_DEBUG_LOGS}, debug_active_by={config.debug_active_by}, debug_end_by={config.debug_end_by}")
            return
        try:
            connection = cx_Oracle.connect(user=config.ORACLE_USER, password=config.ORACLE_PASS, dsn=config.ORACLE_DSN)
            cursor = connection.cursor()
            update_sql = """
            UPDATE LHSWMA_PY_API_DEBUG_LOGS
            SET END_BY = :end_by, END_TIME = TO_DATE(:end_time, 'YYYY-MM-DD HH24:MI:SS'), DEBUG_END_MODE_FLAG = 'A', DEBUG_FLAG = 'F'
            WHERE START_BY = :start_by AND START_TIME = TO_DATE(:start_time, 'YYYY-MM-DD HH24:MI:SS')
            """
            cursor.execute(update_sql, {
                "end_by": start_by,
                "end_time": expiry_time,
                "start_by": start_by,
                "start_time": start_time
            })
            connection.commit()
            logging.info(f"[DEBUG LOG FLAG] Debug logs expired, END_BY updated to {start_by}, DEBUG_END_MODE_FLAG set to 'A', DEBUG_FLAG set to 'F' at {expiry_time}")
        except Exception as e:
            logging.error(f"Failed to update debug logs after TTL: {e}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                connection.close()
        config.SAVE_DEBUG_LOGS = False
        config.debug_end_by = start_by
        config.end_time = expiry_time
        logging.info(f"[DEBUG LOG FLAG] Debug logs disabled after TTL for user: {start_by}")

    # Reset the interrupt event before starting TTL thread
    _ttl_interrupt_event.clear()
    threading.Thread(target=expire_debug_logs, args=(config.debug_active_by, config.start_time), daemon=True).start()
    return {
        "SAVE_DEBUG_LOGS": config.SAVE_DEBUG_LOGS,
        "debug_active_by": config.debug_active_by,
        "debug_end_by": config.debug_end_by,
        "start_time": config.start_time,
        "end_time": config.end_time
    }

def disable_debug_logs(debug_active_by, debug_end_by, start_time, end_time, app_code):
    config.SAVE_DEBUG_LOGS = False
    config.debug_active_by = debug_active_by
    config.debug_end_by = debug_end_by
    config.app_code = app_code
    # Set END_TIME to now if not provided
    def get_now_ddmmyyyy():
        return datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    config.end_time = get_now_ddmmyyyy() if not end_time else end_time
    end_time_oracle = config.end_time
    logging.info(f"[DEBUG LOG FLAG] Disabling debug logs for user: {debug_active_by} (manual)")
    # Interrupt TTL thread if running
    _ttl_interrupt_event.set()
    try:
        connection = cx_Oracle.connect(user=config.ORACLE_USER, password=config.ORACLE_PASS, dsn=config.ORACLE_DSN)
        cursor = connection.cursor()
        update_sql = """
        UPDATE LHSWMA_PY_API_DEBUG_LOGS
        SET END_BY = :end_by, END_TIME = TO_DATE(:end_time, 'DD-MM-YYYY HH24:MI:SS'), DEBUG_FLAG = 'F', DEBUG_END_MODE_FLAG = 'M'
        WHERE APP_CODE = :app_code AND DEBUG_FLAG = 'T'
        """
        params = {
            "end_by": debug_end_by,
            "end_time": end_time_oracle,
            "app_code": app_code 
        }
        logging.info(f"[DEBUG LOG FLAG][DIAG] Executing SQL update with params: {params}")
        cursor.execute(update_sql, params)
        logging.info(f"[DEBUG LOG FLAG][DIAG] Rows affected: {cursor.rowcount}")
        connection.commit()
        logging.info(f"[DEBUG LOG FLAG] Debug logs disabled (manual), END_BY updated to {debug_end_by}, DEBUG_FLAG set to 'F', DEBUG_END_MODE_FLAG set to 'M' at {end_time_oracle}")
    except Exception as e:
        logging.error(f"[DEBUG LOG FLAG][DIAG] Failed to update debug logs: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
    return {
        "SAVE_DEBUG_LOGS": config.SAVE_DEBUG_LOGS,
        "debug_active_by": config.debug_active_by,
        "debug_end_by": config.debug_end_by,
        "start_time": config.start_time,
        "end_time": config.end_time
    }
