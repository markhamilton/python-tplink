#!/usr/bin/env python

import argparse
import sys
# import os
from tplib import TPBulb
import json

from pygments import highlight, lexers, formatters


reload(sys)
sys.setdefaultencoding('utf-8')


def pretty_json(json_text):
    json_formatted = json.dumps(json.loads(json_text), sort_keys=True, indent = 4, separators = (',', ': '))
    colorful_json = highlight(unicode(json_formatted, 'UTF-8'), lexers.JsonLexer(), formatters.TerminalFormatter())
    return colorful_json


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send commands to TP-LINK light bulb")
    parser.add_argument('ip', help="IP address of the TP-LINK bulb")
    parser.add_argument('-y', '--on', action="store_true", help="Turn light on")
    parser.add_argument('-n', '--off', action="store_true", help="Turn light off")
    parser.add_argument('-t', '--transition', type=int, default=0, help="How much time in ms to transition from one state to another.")
    parser.add_argument('--rgb', help="Color value represented as r,g,b --rgb 255,255,255")
    parser.add_argument('--hsv', help="Color value represented as h,s,v --hsv 360,100,100")
    parser.add_argument('--hex', help="color value represented as hex --hex ff0000")
    args = parser.parse_args()

    bulb = TPBulb(args.ip)

    if args.hsv:
        hsv = args.hsv.split(',')
        if len(hsv) != 3:
            raise ValueError("HSV values need to be represented as h,s,v (e.g., 360,100,100)")
        print pretty_json(bulb.color_hsv(int(hsv[0]), int(hsv[1]), int(hsv[2]), transition=args.transition))
    elif args.rgb:
        rgb = args.rgb.split(',')
        if len(rgb) != 3:
            raise ValueError("RGB values need to be represented as r,g,b (e.g., 255,255,255)")
        print pretty_json(bulb.color_rgb(int(rgb[0]), int(rgb[1]), int(rgb[2]), transition=args.transition))
    elif args.hex:
        print pretty_json(bulb.color_hex(args.hex, transition=args.transition))
    elif args.on:
        print pretty_json(bulb.turn_on(transition=args.transition))
    elif args.off:
        print pretty_json(bulb.turn_off(transition=args.transition))

