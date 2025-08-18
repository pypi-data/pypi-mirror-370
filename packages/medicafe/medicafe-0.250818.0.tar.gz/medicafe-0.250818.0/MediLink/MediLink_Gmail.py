# MediLink_Gmail.py
import sys, os, subprocess, time, webbrowser, requests, json, ssl, signal

# Set up Python path to find MediCafe when running directly
def setup_python_path():
    """Set up Python path to find MediCafe package"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_root = os.path.dirname(current_dir)
    
    # Add workspace root to Python path if not already present
    if workspace_root not in sys.path:
        sys.path.insert(0, workspace_root)

# Set up paths before importing MediCafe
setup_python_path()

from MediCafe.core_utils import get_shared_config_loader, extract_medilink_config

# New helpers
from MediLink.gmail_oauth_utils import (
    get_authorization_url as oauth_get_authorization_url,
    exchange_code_for_token as oauth_exchange_code_for_token,
    refresh_access_token as oauth_refresh_access_token,
    is_valid_authorization_code as oauth_is_valid_authorization_code,
    clear_token_cache as oauth_clear_token_cache,
)
from MediLink.gmail_http_utils import (
    generate_self_signed_cert as http_generate_self_signed_cert,
    start_https_server as http_start_https_server,
    inspect_token as http_inspect_token,
)

# Get shared config loader
MediLink_ConfigLoader = get_shared_config_loader()
if MediLink_ConfigLoader:
    load_configuration = MediLink_ConfigLoader.load_configuration
    log = MediLink_ConfigLoader.log
else:
    # Fallback functions if config loader is not available
    def load_configuration():
        return {}, {}
    def log(message, level="INFO"):
        print("[{}] {}".format(level, message))
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread, Event
import platform
import ctypes

config, _ = load_configuration()
medi = extract_medilink_config(config)
local_storage_path = medi.get('local_storage_path', '.')
downloaded_emails_file = os.path.join(local_storage_path, 'downloaded_emails.txt')

server_port = 8000
cert_file = 'server.cert'
key_file = 'server.key'
# Try to find openssl.cnf in various locations
openssl_cnf = 'openssl.cnf'  # Use relative path since we're running from MediLink directory
if not os.path.exists(openssl_cnf):
    log("Could not find openssl.cnf at: " + os.path.abspath(openssl_cnf))
    # Try MediLink directory
    medilink_dir = os.path.dirname(os.path.abspath(__file__))
    medilink_openssl = os.path.join(medilink_dir, 'openssl.cnf')
    log("Trying MediLink directory: " + medilink_openssl)
    if os.path.exists(medilink_openssl):
        openssl_cnf = medilink_openssl
        log("Found openssl.cnf at: " + openssl_cnf)
    else:
        # Try one directory up
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        alternative_path = os.path.join(parent_dir, 'MediBot', 'openssl.cnf')
        log("Trying alternative path: " + alternative_path)
        if os.path.exists(alternative_path):
            openssl_cnf = alternative_path
            log("Found openssl.cnf at: " + openssl_cnf)
        else:
            log("Could not find openssl.cnf at alternative path either")

httpd = None  # Global variable for the HTTP server
shutdown_event = Event()  # Event to signal shutdown

# Define the scopes for the Gmail API and other required APIs
SCOPES = ' '.join([
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/script.external_request',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/script.scriptapp',
    'https://www.googleapis.com/auth/drive'
])

# Path to token.json file
TOKEN_PATH = 'token.json'

# Determine the operating system and version
os_name = platform.system()
os_version = platform.release()

# Set the credentials path based on the OS and version
if os_name == 'Windows' and 'XP' in os_version:
    CREDENTIALS_PATH = 'F:\\Medibot\\json\\credentials.json'
else:
    CREDENTIALS_PATH = 'json\\credentials.json'

# Log the selected path for verification
log("Using CREDENTIALS_PATH: {}".format(CREDENTIALS_PATH), config, level="INFO")

REDIRECT_URI = 'https://127.0.0.1:8000'

def get_authorization_url():
    return oauth_get_authorization_url(CREDENTIALS_PATH, REDIRECT_URI, SCOPES, log)

def exchange_code_for_token(auth_code, retries=3):
    return oauth_exchange_code_for_token(auth_code, CREDENTIALS_PATH, REDIRECT_URI, log, retries=retries)

def get_access_token():
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'r') as token_file:
            token_data = json.load(token_file)
            log("Loaded token data:\n {}".format(token_data))
            if 'access_token' in token_data and 'expires_in' in token_data:
                try:
                    token_time = token_data.get('token_time', time.time())
                    token_expiry_time = token_time + token_data['expires_in']
                except KeyError as e:
                    log("KeyError while accessing token data: {}".format(e))
                    return None
                if token_expiry_time > time.time():
                    log("Access token is still valid. Expires in {} seconds.".format(token_expiry_time - time.time()))
                    return token_data['access_token']
                else:
                    log("Access token has expired. Current time: {}, Expiry time: {}".format(time.time(), token_expiry_time))
                    new_token_data = oauth_refresh_access_token(token_data.get('refresh_token'), CREDENTIALS_PATH, log)
                    if 'access_token' in new_token_data:
                        new_token_data['token_time'] = time.time()
                        with open(TOKEN_PATH, 'w') as token_file:
                            json.dump(new_token_data, token_file)
                        log("Access token refreshed successfully. New token data: {}".format(new_token_data))
                        return new_token_data['access_token']
                    else:
                        log("Failed to refresh access token. New token data: {}".format(new_token_data))
                        return None
    log("Access token not found. Please authenticate.")
    return None

def refresh_access_token(refresh_token):
    return oauth_refresh_access_token(refresh_token, CREDENTIALS_PATH, log)

def bring_window_to_foreground():
    """Brings the current window to the foreground on Windows."""
    try:
        if platform.system() == 'Windows':
            pid = os.getpid()
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            current_pid = ctypes.c_ulong()
            ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(current_pid))
            if current_pid.value != pid:
                ctypes.windll.user32.SetForegroundWindow(hwnd)
                if ctypes.windll.user32.GetForegroundWindow() != hwnd:
                    ctypes.windll.user32.ShowWindow(hwnd, 9)
                    ctypes.windll.user32.SetForegroundWindow(hwnd)
    except Exception as e:
        log("Error bringing window to foreground: {}".format(e))

class RequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-type', 'application/json')

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_headers()
        self.end_headers()

    def do_POST(self):
        if self.path == '/download':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            links = data.get('links', [])
            log("Received links: {}".format(links))
            file_ids = [link.get('fileId', None) for link in links if link.get('fileId')]
            log("File IDs received from client: {}".format(file_ids))
            download_docx_files(links)
            self.send_response(200)
            self._set_headers()
            self.end_headers()
            response = json.dumps({"status": "success", "message": "All files downloaded", "fileIds": file_ids})
            self.wfile.write(response.encode('utf-8'))
            shutdown_event.set()
            bring_window_to_foreground()
        elif self.path == '/shutdown':
            log("Shutdown request received.")
            self.send_response(200)
            self._set_headers()
            self.end_headers()
            response = json.dumps({"status": "success", "message": "Server is shutting down."})
            self.wfile.write(response.encode('utf-8'))
            shutdown_event.set()
        elif self.path == '/delete-files':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            file_ids = data.get('fileIds', [])
            log("File IDs to delete received from client: {}".format(file_ids))
            if not isinstance(file_ids, list):
                self.send_response(400)
                self._set_headers()
                self.end_headers()
                response = json.dumps({"status": "error", "message": "Invalid fileIds parameter."})
                self.wfile.write(response.encode('utf-8'))
                return
            self.send_response(200)
            self._set_headers()
            self.end_headers()
            response = json.dumps({"status": "success", "message": "Files deleted successfully."})
            self.wfile.write(response.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        log("Full request path: {}".format(self.path))
        if self.path.startswith("/?code="):
            auth_code = self.path.split('=')[1].split('&')[0]
            auth_code = requests.utils.unquote(auth_code)
            log("Received authorization code: {}".format(auth_code))
            if oauth_is_valid_authorization_code(auth_code, log):
                try:
                    token_response = exchange_code_for_token(auth_code)
                    if 'access_token' not in token_response:
                        if token_response.get("status") == "error":
                            self.send_response(400)
                            self.send_header('Content-type', 'text/html')
                            self.end_headers()
                            self.wfile.write(token_response["message"].encode())
                            return
                        raise ValueError("Access token not found in response.")
                except Exception as e:
                    log("Error during token exchange: {}".format(e))
                    self.send_response(500)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write("An error occurred during authentication. Please try again.".encode())
                else:
                    log("Token response: {}".format(token_response))
                    if 'access_token' in token_response:
                        with open(TOKEN_PATH, 'w') as token_file:
                            json.dump(token_response, token_file)
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        self.wfile.write("Authentication successful. You can close this window now.".encode())
                        initiate_link_retrieval(config)
                    else:
                        log("Authentication failed with response: {}".format(token_response))
                        if 'error' in token_response:
                            error_description = token_response.get('error_description', 'No description provided.')
                            log("Error details: {}".format(error_description))
                        if token_response.get('error') == 'invalid_grant':
                            log("Invalid grant error encountered. Authorization code: {}, Response: {}".format(auth_code, token_response))
                            check_invalid_grant_causes(auth_code)
                            oauth_clear_token_cache(TOKEN_PATH, log)
                            user_message = "Authentication failed: Invalid or expired authorization code. Please try again."
                        else:
                            user_message = "Authentication failed. Please check the logs for more details."
                        self.send_response(400)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        self.wfile.write(user_message.encode())
                        shutdown_event.set()
            else:
                log("Invalid authorization code format: {}".format(auth_code))
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write("Invalid authorization code format. Please try again.".encode())
                shutdown_event.set()
        elif self.path == '/downloaded-emails':
            self.send_response(200)
            self._set_headers()
            self.end_headers()
            downloaded_emails = load_downloaded_emails()
            response = json.dumps({"downloadedEmails": list(downloaded_emails)})
            self.wfile.write(response.encode('utf-8'))
        else:
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'HTTPS server is running.')

def generate_self_signed_cert(cert_file, key_file):
    http_generate_self_signed_cert(openssl_cnf, cert_file, key_file, log, subprocess)

def run_server():
    global httpd
    try:
        log("Attempting to start server on port " + str(server_port))
        if not os.path.exists(cert_file):
            log("Error: Certificate file not found: " + cert_file)
        if not os.path.exists(key_file):
            log("Error: Key file not found: " + key_file)
        httpd = HTTPServer(('0.0.0.0', server_port), RequestHandler)
        httpd.socket = ssl.wrap_socket(httpd.socket, certfile=cert_file, keyfile=key_file, server_side=True)
        log("Starting HTTPS server on port {}".format(server_port))
        httpd.serve_forever()
    except Exception as e:
        log("Error in serving: {}".format(e))
        stop_server()

def stop_server():
    global httpd
    if httpd:
        log("Stopping HTTPS server.")
        httpd.shutdown()
        httpd.server_close()
        log("HTTPS server stopped.")
    shutdown_event.set()
    bring_window_to_foreground()

def load_downloaded_emails():
    downloaded_emails = set()
    if os.path.exists(downloaded_emails_file):
        with open(downloaded_emails_file, 'r') as file:
            downloaded_emails = set(line.strip() for line in file)
    log("Loaded downloaded emails: {}".format(downloaded_emails))
    return downloaded_emails

def download_docx_files(links):
    downloaded_emails = load_downloaded_emails()
    for link in links:
        try:
            url = link.get('url', '')
            filename = link.get('filename', '')
            log("Processing link: url='{}', filename='{}'".format(url, filename))
            lower_name = (filename or '').lower()
            looks_like_csv = any(lower_name.endswith(ext) for ext in ['.csv', '.tsv', '.txt', '.dat'])
            if looks_like_csv:
                log("[CSV Routing Preview] Detected CSV-like filename: {}. Would route to CSV processing directory.".format(filename))
            if filename in downloaded_emails:
                log("Skipping already downloaded email: {}".format(filename))
                continue
            log("Downloading .docx file from URL: {}".format(url))
            response = requests.get(url, verify=False)
            if response.status_code == 200:
                file_path = os.path.join(local_storage_path, filename)
                with open(file_path, 'wb') as file:
                    file.write(response.content)
                log("Downloaded .docx file: {}".format(filename))
                downloaded_emails.add(filename)
                with open(downloaded_emails_file, 'a') as file:
                    file.write(filename + '\n')
            else:
                log("Failed to download .docx file from URL: {}. Status code: {}".format(url, response.status_code))
        except Exception as e:
            log("Error downloading .docx file from URL: {}. Error: {}".format(url, e))

def open_browser_with_executable(url, browser_path=None):
    try:
        if browser_path:
            log("Attempting to open URL with provided executable: {} {}".format(browser_path, url))
            process = subprocess.Popen([browser_path, url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            if process.returncode == 0:
                log("Browser opened with provided executable path using subprocess.Popen.")
            else:
                log("Browser failed to open using subprocess.Popen. Return code: {}. Stderr: {}".format(process.returncode, stderr))
        else:
            log("No browser path provided. Attempting to open URL with default browser: {}".format(url))
            webbrowser.open(url)
            log("Default browser opened.")
    except Exception as e:
        log("Failed to open browser: {}".format(e))

def initiate_link_retrieval(config):
    log("Initiating browser via implicit GET.")
    medi = extract_medilink_config(config)
    url_get = "https://script.google.com/macros/s/{}/exec?action=get_link".format(medi.get('webapp_deployment_id', ''))
    open_browser_with_executable(url_get)
    log("Preparing POST call.")
    url = "https://script.google.com/macros/s/{}/exec".format(medi.get('webapp_deployment_id', ''))
    downloaded_emails = list(load_downloaded_emails())
    payload = {"downloadedEmails": downloaded_emails}
    access_token = get_access_token()
    if not access_token:
        log("Access token not found. Please authenticate first.")
        shutdown_event.set()
        return
    token_info = http_inspect_token(access_token, log, delete_token_file_fn=delete_token_file, stop_server_fn=stop_server)
    if token_info is None:
        log("Access token is invalid. Please re-authenticate.")
        shutdown_event.set()
        return
    headers = {'Authorization': 'Bearer {}'.format(access_token), 'Content-Type': 'application/json'}
    log("Request headers: {}".format(headers))
    log("Request payload: {}".format(payload))
    handle_post_response(url, payload, headers)

def handle_post_response(url, payload, headers):
    try:
        response = requests.post(url, json=payload, headers=headers)
        log("Response status code: {}".format(response.status_code))
        log("Response body: {}".format(response.text))
        if response.status_code == 200:
            response_data = response.json()
            log("Parsed response data: {}".format(response_data))
            if response_data.get("status") == "error":
                log("Error message from server: {}".format(response_data.get("message")))
                print("Error: {}".format(response_data.get("message")))
                shutdown_event.set()
            else:
                log("Link retrieval initiated successfully.")
        elif response.status_code == 401:
            log("Unauthorized. Check if the token has the necessary scopes.Response body: {}".format(response.text))
            token_info = http_inspect_token(headers['Authorization'].split(' ')[1], log, delete_token_file_fn=delete_token_file, stop_server_fn=stop_server)
            log("Token details: {}".format(token_info))
            shutdown_event.set()
        elif response.status_code == 403:
            log("Forbidden access. Ensure that the OAuth client has the correct permissions. Response body: {}".format(response.text))
            shutdown_event.set()
        elif response.status_code == 404:
            log("Not Found. Verify the URL and ensure the Apps Script is deployed correctly. Response body: {}".format(response.text))
            shutdown_event.set()
        else:
            log("Failed to initiate link retrieval. Unexpected status code: {}. Response body: {}".format(response.status_code, response.text))
            shutdown_event.set()
    except requests.exceptions.RequestException as e:
        log("RequestException during link retrieval initiation: {}".format(e))
        shutdown_event.set()
    except Exception as e:
        log("Unexpected error during link retrieval initiation: {}".format(e))
        shutdown_event.set()

def inspect_token(access_token):
    return http_inspect_token(access_token, log, delete_token_file_fn=delete_token_file, stop_server_fn=stop_server)

def delete_token_file():
    try:
        if os.path.exists(TOKEN_PATH):
            os.remove(TOKEN_PATH)
            log("Deleted token.json successfully.")
        else:
            log("token.json does not exist.")
    except Exception as e:
        log("Error deleting token.json: {}".format(e))

def signal_handler(sig, frame):
    log("Signal received: {}. Initiating shutdown.".format(sig))
    stop_server()
    sys.exit(0)

def auth_and_retrieval():
    access_token = get_access_token()
    if not access_token:
        log("Access token not found or expired. Please authenticate first.")
        auth_url = get_authorization_url()
        open_browser_with_executable(auth_url)
        shutdown_event.wait()
    else:
        log("Access token found. Proceeding.")
        initiate_link_retrieval(config)
        shutdown_event.wait()

def is_valid_authorization_code(auth_code):
    return oauth_is_valid_authorization_code(auth_code, log)

def clear_token_cache():
    oauth_clear_token_cache(TOKEN_PATH, log)

def check_invalid_grant_causes(auth_code):
    log("FUTURE IMPLEMENTATION: Checking common causes for invalid_grant error with auth code: {}".format(auth_code))

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    try:
        generate_self_signed_cert(cert_file, key_file)
        from threading import Thread
        log("Starting server thread.")
        server_thread = Thread(target=run_server)
        server_thread.daemon = True
        server_thread.start()
        auth_and_retrieval()
        log("Stopping HTTPS server.")
        stop_server()
        log("Waiting for server thread to finish.")
        server_thread.join()
    except KeyboardInterrupt:
        log("KeyboardInterrupt received, stopping server.")
        stop_server()
        sys.exit(0)
    except Exception as e:
        log("An error occurred: {}".format(e))
        stop_server()
        sys.exit(1)