import requests
import os


class BancaRepository:
    def __init__(self) -> None:
        self.__url = os.getenv("BANCA_SERVICE_URL")
        self.__headers = {"Content-Type": "application/json"}

    def get_balance(self, token: str) -> dict:
        response = requests.post(
            f"{self.__url}/balance", headers=self.__headers, json={"token": token}
        )
        return response.json()

    def bet(self, token: str, amount: float) -> dict:
        response = requests.post(
            f"{self.__url}/bet",
            headers=self.__headers,
            json={"token": token, "amount": amount},
        )
        return response.json()

    def win(self, token: str, amount: float) -> dict:
        response = requests.post(
            f"{self.__url}/win",
            headers=self.__headers,
            json={"token": token, "amount": amount},
        )
        return response.json()

    def get_auth(self, token: str) -> dict:
        response = requests.post(
            f"{self.__url}/auth", headers=self.__headers, json={"token": token}
        )
        return response.json()
