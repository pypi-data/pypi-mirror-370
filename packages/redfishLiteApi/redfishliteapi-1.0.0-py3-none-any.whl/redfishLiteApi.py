import argparse
import json
import requests
from requests.auth import HTTPBasicAuth
import sys
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

VERSION = "1.0.0"

def parse_args():
    parser = argparse.ArgumentParser(description='Redfish Lite API Tool')
    parser.add_argument('--url', required=True, help='Target Redfish API endpoint')
    parser.add_argument('--method', required=True, choices=['get', 'post', 'patch'], help='HTTP method')
    parser.add_argument('-U', '--username', help='Username for authentication')
    parser.add_argument('-P', '--password', help='Password for authentication')
    parser.add_argument('--json_file', help='Path to JSON file for request body (only for POST or PATCH)')
    parser.add_argument('--find', nargs='+', help='Find and display value(s) of specific field(s) in JSON response (only for GET)')
    parser.add_argument('--save', help='Save response output to specified file')
    parser.add_argument('--header', action='append', help='Custom header(s), format: Key:Value')
    parser.add_argument('--version', action='store_true', help='Show tool version and exit')
    return parser.parse_args()

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

def main():
    args = parse_args()

    if args.version:
        print(f"redfishLiteApi version: {VERSION}")
        return

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    if args.header:
        for header in args.header:
            try:
                key, value = header.split(':', 1)
                headers[key.strip()] = value.strip()
            except ValueError:
                print(f"❌ Invalid header format: {header}. Use Key:Value")
                sys.exit(1)

    payload = load_json(args.json_file) if args.json_file else None
    auth = HTTPBasicAuth(args.username, args.password) if args.username and args.password else None

    try:
        timeout = 10  # seconds

        if args.method == 'get':
            resp = requests.get(args.url, auth=auth, headers=headers, verify=False, timeout=timeout)
        elif args.method == 'post':
            resp = requests.post(args.url, auth=auth, headers=headers, json=payload, verify=False, timeout=timeout)
        elif args.method == 'patch':
            resp = requests.patch(args.url, auth=auth, headers=headers, json=payload, verify=False, timeout=timeout)

        print(f"🔁 HTTP Status: {resp.status_code}")
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
