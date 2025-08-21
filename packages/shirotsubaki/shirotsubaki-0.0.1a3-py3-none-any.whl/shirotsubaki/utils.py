def lighten_color(hex_color: str, ratio: float=0.5) -> str:
    """Lightens a color given in hex string and returns it as a hex string.

    Parameters:
        hex_color: A color in hex format.
        ratio: The proportion of white to mix with the original color.
               Should be between 0.0 (no change) and 1.0 (full white).
               Default is 0.5.

    Returns:
        A lightened color in hex format.

    Example:
        from shirotsubaki import utils as stutils
        color = stutils.lighten_color('#336699', ratio=0.5)  # -> '#99B2CC'
    """
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return (
        f'#{int(r + (255 - r) * ratio):02X}'
        f'{int(g + (255 - g) * ratio):02X}'
        f'{int(b + (255 - b) * ratio):02X}'
    )
