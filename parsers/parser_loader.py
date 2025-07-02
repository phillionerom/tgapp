from parsers.liquidaciones_parser import LiquidacionesParser
from parsers.chollometro_parser import ChollometroParser
from parsers.chollacos_parser import ChollacosParser


def get_parser_for(channel):
    # Return the right parser function for a given channel

    parsers = {
        "liquidaciones": LiquidacionesParser(),
        "chollometro": ChollometroParser(),
        "chollacos": ChollacosParser()
    }

    if channel not in parsers:
        print(f"🔴 The channel `{channel}` is not configured and does not have parser. Please check! 👀")
        return None
    
    return parsers[channel]