class KawaSecrets:

    def __init__(self, secrets: dict):
        self.__secrets: dict = secrets

    def get(self, key: str) -> str:
        if key not in self.__secrets:
            raise Exception(f'Secret with name {key} could not be found in Kawa. '
                            f'Please configure it in the secret section')
        return self.__secrets.get(key)
