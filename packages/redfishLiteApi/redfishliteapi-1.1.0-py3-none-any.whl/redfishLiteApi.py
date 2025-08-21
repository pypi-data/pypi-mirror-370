import argparse
import json
import requests
from requests.auth import HTTPBasicAuth
import sys
import urllib3
import os
from urllib.parse import urlparse
from urllib.parse import urljoin
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

VERSION = "1.1.0"

def parse_args():
    parser = argparse.ArgumentParser(description='Redfish Lite API Tool')

    # Exclusive group for version
    exclusive = parser.add_mutually_exclusive_group()
    exclusive.add_argument('--version', action='store_true', help='Show tool version and exit')

    # Regular arguments
    parser.add_argument('--url', help='Target Redfish API endpoint')
    parser.add_argument('--method', choices=['get', 'post', 'patch'], help='HTTP method')
    parser.add_argument('-U', '--username', help='Username for authentication')
    parser.add_argument('-P', '--password', help='Password for authentication')
    parser.add_argument('--json_file', help='Path to JSON file for request body (only for POST or PATCH)')
    parser.add_argument('--find', nargs='+', help='Find and display value(s) of specific field(s) in JSON response (only for GET)')
    parser.add_argument('--save', help='Save response output to specified file')
    parser.add_argument('--header', action='append', help='Custom header(s), format: Key:Value')
    parser.add_argument('--all', action='store_true', help='Recursively follow @odata.id and save all data into folders')
    parser.add_argument('--file_name', default='redfish_dump', help='Folder name to save files when using --all')
    parser.add_argument('--session_token', help='Use existing Redfish session token')
    parser.add_argument('--login_session', action='store_true', help='Automatically login to get Redfish session token')

    args = parser.parse_args()

    if not args.version:
        if not args.url or not args.method:
            parser.error("the following arguments are required: --url, --method")

    return args

def load_json(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading JSON file: {e}")
        sys.exit(1)

def extract_fields(obj, field_names):
    results = []
    def recursive_search(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in field_names:
                    results.append(f"{k}: {v}")
                recursive_search(v)
        elif isinstance(o, list):
            for item in o:
                recursive_search(item)
    recursive_search(obj)
    return results

def handle_save_response(resp, save_path):
    if save_path:
        try:
            content = resp.json()
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=4, ensure_ascii=False)
        except ValueError:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(resp.text)
        print(f"💾 Response saved to {save_path}")


def sanitize_filename(url):
    path = urlparse(url).path.strip('/')
    return path.replace('/', os.sep) or 'root'

def recursive_fetch(url, auth, headers, base_path, visited, depth=0, max_depth=10):
    if url in visited or depth > max_depth:
        return
    visited.add(url)

    try:
        resp = requests.get(url, headers=headers, auth=auth, verify=False, timeout=10)
        if resp.status_code != 200:
            print(f"⚠️ Failed to fetch {url} (status: {resp.status_code})")
            return

        try:
            data = resp.json()
        except ValueError:
            print(f"⚠️ Non-JSON response at {url}")
            return

        # Save current data
        path = os.path.join(base_path, sanitize_filename(url))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path + '.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"💾 Saved: {path}.json")

        # Recursively fetch inner odata.id
        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, dict) and '@odata.id' in v:
                    full_url = urljoin(url, v['@odata.id'])
                    recursive_fetch(full_url, auth, headers, base_path, visited, depth + 1, max_depth)
                elif isinstance(v, list):
                    for item in v:
                        if isinstance(item, dict) and '@odata.id' in item:
                            full_url = urljoin(url, item['@odata.id'])
                            recursive_fetch(full_url, auth, headers, base_path, visited, depth + 1, max_depth)
    except Exception as e:
        print(f"❌ Error fetching {url}: {e}")


def main():
    args = parse_args()

    if args.version:
        print(f"redfishLiteApi version: {VERSION}")
        return

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    # Add custom headers
    if args.header:
        for header in args.header:
            try:
                key, value = header.split(':', 1)
                headers[key.strip()] = value.strip()
            except ValueError:
                print(f"❌ Invalid header format: {header}. Use Key:Value")
                sys.exit(1)

    # Handle session token or login session
    session_token = None
    if args.session_token:
        session_token = args.session_token
        headers['X-Auth-Token'] = session_token
    elif args.login_session and args.username and args.password:
        login_url = urljoin(args.url, '/redfish/v1/SessionService/Sessions')
        login_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        login_body = {
            'UserName': args.username,
            'Password': args.password
        }
        try:
            login_resp = requests.post(login_url, headers=login_headers, json=login_body, verify=False, timeout=10)
            if login_resp.status_code in [200, 201]:
                session_token = login_resp.headers.get('X-Auth-Token')
                if not session_token:
                    print("❌ Login succeeded but no token returned.")
                    sys.exit(1)
                headers['X-Auth-Token'] = session_token
                print("🔑 Redfish session login successful.")
            else:
                print(f"❌ Login failed (HTTP {login_resp.status_code})")
                sys.exit(1)
        except Exception as e:
            print(f"❌ Login error: {e}")
            sys.exit(1)

    # Fallback to Basic Auth if no token
    auth = None
    if not session_token and args.username and args.password:
        auth = HTTPBasicAuth(args.username, args.password)

    # Load JSON payload if applicable
    payload = load_json(args.json_file) if args.json_file else None

    try:
        timeout = 10
        if args.method == 'get':
            resp = requests.get(args.url, auth=auth, headers=headers, verify=False, timeout=timeout)
        elif args.method == 'post':
            resp = requests.post(args.url, auth=auth, headers=headers, json=payload, verify=False, timeout=timeout)
        elif args.method == 'patch':
            resp = requests.patch(args.url, auth=auth, headers=headers, json=payload, verify=False, timeout=timeout)

        print(f"🔁 HTTP Status: {resp.status_code}")

        # Handle --all for recursive crawl
        if hasattr(args, 'all') and args.all:
            base_path = args.file_name
            print(f"🌐 Recursively fetching data from {args.url} into folder: {base_path}")
            os.makedirs(base_path, exist_ok=True)
            visited = set()
            recursive_fetch(args.url, auth, headers, base_path, visited)
            return

        # Handle response output
        try:
            data = resp.json()
            if args.method == 'get' and args.find:
                matches = extract_fields(data, args.find)
                if matches:
                    for i, match in enumerate(matches, 1):
                        print(f"[{i}] {match}")
                else:
                    print("⚠️  No matching fields found.")
            else:
                print(json.dumps(data, indent=4))
            handle_save_response(resp, args.save)
        except ValueError:
            print("⚠️  Response is not JSON:")
            print(resp.text)
            handle_save_response(resp, args.save)

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
