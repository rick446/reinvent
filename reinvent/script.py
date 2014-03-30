import os
import glob
import logging
import logging.config

import yaml
import markdown
from docopt import docopt
from webhelpers import html, text, date

import kajiki

log = None

loader = kajiki.FileLoader('templates', autoescape_text=True)
helpers = dict(
    html=html,
    text=text,
    date=date)

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
    posts = []
    for fn_content in glob.glob('posts/*.md'):
        slug = os.path.basename(fn_content).rsplit('.', 1)[0]
        entry = render_page(
            config,
            fn_out='public/posts/{}.html'.format(slug),
            fn_template='post.html',
            fn_content=fn_content,
            blog=config['blog'],
            h=helpers)
        posts.append(Object.ify(entry))
    posts.sort(key=lambda p: p.meta.date, reverse=True)
    for slug, pg in config['pages'].items():
        render_page(
            config,
            fn_out='public/{}.html'.format(slug),
            fn_template=pg.get('template', 'page.html'),
            fn_content=pg.get('content', None),
            page=pg,
            blog=config['blog'],
            h=helpers,
            posts=posts)

def render_page(config, fn_out, fn_template, fn_content, **kwargs):
    path = '/' + '/'.join(fn_out.split('/')[1:])
    md = markdown.Markdown(extensions=['meta'])
    md_pre = markdown.Markdown(extensions=['meta'])
    Template = loader.import_(fn_template)
    if fn_content is not None:
        with open(fn_content) as fp:
            md_content = fp.read()
        content = md.convert(md_content)
        preview = md_pre.convert(text.truncate(md_content, 300, whole_word=True))
    else:
        content = preview = ''
    with open(fn_out, 'w') as fp:
        context = dict(
            path=path, content=content, preview=preview, **kwargs)
        if hasattr(md, 'Meta'):
            context['meta'] = md.Meta
        for chunk in Template(Object.ify(context)):
            fp.write(chunk)
    return context

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


