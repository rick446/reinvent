import os
import glob
import logging
import logging.config
from itertools import groupby
from datetime import datetime
from collections import defaultdict

import yaml
import markdown
from docopt import docopt
from webhelpers import html, text, date

import kajiki

log = None

extensions = ['meta', 'extra']

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

    # First, gather the posts
    posts = []
    for fn_post in glob.glob('posts/*.md'):
        slug = os.path.basename(fn_post).rsplit('.', 1)[0]
        md = markdown.Markdown(extensions=extensions)
        md_pre = markdown.Markdown(extensions=extensions)
        with open(fn_post) as fp:
            md_content = fp.read()
            html_content = md.convert(md_content)
            html_preview = md_pre.convert(
                text.truncate(md_content, 300, whole_word=True))
        post_data = dict(
            fn=fn_post,
            slug=slug,
            path='posts/{}.html'.format(slug),
            title=md.Meta['title'][0],
            md_content=md_content,
            html_content=html_content,
            html_preview=html_preview,
            meta=md.Meta,
            date=datetime.strptime(md.Meta['date'][0], '%Y-%m-%d'))
        if eval(md.Meta['published'][0]):
            posts.append(Object.ify(post_data))

    posts.sort(key=lambda p: p.date, reverse=True)
    archive = make_archive(posts)

    # Generate post html
    for post in posts:
        render_page(
            config,
            fn_out='public/posts/{}.html'.format(post.slug),
            fn_template='post.html',
            page_id='blog',
            archive=archive,
            **post)

    # Generate archive pages
    for month_data in archive:
        render_page(
            config,
            fn_template='archive.html',
            page_id='blog',
            archive=archive,
            **month_data)

    # Generate other pages
    for slug, pg in config['pages'].items():
        if 'content' in pg:
            with open(pg['content']) as fp:
                md_content = fp.read()
                html_content = markdown.markdown(md_content)
        else:
            html_content = ''
        render_page(
            config,
            fn_out='public/{}.html'.format(slug),
            fn_template=pg.get('template', 'page.html'),
            html_content=html_content,
            title=pg['title'],
            page=pg,
            page_id=slug,
            posts=posts,
            archive=archive)

def render_page(config, fn_out, fn_template, **kwargs):
    log.info('Render %s', fn_out)
    if 'path' in kwargs:
        path = kwargs.pop('path')
    else:
        path = '/' + '/'.join(fn_out.split('/')[1:])
    Template = loader.import_(fn_template)
    with open(fn_out, 'w') as fp:
        context = dict(
            path=path,
            h=helpers,
            blog=config['blog'],
            **kwargs)
        context = Object.ify(context)
        for chunk in Template(context):
            fp.write(chunk)
    return context

def make_archive(posts):
    '''Group posts by month, generating archive data'''
    posts_by_month = defaultdict(list)
    for post in posts:
        dt = post.date
        posts_by_month[dt.replace(day=1)].append(post)

    archive = []
    for month, month_posts in sorted(posts_by_month.items(), reverse=True):
        path='archive-{:%Y-%m}.html'.format(month)
        fn_out = 'public/' + path
        s_month = '{:%B %Y}'.format(month)
        archive_data = Object.ify(dict(
            s_month=s_month,
            title=s_month + ' Archive',
            month=month,
            fn_out=fn_out,
            path=path,
            posts=month_posts,
            count=len(month_posts)))
        archive.append(archive_data)
    return archive

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


