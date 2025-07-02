CATEGORY_TO_CHANNELS = {
    "tecnologia": ["@ofertas_tech"],
    "moda": ["@ofertas_moda"],
    "bebe": ["@ofertas_bebe"],
    "default": ["@D_o_n_Oferton"]
}

def get_channels_for_category(category: str) -> list[str]:
    return CATEGORY_TO_CHANNELS.get(category, CATEGORY_TO_CHANNELS["default"])
