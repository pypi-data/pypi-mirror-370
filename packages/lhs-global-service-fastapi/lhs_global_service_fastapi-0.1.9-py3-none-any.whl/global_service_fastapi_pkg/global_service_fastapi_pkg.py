import configparser
import os 
import cx_Oracle
import logging
import json
import requests
import time 
import threading
import socket
from datetime import datetime
import uuid as uuid_lib

# Configuration class for user-supplied settings
class GlobalServiceConfig:
    def __init__(self, GLOBAL_LOG_URL=None, PROJECT_TYPE=None, FAILED_LOG_FILE=None, APP_CODE=None,
                 ORACLE_DB_HOST=None, ORACLE_DB_PORT=None, ORACLE_DB_SERVICE=None, ORACLE_USER=None, ORACLE_PASS=None, ORACLE_DSN=None,SAVE_DEBUG_LOGS=False):
        self.GLOBAL_LOG_URL = GLOBAL_LOG_URL or os.getenv("GLOBAL_LOG_URL")
        self.PROJECT_TYPE = PROJECT_TYPE or os.getenv("PROJECT_TYPE")
        self.FAILED_LOG_FILE = FAILED_LOG_FILE or os.getenv("FAILED_LOG_FILE")
        self.APP_CODE = APP_CODE or os.getenv("APP_CODE")
        self.ORACLE_DB_HOST = ORACLE_DB_HOST or os.getenv("ORACLE_DB_HOST")
        self.ORACLE_DB_PORT = ORACLE_DB_PORT or os.getenv("ORACLE_DB_PORT")
        self.ORACLE_DB_SERVICE = ORACLE_DB_SERVICE or os.getenv("ORACLE_DB_SERVICE")
        self.ORACLE_USER = ORACLE_USER or os.getenv("ORACLE_DB_USER")
        self.ORACLE_PASS = ORACLE_PASS or os.getenv("ORACLE_DB_PASS")
        self.ORACLE_DSN = ORACLE_DSN or self._build_dsn()
        self.SAVE_DEBUG_LOGS = SAVE_DEBUG_LOGS

    def _build_dsn(self):
        if self.ORACLE_DB_HOST and self.ORACLE_DB_PORT and self.ORACLE_DB_SERVICE:
            return cx_Oracle.makedsn(
                self.ORACLE_DB_HOST,
                int(self.ORACLE_DB_PORT),
                service_name=self.ORACLE_DB_SERVICE
            )
        return None

    def configure(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
        # Rebuild DSN if any DB param is updated and DSN not set directly
        if any(k in kwargs for k in ["ORACLE_DB_HOST", "ORACLE_DB_PORT", "ORACLE_DB_SERVICE"]):
            self.ORACLE_DSN = self._build_dsn()
            
# Singleton config instance
config = GlobalServiceConfig()

def get_flush_interval_sec_from_db():
    try:
        connection = cx_Oracle.connect(user=config.ORACLE_USER, password=config.ORACLE_PASS, dsn=config.ORACLE_DSN)
        cursor = connection.cursor()
        cursor.execute("""
            SELECT PARAMETER_VALUE FROM LHSSYS_PY_PARAMETERS
            WHERE PARAMETER_NAME = 'FLUSH_INTERVAL_SEC'
        """)
        result = cursor.fetchone()
        return int(result[0]) if result else 15  # Default to 15 if not found
    except Exception as e:
        logging.error(f"Failed to fetch FLUSH_INTERVAL_SEC from DB: {e}")
        return 15
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
            
def flush_failed_logs():
    """
    Periodically send logs stored in the JSON file to the GLOBAL_LOG_URL.
    Only delete logs from the file after receiving a 200 OK response.
    """
    while True:
        try:
            if os.path.exists(config.FAILED_LOG_FILE):
                with open(config.FAILED_LOG_FILE, "r+", encoding="utf-8") as f:
                    logs = f.readlines()
                    if logs:
                        remaining_logs = []
                        for log in logs:
                            try:
                                payload = json.loads(log.strip())
                                resp = requests.post(config.GLOBAL_LOG_URL, json=payload, timeout=2.0)
                                if resp.status_code == 200:
                                    logging.info(f"Log sent successfully: {payload}")
                                else:
                                    logging.warning(f"Failed to send log (status {resp.status_code}): {payload}")
                                    remaining_logs.append(log)  # Keep the log if not successful
                            except Exception as e:
                                logging.warning(f"Failed to resend log: {e}")
                                remaining_logs.append(log)  # Keep the log if an exception occurs
                        # Rewrite the file with remaining logs
                        f.seek(0)
                        f.truncate()
                        f.writelines(remaining_logs)
        except Exception as e:
            logging.error(f"Error in periodic log flushing: {e}")
        # Fetch flush interval dynamically from DB each loop
        interval = get_flush_interval_sec_from_db()
        time.sleep(interval)
        
# Start the background thread
threading.Thread(target=flush_failed_logs, daemon=True).start()

# Hostname/IP detection ──
def resolve_hostname(ip: str) -> str:
    try:
        hostname, _, _ = socket.gethostbyaddr(ip)
        return hostname
    except Exception as e:
        logging.warning(f"Could not resolve hostname for IP {ip}: {e}")
        return "unknown"

class MachineIPDetector:
    def get_info(self):
        try:
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            logging.debug(f"Detected machine IP address: {ip_address}, hostname: {hostname}")
            return ip_address, hostname
        except Exception as e:
            logging.error(f"Error detecting machine IP/hostname: {e}")
            return "Unknown", "Unknown"

MACHINE_IP, MACHINE_HOSTNAME = MachineIPDetector().get_info()

# def get_app_version():
#     config = configparser.ConfigParser()
#     config.read(os.path.join(os.path.dirname(__file__), '..', 'config.properties'))
#     return config.get('APP VERSION', 'app_version')

def get_app_version():
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "config.properties"
    )
    config = configparser.ConfigParser()
    config.read(config_path)
    try:
        return config.get("APP VERSION", "APP_VERSION").strip('"').strip("'")
    except Exception:
        return "Unknown"

# ── Step-wise Logger ─
class StepLogger:
    def __init__(self):
        self.steps = []  # List of (step_number, timestamp, step_name)

    def log(self, step_name):
        # Add step with timestamp and step number
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        step_number = len(self.steps) + 1
        self.steps.append((step_number, timestamp, step_name))

    def get_log_remark(self):
        # Return multi-line string as per required format
        lines = [f"Step {num}: {ts} {name}" for num, ts, name in self.steps]
        return "\n".join(lines)
    
def get_real_client_ip(request):
    # FastAPI: request.headers is a case-insensitive dict-like object
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    # Fallback to request.client.host
    if hasattr(request, "client") and request.client:
        return request.client.host
    return ""
    
def build_global_log_payload(
    request, app_version=None, request_body=None, uuid=None, payload_rrn=None,
    payload_request_status_code=None, payload_response_status_msg=None
):
    session = request.session
    req_uuid = uuid or request.headers.get("x-request-uuid") or str(uuid_lib.uuid4())[:16]
    client_ip = get_real_client_ip(request)
    logging.info(f"Detected client IP: {client_ip} from headers: {request.headers.get('x-forwarded-for')}")
    payload_rrn_val = payload_rrn or str(uuid_lib.uuid4())[:8]

    # Try to extract identifier from the request body if available. Supports dict and JSON string formats, including those with single quotes
    identifier = {}
    try:
        if request_body:
            if isinstance(request_body, dict):
                identifier = request_body.get("payload_identifier", {})
            elif isinstance(request_body, str):
                try:
                    parsed = json.loads(request_body)
                except Exception as e:
                    # Fallback: replace single quotes with double quotes if normal json.loads fails
                    try:
                        parsed = json.loads(request_body.replace("'", "\""))
                    except Exception as e:
                        parsed = {}
                identifier = parsed.get("payload_identifier", {})
    except Exception:
        identifier = {}

    # Defensive: If identifier is empty, try to extract from request_body as dict (for FastAPI Pydantic models)
    if not identifier and request_body and hasattr(request_body, 'get'):
        identifier = request_body.get('payload_identifier', {})
    # Defensive: If still missing, try to extract from request (Pydantic model instance)
    if not identifier and hasattr(request, 'payload_identifier'):
        identifier = getattr(request, 'payload_identifier', {})

    # Parse identifier timestamp if present and convert to ISO format
    raw_timestamp = identifier.get("timestamp")
    if raw_timestamp:
        try:
            # Try parsing format: 24-04-2025 18:14:24
            parsed_timestamp = datetime.strptime(raw_timestamp, "%d-%m-%Y %H:%M:%S")
            iso_timestamp = parsed_timestamp.isoformat()
        except Exception:
            iso_timestamp = datetime.now().isoformat()
    else:
        iso_timestamp = datetime.now().isoformat()

    payload = {
        "app_code": config.APP_CODE,
        "app_version": app_version if app_version is not None else get_app_version(),
        "group_code": identifier.get("group_code"),
        "appkey": identifier.get("appkey"),
        "payload_urn": req_uuid,
        "payload_rrn": payload_rrn_val,
        "endpoint": str(request.url.path),
        "client_ip": identifier.get("client_ip") or client_ip,
        "client_hostname": identifier.get("client_hostname") or resolve_hostname(client_ip),
        "server_ip": MACHINE_IP,
        "server_hostname": MACHINE_HOSTNAME,
        "calling_app_name": identifier.get("calling_app_name"),
        "payload_request_status_code": payload_request_status_code,
        "payload_response_status_msg": payload_response_status_msg,
        "payload_timestamp": iso_timestamp,
        "BROWSER_USER_AGENT": identifier.get("client_browser") or request.headers.get("user-agent", ""),
        "user_code": identifier.get("user_code") or "UNKNOWN_USER",
        "lastupdate": datetime.now().isoformat(),
    }
    return payload

def send_log_to_global_service(payload: dict):
    try:
        # For the web log API, rename LOGIN_RRN to login_rrn if present
        web_payload = dict(payload)
        if "LOGIN_RRN" in web_payload:
            web_payload["login_rrn"] = web_payload.pop("LOGIN_RRN")
        resp = requests.post(config.GLOBAL_LOG_URL, json=web_payload, timeout=2.0)
        resp.raise_for_status()
    except Exception as e:
        logging.warning(f"Failed to send log to {config.GLOBAL_LOG_URL}, saving locally. Reason: {e}")
        try:
            with open(config.FAILED_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(payload) + "\n")
        except Exception as e2:
            logging.error(f"Could not save failed log to file: {e2}")
            
# Oracle DB Logging 
def save_step_logs_to_oracle(payload: dict, step_logger: 'StepLogger', request_body: str, response_body: str, log_type="INFO",user_code=None):
    """
    Save each step in StepLogger as a separate row in LHSWMA_PY_API_ACTIVITY_LOGS.
    Prevent duplicate logs for the same payload_urn, PAYLOAD_RRN, and LOG_REMARK.
    """
    try:
        connection = cx_Oracle.connect(user=config.ORACLE_USER, password=config.ORACLE_PASS, dsn=config.ORACLE_DSN)
        cursor = connection.cursor()
        insert_sql = """
        INSERT INTO LHSWMA_PY_API_ACTIVITY_LOGS (
            ENTRY_ROWID_SEQ, APP_CODE, PAYLOAD_URN, PAYLOAD_RRN, LOG_REMARK, USER_CODE, LASTUPDATE, FLAG
        )
        VALUES (
            LHSWMA_PY_API_ACTIVITY_LOGS_SEQ.NEXTVAL, :app_code, :payload_urn, :payload_rrn, :log_remark, :user_code, SYSDATE, :flag
        )
        """
        check_sql = """
        SELECT COUNT(*) FROM LHSWMA_PY_API_ACTIVITY_LOGS
        WHERE PAYLOAD_URN = :payload_urn
          AND PAYLOAD_RRN = :payload_rrn
          AND LOG_REMARK = :log_remark
        """
        uuid_val = payload.get("PAYLOAD_URN") or payload.get("payload_urn")
        payload_rrn = payload.get("PAYLOAD_RRN") or payload.get("payload_rrn", "")
        # Always fallback to 'UNKNOWN_USER' if user_code is missing
        user_code_final = payload.get("user_code") or "UNKNOWN_USER"
        app_code = payload.get("APP_CODE", config.APP_CODE)
        flag = payload.get("FLAG", None)
        log_remark = step_logger.get_log_remark()
        logging.info(f"[save_step_logs_to_oracle] Inserting log with user_code: {user_code_final}")
        # Only one row per request, with all steps in LOG_REMARK
        cursor.execute(check_sql, {
            "payload_urn": uuid_val,
            "payload_rrn": payload_rrn,
            "log_remark": log_remark,
        })
        exists = cursor.fetchone()[0]
        if not exists:
            cursor.execute(insert_sql, {
                "app_code": app_code,
                "payload_urn": uuid_val,
                "payload_rrn": payload_rrn,
                "log_remark": log_remark,
                "user_code": user_code_final,
                "flag": flag,
            })
        connection.commit()
    except Exception as e:
        logging.error(f"Failed to save step logs to Oracle DB: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
    # Clear logged steps to avoid duplicate inserts in subsequent calls
    step_logger.steps.clear()

# Debug log saving logic for LHSWMA_PY_API_DEBUG_LOGS
def save_debug_log_to_oracle(
    payload: dict,
    request_body: str,
    response_body: str,
    debug_logs: str = "",
    debug_active_by: str = None,
    debug_end_by: str = None,
    start_time: str = None,
    end_time: str = None,
    flag: str = None
):
    """
    Save a debug log entry to LHSWMA_PY_API_DEBUG_LOGS table.
    Prevent duplicate logs for the same UUID, PAYLOAD_RRN, ENDPOINT, and START_TIME.
    """
    try:
        print("[DEBUG] save_debug_log_to_oracle called")
        print(f"[DEBUG] Payload: {payload}")
        print(f"[DEBUG] request_body: {request_body}")
        print(f"[DEBUG] response_body: {response_body}")
        print(f"[DEBUG] debug_logs: {debug_logs}")
        connection = cx_Oracle.connect(user=config.ORACLE_USER, password=config.ORACLE_PASS, dsn=config.ORACLE_DSN)
        cursor = connection.cursor()
        # insert_sql = """
        # INSERT INTO LHSWMA_PY_API_DEBUG_LOGS (
        #     ENTRY_ROWID_SEQ, APP_CODE, UUID, PAYLOAD_RRN, ENDPOINT, DEBUG_ACTIVE_BY, DEBUG_END_BY, START_TIME, END_TIME,
        #     PAYLOAD_REQUEST, PAYLOAD_RESPONSE, DEBUG_LOGS, USER_CODE, LASTUPDATE, FLAG
        # )
        # VALUES (
        #     LHSWMA_PY_API_DEBUG_LOGS_SEQ.NEXTVAL, :app_code, :uuid, :payload_rrn, :endpoint, :debug_active_by, :debug_end_by, TO_DATE(:start_time, 'YYYY-MM-DD HH24:MI:SS'), TO_DATE(:end_time, 'YYYY-MM-DD HH24:MI:SS'),
        #     :payload_request, :payload_response, :debug_logs, :user_code, SYSDATE, :flag
        # )
        insert_sql = """
        INSERT INTO LHSWMA_PY_API_DEBUG_LOGS (
            ENTRY_ROWID_SEQ, APP_CODE, PAYLOAD_URN, PAYLOAD_RRN, ENDPOINT, START_BY, END_BY, START_TIME, END_TIME,
            USER_CODE, LASTUPDATE, FLAG,
            PAYLOAD_REQUEST, PAYLOAD_RESPONSE, DEBUG_LOGS, DEBUG_FLAG
        )
        VALUES (
            LHSWMA_PY_API_DEBUG_LOGS_SEQ.NEXTVAL, :app_code, :payload_urn, :payload_rrn, :endpoint, :start_by, :end_by, TO_DATE(:start_time, 'YYYY-MM-DD HH24:MI:SS'), TO_DATE(:end_time, 'YYYY-MM-DD HH24:MI:SS'),
            :user_code, SYSDATE, :flag,
            :payload_request, :payload_response, :debug_logs, :debug_flag
        )
        """
        check_sql = """
        SELECT COUNT(*) FROM LHSWMA_PY_API_DEBUG_LOGS
        WHERE PAYLOAD_URN = :payload_urn
          AND PAYLOAD_RRN = :payload_rrn
          AND ENDPOINT = :endpoint
          AND START_TIME = :start_time
        """
        uuid_val = payload.get("PAYLOAD_URN") or payload.get("payload_urn")
        payload_rrn = payload.get("PAYLOAD_RRN") or payload.get("payload_rrn", "")
        endpoint = payload.get("ENDPOINT") or payload.get("endpoint", "")
        user_code = payload.get("user_code") or payload.get("USER_CODE") or "UNKNOWN_USER"
        app_code = payload.get("APP_CODE", config.APP_CODE)
        debug_active_by = debug_active_by
        debug_end_by = debug_end_by 
        start_time_obj = start_time 
        end_time_obj = end_time 
        print(f"[DEBUG] Insert/Check values: payload_urn={uuid_val}, payload_rrn={payload_rrn}, endpoint={endpoint}, start_time={start_time_obj}")
        # Check for duplicates
        cursor.execute(check_sql, {
            "payload_urn": uuid_val,
            "payload_rrn": payload_rrn,
            "endpoint": endpoint,
            "start_time": start_time_obj,
        })
        exists = cursor.fetchone()[0]
        print(f"[DEBUG] Duplicate exists: {exists}")
        if not exists:
            cursor.execute(insert_sql, {
                "app_code": app_code,
                "payload_urn": uuid_val,
                "payload_rrn": payload_rrn,
                "endpoint": endpoint,
                "start_by": debug_active_by,
                "end_by": debug_end_by,
                "start_time": start_time_obj,
                "end_time": end_time_obj,
                "payload_request": request_body or "",
                "payload_response": response_body or "",
                "debug_logs": debug_logs or "No debug logs",
                "user_code": user_code,
                "flag": flag,
                "debug_flag": 'T',
            })
            print("[DEBUG] Inserted debug log row.")
        else:
            print("[DEBUG] Duplicate debug log row, not inserting.")
        connection.commit()
    except Exception as e:
        print(f"[DEBUG][ERROR] Failed to save debug log to Oracle DB: {e}")
        logging.error(f"Failed to save debug log to Oracle DB: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

