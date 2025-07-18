import random

def get_random_desktop_user_agent() -> str:
    platforms = [
        "Windows NT 10.0; Win64; x64",
        "Windows NT 6.1; Win64; x64",
        "Macintosh; Intel Mac OS X 10_15_7",
        "Macintosh; Intel Mac OS X 12_4",
        "X11; Linux x86_64"
    ]

    browsers = [
        {
            "name": "chrome",
            "template": "Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36",
            "versions": ["121.0.0.0", "122.0.0.0", "123.0.0.0", "124.0.0.0"]
        },
        {
            "name": "firefox",
            "template": "Mozilla/5.0 ({platform}; rv:{version}) Gecko/20100101 Firefox/{version}",
            "versions": ["110.0", "111.0", "112.0", "113.0"]
        },
        {
            "name": "safari",
            "template": "Mozilla/5.0 ({platform}) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{version} Safari/605.1.15",
            "versions": ["14.0", "14.1", "15.0"]
        },
        {
            "name": "edge",
            "template": "Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36 Edg/{version}",
            "versions": ["110.0.1587.50", "111.0.1661.41", "112.0.1722.48"]
        },
        {
            "name": "opera",
            "template": "Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36 OPR/{opr_version}",
            "versions": [
                ("121.0.0.0", "94.0.4606.76"),
                ("122.0.0.0", "95.0.4635.54"),
                ("123.0.0.0", "96.0.4664.45")
            ]
        }
    ]

    browser = random.choice(browsers)
    platform = random.choice(platforms)

    if browser["name"] == "opera":
        chrome_version, opr_version = random.choice(browser["versions"])
        return browser["template"].format(platform=platform, version=chrome_version, opr_version=opr_version)
    else:
        version = random.choice(browser["versions"])
        return browser["template"].format(platform=platform, version=version)
