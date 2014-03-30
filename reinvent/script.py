import logging
import logging.config

import yaml
import markdown
from docopt import docopt
from webhelpers import html, date

import kajiki

log = None

loader = kajiki.FileLoader('templates', autoescape_text=True)

def remake_blog():
    global log
    args = docopt("""Usage:
        remake-blog [options]

    Options:
        -h --help                   show this help message and exit
        -c --config=CONFIG          use the given config file [default: blog.yml]
    """)
    with open(args['--config']) as fp:
        config = yaml.load(fp)
    logging.config.dictConfig(config['logging'])
    log = logging.getLogger(__name__)
    log.info('Logging configured')
    helpers = dict(
        html=html,
        date=date)
    for slug, pg in config['pages'].items():
        render_page(
            config,
            fn_out='public/{}.html'.format(slug),
            fn_template=pg.get('template', 'page.html'),
            fn_content=pg.get('content', None),
            page=pg,
            blog=config['blog'],
            h=helpers)

def render_page(config, fn_out, fn_template, fn_content, **kwargs):
    Template = loader.import_(fn_template)
    if fn_content is not None:
        with open(fn_content) as fp:
            content = markdown.markdown(fp.read())
    else:
        content = ''
    with open(fn_out, 'w') as fp:
        context = dict(content=content, **kwargs)
        for chunk in Template(Object.ify(context)):
            fp.write(chunk)

class Object(dict):

    def __getattr__(self, name):
        try:
            return self.__getitem__(name)
        except IndexError:
            raise AttributeError(name)

    @classmethod
    def ify(cls, d):
        if isinstance(d, dict):
            return Object(
                (k, Object.ify(v))
                for k, v in d.items())
        elif isinstance(d, list):
            return [Object.ify(v) for v in d]
        else:
            return d


