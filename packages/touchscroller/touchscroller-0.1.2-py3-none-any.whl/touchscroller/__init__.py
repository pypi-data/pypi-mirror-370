import uinput
import time


class TouchScroller:

    def __init__(self, width=4000, height=3000, auto_sleep=True):
        self.width = width
        self.height = height
        self.x = width // 2
        self.y = height // 2
        self.tracking_id = 0
        self.device = uinput.Device(
            [
                uinput.BTN_LEFT,
                uinput.BTN_TOOL_FINGER,
                uinput.BTN_TOUCH,
                uinput.BTN_TOOL_DOUBLETAP,
                uinput.ABS_MT_SLOT + (0, 2, 0, 0),
                uinput.ABS_MT_TRACKING_ID + (0, 65535, 0, 0),
                uinput.ABS_MT_POSITION_X + (0, self.width, 0, 0),
                uinput.ABS_MT_POSITION_Y + (0, self.height, 0, 0),
            ]
        )
        self.auto_sleep = auto_sleep
        if self.auto_sleep:
            time.sleep(0.1)

    def down(self, x=None, y=None):
        self.x = x if x is not None else self.width // 2
        self.y = y if y is not None else self.height // 2
        for slot in [0, 1]:
            self.device.emit(uinput.ABS_MT_SLOT, slot, syn=False)
            self.device.emit(uinput.ABS_MT_TRACKING_ID, self.tracking_id, syn=False)
            self.device.emit(uinput.ABS_MT_POSITION_X, self.x, syn=False)
            self.device.emit(uinput.ABS_MT_POSITION_Y, self.y, syn=False)
            self.tracking_id = (self.tracking_id + 1) % 65536
        self.device.emit(uinput.BTN_TOUCH, 1, syn=False)
        self.device.emit(uinput.BTN_TOOL_DOUBLETAP, 1, syn=False)
        self.device.syn()
        if self.auto_sleep:
            time.sleep(0.01)

    def move(self, dx=0, dy=0):
        self.x += dx
        self.y += dy
        self.x = max(0, min(self.x, self.width))
        self.y = max(0, min(self.y, self.height))
        for slot in [0, 1]:
            self.device.emit(uinput.ABS_MT_SLOT, slot, syn=False)
            self.device.emit(uinput.ABS_MT_POSITION_X, self.x, syn=False)
            self.device.emit(uinput.ABS_MT_POSITION_Y, self.y, syn=False)
        self.device.syn()
        if self.auto_sleep:
            time.sleep(0.01)

    def up(self):
        for slot in [0, 1]:
            self.device.emit(uinput.ABS_MT_SLOT, slot, syn=False)
            self.device.emit(uinput.ABS_MT_TRACKING_ID, -1, syn=False)
        self.device.emit(uinput.BTN_TOOL_DOUBLETAP, 0, syn=False)
        self.device.emit(uinput.BTN_TOUCH, 0, syn=False)
        self.device.syn()
        if self.auto_sleep:
            time.sleep(0.01)

    def touch(self, x=None, y=None):
        return TouchScroller.Touch(self, x, y)

    class Touch:
        def __init__(self, scroller, x=None, y=None):
            self.scroller = scroller
            self.x = x
            self.y = y

        def __enter__(self):
            self.scroller.down(self.x, self.y)
            return self

        def move(self, dx=0, dy=0):
            self.scroller.move(dx, dy)

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.scroller.up()
