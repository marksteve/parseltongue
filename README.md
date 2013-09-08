# Parseltongue

Render static pages using Markdown, JSON and Jinja2


## Try it

```bash
git clone https://github.com/marksteve/parseltongue.git
cd parseltongue
python setup.py install
git checkout gh-pages
parseltongue
python -m SimpleHTTPServer
```


## How it works

Parseltongue traverses the source directory (`_src` by default) for markdown
files. Each markdown file is rendered as a page.

### Templates

A template is loaded from the templates directory (`_templates` by default) for
each page. If a template of the same name (minus the extension) isn't found,
the template for the parent is loaded. (e.g. For `_src/blog/post.md`, if
`_templates/blog/post.html` is missing then `_templates/blog.html` will be
used.)

### Context

Each page has its own context. This context is retrieved from JSON files of the
same name. (e.g. `_src/page.md` uses `_src/page.json` for context) Level
context (`index.json`) is updated while traversing the source directory. So if
you set a level context value from the source directory root, that value
will be included to the context of all other pages. Index pages (`index.md`)
also get the page listing (`pages`) for its level in its context.

## Warning

This project is still very rough. If you find something wrong or want to add
stuff, feel free to post an issue or a pull request.


## TODO

* Configuration

## License

http://marksteve.mit-license.org
