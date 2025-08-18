# VSRS

A library and command line tool to rescale MSX/ViennaSweeper skins.

Skins are tilemaps for Minesweeper clones. The format was originally
established by Curtis Bright for MSX - Vienna MineSweeper uses a generalized
version of it to support arbitrary square sizes (and, of course, skins).

Requires Pillow.

Requires an image viewer for the `-s` flag (see below).

## Usage

For detailed usage instructions, run the tool with `-h`:
```
$ vsrs -h
usage: vsrs.py [-h] [-s] [-b BACKGROUND] [-o OUTPUT] input output_size

Resize MSX/Vienna MineSweeper skins

positional arguments:
  input                 input file to be scaled or html color code formatted like #rrggbb. If a color code is passed, generate a template for that output size using this as a foreground color
  output_size           output square size, in pixels

options:
  -h, --help            show this help message and exit
  -s, --show            show the generated skin in a popup
  -b, --background BACKGROUND
                        background color for skin
  -o, --output OUTPUT   write output to file OUTPUT

Happy Sweeping!
$
```

### Examples

Scale `in.bmp` to a 33px square size skin and show it in a popup:
```
$ vsrs in.bmp 33 -s
```

Scale `in.bmp` to a 33px square size skin and save it in `out.bmp`:
```
$ vsrs in.bmp 33 -o out.bmp
```

Make a template for a 33px square size skin, using `#ff0000` for the elements and `#0000ff` for the background color, show the result in a popup, and also save it in `out.bmp`:
```
$ vsrs "#ff0000" 33 -o out.bmp -b "#0000ff"
```

