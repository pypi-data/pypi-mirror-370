from beartype import beartype
from beartype.typing import Union

degrees_per_meters = 0.00006


@beartype
def meters_to_degrees(meters: Union[float, int]) -> Union[float, int]:
    return meters * degrees_per_meters
