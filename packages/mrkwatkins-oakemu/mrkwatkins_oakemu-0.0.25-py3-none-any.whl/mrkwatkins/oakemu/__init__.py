from os import path

from pythonnet import load

# Explicitly load all the necessary assemblies up front to help catch any errors early.
assembles = [
    "MrKWatkins.Ast",
    "MrKWatkins.OakAsm",
    "MrKWatkins.OakAsm.Disassembly",
    "MrKWatkins.OakAsm.Disassembly.Z80",
    "MrKWatkins.OakAsm.Formatting",
    "MrKWatkins.OakAsm.IO",
    "MrKWatkins.OakAsm.IO.ZXSpectrum",
    "MrKWatkins.OakAsm.Z80",
    "MrKWatkins.OakEmu",
    "MrKWatkins.OakEmu.Cpus",
    "MrKWatkins.OakEmu.Cpus.Z80",
    "MrKWatkins.OakEmu.Machines.ZXSpectrum",
]

assemblies_path = path.join(path.dirname(__file__), "assemblies")

load("coreclr")

import clr  # noqa: E402

for assembly in assembles:
    clr.AddReference(path.join(assemblies_path, assembly))  # noqa
