#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SPDX-FileCopyrightText: 2024 The Evolution X Project
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

def fetch_maintainers_for_device(device, branch, github_token):
    base_headers = {"Authorization": f"token {github_token}"}
    url = f"https://raw.githubusercontent.com/Evolution-X/OTA/refs/heads/{branch}/builds/{device}.json"
    response = requests.get(url, headers=base_headers)

    if response.status_code != 200:
        print_error(f"Failed to fetch JSON for {device} on branch {branch}. Status code: {response.status_code}")
        return []

    try:
        json_content = response.json()
    except requests.exceptions.JSONDecodeError as e:
        print_error(f"Error decoding JSON for {device} on branch {branch}: {e}")
        return []

    if not json_content or "response" not in json_content or not json_content["response"]:
        print_error(f"JSON for {device} not found on branch {branch}.")
        return []

    maintainers = []
    for maintainer in json_content["response"]:
        github_username = maintainer.get("github")
        maintainer_name = maintainer.get("maintainer")
        oem = maintainer.get("oem")
        device_name = maintainer.get("device")
        if github_username and maintainer_name and oem and device_name:
            maintainers.append((maintainer_name, github_username, oem, device_name))

    return maintainers

def main():
    if len(sys.argv) != 2:
        print_error("Usage: ./update_maintainers.py <GITHUB_TOKEN>")
        sys.exit(1)

    github_token = sys.argv[1]
    branches = fetch_branches(github_token)

    maintainers_map = {}

    for branch in branches:
        print(f"Fetching devices for branch: {branch}...")
        url = f"https://api.github.com/repos/Evolution-X/OTA/contents/builds?ref={branch}"
        devices_response = requests.get(url, headers={"Authorization": f"token {github_token}"})

        if devices_response.status_code != 200:
            print_error(f"Error: Failed to fetch devices for branch {branch}.")
            continue

        devices = [
            os.path.splitext(item["name"])[0]
            for item in devices_response.json()
            if item["name"].endswith(".json")
        ]

        if not devices:
            print(f"No devices found for branch {branch}.")
        else:
            for device in devices:
                print(f"Fetching maintainers for {device} on {branch}...")
                maintainers = fetch_maintainers_for_device(device, branch, github_token)
                for maintainer_name, github_username, oem, device_name in maintainers:
                    if maintainer_name not in maintainers_map:
                        maintainers_map[maintainer_name] = {
                            "name": maintainer_name,
                            "github": github_username,
                            "devices": set()
                        }
                    maintainers_map[maintainer_name]["devices"].add(f"{oem} {device_name}")

    for maintainer in maintainers_map.values():
        maintainer["devices"] = sorted(list(maintainer["devices"]))

    maintainers_list = sorted(maintainers_map.values(), key=lambda x: x["name"])

    maintainers_data = {"maintainers": maintainers_list}
    with open("maintainers.json", "w") as file:
        json.dump(maintainers_data, file, indent=2)

    print(f"Successfully created maintainers.json with {len(maintainers_list)} maintainers.")

if __name__ == "__main__":
    main()
