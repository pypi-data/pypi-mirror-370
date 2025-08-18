from MrKWatkins.OakEmu.Machines.ZXSpectrum.Cpu import Z80 as DotNetZ80  # noqa
from MrKWatkins.OakEmu import BinarySerializer as DotNetBinarySerializer  # noqa

from mrkwatkins.oakemu.zxspectrum.registers import Registers


class Z80:
    def __init__(self, z80: DotNetZ80):
        if not isinstance(z80, DotNetZ80):
            raise TypeError("z80 is not a MrKWatkins.OakEmu.Cpus.Z80.Z80Emulator.")

        self._z80 = z80
        self._registers = Registers(self._z80.Registers)

    @property
    def registers(self):
        return self._registers
