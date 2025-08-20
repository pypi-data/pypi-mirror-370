from .base import FdaSection


class GlaucomaLittmannSection(FdaSection):
    def load(self) -> None:
        self.axial_length = self.fs.read_double()
        self.corneal_curvature_radius = self.fs.read_double()
        self.cylinder = self.fs.read_double()
        self.axis = self.fs.read_double()
        self.sphere = self.fs.read_double()
        self.iol_information = self.fs.read_int()
        self.correcting_lens_information = self.fs.read_int_signed()
        self.correcting_method = self.fs.read_int()
