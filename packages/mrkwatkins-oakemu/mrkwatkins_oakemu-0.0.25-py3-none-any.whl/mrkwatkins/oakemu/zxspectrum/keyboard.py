from MrKWatkins.OakEmu.Machines.ZXSpectrum import Keyboard as DotNetKeyboard  # noqa
from MrKWatkins.OakEmu.Machines.ZXSpectrum import Keys as DotNetKeys  # noqa
from mrkwatkins.oakemu.zxspectrum.keys import Keys


class Keyboard:
    def __init__(self, keyboard: DotNetKeyboard):
        self._keyboard = keyboard

    @property
    def pressed(self) -> Keys:
        return Keys(int(self._keyboard.Pressed))

    @pressed.setter
    def pressed(self, value: Keys):
        self._keyboard.Pressed = DotNetKeys(value)

    def press(self, value: Keys):
        self._keyboard.Press(DotNetKeys(value))

    def depress(self, value: Keys):
        self._keyboard.Depress(DotNetKeys(value))

    def depress_all(self):
        self._keyboard.DepressAll()
