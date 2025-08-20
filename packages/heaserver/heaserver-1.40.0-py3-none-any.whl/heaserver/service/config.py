import configparser

from yarl import URL

from heaserver.service.defaults import DEFAULT_PORT, DEFAULT_BASE_URL


class Configuration:
    """
    Configuration information for the service.
    """
    def __init__(self,
                 base_url: str | URL = DEFAULT_BASE_URL,
                 port: int | str = DEFAULT_PORT,
                 config_file: str | None = None,
                 config_str: str | None = None):
        """
        Initializes the configuration object.

        :param base_url: the base URL of the service. Required.
        :param port: the port the service will listen on. Required.
        :param config_file: an optional INI file with configuration data.
        :param config_str: an optional configuration INI file as a string. Parsed after any config_file.
        """
        self.__base_url = URL(base_url) if base_url else DEFAULT_BASE_URL
        self.__port = int(port) if port else DEFAULT_PORT
        self.__parsed_config = configparser.ConfigParser()
        self.__config_file = config_file
        self.__config_str = config_str
        if config_file:
            self.__parsed_config.read(config_file)
        if config_str:
            self.__parsed_config.read_string(config_str)
        self.__parsed_config.read_dict({})

    @property
    def port(self) -> int:
        """
        The port this service will listen on.
        :return: a port number.
        """
        return self.__port

    @property
    def base_url(self) -> URL:
        """
        This service's base URL.
        :return: a URL.
        """
        return self.__base_url

    @property
    def parsed_config(self) -> configparser.ConfigParser:
        """
        Any configuration information parsed from an INI file or INI string.
        :return: a configparser.ConfigParser object.
        """
        result = configparser.ConfigParser()
        result.read_dict(self.__parsed_config)
        return result

    @property
    def config_file(self) -> str | None:
        """
        The path to a config file.
        :return: the config file path string, or None.
        """
        return self.__config_file

    @property
    def config_str(self) -> str | None:
        """
        A string containing an INI file, if provided in the constructor.
        :return: a config file string, or None.
        """
        return self.__config_str
