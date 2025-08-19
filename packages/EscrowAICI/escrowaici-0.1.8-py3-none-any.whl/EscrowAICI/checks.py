import requests
from EscrowAICI.utils import generate_frontoffice_url


def algo_check(env, project, token):
    baseUrl = generate_frontoffice_url(environment=env)
    get_algo = requests.get(
        f"{baseUrl}/algorithm/project/{project}/",
        headers={
            "Content-type": "application/json",
            "Authorization": "Bearer " + token,
        },
    )

    if len(get_algo.json()) == 0:
        return False, None
    else:
        return True, get_algo.json()[0]["id"]
