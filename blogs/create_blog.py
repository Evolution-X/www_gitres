#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SPDX-FileCopyrightText: 2024 The Evolution X Project
# SPDX-License-Identifier: Apache-2.0

import os
import json
import re
from datetime import datetime

def load_blog_ids():
    blog_ids_path = "blogs.json"
    if os.path.exists(blog_ids_path):
        with open(blog_ids_path, "r") as f:
            return json.load(f)
    else:
        return []

def save_blog_ids(blog_ids):
    with open("blogs.json", "w") as f:
        json.dump(blog_ids, f, indent=2)
        f.write("\n")

def get_available_backgrounds():
    backgrounds = [f[:-4] for f in os.listdir("post_backgrounds") if f.endswith(".png")]
    return backgrounds

def prompt_blog_details(next_blog_id):
    print(f"Creating blog entry with ID {next_blog_id}...\n")

    available_backgrounds = get_available_backgrounds()

    if not available_backgrounds:
        print("Error: No background images found.")
        return None

    print("Available background images:")
    for idx, background in enumerate(available_backgrounds, start=1):
        print(f"{idx}. {background}")

    while True:
        try:
            choice = int(input("Select a background by number: ").strip())
            if 1 <= choice <= len(available_backgrounds):
                background = available_backgrounds[choice - 1]
                break
            else:
                print("Error: Invalid choice. Please select a valid number.")
        except ValueError:
            print("Error: Invalid input. Please enter a number.")

    while True:
        github = input("Enter the author's GitHub username: ").strip()
        if github:
            break
        else:
            print("Error: GitHub username cannot be empty. Please try again.")

    while True:
        author = input("Enter the author: ")
        if re.search(r'\d', author):
            print("Error: Author name should not contain numbers. Please try again.")
        else:
            break

    title = input("Enter the title of the blog: ")

    content = input("Enter the content of the blog: ")

    while True:
        date = input("Enter the date (MM-DD-YYYY): ")
        try:
            datetime.strptime(date, "%m-%d-%Y")
            break
        except ValueError:
            print("Error: Incorrect date format. Please use MM-DD-YYYY.")

    blog = {
        "blogId": next_blog_id,
        "background": background,
        "github": github,
        "author": author,
        "title": title,
        "content": content,
        "date": date
    }

    return blog

def save_blog(blog):
    blog_filename = f"posts/{blog['blogId']}.json"
    with open(blog_filename, "w") as f:
        json.dump(blog, f, indent=2)
        f.write("\n")

def main():
    blog_ids = load_blog_ids()

    if blog_ids:
        next_blog_id = max(blog_ids) + 1
    else:
        next_blog_id = 1

    new_blog = prompt_blog_details(next_blog_id)

    if new_blog:
        save_blog(new_blog)

        blog_ids.append(next_blog_id)

        save_blog_ids(blog_ids)

        print("\nBlog created and saved successfully!")
        print(f"Blog ID: {new_blog['blogId']}")
        print(f"Background: {new_blog['background']}")
        print(f"Github: {new_blog['github']}")
        print(f"Author: {new_blog['author']}")
        print(f"Title: {new_blog['title']}")
        print(f"Content: {new_blog['content']}")
        print(f"Date: {new_blog['date']}")

if __name__ == "__main__":
    main()
