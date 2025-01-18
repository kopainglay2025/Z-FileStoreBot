from bot.config import config

def get_web_link(link):
    if config.WEBSITE_URL_MODE:
        if "start=" in link:
            link_part = link.split("start=")[-1]
            short_url = f"{config.WEBSITE_URL}?link={link_part}"
            return short_url
        else:
            return link