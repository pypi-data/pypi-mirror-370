import typing
from enum import IntEnum

import numpy as np
from MrKWatkins.OakEmu.Machines.ZXSpectrum import Keys as DotNetKeys  # noqa
from MrKWatkins.OakEmu.Machines.ZXSpectrum.Screen import Colour as DotNetColour  # noqa
from MrKWatkins.OakEmu.Machines.ZXSpectrum.Screen import ZXSpectrumScreen as DotNetZXSpectrumScreen  # noqa

from mrkwatkins.oakemu.zxspectrum.zxcolour import ZXColour


class ScreenType(IntEnum):
    FAST = 0
    ACCURATE = 1


class Screen:
    def __init__(self, screen: DotNetZXSpectrumScreen):
        self._screen = screen

    @property
    def type(self) -> ScreenType:
        return ScreenType(int(self._screen.Type))

    @property
    def border(self) -> ZXColour:
        return ZXColour(int(self._screen.Border))

    @border.setter
    def border(self, value: ZXColour):
        self._screen.Border = DotNetColour(value)

    @property
    def renders_border(self) -> ZXColour:
        return self._screen.RendersBorder

    @property
    def renders_flash(self) -> ZXColour:
        return self._screen.RendersFlash

    def get_pixel_colour_screenshot(
        self,
    ) -> np.ndarray[typing.Any, np.dtype[np.float64]]:
        screenshot = self._screen.Image
        pixel_colours = bytes(screenshot.ToPixelColourBytes())
        image_array = np.frombuffer(pixel_colours, dtype=np.uint8)
        return image_array.reshape((screenshot.Height, screenshot.Width))  # Rows first, then columns. 192 arrays, each containing an array of 256 elements.

    def get_rgb_screenshot(self) -> np.ndarray[typing.Any, np.dtype[np.float64]]:
        screenshot = self._screen.Image
        rgb = bytes(screenshot.ToRgb24())
        image_array = np.frombuffer(rgb, dtype=np.uint8)
        return image_array.reshape((screenshot.Height, screenshot.Width, 3))
