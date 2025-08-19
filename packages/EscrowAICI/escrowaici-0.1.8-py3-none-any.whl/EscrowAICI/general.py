import requests
import json
from EscrowAICI.utils import generate_frontoffice_url


def upload_wkey(env, project, org, file, ao, token):
    baseUrl = generate_frontoffice_url(environment=env)
    if ao:
        response = requests.post(
            f"{baseUrl}/composite/wrapped-content-encryption-key/",
            headers={"Authorization": "Bearer " + token, "User-Agent": "curl/7.71.1"},
            data=dict(
                key=json.dumps(
                    '{"name": "AO WCEK","description":"AO WCEK","project": "'
                    + project
                    + '","organization": "'
                    + org
                    + '","is_ds_wcek": false,"is_ao_wcek": true}'
                ),
                description="",
                version_tag="v1.0",
            ),
            files=[("file_name", (file, open(file, "rb")))],
        )
    else:
        response = requests.post(
            f"{baseUrl}/composite/wrapped-content-encryption-key/",
            headers={"Authorization": "Bearer " + token, "User-Agent": "curl/7.71.1"},
            data=dict(
                key=json.dumps(
                    '{"name": "DS WCEK","description":"DS WCEK","project": "'
                    + project
                    + '","organization": "'
                    + org
                    + '","is_ds_wcek": true,"is_ao_wcek": false}'
                ),
                description="",
                version_tag="v1.0",
            ),
            files=[("file_name", (file, open(file, "rb")))],
        )

    return response


def upload_wkey_version(env, project, version, ao, file, token):
    baseUrl = generate_frontoffice_url(environment=env)
    keys = find_keys(env, project, ao, token)
    wkey = keys[0]
    kek = keys[1]

    response = requests.post(
        f"{baseUrl}/wrapped-content-encryption-key-version/",
        headers={"Authorization": "Bearer " + token},
        data={
            "description": "x",
            "version_tag": version,
            "key": wkey,
            "kek_version": kek,
        },
        files=[("file_name", (file, open(file, "rb")))],
    )

    return response


def upload_artifact(env, type, project, file, token):
    baseUrl = generate_frontoffice_url(environment=env)
    if type == "spec":
        name = "Data Specification"
        if env == "dev":
            artifact_type = "c64d8b24-6019-4442-be33-b11e451d2e78"
        elif env == "tst":
            artifact_type = "b5b66d09-3700-4fe0-951d-7b867cc66581"
        elif env == "stg":
            artifact_type = "abbb939c-04e3-4e1d-a661-4fe43bbb68ee"
        else:
            pass
        file_type = "application/pdf"
    elif type == "attest":
        name = "Data Attestation"
        if env == "dev":
            artifact_type = "24056eb6-623f-48db-9d96-6e64a696fb5a"
        elif env == "tst":
            artifact_type = "d8edf5e2-efee-4774-9b92-ca76bff5bd84"
        elif env == "stg":
            artifact_type = "221bd3fe-5f6f-4c40-9ede-e84f16dca256"
        else:
            pass
        file_type = "application/pdf"
    elif type == "valid":
        name = "Validation Criteria"
        if env == "dev":
            artifact_type = "4f3ab0b3-0ded-4362-898e-4741d8855972"
        elif env == "tst":
            artifact_type = "80f7e01f-cad1-47d6-ae93-e9bbe4eee6aa"
        elif env == "stg":
            artifact_type = "62e04315-1a81-4e7a-b604-bd5737b9dff7"
        else:
            pass
        file_type = "application/json"
    else:
        return

    response = requests.post(
        f"{baseUrl}/composite/artifact/",
        headers={"Authorization": "Bearer " + token, "User-Agent": "curl/7.71.1"},
        data={
            "artifact": json.dumps(
                '{"name": "'
                + name
                + '", "artifact_type": "'
                + artifact_type
                + '", "project": "'
                + project
                + '", "description": "x"}'
            ),
            "description": "",
            "version_tag": "v1",
        },
        files=[("file_name", (file, open(file, "rb"), file_type))],
    )

    return response


def upload_artifact_version(env, type, project, version, file, token):
    baseUrl = generate_frontoffice_url(environment=env)
    if type == "spec":
        name = "Data Specification"
        file_type = "application/pdf"
    elif type == "attest":
        name = "Data Attestation"
        file_type = "application/pdf"
    elif type == "valid":
        name = "Validation Criteria"
        file_type = "application/json"
    else:
        return

    artifact_get = requests.get(
        f"{baseUrl}/artifact/",
        headers={
            "Content-type": "application/json",
            "Authorization": "Bearer " + token,
            "User-Agent": "curl/7.71.1",
        },
    )

    ajs = artifact_get.json()
    for i in ajs:
        if i["project"] is not None:
            if project == i["project"]["id"] and name in i["name"]:
                artifact_id = i["id"]

    response = requests.post(
        f"{baseUrl}/artifact-version/",
        headers={"Authorization": "Bearer " + token, "User-Agent": "curl/7.71.1"},
        data={
            "name": name,
            "version_tag": version,
            "description": "",
            "version_description": "",
            "artifact": artifact_id,
        },
        files=[
            ("file_name", (file, open(file, "rb"), file_type)),
            ("file_upload", (file, open(file, "rb"), file_type)),
        ],
    )

    return response


def download_kek(env, project, org, filename, token):
    key_string = find_kek_version(env, project, org, token)
    with open(filename, "w") as file:
        file.write(key_string)


def find_keys(env, project, ao, token):
    baseUrl = generate_frontoffice_url(environment=env)
    if ao:
        wkey_get = requests.get(
            f"{baseUrl}/wrapped-content-encryption-key/?project_id={project}&is_ao_wcek={ao}",
            headers={
                "Content-type": "application/json",
                "Authorization": "Bearer " + token,
                "User-Agent": "curl/7.71.1",
            },
        )
    else:
        wkey_get = requests.get(
            f"{baseUrl}/wrapped-content-encryption-key/?project_id={project}",
            headers={
                "Content-type": "application/json",
                "Authorization": "Bearer " + token,
                "User-Agent": "curl/7.71.1",
            },
        )

    wjs = wkey_get.json()

    for i in wjs:
        if i["project"]["id"] == project and i["is_ao_wcek"] == ao:
            wkey_id = i["id"]
            break

    wkey_version_get = requests.get(
        f"{baseUrl}/wrapped-content-encryption-key-version/",
        headers={
            "Content-type": "application/json",
            "Authorization": "Bearer " + token,
            "User-Agent": "curl/7.71.1",
        },
    )

    wvjs = wkey_version_get.json()

    for i in wvjs:
        if i["key"] == wkey_id:
            kek = i["kek_version"]["id"]
            wkey_v = i["id"]
            break

    return wkey_id, kek, wkey_v


def find_kek_version(env, project, org, token):
    baseUrl = generate_frontoffice_url(environment=env)
    response = requests.get(
        f"{baseUrl}/key-encryption-key/",
        headers={
            "Content-type": "application/json",
            "Authorization": "Bearer " + token,
            "User-Agent": "curl/7.71.1",
        },
    )

    kek = ""
    for i in response.json():
        if i["project"] is not None:
            if i["project"]["id"] == project and i["organization"] == org:
                kek = i["id"]

    response = requests.get(
        f"{baseUrl}/key-encryption-key-version/",
        headers={
            "Content-type": "application/json",
            "Authorization": "Bearer " + token,
            "User-Agent": "curl/7.71.1",
        },
    )

    for i in response.json():
        if i["key_encyption_key"] == kek:
            return i["file_content"]


def find_algo_ds_versions(env, project, algo_version, ds_version, token):
    baseUrl = generate_frontoffice_url(environment=env)
    algo_version_get = requests.get(
        f"{baseUrl}/algorithm-version/",
        headers={
            "Content-type": "application/json",
            "Authorization": "Bearer " + token,
            "User-Agent": "curl/7.71.1",
        },
    )

    avjs = algo_version_get.json()

    a_version = None
    for i in avjs:
        if i["algorithm"]["project"] is not None:
            if (
                i["version_tag"] == algo_version
                and project == i["algorithm"]["project"]["id"]
            ):
                a_version = i["id"]

    ds_version_get = requests.get(
        f"{baseUrl}/dataset-version/",
        headers={
            "Content-type": "application/json",
            "Authorization": "Bearer " + token,
            "User-Agent": "curl/7.71.1",
        },
    )

    dvjs = ds_version_get.json()

    d_version = None
    for i in dvjs:
        if i["dataset"]["project"] is not None:
            if (
                project == i["dataset"]["project"]["id"]
                and i["version_tag"] == ds_version
            ):
                d_version = i["id"]

    return a_version, d_version


def find_run_config(env, project, algo_version, ds_version, token):
    baseUrl = generate_frontoffice_url(environment=env)
    versions = find_algo_ds_versions(env, project, algo_version, ds_version, token)
    response = requests.get(
        f"{baseUrl}/run-configuration/?project_id={project}",
        headers={"Authorization": "Bearer " + token, "User-Agent": "curl/7.71.1"},
    )

    for i in response.json():
        if i is not None:
            if i["dataset_version"] is not None and i["algorithm_version"] is not None:
                if (
                    i["dataset_version"]["id"] == versions[1]
                    and i["algorithm_version"]["id"] == versions[0]
                ):
                    if i["run_requested"] is True:
                        return i["id"]

    return ""
