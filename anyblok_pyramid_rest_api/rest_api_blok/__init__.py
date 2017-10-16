"""Blok declaration example
"""
from anyblok.blok import Blok
from .pyramid_adapter import declare_json_data_adapter


class Rest_api_blok(Blok):
    """Rest_api_blok's Blok class definition
    """
    version = "0.1.0"
    required = ['anyblok-core']

    @classmethod
    def import_declaration_module(cls):
        """Python module to import in the given order at start-up
        """
        pass

    @classmethod
    def reload_declaration_module(cls, reload):
        """Python module to import while reloading server (ie when
        adding Blok at runtime
        """
        pass

    @classmethod
    def pyramid_load_config(cls, config):
        declare_json_data_adapter(config)
        config.include("cornice")
