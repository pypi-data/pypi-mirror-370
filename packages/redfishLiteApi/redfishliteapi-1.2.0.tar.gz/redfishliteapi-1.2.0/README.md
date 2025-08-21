
# 🔧 redfishLiteApi

A lightweight command-line tool to interact with Redfish APIs using `GET`, `POST`, and `PATCH` methods. Designed for quick testing, debugging, and field extraction.

----------

## 📦 Features

-   ✅ Support for `GET`, `POST`, and `PATCH`
    
-   🔐 Basic Authentication (`-U` / `-P`)
    
-   🪪 Redfish Session Token support (`--session_token`)
    
-   🔑 Auto-login to get Redfish session token (`--login_session`)
    
-   📁 JSON body input via file (`--json_file`)
    
-   🔍 Recursive field value search with `--find` (supports multiple fields)
    
-   💾 Save response to file (`--save`)
    
-   🧾 Custom HTTP headers (`--header`)
-   🌐 Recursively fetch all linked resources (`--all`) and save to folder (`--file_name`)
    
-   ⏱️ 10-second request timeout to prevent hanging
    
-   🧯 Disable SSL verification warnings
    
-   📡 HTTP Status display
    
-   ⚠️ JSON parse error handling with fallback to raw text
    
-   🔢 `--version` support

-   🧭 Deep field path search across all linked resources (`--find_path`)
    

----------

## 🚀 Usage

`python redfishLiteApi.py --url <API_URL> --method <get|post|patch> [OPTIONS]` 

### 🌐 Example: Recursively fetch all resources

`python redfishLiteApi.py --url https://<host>/redfish/v1/Systems --method get --all --file_name dump_folder`

### 🪪 Example: Use Redfish session token

`python redfishLiteApi.py --url https://<host>/redfish/v1/Systems --method get --session_token <TOKEN>`

### 🔑 Example: Auto-login to get session token

`python redfishLiteApi.py --url https://<host>/redfish/v1/Systems --method get --login_session -U admin -P password`

### 🧭 Example: Deep search for field path

`python redfishLiteApi.py --url https://<host>/redfish/v1/ --method get -U admin -P password --find_path key`
----------

## 🧠 Argument Summary

Argument

Description

`--url`

Redfish API endpoint URL (required)

`--method`

HTTP method: `get`, `post`, or `patch` (required)

`-U` / `--username`

Basic auth username

`-P` / `--password`

Basic auth password

`--json_file`

Path to JSON file for POST or PATCH body

`--find`

One or more JSON field names to recursively extract (GET only)

`--find_path`  

Find and print the value and API path of specific field(s) recursively across all linked resources (GET only)

`--save`

Save the response body to a file

`--header`

Custom headers in `Key:Value` format (can be repeated)

`--session_token`

Use existing Redfish session token for authentication

`--login_session`

Automatically login and get Redfish session token

`--all`

Recursively follow `@odata.id` and save all data into folders

`--file_name`

Folder name to save files when using `--all` 

`--version`

Show current version and exit

----------

## ⚠️ Notes

-   SSL certificate verification is disabled (`verify=False`).
    
-   Timeout is hardcoded to 10 seconds.
    
-   HTTP error handling is basic — be sure to inspect the response if you encounter unexpected results.
    

----------

## 🛠 Dependencies

-   Python 3.x
    
-   `requests`
    

Install dependencies via:

`pip install -r requirements.txt` 

`requirements.txt` content:

`requests` 

----------

## 📜 License

MIT License

## 📬 Contact

For questions, feature requests, or business inquiries, please contact:

**Jeffery Lin**  
📧 jeffery12240122@gmail.com

Or open an issue on [GitHub](https://github.com/jeffery12240122/redfishLiteAPI).