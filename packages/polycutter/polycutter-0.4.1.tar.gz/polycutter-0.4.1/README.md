
# polycutter

lossless video cutting tool using ffmpeg

cuts video segments and stitches them together without re-encoding

## usage

```sh
# basic usage
polycutter cut -i input.mp4 -o output.mp4 --segments "00:08-00:45,04:43-05:18"

# cut from timestamp to end
polycutter cut -i input.mp4 -o output.mp4 --segments "00:37-_"

# extract segments to separate files
polycutter cut -i input.mp4 -o "clip_{}.mp4" --segments "1:30-2:00,3:15-4:30" --no-merge

# analyze video properties
polycutter probe -i input.mp4 --keyframes
```

## install

```sh
poetry install
```
