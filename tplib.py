
import socket
import json
import colorsys
import datetime


def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))


class TPBulb:

    ip = "10.0.0.200"
    port = "9999"

    def __init__(self, ip_address):
        self.ip = ip_address

    # FIXME: Scanning doesn't quite work yet
    def scan(self):
        sock = socket.socket(socket.AF_INET,
                             socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # sock.bind(('', 9999))
        message = self.encrypt(json.dumps({"system":{"get_sysinfo":{}}}))
        sock.sendto(message, ('255.255.255.255', 9999))

        # while True:
        data, addr = sock.recvfrom(2048)
        return self.decrypt(data)


    def daystat(self, month=datetime.datetime.today().month, year=datetime.datetime.today().year):
        return self.send({'smartlife.iot.common.schedule': {'get_daystat': {'month': month, 'year': year}}})

    def cloud(self):
        return self.send({'smartlife.iot.common.cloud': {'get_info': {}}})

    def schedule(self):
        return self.send({'smartlife.iot.common.schedule': {'get_rules': {}}})

    def details(self):
        return self.send({'smartlife.iot.smartbulb.lightingservice': {'get_light_details': {}}})

    def color_hex(self, hex_color, transition=0):
        h = hex_color.lstrip('#')
        if len(h) == 3:
            h = h[0] + h[0] + h[1] + h[1] + h[2] + h[2]
        elif len(h) != 6:
            raise IOError("Not valid hex format")
        rgb = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
        return self.color_rgb(rgb[0], rgb[1], rgb[2], transition)

    def color_rgb(self, r, g, b, transition=0):
        r = clamp(r, 0, 255)
        g = clamp(g, 0, 255)
        b = clamp(b, 0, 255)
        hsv = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
        return self.color_hsv(int(hsv[0] * 360),int(hsv[1] * 100), int(hsv[2] * 100),transition)

    def color_hsv(self, h, s, v, transition=0):
        # clamp values
        while h > 360:
            h -= 360
        while h < 0:
            h += 360
        s = clamp(s, 0, 100)
        v = clamp(v, 0, 100)

        message = {
            'smartlife.iot.smartbulb.lightingservice': {
                'transition_light_state': {
                    'ignore_default': 1,
                    'on_off': 1,
                    'transition_period': transition,
                    'hue': int(h),
                    'saturation': int(s),
                    'brightness': int(v),
                    'color_temp': 0
                }
            }
        }
        return self.send(message)

    def color_temp(self, temp, transition=0):
        pass

    def turn_off(self, transition=0):
        message = {'smartlife.iot.smartbulb.lightingservice': {
            'transition_light_state': {
                'ignore_default': 1,
                'on_off': 0,
                'transition_period': transition}}}
        return self.send(message)

    def turn_on(self, ignore_default=1, transition=0):
        message = {'smartlife.iot.smartbulb.lightingservice': {
            'transition_light_state': {
                'ignore_default': ignore_default,
                'on_off': 1,
                'transition_period': transition}}}
        return self.send(message)

    def decrypt(self, message, key=0xAB):
        new_message = ""
        for c in message:
            new_message += chr(ord(c) ^ key)
            key = ord(c)
        return new_message

    def encrypt(self, message, key=0xAB):
        new_message = ""
        for c in message:
            new_char = chr(ord(c) ^ key)
            new_message += new_char
            key = ord(new_char)
        return new_message

    def send(self, message):
        if not self.ip:
            raise IOError("IP not set")

        message = self.encrypt(json.dumps(message))
        sock = socket.socket(socket.AF_INET,
                             socket.SOCK_DGRAM)
        sock.sendto(message, (self.ip, int(self.port)))

        data, addr = sock.recvfrom(1024)
        return self.decrypt(data)


