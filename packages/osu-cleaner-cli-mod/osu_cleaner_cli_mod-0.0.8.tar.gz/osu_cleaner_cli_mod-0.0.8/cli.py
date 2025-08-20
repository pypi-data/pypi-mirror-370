#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Modified osu-cleaner-cli by Layerex + requested behavior
# Copyright (C) 2022 Layerex
# Licensed under the GNU GPL v3 (see LICENSE)
#

from __future__ import annotations
import argparse
import concurrent.futures as cf
import os
import re
import shutil
import stat
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Set, Tuple, List, Dict

__prog__ = "osu-cleaner-cli-mod"
__version__ = "0.0.8"
__author__ = "Layerex"
__desc__ = "Remove unwanted files from osu! Songs directory. Modified Version"

EXT = {
    "videos": (".avi", ".flv", ".mp4", ".wmv", ".mkv"),
    "images": (".png", ".jpg", ".jpeg"),
    "hitsounds": (".wav", ".ogg"),
    "beatmaps": (".osu",),
    "storyboards": (".osb",),
    "skin_ini": (".ini",),
}

SKIN_PREFIXES = tuple(
    s.lower()
    for s in (
        "cursor","hit","lighting","particle","sliderpoint","approachcircle","followpoint",
        "hitcircle","reversearrow","slider","default-","spinner-","sliderscorepoint",
        "taiko","pippidon","fruit-","scorebar-","score-","selection-mod-","comboburst",
        "menu-button-background","multi-skipped","play-","star2","inputoverlay-",
        "scoreentry-","ready","count","go.png","section-fail","section-pass","ranking-",
        "pause-","fail-background",
    )
)

QUOTED_RE = re.compile(r"\"(.*?)\"")
CONTROL_CHARS_RE = re.compile(r"[\x00-\x1F\x7F]")


@dataclass(frozen=True)
class Flags:
    delete_videos: bool
    delete_hitsounds: bool
    delete_backgrounds: bool
    delete_skin_elements: bool
    delete_storyboards: bool
    delete_skin_ini: bool
    delete_images_combo: bool


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        prog=__prog__,
        description="Remove unwanted files from osu! Songs directory (fast & safe).",
    )
    ap.add_argument("osu_songs_directory", nargs="?", help="Path to osu! Songs directory")
    ap.add_argument("--delete-videos", action="store_true")
    ap.add_argument("--delete-hitsounds", action="store_true")
    ap.add_argument("--delete-backgrounds", action="store_true")
    ap.add_argument("--delete-skin-elements", action="store_true")
    ap.add_argument("--delete-storyboard-elements", action="store_true")
    ap.add_argument("--delete-all", action="store_true", help="Delete videos, images, hitsounds, etc.")
    ap.add_argument("--force", action="store_true", help="Actually delete (otherwise dry-run).")
    ap.add_argument("--threads", type=int, default=min(32, (os.cpu_count() or 4) * 5),
                    help="Parallel deletion workers (IO-bound).")
    return ap.parse_args()


def resolve_base(path_arg: str | None) -> Path:
    base = Path(path_arg or input("Enter the path to your osu! Songs directory: ")).expanduser().resolve()
    if not base.exists() or not base.is_dir():
        raise SystemExit(f"[error] Not a directory: {base}")
    return base


def compute_flags(args: argparse.Namespace) -> Flags:
    dv = args.delete_videos or args.delete_all
    dh = args.delete_hitsounds or args.delete_all
    db = args.delete_backgrounds or args.delete_all
    ds = args.delete_skin_elements or args.delete_all
    dst = args.delete_storyboard_elements or args.delete_all

    d_ini = ds

    combo = db and ds and dst
    if combo:
        db = ds = dst = False

    if not any([dv, dh, db, ds, d_ini, dst, combo]):
        raise SystemExit("No delete flags specified. Nothing to do.")

    return Flags(
        delete_videos=dv,
        delete_hitsounds=dh,
        delete_backgrounds=db,
        delete_skin_elements=ds,
        delete_storyboards=dst,
        delete_skin_ini=d_ini,
        delete_images_combo=combo,
    )


def force_remove_readonly(func, path, _exc):
    try:
        os.chmod(path, stat.S_IWRITE)
    except OSError:
        pass
    func(path)


def read_text_quiet(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""



def _norm(s: str) -> str:
    s = s.replace("\\", "/")
    s = CONTROL_CHARS_RE.sub("", s)
    s = unicodedata.normalize("NFKC", s)
    s = s.strip().strip('"').strip("'")
    if s.startswith("./"):
        s = s[2:]
    if s.startswith("/"):
        s = s[1:]
    return s.lower()


def build_file_index(beatmap_dir: Path) -> tuple[Dict[str, Path], Dict[str, List[Path]]]:
    norm_map: Dict[str, Path] = {}
    base_map: Dict[str, List[Path]] = {}
    start = beatmap_dir.resolve()
    for root, _, files in os.walk(start):
        root_p = Path(root)
        for f in files:
            p = root_p / f
            try:
                rel = p.relative_to(start)
            except Exception:
                continue
            rel_norm = _norm(rel.as_posix())
            norm_map[rel_norm] = p
            base = _norm(p.name)
            base_map.setdefault(base, []).append(p)
    return norm_map, base_map


def map_ref_to_existing(raw: str, base_dir: Path,
                        norm_map: Dict[str, Path],
                        base_map: Dict[str, List[Path]]) -> Path | None:
    s = _norm(raw)
    if not s:
        return None

    if s in norm_map:
        return norm_map[s]

    base = _norm(Path(s).name)
    if base in base_map:
        return sorted(base_map[base], key=lambda p: len(p.relative_to(base_dir).parts))[0]

    return None


def extract_audio_paths_from_osu(beatmap_dir: Path) -> Set[Path]:
    audio: Set[Path] = set()
    for osu_file in beatmap_dir.glob("*.osu"):
        try:
            with osu_file.open("r", encoding="utf-8", errors="ignore") as fh:
                for line in fh:
                    if line.startswith("AudioFilename:"):
                        audio_name = line.split(":", 1)[1].strip()
                        if audio_name:
                            audio.add(beatmap_dir / audio_name)
        except OSError:
            pass
    return audio


def extract_quoted_paths(p: Path, norm_map: Dict[str, Path], base_map: Dict[str, List[Path]]) -> Iterable[Path]:
    txt = read_text_quiet(p)
    base = p.parent
    for raw in QUOTED_RE.findall(txt):
        mapped = map_ref_to_existing(raw, base, norm_map, base_map)
        if mapped is not None:
            yield mapped
            continue

        cleaned = _norm(raw)
        if not cleaned:
            continue
        try:
            yield (base / cleaned)
        except Exception:
            continue


def is_skin_element(file: Path) -> bool:
    name = file.name.lower()
    return name.startswith(SKIN_PREFIXES) and file.suffix.lower() in EXT["images"]


def collect_references(beatmap_dir: Path) -> Tuple[Set[Path], Set[Path]]:
    ref_osu: Set[Path] = set()
    ref_osb: Set[Path] = set()
    norm_map, base_map = build_file_index(beatmap_dir)

    for osu_file in beatmap_dir.glob("*.osu"):
        for p in extract_quoted_paths(osu_file, norm_map, base_map):
            ref_osu.add(p)

    for osb_file in beatmap_dir.glob("*.osb"):
        for p in extract_quoted_paths(osb_file, norm_map, base_map):
            ref_osb.add(p)

    return ref_osu, ref_osb


def should_delete_file(
    file: Path,
    flags: Flags,
    main_audio_paths: Set[Path],
    referenced_by_osu: Set[Path],
    referenced_by_osb: Set[Path],
) -> bool:
    suf = file.suffix.lower()

    if flags.delete_images_combo:
        if suf in EXT["images"] or suf in EXT["storyboards"]:
            return True

    if flags.delete_videos and suf in EXT["videos"]:
        return True

    if flags.delete_hitsounds and suf in EXT["hitsounds"]:
        try:
            return file not in main_audio_paths
        except OSError:
            return True

    if flags.delete_skin_ini and suf in EXT["skin_ini"]:
        return True

    if flags.delete_skin_elements and is_skin_element(file):
        return True

    if flags.delete_backgrounds and (file in referenced_by_osu) and suf in EXT["images"]:
        return True

    if flags.delete_storyboards:
        if suf in EXT["storyboards"]:
            return True
        if (file in referenced_by_osb) and (suf in EXT["images"] or suf in EXT["videos"]):
            return True

    return False



def plan_for_beatmap(beatmap_dir: Path, flags: Flags) -> Set[Path]:
    to_delete: Set[Path] = set()

    ref_osu, ref_osb = collect_references(beatmap_dir)
    main_audio = extract_audio_paths_from_osu(beatmap_dir)

    for root, dirs, files in os.walk(beatmap_dir, topdown=False):
        root_p = Path(root)

        for d in dirs:
            subdir = root_p / d
            if subdir != beatmap_dir:
                to_delete.add(subdir) 

        if root_p != beatmap_dir:
            continue

        for f in files:
            file = root_p / f
            if should_delete_file(file, flags, main_audio, ref_osu, ref_osb):
                to_delete.add(file)

    return to_delete


def scan_and_plan(base: Path, flags: Flags) -> Set[Path]:
    print(f"[scan] {base}")
    planned: Set[Path] = set()

    for beatmap_dir in sorted([p for p in base.iterdir() if p.is_dir()]):
        print(f"  > {beatmap_dir.name}")
        planned.update(plan_for_beatmap(beatmap_dir, flags))

    for p in base.iterdir():
        if p.is_file():
            planned.add(p)

    return planned


def delete_path(p: Path) -> tuple[Path, bool, str | None]:
    try:
        if p.is_dir():
            shutil.rmtree(p, onerror=force_remove_readonly)
        else:
            p.unlink()
        return (p, True, None)
    except Exception as e:
        return (p, False, str(e))


def execute_plan(to_delete: Set[Path], *, threads: int, force: bool) -> None:
    num_files = sum(1 for p in to_delete if p.is_file())
    num_dirs = sum(1 for p in to_delete if p.is_dir())
    print(f"[plan] Will remove {num_files} files and {num_dirs} folders.")

    if not force:
        print("Dry-run only. Use --force to actually delete.")
        return

    print(f"[delete] Using {threads} workers...")
    ok = fail = 0
    with cf.ThreadPoolExecutor(max_workers=max(1, threads)) as ex:
        futures = [ex.submit(delete_path, p) for p in to_delete]
        for fut in cf.as_completed(futures):
            p, success, err = fut.result()
            if success:
                ok += 1
            else:
                fail += 1
                print(f"[fail] {p} -> {err}")

    print(f"[done] Deleted {ok} items. Failed: {fail}.")
    if fail:
        print("Some items were read-only or locked; close osu!/Explorer and retry.")


def main() -> None:
    args = parse_args()
    base = resolve_base(args.osu_songs_directory)
    flags = compute_flags(args)
    to_delete = scan_and_plan(base, flags)
    if not to_delete:
        print("[done] Nothing to remove.")
        return
    execute_plan(to_delete, threads=args.threads, force=args.force)


if __name__ == "__main__":
    main()
