from MrKWatkins.OakEmu.Machines.ZXSpectrum.Cpu import Z80Registers as DotNetZ80Registers  # noqa
from MrKWatkins.OakEmu import BinarySerializer as DotNetBinarySerializer  # noqa


class Registers:
    def __init__(self, registers: DotNetZ80Registers):
        if not isinstance(registers, DotNetZ80Registers):
            raise TypeError("registers is not a MrKWatkins.OakEmu.Cpus.Z80.Registers.")

        self._registers = registers

    @property
    def a(self):
        return self._registers.A

    @a.setter
    def a(self, value: int):
        self._registers.A = value

    @property
    def f(self):
        return self._registers.F

    @f.setter
    def f(self, value: int):
        self._registers.F = value

    @property
    def af(self):
        return self._registers.AF

    @af.setter
    def af(self, value: int):
        self._registers.AF = value

    @property
    def b(self):
        return self._registers.B

    @b.setter
    def b(self, value: int):
        self._registers.B = value

    @property
    def c(self):
        return self._registers.C

    @c.setter
    def c(self, value: int):
        self._registers.BC = value

    @property
    def bc(self):
        return self._registers.BC

    @bc.setter
    def bc(self, value: int):
        self._registers.BC = value

    @property
    def d(self):
        return self._registers.D

    @d.setter
    def d(self, value: int):
        self._registers.D = value

    @property
    def e(self):
        return self._registers.E

    @e.setter
    def e(self, value: int):
        self._registers.DE = value

    @property
    def de(self):
        return self._registers.DE

    @de.setter
    def de(self, value: int):
        self._registers.DE = value

    @property
    def h(self):
        return self._registers.H

    @h.setter
    def h(self, value: int):
        self._registers.H = value

    @property
    def l(self):  # noqa: E743
        return self._registers.L

    @l.setter
    def l(self, value: int):  # noqa: E743
        self._registers.L = value

    @property
    def hl(self):
        return self._registers.HL

    @hl.setter
    def hl(self, value: int):
        self._registers.HL = value

    @property
    def ixh(self):
        return self._registers.IXH

    @ixh.setter
    def ixh(self, value: int):
        self._registers.IXH = value

    @property
    def ixl(self):
        return self._registers.IXL

    @ixl.setter
    def ixl(self, value: int):
        self._registers.IXL = value

    @property
    def ix(self):
        return self._registers.IX

    @ix.setter
    def ix(self, value: int):
        self._registers.IX = value

    @property
    def iyh(self):
        return self._registers.IYH

    @iyh.setter
    def iyh(self, value: int):
        self._registers.IYH = value

    @property
    def iyl(self):
        return self._registers.IYL

    @iyl.setter
    def iyl(self, value: int):
        self._registers.IYL = value

    @property
    def iy(self):
        return self._registers.IY

    @iy.setter
    def iy(self, value: int):
        self._registers.IY = value

    @property
    def pc(self):
        return self._registers.PC

    @pc.setter
    def pc(self, value: int):
        self._registers.PC = value

    @property
    def sp(self):
        return self._registers.SP

    @sp.setter
    def sp(self, value: int):
        self._registers.SP = value
