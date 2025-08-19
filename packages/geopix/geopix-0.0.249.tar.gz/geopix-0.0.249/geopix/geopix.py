from beartype import beartype
from beartype.typing import Dict, Union


class GeoPix:
    @beartype
    def __init__(
        self,
        min_lat: Union[int, float],
        max_lat: Union[int, float],
        min_lon: Union[int, float],
        max_lon: Union[int, float],
        width: Union[int, float, None] = None,
        height: Union[int, float, None] = None,
    ) -> None:
        self.min_lat = min_lat
        self.max_lat = max_lat
        self.min_lon = min_lon
        self.max_lon = max_lon
        self.image_width = width
        self.image_height = height

    @beartype
    def get_abs_geo_points_from_rel_pixel_points(
        self, min_x_rel: Union[int, float], min_y_rel: Union[int, float]
    ) -> Dict:
        # min_lon, max_lon, max_lat, min_lat, min_x_rel, min_y_rel
        # min_x_rel and min_y_rel pixel coords are relative to the max_lat min_lon
        return {
            "lat": self.min_lat + (self.max_lat - self.min_lat) * (1 - min_y_rel),
            "lon": self.min_lon + (self.max_lon - self.min_lon) * (min_x_rel),
        }

    @beartype
    def get_abs_geo_points_from_abs_pixel_points(self, min_x: Union[int, float], min_y: Union[int, float]
    ) -> Dict:
        if self.image_width == None or self.image_height == None:
            raise Exception(
                "image_width and image_height must be set in the constructor"
            )
        return self.get_abs_geo_points_from_rel_pixel_points(min_x_rel=min_x/self.image_width, min_y_rel=min_y/self.image_height)

    def get_abs_pixel_points_from_abs_geo_points(
        self, lat: Union[int, float], lon: Union[int, float]
    ) -> Dict:
        if self.image_width == None or self.image_height == None:
            raise Exception(
                "image_width and image_height must be set in the constructor"
            )

        # min_lon, max_lon, max_lat, min_lat, lon, lat
        # x and y geo coords are in latitude, longitude
        return {
            "x": round(
                (lon - self.min_lon) / (self.max_lon - self.min_lon) * self.image_width,
                2,
            ),
            "y": round(
                (self.max_lat - lat)
                / (self.max_lat - self.min_lat)
                * self.image_height,
                2,
            ),
        }

    def get_rel_pixel_points_from_abs_geo_points(
        self, lat: Union[int, float], lon: Union[int, float]
    ) -> Dict:
        # min_lon, max_lon, max_lat, min_lat, lon, lat
        # x and y geo coords are in latitude, longitude
        return {
            "x": (lon - self.min_lon) / (self.max_lon - self.min_lon),
            "y": (self.max_lat - lat) / (self.max_lat - self.min_lat),
        }

    def get_abs_geo_box_from_rel_pixel_box(
        self,
        min_x_rel: Union[int, float],
        max_x_rel: Union[int, float],
        min_y_rel: Union[int, float],
        max_y_rel: Union[int, float],
    ) -> Dict:
        # return coords for bounding box in lon,lat format
        return {
            "min_lat": self.max_lat - (self.max_lat - self.min_lat) * max_y_rel,
            "max_lat": self.max_lat - (self.max_lat - self.min_lat) * min_y_rel,
            "min_lon": self.min_lon + (self.max_lon - self.min_lon) * min_x_rel,
            "max_lon": self.min_lon + (self.max_lon - self.min_lon) * max_x_rel,
        }

    def get_abs_geo_box_from_abs_pixel_box(
        self,
        min_x: Union[int, float],
        max_x: Union[int, float],
        min_y: Union[int, float],
        max_y: Union[int, float],
    ) -> Dict:
        if self.image_width == None or self.image_height == None:
            raise Exception(
                "image_width and image_height must be set in the constructor"
            )

        # Get the relative bbox coords used to calculate geo coords
        min_x_rel, max_x_rel, min_y_rel, max_y_rel = [
            min_x / self.image_width,
            max_x / self.image_width,
            min_y / self.image_height,
            max_y / self.image_height,
        ]

        return self.get_abs_geo_box_from_rel_pixel_box(
            min_x_rel=min_x_rel,
            max_x_rel=max_x_rel,
            min_y_rel=min_y_rel,
            max_y_rel=max_y_rel,
        )

    def get_rel_pixel_box_from_abs_geo_box(
        self,
        min_lat: Union[int, float],
        max_lat: Union[int, float],
        min_lon: Union[int, float],
        max_lon: Union[int, float],
    ) -> Dict:
        # return coords for bounding box in pixel coords for a specific image
        # as percentage of image width and height
        return {
            "min_x_rel": (min_lon - self.min_lon) / (self.max_lon - self.min_lon),
            "max_x_rel": (max_lon - self.min_lon) / (self.max_lon - self.min_lon),
            "min_y_rel": (self.max_lat - max_lat) / (self.max_lat - self.min_lat),
            "max_y_rel": (self.max_lat - min_lat) / (self.max_lat - self.min_lat),
        }

    def get_abs_pixel_box_from_abs_geo_box(
        self,
        min_lat: Union[int, float],
        max_lat: Union[int, float],
        min_lon: Union[int, float],
        max_lon: Union[int, float],
    ) -> Dict:
        if self.image_width == None or self.image_height == None:
            raise Exception(
                "image_width and image_height must be set in the constructor"
            )

        rel_pixel_box = self.get_rel_pixel_box_from_abs_geo_box(
            min_lat=min_lat,
            max_lat=max_lat,
            min_lon=min_lon,
            max_lon=max_lon,
        )

        return {
            "min_x": round(rel_pixel_box["min_x_rel"] * self.image_width, 2),
            "max_x": round(rel_pixel_box["max_x_rel"] * self.image_width, 2),
            "min_y": round(rel_pixel_box["min_y_rel"] * self.image_height, 2),
            "max_y": round(rel_pixel_box["max_y_rel"] * self.image_height, 2),
        }
