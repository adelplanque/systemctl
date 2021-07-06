from importlib import resources
import jinja2
import tempfile

from mapproxy.wsgiapp import make_wsgi_app

from ..config import config


def mapproxy_conf_file():
    cfg_file = tempfile.NamedTemporaryFile("w")
    config_mapproxy = \
        jinja2.Template(resources.read_text("myproject.config", "mapproxy.yaml")) \
              .render(config)
    print(config_mapproxy)
    cfg_file.write(config_mapproxy)
    cfg_file.flush()
    return cfg_file


with mapproxy_conf_file() as cfg_file:
    application = make_wsgi_app(cfg_file.name)
