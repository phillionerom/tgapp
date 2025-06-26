from parsers import (
    liquidaciones_parser,
    chollometro_parser
)

def get_parser_for(channel):
    # Return the right parser function for a given channel
    parsers = {
        "liquidaciones": liquidaciones_parser,
        "chollometro": chollometro_parser,
    }
    return parsers[channel]