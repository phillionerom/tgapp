PUBLICATION_GROUPS = {
    "moda_group": {
        "telegram_channels": ["DonModa"],
        "instagram": True,
        "facebook": False,
        "web": True
    },
    "tech_group": {
        "telegram_channels": ["DonElectronica"],
        "instagram": True,
        "facebook": True,
        "web": False
    },
    "default": {
        "telegram_channels": ["@D_o_n_OFERTON"],
        "instagram": True,
        "facebook": False,
        "web": False
    }
}

CATEGORY_TO_GROUP = {
    "moda": "moda_group",
    "deportes": "moda_group",
    "ocio": "moda_group",
    "electronica": "tech_group",
    "smartphones": "tech_group",
}


def get_publication_targets(category: str) -> dict:
    group = CATEGORY_TO_GROUP.get(category, "default")
    return PUBLICATION_GROUPS.get(group, PUBLICATION_GROUPS["default"])