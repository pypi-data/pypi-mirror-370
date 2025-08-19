# Function that clamps a number between a minimum and maximum value
def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))
