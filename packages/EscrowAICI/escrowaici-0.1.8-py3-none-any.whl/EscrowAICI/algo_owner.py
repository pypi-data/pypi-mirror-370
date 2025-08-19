import requests
import sseclient
import json
import os
from EscrowAICI.utils import generate_frontoffice_url, generate_notifications_url


def upload_algo(
    env,
    project,
    name,
    version_description,
    algo_type,
    file,
    token,
    algorithm_description,
    algo_version_tag,
):
    try:
        baseUrl = generate_frontoffice_url(environment=env)
        data_attestation, validation_criteria = find_artifacts(
            env, project, algo_type, token
        )

        response = requests.post(
            f"{baseUrl}/api/v1/algorithm/",
            headers={
                "Authorization": f"Bearer {token}",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15",
            },
            data={
                "project_id": project,
                "name": name,
                "description": algorithm_description,
                "version_description": version_description,
                "version_tag": algo_version_tag,
                "algorithm_type": algo_type,
                "validation_criteria_version": validation_criteria,
                "data_attestation_version": data_attestation,
                "upload_type": "Upload Zip",
                "upload_file_name": os.path.basename(file),
            },
            files=[("file_name", (file, open(file, "rb")))],
        )

        return response
    except Exception as e:
        print("Error uploading Algorithm to Escrow")
        print(e)
        raise (e)


def get_algorithm_version_tag_default(env, token, algorithm_id):
    try:
        version_tag = ""
        baseUrl = generate_frontoffice_url(environment=env)
        resp = requests.get(
            f"{baseUrl}/algorithm-version/?algorithm_id={algorithm_id}",
            headers={
                "Content-type": "application/json",
                "Authorization": "Bearer " + token,
                "User-Agent": "curl/7.71.1",
            },
        )
        algorithm_versions = resp.json()
        version_number = len(algorithm_versions)
        version_tag = f"v{str(version_number + 1)}"
        return version_tag
    except Exception as e:
        print("Error uploading Algorithm to Escrow")
        print(e)
        raise (e)


def get_algo_notification(env, project, token):
    baseNotificationsUrl = generate_notifications_url(environment=env)
    client = sseclient.SSEClient(
        f"{baseNotificationsUrl}/project-notifications/{project}/?token={token}"
    )
    for event in client:
        if event.event != "stream-open" and event.event != "keep-alive":
            if event.data != "":
                data = json.loads(event.data)
                message = data.get("message")
                algorithm_version_id = data.get("data").get("algorithm_version_id")
                run_id = data.get("run_id") or data.get("run")
                run_config_id = data.get("run_configuration_id")
                if algorithm_version_id:
                    if not run_id and not run_config_id:
                        print(f"\033[1m\033[92mESCROWAI: \033[0m\033[0m{message}")
                        if message == "Docker Push Succeeded":
                            return True
                        if (
                            message == "File Validation Failed"
                            or message == "Unable to check Entrypoint file"
                            or message == "Docker Build Failed"
                        ):
                            return False


def find_artifacts(env, project, algo_type, token):
    try:
        baseUrl = generate_frontoffice_url(environment=env)
        artifact_get = requests.get(
            f"{baseUrl}/artifact/?project_id={project}",
            headers={
                "Content-type": "application/json",
                "Authorization": "Bearer " + token,
                "User-Agent": "curl/7.71.1",
            },
        )

        ajs = artifact_get.json()

        data_attestation_artifact_id = None
        validation_criteria_artifact_id = None

        for i in ajs:
            if (
                i.get("artifact_type")
                and i.get("artifact_type").get("name") == "validation_criteria"
            ):
                validation_criteria_artifact_id = i["id"]
            if (
                i.get("artifact_type")
                and i.get("artifact_type").get("name") == "data_attestation"
            ):
                data_attestation_artifact_id = i["id"]

        if not data_attestation_artifact_id:
            raise Exception("Could not find a Data Attestation artifact on the project")

        if not validation_criteria_artifact_id and algo_type == "validation":
            raise Exception(
                "Could not find a Validation Criteria artifact on the project"
            )

        artifact_v_get = requests.get(
            f"{baseUrl}/artifact-version/?artifact_id={data_attestation_artifact_id}",
            headers={
                "Content-type": "application/json",
                "Authorization": "Bearer " + token,
                "User-Agent": "curl/7.71.1",
            },
        )
        attest_id = artifact_v_get.json()[0]["version_tag"]

        valid_id = None
        if validation_criteria_artifact_id:
            artifact_v_get = requests.get(
                f"{baseUrl}/artifact-version/?artifact_id={validation_criteria_artifact_id}",
                headers={
                    "Content-type": "application/json",
                    "Authorization": "Bearer " + token,
                    "User-Agent": "curl/7.71.1",
                },
            )
            valid_id = artifact_v_get.json()[0]["version_tag"]

    except Exception as e:
        print("Error retrieving artifact versions")
        print(e)
        raise (e)

    return attest_id, valid_id
