import pathlib
import shutil
import os
import yaml
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def encrypt_algo(folder, key):
    with open(folder + "/secrets.yaml", "r") as f:
        try:
            files = yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(e)

    for f in files["secretFiles"]:
        newpaths = ["", ""]
        newpaths[0] = folder + "/" + f[0]
        newpaths[1] = folder + "/" + f[1]

        salt = os.urandom(8)
        pbkdf2_hash = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            salt=salt,
            length=32 + 12,
            iterations=10000,
        )

        derived_password = pbkdf2_hash.derive(key)
        key = derived_password[0:32]
        iv = derived_password[32 : (32 + 12)]

        # read file
        with open(newpaths[1], "rb") as encrypt:
            data = encrypt.read()

        encrypted = AESGCM(key).encrypt(iv, data, None)
        encrypted = b"Salted__" + salt + encrypted

        # write new encrypted file, delete old
        with open(newpaths[0], "wb") as write:
            write.write(encrypted)
        pathlib.Path(newpaths[1]).unlink()

    # zip folder
    shutil.make_archive(folder, "zip", folder)


def pad(s):
    while len(s) % 16 != 0:
        s = s + " "
    return s
