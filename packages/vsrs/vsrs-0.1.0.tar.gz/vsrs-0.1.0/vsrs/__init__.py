import argparse
from PIL import Image
from vsrs.rescale import rescale
from vsrs.dims import VsSkinOffsetCalculator


def parse_args():
    parser = argparse.ArgumentParser(
        description="Resize MSX/Vienna MineSweeper skins",
        epilog="Happy Sweeping!",
    )
    parser.add_argument(
        "-s", "--show", action="store_true", help="show the generated skin in a popup"
    )
    parser.add_argument(
        "-b", "--background", default="#00ff00", help="background color for skin"
    )
    parser.add_argument(
        "input",
        help="input file to be scaled or html color code formatted like #rrggbb. If a color code is passed, generate a template for that output size using this as a foreground color",
    )
    parser.add_argument("output_size", type=int, help="output square size, in pixels")
    parser.add_argument(
        "-o", "--output", default=None, help="write output to file OUTPUT"
    )
    return parser.parse_args()


def handle_im(args, im):
    outim = rescale(im, args.output_size, args.background)
    if args.output:
        outim.save(args.output)
    if args.show:
        outim.show()


def main():
    args = parse_args()
    if args.input.startswith("#"):
        calc = VsSkinOffsetCalculator(16)
        im = Image.new(
            "RGB",
            (144, calc.msx_h()),
            args.input,
        )
        return handle_im(args, im)
    with Image.open(args.input) as im:
        return handle_im(args, im)


if __name__ == "__main__":
    main()
