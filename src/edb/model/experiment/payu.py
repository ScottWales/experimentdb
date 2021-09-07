from .base import Experiment
from ..file import File
from pathlib import Path
import os


class Payu(Experiment):
    type = "payu"
    file_pattern = ["output*/ocean/*.nc", "output*/ice/OUTPUT/*.nc"]

    def identify_stream(self, file: File) -> str:
        parts = Path(file.relative_path).parts

        domain = parts[1]

        if domain == "ocean":
            return os.path.splitext(parts[-1])[0]

        if domain == "ice":
            start = parts[-1].split(".")[0]
            if parts[-1].endswith("-daily.nc"):
                return f"{start}_daily"
            else:
                return start

        raise NotImplementedError(file.relative_path)
