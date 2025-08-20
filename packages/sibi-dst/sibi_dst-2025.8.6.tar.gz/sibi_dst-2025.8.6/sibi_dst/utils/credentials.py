import os


class ConfigLoader:
    def __init__(self, prefix, keys, defaults=None):
        """
        Initialize a ConfigLoader instance.

        :param prefix: The prefix for the environment variables.
        :param keys: A list of keys to extract.
        :param defaults: A dictionary of default values if environment variables are not set.
        """
        self.prefix = prefix
        self.keys = keys
        self.defaults = defaults or {}

    def load(self):
        """
        Load the configuration from environment variables.

        :return: A dictionary of configuration values.
        """
        config = {}
        for key in self.keys:
            env_var = f"{self.prefix}_{key}"
            config[key.lower()] = os.environ.get(env_var, self.defaults.get(key.lower(), ''))
        return config


class ConfigManager:
    """
    A class to manage and load multiple configurations.
    """

    def __init__(self):
        self.configurations = {}

    def add_config(self, name, prefix, keys, defaults=None):
        """
        Add a configuration to the manager.

        :param name: The name of the configuration.
        :param prefix: The prefix for the environment variables.
        :param keys: A list of keys to extract.
        :param defaults: A dictionary of default values if environment variables are not set.
        """
        loader = ConfigLoader(prefix, keys, defaults)
        self.configurations[name] = loader.load()

    def get_config(self, name):
        """
        Get a specific configuration by name.

        :param name: The name of the configuration.
        :return: The configuration dictionary.
        """
        return self.configurations.get(name, {})
