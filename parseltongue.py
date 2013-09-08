"""
parseltongue
"""

import collections
import json
import logging
import os


from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateNotFound
from markdown2 import markdown


__version__ = '0.0.1'


# Setup logging

logger = logging.getLogger('parseltongue')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


# Config

Config = collections.namedtuple(
    'Config',
    'src_path templates_path',
)

config = Config(
    src_path='_src',
    templates_path='_templates',
)


class Page(object):

    def __init__(self, src_path, template):
        self.src_path = src_path
        self.template = template
        with open(src_path, 'r') as f:
            self.body = markdown(f.read(), extras=['fenced-code-blocks'])
        self.context = dict()

    def __repr__(self):
        return "<Page %r>" % self.src_path

    @property
    def is_index(self):
        return remext(self.src_path).endswith('/index')

    @property
    def render_path(self):
        return os.path.join(
            os.getcwd(),
            remext(remsrc(self.src_path)) + '.html',
        )

    @property
    def url(self):
        url = os.path.join('/', remext(remsrc(self.src_path)))
        if self.is_index:
            return url[:-len('index')]
        else:
            return url + '.html'

    def render(self):
        # Create parent dirs
        try:
            os.makedirs(os.path.dirname(self.render_path))
        except OSError:
            pass

        # Render page
        with open(self.render_path, 'w') as f:
            f.write(self.template.render(page=self, **self.context))


def remext(s):
    return s.rsplit('.', 1)[0]


def remsrc(s):
    return s.replace(config.src_path, '').lstrip('/')


def main():
    logger.info("\nParseltongue %s", __version__)

    env = Environment(loader=FileSystemLoader(config.templates_path))

    def get_template(page_path, dir_path):
        for path in page_path, dir_path:
            template_path = remext(remsrc(path)) + '.html'
            try:
                return env.get_template(template_path)
            except TemplateNotFound:
                continue

    def get_context(path):
        context_path = remext(path) + '.json'
        try:
            with open(context_path) as f:
                return json.loads(f.read())
        except IOError:
            return dict()

    context = dict()
    nav = dict()

    logger.info('\nPages\n')

    for dir_path, _, filenames in os.walk(config.src_path):
        pages = []
        index = None

        # Update context from this level's context
        context.update(**get_context(os.path.join(dir_path, 'index')))

        # Load pages for this level
        for filename in filenames:
            if not (filename.endswith('md') or filename.endswith('markdown')):
                continue

            page_path = os.path.join(dir_path, filename)

            # Get template
            template = get_template(page_path, dir_path)
            if not template:
                logger.error("Template for %s not found.", page_path)
                exit(1)

            # Creat page instance
            page = Page(page_path, template)

            # Update with current context
            page.context.update(**context)

            if page.is_index:
                index = page
            else:
                page.context.update(get_context(page_path))
                pages.append(page)
                logger.info("%s", page_path)
                logger.info("  Context: %r", page.context)

        if index:
            index.context.update(pages=pages)
            logger.info("%s", index.src_path)
            logger.info("  Context: %r", index.context)

        # Update nav
        nav[os.path.join('/', remsrc(dir_path))] = dict(
            index=index,
            pages=pages,
        )

    logger.info('\nRender\n')

    # Render all
    for path, level in nav.iteritems():
        logger.info("%s", path)
        for page in level['pages'] + [level['index']]:
            logger.info("  %s -> %s", page.src_path, page.render_path)
            page.context.update(nav=nav)
            page.render()


if __name__ == '__main__':
    main()
