#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SPDX-FileCopyrightText: 2024 The Evolution X Project
# SPDX-License-Identifier: Apache-2.0

import os
import sys
import requests
import json

def print_error(message):
    """Prints an error message."""
    print(f"\033[91m{message}\033[0m")

def main():
    if len(sys.argv) != 2:
        print_error("Usage: python update_devices.py <GITHUB_TOKEN>")
        sys.exit(1)

    github_token = sys.argv[1]
    base_headers = {"Authorization": f"token {github_token}"}

    # Fetch & print branches
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

    devices_json = {}

    # Fetch devices for each branch
    for branch in branches:
        print(f"Fetching devices for branch: {branch}...")
        url = f"https://api.github.com/repos/Evolution-X/OTA/contents/builds?ref={branch}"
        devices_response = requests.get(url, headers=base_headers)

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
                devices_json.setdefault(device, []).append(branch)

    sorted_devices = sorted(devices_json.items(), key=lambda x: x[0])

    with open("devices.json", "w") as file:
        json.dump(dict(sorted_devices), file, indent=2)

    # Fetch device images
    os.makedirs("images", exist_ok=True)
    for device in devices_json:
        output_path = f"images/{device}.png"

        if os.path.exists(output_path):
            print(f"Image for {device} already exists. Skipping fetching.")
            continue

        print(f"Fetching image for device: {device}...")
        image_url = f"https://raw.githubusercontent.com/LineageOS/lineage_wiki/refs/heads/main/images/devices/{device}.png"
        image_response = requests.head(image_url)

        if image_response.status_code == 200:
            with open(output_path, "wb") as img_file:
                img_file.write(requests.get(image_url).content)
        else:
            print_error(f"Image for {device} does not exist on LineageOS wiki.")

    # Create installation instructions
    os.makedirs("instructions", exist_ok=True)
    for device, branches in devices_json.items():
        for branch in branches:
            print(f"Creating instructions for {device} on branch {branch}...")
            branch_dir = f"instructions/{branch}"
            os.makedirs(branch_dir, exist_ok=True)
            md_file = f"{branch_dir}/{device}.md"

            if os.path.exists(md_file):
                continue

            json_url = f"https://raw.githubusercontent.com/Evolution-X/OTA/refs/heads/{branch}/builds/{device}.json"
            response = requests.get(json_url)

            if response.status_code != 200:
                print_error(f"Failed to fetch JSON for {device} on branch {branch}. Status code: {response.status_code}")
                print_error(f"Response content: {response.text}")
                continue

            try:
                json_content = response.json()
            except requests.exceptions.JSONDecodeError as e:
                print_error(f"Error decoding JSON for {device} on branch {branch}: {e}")
                print_error(f"Response content: {response.text}")
                continue

            if not json_content or "response" not in json_content or not json_content["response"]:
                print_error(f"JSON for {device} not found on branch {branch}.")
                continue

            initial_images = json_content["response"][0].get("initial_installation_images", [])
            fastboot_commands = "\n\n".join(
                f"```fastboot flash {img} {img}.img```" if img != "super_empty" else
                "```fastboot wipe-super super_empty.img```"
                for img in initial_images
            )
            fastboot_commands += "\n\n```fastboot reboot recovery```\n\n"

            images_to_download = ", ".join(initial_images + ["rom"])
            download_url = json_content["response"][0]["download"]
            version = download_url.split("/")[-3]
            download_url = f"https://sourceforge.net/projects/evolution-x/files/{device}/{version}/"

            with open(md_file, "w") as md:
                md.write(
                    f"""## THESE INSTRUCTIONS ASSUME YOUR DEVICE'S BOOTLOADER IS ALREADY UNLOCKED\n\n
1. Download {images_to_download} for {device} from [{download_url}]({download_url})
2. Reboot to bootloader
3.
{fastboot_commands}
4. While in recovery, navigate to Factory reset -> Format data/factory reset and confirm to format the device.
5. When done formatting, go back to the main menu and then navigate to Apply update -> Apply from ADB
6. adb sideload rom.zip (replace "rom" with actual filename)
7. (optional) Reboot to recovery (fully) to sideload any add-ons
8. Reboot to system & #KeepEvolving
"""
                )

    print("Done.")

if __name__ == "__main__":
    main()
