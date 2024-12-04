# [Evolution-X](https://evolution-x.org/blog) blog.

## Directory Structure

```
/project-directory
│
├── blogs.json                # Stores list of blog IDs to ensure unique blog IDs
├── post_backgrounds/         # Directory containing available .png background images
│   ├── background1.png       # Example background image
│   ├── background2.png       # Example background image
│   └── background3.png       # Example background image
├── posts/                    # Directory where blog entries are saved as .json files
│   ├── 1.json                # Blog entry with ID 1
│   └── 2.json                # Blog entry with ID 2
└── create_blog.py            # The Python script for creating blog entries
```

## Blog Post Format

Each blog entry is saved as a JSON file in the `posts/` directory. The format for each blog post is as follows:

```json
{
  "blogId": 1,
  "background": "background1",
  "github": "anierinbliss",
  "author": "Anierin Bliss",
  "title": "Example blog",
  "content": "This is an example.",
  "date": "12-06-2024"
}
```

## Blog Post Fields

- **`blogId`**:  
  A unique ID for the blog post, automatically assigned by the script (e.g., `1`, `2`, etc.). This ID is used to name the blog's JSON file (e.g., `1.json`).

- **`background`**:  
  The name of the background image (without the `.png` extension) from the `post_backgrounds/` directory. For example, use `"background1"` for `background1.png`.

- **`github`**:  
  The GitHub username of the blog author (e.g., `anierin bliss`).

- **`author`**:  
  The full name of the author. Only alphabetic characters are allowed (e.g., `"Anierin Bliss"`).

- **`title`**:  
  The title of the blog post, briefly describing its content (e.g., `"Example blog"`).

- **`content`**:  
  The main text content of the blog post (e.g., `"This is an example."`).

- **`date`**:  
  The publication date of the blog post in `MM-DD-YYYY` format (e.g., `"12-06-2024"`).


## Script Usage

```bash
ab@Evolution-X:~/www_gitres/blogs$ ./create_blog.py
```

```
Enter the background image filename (without extension): background1
Enter the author's GitHub username: anierin
Enter the author: Anierin Bliss
Enter the title of the blog: Example blog
Enter the content of the blog: This is an example.
Enter the date (MM-DD-YYYY): 12-06-2024
```
