![Intro](https://github.com/theamallalgi/shownamer/blob/main/dependencies/header.png?raw=true)

# Shownamer - Media Renamer

A lightweight Python CLI tool that renames TV show episode video files by fetching their actual episode titles. Movies are not supported, All TV Shows and Sitcoms are supported.

> [!NOTE]
> Fetches details and Names from [TVmaze](https://www.tvmaze.com/).

## Features

- Automatically detects and renames files like:

  ```
  Before: Malcolm in the Middle S01E10.mkv
  After: Malcolm in the Middle S01E10 - Stock Car Races.mkv
  ```

- Fetches episode titles using the free TVmaze API.
- Cleans illegal filename characters automatically.
- CLI flags for:
  - Custom directory
  - File extension filter
  - Available Show Names
  - Dry-run mode
  - Verbose logging

## Usage

### Requirements

- Python 3.6+

Install requirements:

```bash
pip install shownamer
```

### Run the script

```bash
shownamer --help
```

## Available Flags

| Flag        | Description                                                                           |
| ----------- | ------------------------------------------------------------------------------------- |
| `--dir`     | Directory to scan for files (default: current working directory)                      |
| `--ext`     | File extensions to consider (default: `.mkv`, `.mp4`, `.avi`, `.mov`, `.flv`)         |
| `--dry-run` | Show what would be renamed, without actually renaming any files                       |
| `--verbose` | Show skipped files, errors, and debug output                                          |
| `--name`    | List detected show names along with season and episode counts                         |
| `--format`  | Custom rename format using placeholders: `{name}`, `{season}`, `{episode}`, `{title}` |
| `--version` | Print the tool version and exit                                                       |

### Example Usage

```bash
# Rename all valid video files in the current directory
shownamer

# Specify a custom directory
shownamer --dir "/path/to/your/episodes"

# Preview changes without renaming files
shownamer --dry-run

# Show detected show names with season/episode stats
shownamer --name

# Limit to specific extensions
shownamer --ext mkv mp4 avi

# Verbose mode (shows skipped files, debug info)
shownamer --verbose
```

## Filename Formats

```sh
{name} # show name
{season} # season number (as integer)
{episode} # episode number (as integer)
{title} # episode title (sanitized for filesystem)
```

```sh
shownamer --format "{name} - S{season:02}E{episode:02} - {title}" # Default Format

# Other Examples
shownamer --format "{title} [{name} S{season:02}E{episode:02}]" # Title-first format
shownamer --format "E{episode:02} - {title}" # Episode code only
shownamer --format "{name} - {title}" # Name only
```

The script supports the following file name pattern:

```sh
Malcolm in the Middle S01E10.mkv
Malcolm_in_the_Middle_S01E10.avi
Malcolm-in-the-Middle-E10.mp4
Malcolm.in.the.Middle.S02E03.mkv
TheOffice_E05.avi # No Season Specified, Defaults to Season One
```

All of the following are supported:

- Spaces, dots, underscores, dashes
- Optional season (defaults to season 1 if not found)

## FAQ

### Will this overwrite existing files?

No. The script does not overwrite files. It renames only when the target filename does not exist. You can use `--dry-run` to preview the result first.

### Does it fetch subtitles or cover images?

No. This tool only renames the video files with accurate episode titles.

## Contributions

Pull requests, suggestions, and issues are welcome! Let's make it smarter and broader (e.g., subtitle renaming, fuzzy matching, show aliases, etc.).
