def clamp(val, min_val, max_val):
    return max(min_val, min(val, max_val))

def lerp(a, b, t):
    return a + (b - a) * t