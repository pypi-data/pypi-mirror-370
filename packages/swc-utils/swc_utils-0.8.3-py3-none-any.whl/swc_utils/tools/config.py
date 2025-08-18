import os


class Config:
    """
    A simple configuration reader that reads key-value pairs from a file.
    Should any of the keys be present as an environment variable, the value from the environment variable will be used instead.
    The file should have the following format:
    ```
    # This is a comment
    string=this is a string
    integer=123
    boolean1=true
    boolean2=True
    boolean3=1
    list=1,2,3,4
    ```
    """
    def __init__(self, config_file: str):
        """
        :param config_file: Path to the configuration file.
        """
        self.config_file = config_file
        self.env_config = os.environ
        self.__config = self.__read_config()

    def __read_config(self):
        config = {}
        with open(self.config_file, 'r', encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=')
                    config[key] = value
        return config

    def __getitem__(self, item):
        return self.get(item)

    def get(self, key: str, default: str = None) -> str:
        return self.env_config.get(key) or self.__config.get(key, default)

    def get_bool(self, key: str, default: bool = None) -> bool:
        return self.get(key, default) in ['True', 'true', '1']

    def get_list(self, key: str, default: list[str] = None) -> list[str]:
        return self.get(key, default).split(',')

    def get_int(self, key: str, default: int = None) -> int:
        return int(self.get(key, default))
