import argparse
import os
import re
import json
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

import requests
from guessit import guessit
from imdb import Cinemagoer

DEFAULT_EXTENSIONS = [".mkv", ".mp4", ".avi", ".mov", ".flv"]
TOOL_VERSION = "1.5.0"

# Match: ShowName_S01E05, Show.Name-S1E5, Show Name S01E05 etc.
FILENAME_PATTERN = re.compile(
    r"^(?P<show>.+?)[\s._-]*[Ss]?(?P<season>\d{1,2})?[Ee](?P<episode>\d{2})",
    re.IGNORECASE,
)

INVALID_CHARS = r'\/:*?"<>|' + "\0"
CACHE_FILE = os.path.expanduser("~/.shownamer_cache.json")

# Cinemagoer instance
ia = Cinemagoer()

# Caches
title_cache = {}
show_cache = {}

def load_cache():
    """Load movie cache from disk."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_cache(cache):
    """Save movie cache to disk."""
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)

movie_cache = load_cache()

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
            "https://api.tvmaze.com/singlesearch/shows",
            params={"q": clean_name},
            timeout=30,
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        if verbose:
            print(f"[fail] Network error for show '{clean_name}': {e}")
        return None, None, None

    if response.status_code != 200:
        if verbose:
            print(f"[fail] Failed to find show: {clean_name}")
        return None, None, None

    data = response.json()
    show_cache[raw_show_name] = (data["id"], data["name"], data.get("premiered", "   ")[:4])
    return data["id"], data["name"], data.get("premiered", "   ")[:4]

def get_episode_title(show_id, season, episode, verbose=False):
    """Query TVmaze API for episode title."""
    cache_key = (show_id, season, episode)
    if cache_key in title_cache:
        return title_cache[cache_key]

    try:
        response = requests.get(
            f"https://api.tvmaze.com/shows/{show_id}/episodebynumber",
            params={"season": season, "number": episode},
            timeout=30,
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

        show_id, canonical_name, year = get_show_id_and_name(raw_show, verbose)
        if not show_id:
            continue

        canonical_names[raw_show] = canonical_name
        stats[canonical_name][season] += 1

    if not stats:
        print("No recognizable TV show files found.")
        return

    print("Detected Series Summary:")
    for show, seasons in stats.items():
        print(f"  {show} ({year}):")
        for season, count in sorted(seasons.items()):
            print(f"    Season {season:02}: {count} episode(s)")

def rename_files(directory, extensions, dry_run=False, verbose=False, format_str=None, subst=None):
    # This function remains sequential as TV show episodes often benefit from caching series info
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

        show_id, canonical_name, show_year = get_show_id_and_name(raw_show, verbose)
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
                year=show_year,
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

def fetch_movie_data(title, verbose=False):
    """Fetch movie data from IMDb, designed to be run in a thread pool."""
    if title in movie_cache:
        if verbose:
            print(f"[cache] Found in-memory cache for '{title}'")
        return title, movie_cache[title]

    if verbose:
        print(f"[query] Searching for movie: '{title}'")
    try:
        movies = ia.search_movie(title)
        if not movies:
            return title, None
        
        # Fetch full movie data
        movie = ia.get_movie(movies[0].movieID)
        result = {"title": movie.get("title"), "year": movie.get("year")}
        movie_cache[title] = result
        return title, result
    except Exception as e:
        if verbose:
            print(f"[fail] Error fetching data for '{title}': {e}")
        return title, None

def rename_movie_files(directory, extensions, dry_run=False, verbose=False, format_str=None, subst=None):
    files_to_process = []
    for filename in os.listdir(directory):
        name, ext = os.path.splitext(filename)
        if ext.lower() not in extensions:
            continue

        guess = guessit(filename)
        if guess.get("type") != "movie":
            if verbose:
                print(f"[skip] {filename}: not a movie")
            continue

        title = guess.get("title")
        if not title:
            if verbose:
                print(f"[skip] {filename}: no title found")
            continue
        
        files_to_process.append((filename, title, ext))

    # Fetch movie data concurrently
    titles_to_fetch = list(set([f[1] for f in files_to_process if f[1] not in movie_cache]))
    with ThreadPoolExecutor(max_workers=10) as executor:
        list(executor.map(fetch_movie_data, titles_to_fetch, [verbose] * len(titles_to_fetch)))

    # Rename files sequentially after fetching data
    for filename, title, ext in files_to_process:
        if title not in movie_cache or not movie_cache[title]:
            print(f"[fail] {filename}: could not find movie data for '{title}'")
            continue

        movie_data = movie_cache[title]
        movie_name = movie_data.get("title")
        movie_year = movie_data.get("year")

        safe_name = sanitize_filename(movie_name, subst=subst)

        if not format_str:
            format_str = "{name} ({year})"

        try:
            new_basename = format_str.format(name=safe_name, year=movie_year)
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
    
    save_cache(movie_cache) # Save the updated cache to disk

def main():
    parser = argparse.ArgumentParser(
        description="Rename TV episode and movie files the way you want.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("-m", "--movie", action="store_true", help="Rename movie files instead of TV shows")
    parser.add_argument("-d", "--dir", default=os.getcwd(), help="Directory with media files (default: current directory)")
    parser.add_argument("-e", "--ext", nargs="*", default=DEFAULT_EXTENSIONS, help="Allowed media file extensions")
    parser.add_argument("-D", "--dry-run", action="store_true", help="Preview changes without renaming files")
    parser.add_argument(
        "-f",
        "--format",
        type=str,
        help="""Custom format string.
For shows: {name}, {season}, {episode}, {title}, {year}
For movies: {name}, {year}""",
    )
    parser.add_argument("-n", "--name", action="store_true", help="List canonical show names and episode counts")
    parser.add_argument("-s", "--subst", type=str, default=None, help="Replace illegal characters with a specific character")
    parser.add_argument("-V", "--verbose", action="store_true", help="Show debug and skip messages")
    parser.add_argument("-v", "--version", action="store_true", help="Show version")

    args = parser.parse_args()
    extensions = [e if e.startswith(".") else "." + e for e in args.ext]

    if args.subst and args.subst in INVALID_CHARS:
        print(f"[fail] Invalid replacement character: '{args.subst}' is an illegal character.")
        return

    if args.version:
        print(f"shownamer version {TOOL_VERSION}")
        return

    if args.movie:
        rename_movie_files(
            directory=args.dir,
            extensions=extensions,
            dry_run=args.dry_run,
            verbose=args.verbose,
            format_str=args.format,
            subst=args.subst,
        )
    elif args.name:
        list_series_summary(args.dir, extensions, args.verbose)
    else:
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
