# osu-cleaner-cli-mod

> Modified fork of [Layerex/osu-cleaner-cli](https://github.com/Layerex/osu-cleaner-cli)  
> Original work © 2022 Layerex — GPL-3.0 license. This repository redistributes modified code under the same license.

Remove unwanted files from osu! Songs directory. A rewrite of [that](https://github.com/henntix/osu-cleaner) tool, which is not cross-platform and does not work as intended.

## What's changed in this fork
- Cleans more thoroughly: also removes matching unwanted files located in subfolders inside beatmaps.
- Safer by default: runs in **dry-run mode** unless `--force` is specified.

## Installation

```bash
pip install osu-cleaner-cli-mod
```

## Usage

```
usage: osu-cleaner-cli-mod [-h] [--delete-videos] [--delete-hitsounds]
                           [--delete-backgrounds] [--delete-skin-elements]
                           [--delete-storyboard-elements] [--delete-all]
                           [--force]
                           [osu_songs_directory]

Remove unwanted files from osu! Songs directory.

positional arguments:
  osu_songs_directory                                 Path to your osu! Songs directory

options:
  -h, --help                                          Show this help message and exit
  --delete-videos                                     Remove video files (.mp4, .avi, .flv, .mkv, .wmv)
  --delete-hitsounds                                  Remove extra hitsounds (.wav, .ogg) not used as BGM
  --delete-backgrounds                                Remove beatmap background images
  --delete-skin-elements                              Remove embedded skin graphics
  --delete-storyboard-elements                        Remove storyboard files (.osb) and their assets
  --delete-all                                        Remove all of the above categories
  --force                                             Actually delete files (default is dry-run)

If no arguments or only osu! Songs directory specified, script will start in interactive mode.
```
