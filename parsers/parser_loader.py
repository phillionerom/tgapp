from parsers.liquidaciones_parser import LiquidacionesParser
from parsers.chollometro_parser import ChollometroParser


def get_parser_for(channel):
    # Return the right parser function for a given channel
    parsers = {
        "liquidaciones": LiquidacionesParser(),
        "chollometro": ChollometroParser(),
    }
    return parsers[channel]