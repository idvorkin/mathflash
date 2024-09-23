import os
import hyperdiv as hd


class keyboard_capture(hd.Plugin):
    _assets_root = os.path.join(os.path.dirname(__file__), "assets")
    _assets = [
        "https://craig.global.ssl.fastly.net/js/mousetrap/mousetrap.min.js?a4098",
        "keyboard_capture.js",
    ]

    # https://docs.hyperdiv.io/reference/prop-types/List
    # TODO I should create a type for valid capture_values (but not today), See hd.ClampedType
    capture = hd.Prop(hd.List(hd.String), [])
    pressed_event = hd.Prop(hd.StringEvent, "")
    last_pressed = hd.Prop(hd.PureString, "")
