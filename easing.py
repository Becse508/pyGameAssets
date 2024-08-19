import math


def linear(t):
    return t

def SineIn(t):
    return -math.cos(t * math.pi / 2) + 1

def SineOut(t):
    return math.sin(t * math.pi / 2)

def SineInOut(t):
    return -(math.cos(math.pi * t) - 1) / 2

def QuadIn(t):
    return t * t

def QuadOut(t):
    return -t * (t - 2)

def QuadInOut(t):
    t *= 2
    if t < 1:
        return t * t / 2
    else:
        t -= 1
        return -(t * (t - 2) - 1) / 2

def CubicIn(t):
    return t * t * t

def CubicOut(t):
    t -= 1
    return t * t * t + 1

def CubicInOut(t):
    t *= 2
    if t < 1:
        return t * t * t / 2
    else:
        t -= 2
        return (t * t * t + 2) / 2

def QuartIn(t):
    return t * t * t * t

def QuartOut(t):
    t -= 1
    return -(t * t * t * t - 1)

def QuartInOut(t):
    t *= 2
    if t < 1:
        return t * t * t * t / 2
    else:
        t -= 2
        return -(t * t * t * t - 2) / 2

def QuintIn(t):
    return t * t * t * t * t

def QuintOut(t):
    t -= 1
    return t * t * t * t * t + 1

def QuintInOut(t):
    t *= 2
    if t < 1:
        return t * t * t * t * t / 2
    else:
        t -= 2
        return (t * t * t * t * t + 2) / 2

def ExpoIn(t):
    return math.pow(2, 10 * (t - 1))

def ExpoOut(t):
    return -math.pow(2, -10 * t) + 1

# FIXME: too large walues
def ExpoInOut(t):
    t *= 2
    if t < 1:
        return math.pow(2, 10 * (t - 1)) / 2
    else:
        t -= 1
        return -math.pow(2, -10 * t) - 1

# FIXME: math domain error
def CircIn(t):
    return 1 - math.sqrt(1 - t * t)

def CircOut(t):
    t -= 1
    return math.sqrt(1 - t * t)

def CircInOut(t):
    t *= 2
    if t < 1:
        return -(math.sqrt(1 - t * t) - 1) / 2
    else:
        t -= 2
        return (math.sqrt(1 - t * t) + 1) / 2
    



EASING_FUNCTIONS = {
    "linear": linear,
    "cubic_in": CubicIn,
    "cubic_out": CubicOut,
    "cubic_in_out": CubicInOut,
    "quadric_in": QuadIn,
    "quadric_out": QuadOut,
    "quadric_in_out": QuadInOut,
    "cubic_in": CubicIn,
    "cubic_out": CubicOut,
    "cubic_in_out": CubicInOut,
    "sine_in": SineIn,
    "sine_out": SineOut,
    "sine_in_out": SineInOut,
    "exponential_in": ExpoIn,
    "exponential_out": ExpoOut,
    "exponential_in_out": ExpoInOut,
    "circular_in": CircIn,
    "circular_out": CircOut,
    "circular_in_out": CircInOut,
    "quartic_in": QuartIn,
    "quartic_out": QuartOut,
    "quartic_in_out": QuartInOut,
    "quintic_in": QuintIn,
    "quintic_out": QuintOut,
    "quintic_in_out": QuintInOut,
}
