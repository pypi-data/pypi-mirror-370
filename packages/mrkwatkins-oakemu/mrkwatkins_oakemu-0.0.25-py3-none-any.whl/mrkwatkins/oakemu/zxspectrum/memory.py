from MrKWatkins.OakEmu import Memory as DotNetZXSpectrumMemory  # noqa
from MrKWatkins.OakEmu import BinarySerializer as DotNetBinarySerializer  # noqa


class Memory:
    def __init__(self, memory: DotNetZXSpectrumMemory):
        self._memory = memory

    def __getitem__(self, index):
        if index < 0 or index > 65535:
            raise IndexError(f"index {index} is not in the range 0 - 65535")

        return self._memory.ReadByte(index)

    def __setitem__(self, index, value):
        if index < 0 or index > 65535:
            raise IndexError(f"Index {index} is not in the range 0 - 65535")
        if value < 0 or value > 255:
            raise OverflowError(f"value {value} is not in the range 0 - 255")

        self._memory.SetByte(index, value)

    def __getstate__(self):
        state = {
            "_memory": bytes(DotNetBinarySerializer.Serialize(self._memory)),
        }
        return state

    def __setstate__(self, state):
        self._memory = DotNetBinarySerializer.Deserialize[DotNetZXSpectrumMemory](state["_memory"])
