"""
Substituion cipher solver, by outsourcing to https://quipqiup.com/.

The gist of this code is ripped from 
https://github.com/rallip/substituteBreaker. The unit takes the target, and
if it does not look English text but it is clearly printable characters, it
offers it to quipqiup online. 


.. note::

    This unit **does not recurse**. It simply looks for flags in the output of
    quipqiup's best potential solution. Note that Katana might find flags
    that are not in the specific flag format, but also denoted in a 
    "the flag is:" structure.

"""


import json  # json is used for communicating with quipqiup.com
import requests
import io
from typing import Any

from katana.unit import NotEnglishAndPrintableUnit, NotApplicable
from katana.units.crypto import CryptoUnit


def decodeSubstitute(cipher: str, time=3, spaces=True) -> str:
    """
    This is stolen from https://github.com/rallip/substituteBreaker
    All it does is use the ``requests`` module to send the ciphertext to
    quipqiup and returns the results as a string.
    """
    url = "https://6n9n93nlr5.execute-api.us-east-1.amazonaws.com/prod/solve"
    clues = ""
    data = {"ciphertext": cipher, "clues": clues, "solve-spaces": spaces, "time": time}
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
    }

    return requests.post(url, data=json.dumps(data), headers=headers).text


class Unit(NotEnglishAndPrintableUnit, CryptoUnit):

    # Fill in your groups
    GROUPS = ["crypto"]
    BLOCKED_GROUPS = ["crypto"]
    # Default priority is 50
    PRIORITY = 60
    # Do not recurse into self
    RECURSE_SELF = False

    # Inheriting from a CryptoUnit will ensure this will not run on URLs
    # or files that could be anything useful (image, document, audio, etc.)

    def __init__(self, *args, **kwargs):
        super(Unit, self).__init__(*args, **kwargs)
        try:
            self.raw_target = self.target.stream.read().decode("utf-8")
        except UnicodeDecodeError:
            raise units.NotApplicable("unicode error, unlikely usable cryptogram")

        try:
            requests.get(
                "https://6n9n93nlr5.execute-api.us-east-1.amazonaws.com/prod/solve"
            )
        except requests.exceptions.ConnectionError:
            raise units.NotApplicable("cannot reach quipqiup solver")

    def evaluate(self, case: Any) -> None:
        """
        Evaluate the target.
        :param case: A case returned by evaluate
        :return: None
        """

        with io.TextIOWrapper(self.target.stream, encoding="utf-8") as stream:

            j = json.loads(decodeSubstitute(stream.read()))

            found_solution = ""
            best_score = -10
            for sol in j["solutions"]:
                if sol["logp"] > best_score:
                    found_solution = sol["plaintext"]
                    best_score = sol["logp"]

            self.manager.register_data(self, found_solution)
