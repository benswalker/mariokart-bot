import nxbt
import time

SWITCH_ADDRESS = None  # set this after first pairing, e.g. "AB:CD:EF:12:34:56"

def make_state(steer=0.0, throttle=True, brake=False, drift=False, item=False):
    """
    Build an nxbt Pro Controller input state.
    steer:    -1.0 (full left) to 1.0 (full right)
    throttle: hold ZR to accelerate
    brake:    hold ZL (also used for drift)
    drift:    tap/hold ZL while turning
    item:     tap L to use item
    """
    stick_x = int(max(-100, min(100, steer * 100)))

    return {
        "L_STICK": {
            "PRESSED": False,
            "X_VALUE": stick_x,
            "Y_VALUE": -100 if throttle else 0,
        },
        "R_STICK": {"PRESSED": False, "X_VALUE": 0, "Y_VALUE": 0},
        "DPAD_UP":    False,
        "DPAD_DOWN":  False,
        "DPAD_LEFT":  False,
        "DPAD_RIGHT": False,
        "A":          False,
        "B":          brake,
        "X":          False,
        "Y":          False,
        "PLUS":       False,
        "MINUS":      False,
        "L":          item,
        "R":          False,
        "ZL":         drift,
        "ZR":         throttle,
        "HOME":       False,
        "CAPTURE":    False,
        "L_STICK_PRESS": False,
        "R_STICK_PRESS": False,
    }

def neutral_state():
    return make_state(steer=0.0, throttle=False)

class MKController:
    def __init__(self, reconnect_address=SWITCH_ADDRESS):
        print("Initialising nxbt...")
        self.nx = nxbt.Nxbt()
        self.idx = self.nx.create_controller(
            nxbt.PRO_CONTROLLER,
            reconnect_address=reconnect_address
        )

    def wait_for_connection(self):
        print("Waiting for Switch connection...")
        print("On your Switch: System Settings → Controllers and Sensors → Change Grip/Order")
        self.nx.wait_for_connection(self.idx)
        print("Connected!")
        # save address for future reconnects
        addrs = self.nx.get_switch_addresses()
        if addrs:
            print(f"Switch address: {addrs}")
            print(f"Save this in controller.py as SWITCH_ADDRESS = '{addrs[0]}'")

    def send(self, steer=0.0, throttle=True, brake=False, drift=False, item=False):
        state = make_state(steer, throttle, brake, drift, item)
        self.nx.set_controller_input(self.idx, state)

    def send_state(self, state: dict):
        self.nx.set_controller_input(self.idx, state)

    def neutral(self):
        self.nx.set_controller_input(self.idx, neutral_state())

    def tap_a(self, duration=0.1):
        """Tap A — useful for menu navigation."""
        s = neutral_state()
        s["A"] = True
        self.nx.set_controller_input(self.idx, s)
        time.sleep(duration)
        self.nx.set_controller_input(self.idx, neutral_state())

    def keepalive(self):
        """Send neutral input so Switch doesn't sleep."""
        self.neutral()
