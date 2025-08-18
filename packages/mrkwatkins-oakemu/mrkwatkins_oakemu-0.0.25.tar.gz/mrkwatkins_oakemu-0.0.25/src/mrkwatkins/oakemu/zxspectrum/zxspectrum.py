import typing
from enum import IntEnum
from os import PathLike
from pathlib import Path

import numpy as np
from MrKWatkins.OakAsm.IO.ZXSpectrum import ZXSpectrumFile as DotNetZXSpectrumFile  # noqa
from MrKWatkins.OakEmu import BinarySerializer as DotNetBinarySerializer  # noqa
from MrKWatkins.OakEmu.Machines.ZXSpectrum import EmulatorType as DotNetEmulatorType  # noqa
from MrKWatkins.OakEmu.Machines.ZXSpectrum import ZXSpectrum as DotNetZXSpectrum  # noqa
from MrKWatkins.OakEmu.Machines.ZXSpectrum.Screen import ScreenConverter as DotNetScreenConverter  # noqa
from MrKWatkins.OakEmu.Machines.ZXSpectrum.Screen import ScreenType as DotNetScreenType  # noqa
from System import Exception as DotNetException  # noqa
from System.IO import File  # noqa

from mrkwatkins.oakemu.zxspectrum.disposable import Disposable
from mrkwatkins.oakemu.zxspectrum.keyboard import Keyboard
from mrkwatkins.oakemu.zxspectrum.memory import Memory
from mrkwatkins.oakemu.zxspectrum.screen import Screen, ScreenType
from mrkwatkins.oakemu.zxspectrum.z80 import Z80


class EmulatorType(IntEnum):
    FAST = 0
    ACCURATE = 1


def get_spectrum(zx: DotNetZXSpectrum | None, emulator_type: EmulatorType | None, screen_type: ScreenType | None) -> DotNetZXSpectrum:
    if zx is not None:
        if not isinstance(zx, DotNetZXSpectrum):
            raise TypeError("zx is not a MrKWatkins.OakEmu.Machines.ZXSpectrum.ZXSpectrum.")
        if emulator_type is not None:
            raise ValueError("Cannot specify both zx and emulator_type.")
        if screen_type is not None:
            raise ValueError("Cannot specify both zx and screen_type.")
        return zx

    emulator_type = EmulatorType.FAST if emulator_type is None else emulator_type
    screen_type = ScreenType.ACCURATE if screen_type is None else screen_type

    return DotNetZXSpectrum.Create48k(DotNetEmulatorType(emulator_type), DotNetScreenType(screen_type))


class ZXSpectrum:
    def __init__(self, zx: DotNetZXSpectrum | None = None, emulator_type: EmulatorType | None = None, screen_type: ScreenType | None = None):
        self._zx = get_spectrum(zx, emulator_type, screen_type)
        self._cpu = Z80(self._zx.Cpu)
        self._keyboard = Keyboard(self._zx.Keyboard)
        self._memory = Memory(self._zx.Memory)
        self._screen = Screen(self._zx.Screen)

    @property
    def type(self) -> EmulatorType:
        return EmulatorType(int(self._zx.Type))

    @property
    def cpu(self) -> Z80:
        return self._cpu

    @property
    def keyboard(self) -> Keyboard:
        return self._keyboard

    @property
    def memory(self) -> Memory:
        return self._memory

    @property
    def screen(self) -> Screen:
        return self._screen

    def get_screen_memory(self) -> np.ndarray[typing.Any, np.dtype[np.float64]]:
        screen = bytes(self._zx.CopyScreenMemory())
        return np.frombuffer(screen, dtype=np.uint8)

    def execute_frame(self) -> None:
        self._zx.ExecuteFrame()

    def record_oer(self, path: PathLike) -> Disposable:
        disposable = self._zx.RecordOer(str(path))
        return Disposable(disposable)

    def record_gif(self, path: PathLike) -> Disposable:
        disposable = self._zx.Screen.RecordGif(str(path))
        return Disposable(disposable)

    def dump(self, path: str | PathLike, exception: Exception | None = None):
        dot_net_exception = exception if isinstance(exception, DotNetException) else None
        dump = self._zx.Dump(dot_net_exception)
        dump_path = str(Path(path))
        dump.SaveHtml(dump_path)

    def __getstate__(self):
        state = {
            "_zx": bytes(DotNetBinarySerializer.Serialize(self._zx)),
        }
        return state

    def __setstate__(self, state):
        self._zx = DotNetBinarySerializer.Deserialize[DotNetZXSpectrum](state["_zx"])

        self._cpu = Z80(self._zx.Cpu)
        self._keyboard = Keyboard(self._zx.Keyboard)
        self._memory = Memory(self._zx.Memory)
        self._screen = Screen(self._zx.Screen)
