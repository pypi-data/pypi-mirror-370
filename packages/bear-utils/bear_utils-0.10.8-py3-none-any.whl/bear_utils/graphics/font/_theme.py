from bear_utils.constants._meta import RichStrEnum, StrValue as Value


class CyberTheme(RichStrEnum):
    """Namespace for cyberpunk color theme constants."""

    primary = Value("bright_magenta", "Primary color")
    neon_green = Value("bright_green", "Neon green color")
    neon_cyan = Value("bright_cyan", "Neon cyan color")
    warning = Value("bright_yellow", "Warning color")
    error = Value("bright_red", "Error color")
    credits = Value("bright_yellow", "Credits color")
    data = Value("bright_blue", "Data color")
    system = Value("dim white", "System color")


class FontStyle(RichStrEnum):
    """Enumeration for block font styles."""

    SOLID = Value("solid", "█")
    HOLLOW = Value("hollow", "░")
    PIPES = Value("pipes", "|")
    OUTLINE = Value("outline", "■")
    DASHED = Value("dashed", "─")
    DOTTED = Value("dotted", "·")
    ZIGZAG = Value("zigzag", "╱")  # noqa: RUF001
    CROSSED = Value("crossed", "╳")  # noqa: RUF001
    FANCY = Value("fancy", "◆")
    RIGHT_ARROWS = Value("right_arrows", "▶")
    LEFT_ARROWS = Value("left_arrows", "◀")
    STARS = Value("stars", "★")
