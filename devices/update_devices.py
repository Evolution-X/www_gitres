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

def main():
    if len(sys.argv) != 2:
        print_error("Usage: python update_devices.py <GITHUB_TOKEN>")
        sys.exit(1)

    github_token = sys.argv[1]
    base_headers = {"Authorization": f"token {github_token}"}

    versions_path = os.path.join(os.path.dirname(__file__), "../version/versions.json")
    try:
        with open(versions_path, "r") as vf:
            version_data = json.load(vf)
            version_order = [entry["branch"] for entry in version_data]
    except Exception as e:
        print_error(f"Error reading versions.json: {e}")
        sys.exit(1)

    # Fetch OTA branches
    print("Fetching OTA branches...")
    response = requests.get(
        "https://api.github.com/repos/Evolution-X/OTA/branches", headers=base_headers
    )
    if response.status_code != 200:
        print_error("Error: Failed to fetch OTA branch data.")
        sys.exit(1)

    fetched_branches = [branch["name"] for branch in response.json()]
    if not fetched_branches:
        print_error("No OTA branches found.")
        sys.exit(1)

    branches = [b for b in version_order if b in fetched_branches]

    print("\nOTA branches found:")
    for branch in branches:
        print(f"- {branch}")

    devices_json = {}

    # Fetch devices for each branch on OTA
    for branch in branches:
        print(f"Fetching devices on {branch}...")
        url = f"https://api.github.com/repos/Evolution-X/OTA/contents/builds?ref={branch}"
        devices_response = requests.get(url, headers=base_headers)

        if devices_response.status_code != 200:
            print_error(f"Error: Failed to fetch devices on {branch}.")
            continue

        devices = [
            os.path.splitext(item["name"])[0]
            for item in devices_response.json()
            if item["name"].endswith(".json")
        ]

        if not devices:
            print(f"No devices found on {branch}.")
        else:
            for device in devices:
                if device not in devices_json:
                    devices_json[device] = []
                devices_json[device].append(branch)

    devices_json_array = [{"codename": device, "branches": branches} for device, branches in devices_json.items()]
    devices_json_array = sorted(devices_json_array, key=lambda x: x["codename"])

    with open("devices.json", "w") as file:
        json.dump(devices_json_array, file, indent=2)

    # Check if device images exist
    print("Checking if device images exist...")
    os.makedirs("images", exist_ok=True)

    for device in devices_json:
        device_name = device
        output_path = f"images/{device_name}.webp"

        if not os.path.exists(output_path):
            url = f"https://api.github.com/repos/LineageOS/lineage_wiki/contents/images/devices/{device_name}.png?ref=main"
            headers = {"Authorization": f"token {github_token}"}
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                print(f"\033[93m[WARNING]\033[0m {device_name}.webp does not exist locally.")
                print(f"Please download the image manually from:\nhttps://raw.githubusercontent.com/LineageOS/lineage_wiki/refs/heads/main/images/devices/{device_name}.png")
                print(f"Then convert it to webp at 90% quality with a compression level of 6.")
            else:
                print(f"\033[93m[WARNING]\033[0m {device_name}.png is not available on the LineageOS GitHub.")
                print("Please retrieve the image from another source (e.g., manufacturer site, or XDA forums).")
                print(f"Then convert it to webp at 90% quality with a compression level of 6.")

    print("Done.")

if __name__ == "__main__":
    main()
