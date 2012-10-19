"""
parseltongue
"""

from datetime import datetime
import collections
import glob
import logging
import os


from jinja2 import Environment, FileSystemLoader
from markdown2 import markdown


__version__ = '0.0.0'


# Setup logging

logger = logging.getLogger('parseltongue')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


# Config

Config = collections.namedtuple('Config',
    'posts_dir templates_dir latest_count')

config = Config(
    posts_dir='_posts',
    templates_dir='_templates',
    latest_count=5,
    )


# Post model

class Post(collections.namedtuple('Post',
    'title body created modified published listed url')):
    """
    The post model. Post metadata is from the file itself. Much cleaner than
    adding headers.
    """

    @classmethod
    def from_file(cls, path):
        with open(path, 'r') as f:
            contents = f.readlines()
            title = contents[0].strip()
            body = markdown(''.join(contents[1:]).strip())

        post_st = os.stat(path)
        created = datetime.fromtimestamp(int(post_st.st_ctime))
        modified = datetime.fromtimestamp(int(post_st.st_mtime))

        post_bn = os.path.basename(path)
        published = not post_bn.startswith('__')
        listed = not post_bn.startswith('_')
        url = "%s/%s/%s/%s.html" % (created.year, created.month, created.day,
            post_bn.rsplit('.', 1)[0])

        return cls(title, body, created, modified, published, listed, url)


def load_posts():
    """
    Loads all posts from posts directory
    """

    if not os.path.exists(config.posts_dir):
        raise IOError("%s does not exist!", config.posts_dir)

    posts = []
    for post_path in glob.glob(os.path.join(config.posts_dir, '*.md')):
        posts.append(Post.from_file(post_path))

    logger.info("Loaded %d posts.", len(posts))

    return list(reversed(sorted(posts, key=lambda post: post.created)))


def render_posts(env, posts):
    """
    Renders post pages (and listings later)
    """

    post_template = env.get_template('post.html')

    templates = env.list_templates()

    for post in posts:
        if not post.published:
            logger.info("Skipped %s", post.url)
            continue

        post_bn = os.path.basename(post.url)

        template = (env.get_template(post_bn) if post_bn in templates else
            post_template)

        # Create parent dirs
        try:
            os.makedirs(os.path.dirname(post.url))
        except OSError:
            pass

        # Render post
        with open(post.url, 'w') as f:
            f.write(template.render(post=post))

        logger.info("Rendered %s", post.url)


def render_index(env, posts):
    """
    Renders index page
    """

    index_template = env.get_template('index.html')

    latest = []
    i = 0
    for post in posts:
        if i >= config.latest_count:
            break
        elif post.listed:
            latest.append(post)
            i += 1

    with open('index.html', 'w') as f:
        f.write(index_template.render(latest=latest))


def main():
    logger.info("\nParseltongue %s", __version__)

    env = Environment(loader=FileSystemLoader(config.templates_dir))

    logger.info("\nLoading posts...")
    posts = load_posts()

    logger.info("\nRendering posts...")
    render_posts(env, posts)

    logger.info("\nRendering index page...")
    render_index(env, posts)

    logger.info("\nDone!\n")


if __name__ == '__main__':
    main()
