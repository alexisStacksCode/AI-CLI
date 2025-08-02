def clamp_float(value: float, min_value: float, max_value: float) -> float:
    if value < min_value:
        return min_value
    elif value > max_value:
        return max_value
    else:
        return value

def clamp_int(value: int, min_value: int, max_value: int) -> int:
    if value < min_value:
        return min_value
    elif value > max_value:
        return max_value
    else:
        return value
