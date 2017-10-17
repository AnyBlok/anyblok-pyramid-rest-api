from anyblok.blok import Blok


class TestBlok1(Blok):

    version = '0.1.0'
    required = ['anyblok-core', 'rest_api_blok']

    @classmethod
    def import_declaration_module(cls):
        from . import model # noqa

    @classmethod
    def reload_declaration_module(cls, reload):
        from . import model # noqa
        reload(model)

    @classmethod
    def pyramid_load_config(cls, config):
        config.scan(cls.__module__ + '.views')
