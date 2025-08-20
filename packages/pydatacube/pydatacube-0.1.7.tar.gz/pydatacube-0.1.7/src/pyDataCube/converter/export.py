from ..cube.BaseCube import BaseCube


class QB4OLAPExport:
    def __init__(self, cube: BaseCube, filename: str) -> None:
        self.cube = cube
        self.filename = filename

    def export(self):
        self.cube._metadata.serialize(destination=self.filename)
