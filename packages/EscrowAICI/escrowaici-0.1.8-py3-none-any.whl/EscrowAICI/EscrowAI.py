import requests
import threading
from EscrowAICI.algo_owner import (
    upload_algo,
    get_algo_notification,
    get_algorithm_version_tag_default,
)
from EscrowAICI.checks import algo_check
from EscrowAICI.encryption import encrypt_algo
import os
import base64
import jwt
import datetime
from EscrowAICI.utils import generate_frontoffice_url


def threaded(func):
    def wrapper(*args, **kwargs):
        def run_and_capture():
            try:
                func(*args, **kwargs)
            except Exception as e:
                wrapper.exception = e

        thread = threading.Thread(target=run_and_capture)
        thread.start()
        thread.join()

    wrapper.exception = None
    return wrapper


class EscrowAI:
    # public variables

    user = ""
    project = ""
    org = ""
    env = ""

    # private variables

    __token = ""
    __cek = ""
    __auth_key = ""

    __auth_audience = {
        "dev": {"audience": "dev.api.beekeeperai"},
        "tst": {"audience": "testing.api.beekeeperai"},
        "stg": {"audience": "staging.api.beekeeperai"},
        "prod": {"audience": "frontoffice.beekeeperai"},
    }

    # constructor

    def __init__(
        self,
        authKey: str,
        project_id: str,
        organization_id: str,
        user=None,
        environment="prod",
    ):
        self.env = environment
        self.project = project_id
        self.org = organization_id
        self.user = user
        self.__get_auth_key(authKey)
        self.__login(self.__auth_key)
        self.get_cek()
        self.type = self.__get_type()

    # methods

    def __get_auth_key(self, b64encoded_priv_key: str):
        self.__auth_key = base64.b64decode(b64encoded_priv_key)

    def __login(self, key: str):
        # Generate JWT
        try:
            payload = {
                "iss": "EscrowAI-SDK",  # Issuer
                "exp": datetime.datetime.utcnow()
                + datetime.timedelta(minutes=5),  # Expiration
                "aud": self.__auth_audience.get(self.env).get("audience"),  # Audience
                "sub": self.project,  # Subject (project id)
                "org": self.org,
                "user": self.user,
            }

            # Sign JWT with private key
            token = jwt.encode(payload, key, algorithm="RS256")

            self.__token = token
        except Exception as e:
            raise Exception(f"Error signing jwt with auth key: {e}")

    def __get_type(self):
        baseUrl = generate_frontoffice_url(environment=self.env)
        try:
            response = requests.get(
                f"{baseUrl}/project/" + self.project + "/",
                headers={
                    "Content-type": "application/json",
                    "Authorization": "Bearer " + self.__token,
                    "User-Agent": "curl/7.71.1",
                },
            )

            if response.status_code > 299:
                raise Exception(f"Error fetching project details: {response.reason}")

            return response.json().get("project_model_type")
        except Exception as e:
            print("Error fetching project details from Escrow")
            print(e)
            raise (e)

    def __refresh_token(self):
        if len(self.__auth_key) > 1:
            self.__login(self.__auth_key)
        else:
            raise Exception("Error: Couldn't find an auth key..")

    def get_cek(self):
        encoded_key = os.environ.get("CONTENT_ENCRYPTION_KEY")
        decoded_key = base64.b64decode(encoded_key)
        self.__cek = decoded_key

    def encrypt_algo(self, directory: str, key_from_file=False, secret=""):
        if key_from_file:
            with open(secret, "rb") as read:
                key = read.read()
            encrypt_algo(directory, key)
        else:
            encrypt_algo(directory, self.__cek)

    @threaded
    def upload_algorithm(
        self,
        filename: str,
        name: str,
        algo_type="validation",
        version=None,
        description="null",
        notification=True,
        algo_description="null",
    ):
        self.__refresh_token()

        try:
            if self.type == "validation" and algo_type != self.type:
                raise Exception(
                    "Validation projects can only have validation algorithms"
                )

            exists, id = algo_check(self.env, self.project, self.__token)
            if not version:
                if exists:
                    version = get_algorithm_version_tag_default(
                        self.env, self.__token, id
                    )
                else:
                    version = "v1"

            response = upload_algo(
                env=self.env,
                project=self.project,
                name=name,
                version_description=description,
                algo_type=algo_type,
                file=filename,
                token=self.__token,
                algorithm_description=algo_description,
                algo_version_tag=version,
            )
            if response.status_code != 201:
                raise Exception(f"Error: {response.status_code} \n{response.text}")

            if notification:
                success = get_algo_notification(self.env, self.project, self.__token)
                if not success:
                    raise Exception("Algorithm upload error.")
        except Exception as e:
            print(e)
            raise (e)
