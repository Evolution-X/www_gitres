#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SPDX-FileCopyrightText: 2025 The Evolution X Project
# SPDX-License-Identifier: Apache-2.0

import os
import sys
import requests
import json

def print_error(message):
    print(f"\033[91m{message}\033[0m")

def fetch_branches(github_token):
    base_headers = {"Authorization": f"token {github_token}"}
    print("Fetching branches...")
    response = requests.get(
        "https://api.github.com/repos/Evolution-X/OTA/branches", headers=base_headers
    )
    if response.status_code != 200:
        print_error("Error: Failed to fetch branch data.")
        sys.exit(1)

    branches = [branch["name"] for branch in response.json()]
    if not branches:
        print_error("No branches found.")
        sys.exit(1)

    print("\nBranches found:")
    for branch in branches:
        print(f"- {branch}")

    return branches

def fetch_json_content(url, github_token):
    headers = {"Authorization": f"token {github_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print_error(f"Failed to fetch content from {url}. Status code: {response.status_code}")
        return None
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError as e:
        print_error(f"Error decoding JSON from {url}: {e}")
        return None

def fetch_maintainers_for_device(device_filename, branch, github_token):
    url = f"https://api.github.com/repos/Evolution-X/OTA/contents/builds/{device_filename}?ref={branch}"
    content_info = fetch_json_content(url, github_token)
    if not content_info or "content" not in content_info or "encoding" not in content_info:
        return []

    if content_info["encoding"] == "base64":
        import base64
        try:
            decoded_content = base64.b64decode(content_info["content"]).decode("utf-8")
            data = json.loads(decoded_content)
        except base64.binascii.Error as e:
            print_error(f"Error decoding base64 content for {device_filename} on branch {branch}: {e}")
            return []
        except json.JSONDecodeError as e:
            print_error(f"Error decoding JSON content for {device_filename} on branch {branch}: {e}")
            return []
    else:
        print_error(f"Error: Unexpected encoding for {device_filename} on branch {branch}.")
        return []

    if not data or "response" not in data or not data["response"]:
        print_error(f"No maintainer entries for {device_filename} on branch {branch}.")
        return []

    entries = []
    for m in data["response"]:
        github_username = m.get("github")
        maintainer_name = m.get("maintainer")
        oem = m.get("oem")
        device_name = m.get("device")
        maintained = m.get("currently_maintained", False)
        if github_username and maintainer_name and oem and device_name:
            entries.append((maintainer_name, github_username, oem, device_name, maintained))
    return entries

def main():
    if len(sys.argv) != 2:
        print_error("Usage: ./update_maintainers.py <GITHUB_TOKEN>")
        sys.exit(1)

    github_token = sys.argv[1]
    branches = fetch_branches(github_token)
    current_maintainers_data = {}
    previous_maintainers_data = {}

    if os.path.exists("maintainers.json"):
        with open("maintainers.json", "r") as f:
            try:
                existing_data = json.load(f)
                for maintainer in existing_data.get("active_maintainers", []) + existing_data.get("inactive_maintainers", []):
                    prev_maintained = maintainer.get("currently_maintains", [])
                    prev_used_to_maintain = maintainer.get("used_to_maintain", [])
                    previous_maintainers_data[maintainer["name"]] = {
                        "github": maintainer["github"],
                        "currently_maintains": {item["codename"]: item for item in prev_maintained},
                        "used_to_maintain": {item["codename"]: item for item in prev_used_to_maintain},
                    }
            except json.JSONDecodeError:
                print_error("Warning: Could not decode existing maintainers.json. Starting fresh.")

    for branch in branches:
        print(f"\nProcessing branch: {branch}")
        url = f"https://api.github.com/repos/Evolution-X/OTA/contents/builds?ref={branch}"
        device_files_data = fetch_json_content(url, github_token)
        if not device_files_data or not isinstance(device_files_data, list):
            print_error(f"Error fetching or parsing device list for branch {branch}.")
            continue

        device_files = [
            item["name"]
            for item in device_files_data
            if item.get("type") == "file" and item.get("name", "").endswith(".json")
        ]
        if not device_files:
            print(f"No devices found on branch {branch}.")
            continue

        for device_filename in device_files:
            print(f"  Fetching {device_filename} …")
            entries = fetch_maintainers_for_device(device_filename, branch, github_token)
            codename = os.path.splitext(device_filename)[0]
            for name, github_user, oem, dev, is_active in entries:
                modified_device_name = f"{oem} {dev}"
                device_info = {"device": modified_device_name, "codename": codename}
                if name not in current_maintainers_data:
                    current_maintainers_data[name] = {
                        "github": github_user,
                        "currently_maintains": {},
                        "used_to_maintain": {},
                    }
                if is_active:
                    current_maintainers_data[name]["currently_maintains"][codename] = device_info
                    if codename in current_maintainers_data[name]["used_to_maintain"]:
                        del current_maintainers_data[name]["used_to_maintain"][codename]
                else:
                    if codename not in current_maintainers_data[name]["currently_maintains"]:
                        current_maintainers_data[name]["used_to_maintain"][codename] = device_info

    active_maintainers_list = []
    inactive_maintainers_list = []

    for name, data in current_maintainers_data.items():
        maintainer_info = {
            "name": name,
            "github": data["github"],
        }
        if data["currently_maintains"]:
            maintainer_info["currently_maintains"] = sorted(data["currently_maintains"].values(), key=lambda x: x["device"])
        if data["used_to_maintain"]:
            maintainer_info["used_to_maintain"] = sorted(data["used_to_maintain"].values(), key=lambda x: x["device"])

        if maintainer_info.get("currently_maintains"):
            active_maintainers_list.append(maintainer_info)
        elif maintainer_info.get("used_to_maintain"):
            inactive_maintainers_list.append(maintainer_info)

    active_maintainers_list.sort(key=lambda x: x["name"])
    inactive_maintainers_list.sort(key=lambda x: x["name"])

    output_data = {
        "active_maintainers": active_maintainers_list,
        "inactive_maintainers": inactive_maintainers_list,
    }

    with open("maintainers.json", "w") as f:
        json.dump(output_data, f, indent=2)
        f.write("\n")

    print(f"\nWrote {len(active_maintainers_list)} active maintainers to maintainers.json")
    print(f"Wrote {len(inactive_maintainers_list)} inactive maintainers to maintainers.json")

if __name__ == "__main__":
    main()
