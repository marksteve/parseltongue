"""
parseltongue
"""

from datetime import datetime
import collections
import glob
import logging
import os
import re
import time


from jinja2 import Environment, FileSystemLoader
from markdown2 import markdown


__version__ = '0.0.0'
POSTED_PAT = re.compile("<!-- posted: (\d+) -->")


# Setup logging

logger = logging.getLogger('parseltongue')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


# Config

Config = collections.namedtuple('Config',
    'posts_dir templates_dir post_template latest_count pages_count')

config = Config(
    posts_dir='_posts',
    templates_dir='_templates',
    post_template='post.html',
    latest_count=5,
    pages_count=5,
    )


# Post model

class Post(object):
    """
    The post model. Post metadata is from the file itself. Much cleaner than
    adding headers.
    """
    def __init__(self, title, body, posted, path, template):
        self.title = title
        self.body = body
        self.posted = posted
        self.path = path
        self.template = template

    @property
    def post_bn(self):
        return os.path.basename(self.path).rsplit('.', 1)[0]

    @property
    def is_draft(self):
        return self.post_bn.startswith('__')

    @property
    def is_listed(self):
        return not self.post_bn.startswith('_')

    @property
    def type(self):
        return 'post' if self.template.name == config.post_template else 'page'

    @property
    def url_path(self):
        if self.type == 'post':
            url_path = "%s/%s/%s/%s.html" % (
                self.posted.year,
                self.posted.month,
                self.posted.day,
                self.post_bn,
            )
        elif self.type == 'page':
            url_path = "%s.html" % self.post_bn
        return url_path

    @classmethod
    def load(cls, path, template):
        with open(path, 'r') as f:
            contents = f.read()
        title, body = contents.split('\n', 1)
        body = markdown(body, extras=['fenced-code-blocks'])

        match = POSTED_PAT.search(body)
        if match:
            posted_ts = int(match.group(1))
            posted = datetime.fromtimestamp(posted_ts)
        else:
            posted = datetime.now()
            with open(path, 'a') as f:
                posted_ts = int(time.mktime(posted.timetuple()))
                f.write("<!-- posted: %d -->" % posted_ts)

        return cls(title, body, posted, path, template)

    def render(self):
        # Create parent dirs
        try:
            os.makedirs(os.path.dirname(self.url_path))
        except OSError:
            pass

        # Render post
        with open(self.url_path, 'w') as f:
            f.write(self.template.render(post=self))


def load_posts(env):
    """
    Loads all posts from posts directory
    """


    post_template = env.get_template(config.post_template)
    templates = env.list_templates()
    posts = []

    for post_path in glob.glob(os.path.join(config.posts_dir, '*.md')):
        template_name = os.path.basename(post_path).rsplit('.', 1)[0] + '.html'
        template = (env.get_template(template_name) if template_name in
                    templates else post_template)
        posts.append(Post.load(post_path, template))

    logger.info("Loaded %d posts.", len(posts))

    return list(reversed(sorted(posts, key=lambda post: post.posted)))


def render_posts(env, posts):
    """
    Renders post pages (and listings later)
    """

    for post in posts:
        if post.is_draft:
            logger.info("Skipped %s", post.url_path)
            continue
        post.render()
        logger.info("Rendered %s", post.url_path)


def render_index(env, posts):
    """
    Renders index page
    """

    index_template = env.get_template('index.html')

    latest = []
    pages = []
    i = 0
    j = 0
    for post in posts:
        max_latest = i >= config.latest_count
        max_pages = j >= config.pages_count
        if post.is_listed:
            if post.type == 'post' and not max_latest:
                latest.append(post)
                i += 1
            elif post.type == 'page' and not max_pages:
                pages.append(post)
                j += 1
        if  max_latest and max_pages:
            break

    with open('index.html', 'w') as f:
        f.write(index_template.render(latest=latest, pages=pages))


def main():
    logger.info("\nParseltongue %s", __version__)

    env = Environment(loader=FileSystemLoader(config.templates_dir))

    logger.info("\nLoading posts...")
    posts = load_posts(env)

    logger.info("\nRendering posts...")
    render_posts(env, posts)

    logger.info("\nRendering index page...")
    render_index(env, posts)

    logger.info("\nDone!\n")


if __name__ == '__main__':
    main()
