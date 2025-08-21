from typing import List, Tuple

from .base import FdaSection


class DiscSegmentationSection(FdaSection):
    def load(self) -> None:
        # Note: for some reason all coordinates in this section are in (y, x) order

        self.version = self.fs.read_ascii(32)
        self.disc_radius_left_y = self.fs.read_int()
        self.disc_radius_left_x = self.fs.read_int()
        self.disc_radius_bottom_y = self.fs.read_int()
        self.disc_radius_bottom_x = self.fs.read_int()
        self.disc_radius_right_y = self.fs.read_int()
        self.disc_radius_right_x = self.fs.read_int()
        self.disc_radius_top_y = self.fs.read_int()
        self.disc_radius_top_x = self.fs.read_int()
        self.horizontal_disc_radius = self.fs.read_double()
        self.vertical_disc_radius = self.fs.read_double()
        self.disc_projection_area = self.fs.read_double()
        self.fs.skip(8)  # Repeat of disc_projection_area??
        self.disc_volume = self.fs.read_double()
        self.cup_area = self.fs.read_double()
        self.cup_volume = self.fs.read_double()
        self.rim_area = self.fs.read_double()
        self.fs.skip(24)  # These seem to be zeroes
        self.width_projection = self.fs.read_int()
        self.height_projection = self.fs.read_int()

        self.disc_rim_point_count = self.fs.read_int()
        self.disc_rim_points: List[Tuple[float, float]] = []
        for _ in range(self.disc_rim_point_count):
            y = self.fs.read_double()
            x = self.fs.read_double()
            self.disc_rim_points.append((x, y))
        self.cup_position_point_count = self.fs.read_int()
        self.cup_position_points: List[Tuple[float, float]] = []
        for _ in range(self.cup_position_point_count):
            y = self.fs.read_double()
            x = self.fs.read_double()
            self.cup_position_points.append((x, y))
        self.project_area_offset = self.fs.read_double()
