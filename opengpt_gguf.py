from typing import BinaryIO, Any
from enum import IntEnum
import struct
import numpy

class GGUFValueType(IntEnum):
    UINT8 = 0
    INT8 = 1
    UINT16 = 2
    INT16 = 3
    UINT32 = 4
    INT32 = 5
    FLOAT32 = 6
    BOOL = 7
    STRING = 8
    ARRAY = 9
    UINT64 = 10
    INT64 = 11
    FLOAT64 = 12

class GGUFParser:
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.metadata = {}
        self.tensors = {}
        self.header = {}

    def parse(self) -> dict[str, Any]:
        """Parse the GGUF file and return metadata and tensor information."""
        with open(self.file_path, "rb") as file:
            magic = file.read(4)
            if magic != b"GGUF":
                raise ValueError("Invalid GGUF file: magic number mismatch")

            version = struct.unpack("<I", file.read(4))[0]
            if version < 2:
                raise ValueError(f"Unsupported GGUF version: {version}")

            tensor_count = struct.unpack("<Q", file.read(8))[0]
            metadata_count = struct.unpack("<Q", file.read(8))[0]

            self.header = {
                "magic": magic.decode(),
                "version": version,
                "tensor_count": tensor_count,
                "metadata_count": metadata_count,
            }
            self.metadata = self._read_metadata(file, metadata_count)
            self.tensors = self._read_tensor_info(file, tensor_count)

            return {
                "header": self.header,
                "metadata": self.metadata,
                "tensors": self.tensors,
            }

    @staticmethod
    def _read_string(file: BinaryIO) -> str:
        """Read a length-prefixed string."""
        length = struct.unpack("<Q", file.read(8))[0]
        return file.read(length).decode()

    def _read_value(self, file: BinaryIO, value_type: int) -> Any:
        """Read a value based on its type."""
        if value_type == GGUFValueType.UINT8:
            return struct.unpack("<B", file.read(1))[0]
        elif value_type == GGUFValueType.INT8:
            return struct.unpack("<b", file.read(1))[0]
        elif value_type == GGUFValueType.UINT16:
            return struct.unpack("<H", file.read(2))[0]
        elif value_type == GGUFValueType.INT16:
            return struct.unpack("<h", file.read(2))[0]
        elif value_type == GGUFValueType.UINT32:
            return struct.unpack("<I", file.read(4))[0]
        elif value_type == GGUFValueType.INT32:
            return struct.unpack("<i", file.read(4))[0]
        elif value_type == GGUFValueType.FLOAT32:
            return struct.unpack("<f", file.read(4))[0]
        elif value_type == GGUFValueType.UINT64:
            return struct.unpack("<Q", file.read(8))[0]
        elif value_type == GGUFValueType.INT64:
            return struct.unpack("<q", file.read(8))[0]
        elif value_type == GGUFValueType.FLOAT64:
            return struct.unpack("<d", file.read(8))[0]
        elif value_type == GGUFValueType.BOOL:
            return struct.unpack("<?", file.read(1))[0]
        elif value_type == GGUFValueType.STRING:
            return self._read_string(file)
        elif value_type == GGUFValueType.ARRAY:
            return self._read_array(file)
        else:
            raise ValueError(f"Unknown value type: {value_type}")

    def _read_array(self, file: BinaryIO) -> list:
        """Read an array value."""
        element_type = struct.unpack("<I", file.read(4))[0]
        length = struct.unpack("<Q", file.read(8))[0]

        array: list = []
        for _ in range(length):
            array.append(self._read_value(file, element_type))

        return array

    def _read_metadata(self, file: BinaryIO, count: int) -> dict[str, Any]:
        """Read metadata key-value pairs."""
        metadata: dict = {}

        for _ in range(count):
            key: str = self._read_string(file)
            value_type = struct.unpack("<I", file.read(4))[0]
            value = self._read_value(file, value_type)
            metadata[key] = value

        return metadata

    def _read_tensor_info(self, file: BinaryIO, count: int) -> dict[str, dict[str, Any]]:
        """Read tensor information."""
        tensors: dict[str, dict[str, Any]] = {}

        for _ in range(count):
            name: str = self._read_string(file)

            n_dimensions = struct.unpack("<I", file.read(4))[0]
            dimensions: list = []
            for _ in range(n_dimensions):
                dimensions.append(struct.unpack("<Q", file.read(8))[0])

            tensor_type = struct.unpack("<I", file.read(4))[0]
            offset = struct.unpack("<Q", file.read(8))[0]

            tensors[name] = {
                "dims": dimensions,
                "type": tensor_type,
                "offset": offset,
                "size": numpy.prod(dimensions) if dimensions else 0
            }

        return tensors

    def get_tensor_data(self, tensor_name: str) -> numpy.ndarray:
        """Extract actual tensor data from the file."""
        if tensor_name not in self.tensors:
            raise ValueError(f"Tensor '{tensor_name}' not found")

        tensor_info = self.tensors[tensor_name]

        with open(self.file_path, "rb") as f:
            # Calculate data offset (after header and tensor info).
            f.seek(tensor_info["offset"])

            # Determine numpy dtype based on tensor type.
            dtype_map: dict = {
                0: numpy.float32, # F32
                1: numpy.float16, # F16
                2: numpy.int8, # Q4_0 (simplified)
            }

            dtype = dtype_map.get(tensor_info["type"], numpy.float32)

            # Read and reshape data.
            total_elements = tensor_info["size"]
            data = numpy.frombuffer(f.read(total_elements * numpy.dtype(dtype).itemsize), dtype=dtype)

            return data.reshape(tensor_info["dims"])

    def print_info(self):
        """Print a summary of the GGUF file contents."""
        print(f"GGUF File: {self.file_path}")
        print(f"Version: {self.header["version"]}")
        print(f"Tensors: {self.header["tensor_count"]}")
        print(f"Metadata entries: {self.header["metadata_count"]}")
        print("\nMetadata:")
        for key, value in self.metadata.items():
            if isinstance(value, list) and len(value) > 10:
                print(f"  {key}: [list with {len(value)} items]")
            else:
                print(f"  {key}: {value}")

        print("\nTensors:")
        for name, info in self.tensors.items():
            print(f"  {name}: {info["dims"]} (type: {info["type"]}, offset: {info["offset"]})")