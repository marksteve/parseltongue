# Parseltongue

Render HTML pages using Markdown and Jinja


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

You put your posts as Markdown files in a `_posts` directory (not yet
configurable) while your Jinja templates reside in `_templates`. Posted
timestamps are automatically determined though you can add an html comment
in your Markdown file to manually specify it. If you need a different template
for a certain post, add a template file of the same filename. You can (should)
take advantage of Jinja features like expressions and template inheritance.

### Drafts and listing

You can prepend an underscore ("_") to the Markdown file's name to mark a post
as unlisted (only applies to the index page right now but will be used in
archives and navigation later). Put two undescores for drafts (not rendered).


## Warning
This project is still very rough. If you find something wrong or want to add
stuff, feel free to post an issue or a pull request.


## TODO

* Navigation
* Archives
* Categories
* Configuration

## License

http://marksteve.mit-license.org
