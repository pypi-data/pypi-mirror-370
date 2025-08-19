from beartype import beartype


@beartype
def poly_to_bbox(poly: list) -> dict:
    lats = [coord[0] for coord in poly]
    lons = [coord[1] for coord in poly]

    min_lat = min(lats)
    min_lon = min(lons)
    max_lat = max(lats)
    max_lon = max(lons)

    poly_bbox = {"top_left": (max_lat, min_lon), "bottom_right": (min_lat, max_lon)}

    return poly_bbox
