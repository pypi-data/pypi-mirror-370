import os
import re
import requests
import argparse
from collections import defaultdict

DEFAULT_EXTENSIONS = [".mkv", ".mp4", ".avi", ".mov", ".flv"]
TOOL_VERSION = "1.2.2"

# Match: ShowName_S01E05, Show.Name-S1E5, Show Name S01E05 etc.
FILENAME_PATTERN = re.compile(
    r"^(?P<show>.+?)[\s._-]*[Ss]?(?P<season>\d{1,2})?[Ee](?P<episode>\d{2})",
    re.IGNORECASE,
)

INVALID_CHARS = r'\/:*?"<>|\0'

# Cache to avoid repeated API calls
show_cache = {}
title_cache = {}


def sanitize_filename(name, subst=None):
    """Remove or replace illegal filename characters."""
    if subst:
        return "".join(c if c not in INVALID_CHARS else subst for c in name)
    else:
        return "".join(c for c in name if c not in INVALID_CHARS)


def get_show_id_and_name(raw_show_name, verbose=False):
    """Query show ID and canonical name from TVmaze API."""
    if raw_show_name in show_cache:
        return show_cache[raw_show_name]

    clean_name = re.sub(r"[\._\-]+", " ", raw_show_name).strip()

    if verbose:
        print(f"[query] Looking up: '{clean_name}'")

    try:
        response = requests.get(
            "https://api.tvmaze.com/singlesearch/shows", params={"q": clean_name}
        )
        response.raise_for_status()  # Raise an exception for bad status codes
    except requests.exceptions.RequestException as e:
        if verbose:
            print(f"[fail] Network error for show '{clean_name}': {e}")
        return None, None

    if response.status_code != 200:
        if verbose:
            print(f"[fail] Failed to find show: {clean_name}")
        return None, None

    data = response.json()
    show_cache[raw_show_name] = (data["id"], data["name"])
    return data["id"], data["name"]


def get_episode_title(show_id, season, episode, verbose=False):
    """Query TVmaze API for episode title."""
    cache_key = (show_id, season, episode)
    if cache_key in title_cache:
        return title_cache[cache_key]

    try:
        response = requests.get(
            f"https://api.tvmaze.com/shows/{show_id}/episodebynumber",
            params={"season": season, "number": episode},
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        if verbose:
            print(f"[fail] Network error for S{season:02}E{episode:02}: {e}")
        return None

    if response.status_code != 200:
        if verbose:
            print(f"[fail] Failed to find episode S{season:02}E{episode:02}")
        return None

    title = response.json()["name"]
    title_cache[cache_key] = title
    return title


def list_series_summary(directory, extensions, verbose=False):
    stats = defaultdict(lambda: defaultdict(int))
    canonical_names = {}

    for filename in os.listdir(directory):
        name, ext = os.path.splitext(filename)
        if ext.lower() not in extensions:
            continue

        match = FILENAME_PATTERN.match(name)
        if not match:
            continue

        raw_show = match.group("show").strip()
        season_str = match.group("season")
        season = int(season_str) if season_str else 1

        show_id, canonical_name = get_show_id_and_name(raw_show, verbose)
        if not show_id:
            continue

        canonical_names[raw_show] = canonical_name
        stats[canonical_name][season] += 1

    if not stats:
        print("No recognizable TV show files found.")
        return

    print("Detected Series Summary:")
    for show, seasons in stats.items():
        print(f"  {show}:")
        for season, count in sorted(seasons.items()):
            print(f"    Season {season:02}: {count} episode(s)")


def rename_files(directory, extensions, dry_run=False, verbose=False, format_str=None, subst=None):
    for filename in os.listdir(directory):
        name, ext = os.path.splitext(filename)
        if ext.lower() not in extensions:
            continue

        match = FILENAME_PATTERN.match(name)
        if not match:
            if verbose:
                print(f"[skip] {filename}: no pattern match")
            continue

        raw_show = match.group("show").strip()
        season_str = match.group("season")
        season = int(season_str) if season_str else 1
        episode = int(match.group("episode"))

        show_id, canonical_name = get_show_id_and_name(raw_show, verbose)
        if not show_id:
            print(f"[fail] {filename}: show not found")
            continue

        episode_title = get_episode_title(show_id, season, episode, verbose)
        if not episode_title:
            print(f"[fail] {filename}: episode not found")
            continue

        safe_title = sanitize_filename(episode_title, subst=subst)
        safe_name = sanitize_filename(canonical_name, subst=subst)

        if not format_str:
            format_str = "{name} S{season:02}E{episode:02} - {title}"

        try:
            new_basename = format_str.format(
                name=safe_name,
                season=season,
                episode=episode,
                title=safe_title,
            )
        except KeyError as e:
            print(f"[fail] Invalid format string key: {e}")
            continue

        new_filename = f"{new_basename}{ext}"
        src = os.path.join(directory, filename)
        dst = os.path.join(directory, new_filename)

        if os.path.exists(dst):
            print(f"[skip] {new_filename} already exists")
            continue

        if dry_run:
            print(f"[dry-run] {filename} → {new_filename}")
        else:
            os.rename(src, dst)
            print(f"[renamed] {filename} → {new_filename}")


def main():
    parser = argparse.ArgumentParser(
        description="Rename TV episode files using episode titles from TVmaze."
    )
    parser.add_argument(
        "--dir",
        default=os.getcwd(),
        help="Directory with video files (default: current directory)",
    )
    parser.add_argument(
        "--ext",
        nargs="*",
        default=DEFAULT_EXTENSIONS,
        help="Allowed video file extensions (default: common types)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without renaming files",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Show debug and skip messages"
    )
    parser.add_argument("--version", action="store_true", help="Show version and exit")
    parser.add_argument(
        "--name",
        action="store_true",
        help="List canonical show names and episode counts",
    )
    parser.add_argument(
        "--format",
        type=str,
        help="Custom format using {name}, {season}, {episode}, {title}",
    )
    parser.add_argument(
        "--subst",
        type=str,
        default=None,
        help=r'Replace illegal characters with a specific character (unsupported: \ / : * ? " < > | \0)'
    )

    args = parser.parse_args()
    extensions = [e if e.startswith(".") else "." + e for e in args.ext]

    if args.subst and args.subst in INVALID_CHARS:
        print(f"[fail] Invalid replacement character: '{args.subst}' is an illegal character.")
        return

    if args.version:
        print(f"shownamer version {TOOL_VERSION}")
        return

    if args.name:
        list_series_summary(args.dir, extensions, args.verbose)
        return

    rename_files(
        directory=args.dir,
        extensions=extensions,
        dry_run=args.dry_run,
        verbose=args.verbose,
        format_str=args.format,
        subst=args.subst,
    )


if __name__ == "__main__":
    main()
