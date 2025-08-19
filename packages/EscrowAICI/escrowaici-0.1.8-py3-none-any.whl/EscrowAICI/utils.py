def generate_frontoffice_url(environment):
    if environment in ["prd", "prod", "production"]:
        return "https://frontoffice.escrow.beekeeperai.com"
    else:
        return f"https://frontoffice.{environment}.escrow.beekeeperai.com"


def generate_notifications_url(environment):
    if environment in ["prd", "prod", "production"]:
        return "https://notification.escrow.beekeeperai.com"
    else:
        return f"https://notification.{environment}.escrow.beekeeperai.com"
