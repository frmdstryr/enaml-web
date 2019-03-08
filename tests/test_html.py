import enaml
import pytest
import inspect
from textwrap import dedent
from utils import compile_source
from web.core.app import WebApplication


@pytest.fixture
def app():
    app = WebApplication.instance() or WebApplication()
    yield app


def test_hello_world(app):
    Page = compile_source(dedent("""
    from web.components.api import *

    enamldef Page(Html):
        Head:
            Title:
                text = "Hello world!"
        Body:
            H1:
                text = "Hello world!"
    """), 'Page')
    view = Page()
    assert view.render()


@pytest.mark.parametrize('tag, attr, query', (
    ('Div', 'cls = "right"', '//div[@class="right"]'),
    ('Div', 'cls = ["btn", "btn-large"]', '//div[@class="btn btn-large"]'),
    ('Span', 'style = "float: left;"', '//span[@style="float: left;"]'),
    ('Span', 'style = {"background": "#fff", "color": "blue"}',
        '//span[@style="background:#fff;color:blue"]'),
    ('Li', 'clickable = True', '//li[@clickable="clickable"]'),
    ('Li', 'draggable = True', '//li[@draggable="true"]'),
    ('Img', 'id = "logo"', '//img[@id="logo"]'),

    # Use attrs for special or non-python html attributes
    ('Div', 'attrs = {"data-tooltip":"Tooltip"}',
        '//div[@data-tooltip="Tooltip"]'),

    # Tail adds after the tag
    ('A', 'tail = "for more info"', '//body[text()="for more info"]'),
))
def test_html(app, tag, attr, query):
    Page = compile_source(dedent("""
    from web.components.api import *

    enamldef Page(Html):
        Body:
            {tag}:
                {attr}
            Div:
                pass
    """.format(tag=tag, attr=attr)), 'Page')
    view = Page()
    print(view.render())
    assert len(view.proxy.widget.xpath(query)) == 1


@pytest.mark.parametrize('tag, attr, default, change, query', (
    ('A', 'href', '"#"', '/home/', '//a[@href="/home/"]'),
    ('Blockquote', 'cite', '"1"', '2', '//blockquote[@cite="2"]'),
    ('Img', 'width', '"100px"', '100%', '//img[@width="100%"]'),
    ('Link', 'rel', '"text/css"', 'favicon', '//link[@rel="favicon"]'),
    ('Map', 'name', '"a"', 'b', '//map[@name="b"]'),
    ('Area', 'shape', '"square"', 'round', '//area[@shape="round"]'),
    ('Td', 'colspan', '"1"', '2', '//td[@colspan="2"]'),
    ('Th', 'colspan', '"1"', '2', '//th[@colspan="2"]'),
    ('Ol', 'type', '"A"', 'a', '//ol[@type="a"]'),
    ('IFrame', 'target', '"a"', 'b', '//iframe[@target="b"]'),
    ('Script', 'type', '"text/css"', 'text/js', '//script[@type="text/js"]'),
    ('Meta', 'name', '"a"', 'b', '//meta[@name="b"]'),
    ('Form', 'method', '"get"', 'post', '//form[@method="post"]'),
    ('Select', 'value', '"0"', '1', '//select[@value="1"]'),
    ('Option', 'selected', 'False', 'True', '//option[@selected="selected"]'),
    ('OptGroup', 'label', '"a"', 'b', '//optgroup[@label="b"]'),
    ('Input', 'type', '"checkbox"', 'text', '//input[@type="text"]'),
    ('Textarea', 'rows', '"10"', '2', '//textarea[@rows="2"]'),
    ('Button', 'type', '"a"', 'b', '//button[@type="b"]'),
    ('Video', 'controls', '"False"', 'True', '//video[@controls="controls"]'),
    ('Source', 'type', '"a"', 'b', '//source[@type="b"]'),
))
def test_html_change(app, tag, attr, default, change, query):
    Page = compile_source(dedent("""
    from web.components.api import *

    enamldef Page(Html):
        attr v = {default}
        Body:
            {tag}:
                {attr} << v
    """.format(tag=tag, attr=attr, default=default)), 'Page')
    view = Page()
    print(view.render())
    print(view.render(v=change))
    assert len(view.proxy.widget.xpath(query)) == 1


def test_tag_proxy(app):
    # To make cov happy
    from web.components.html import ProxyTag
    proxy = ProxyTag()
    with pytest.raises(NotImplementedError):
        proxy.find("")
    with pytest.raises(NotImplementedError):
        proxy.render()


def test_looper(app):
    Page = compile_source(dedent("""
    from web.components.api import *
    from web.core.api import *

    enamldef Page(Html):
        Head:
            Title:
                text = "Hello world"
        Body:
            Ul:
                Looper:
                    iterable = range(10)
                    Li:
                        text = str(loop_item)
    """), 'Page')
    view = Page()
    print(view.render())
    assert len(view.xpath('//*/li')) == 10


def test_raw(app):
    # Test that raw content is rendered
    Page = compile_source(dedent("""
    from web.components.api import *
    from web.core.api import *

    enamldef Page(Html): view:
        attr source = ""
        Head:
            Title:
                text = "Test"
        Body:
            Raw:
                source << view.source
    """), 'Page')
    view = Page()
    print(view.render())  # Make sure empty works
    assert len(view.proxy.widget.xpath('/html/body/div')) == 1

    print(view.render(source="<p>Rendered content!</p>"))
    # Use xpath the widget directly
    assert len(view.proxy.widget.xpath('/html/body/div/p')) == 1

    print(view.render(source="<h1>Rendered content!</h1>"))
    assert len(view.proxy.widget.xpath('/html/body/div/h1')) == 1


def test_raw_proxy(app):
    # To make cov happy
    from web.components.raw import ProxyRawNode
    proxy = ProxyRawNode()
    with pytest.raises(NotImplementedError):
        proxy.set_source("")


def test_markdown(app):
    # Test that raw content is rendered
    Page = compile_source(dedent("""
    from web.components.api import *
    from web.core.api import *

    enamldef Page(Html): view:
        attr source
        Head:
            Title:
                text = "Test"
        Body:
            Markdown:
                source << view.source
    """), 'Page')
    view = Page()
    print(view.render(source="# Hello world\n"))
    # Use xpath the widget directly
    assert len(view.proxy.widget.xpath('/html/body/div/h1')) == 1

    print(view.render(source="\n- Item 1\n- Item 2\n"))
    assert len(view.proxy.widget.xpath('/html/body/div/ul/li')) == 2


def test_markdown_proxy(app):
    # To make cov happy
    from web.components.md import ProxyMarkdown
    proxy = ProxyMarkdown()
    for attr in ('safe_mode', 'output_format', 'tab_length',
                 'extensions', 'extensions_config'):
        with pytest.raises(NotImplementedError):
            getattr(proxy, 'set_%s' % attr)(None)


def test_code(app):
    # Test that raw content is rendered
    Page = compile_source(dedent("""
    from web.components.api import *
    from web.core.api import *

    enamldef Page(Html): view:
        attr source
        attr language = ""   # Guess
        attr highlight_style = "emacs"
        Head:
            Title:
                text = "Test"
        Body:
            Code:
                language << view.language
                highlight_style << view.highlight_style
                source << view.source
    """), 'Page')
    view = Page()
    print(view.render(source="function(a, b){return a+b}"))
    assert len(view.proxy.widget.xpath('/html/body/div/div/pre')) == 1

    print(view.render(source=inspect.getsource(compile_source),
                      language='python'))
    assert len(view.proxy.widget.xpath('/html/body/div/div/pre')) == 1

    print(view.render(highlight_style='colorful'))
    assert len(view.proxy.widget.xpath('/html/body/div/div/pre')) == 1



def test_code_proxy(app):
    # To make cov happy
    from web.components.code import ProxyCode
    proxy = ProxyCode()
    for attr in ('language', 'highlight_style'):
        with pytest.raises(NotImplementedError):
            getattr(proxy, 'set_%s' % attr)(None)


def test_notebook(app):
    # Test that raw content is rendered
    Page = compile_source(dedent("""
    from web.components.api import *
    from web.core.api import *

    enamldef Page(Html): view:
        attr source
        attr version = 4
        Head:
            Title:
                text = "Test"
        Body:
            Notebook:
                source << view.source
                version << view.version
    """), 'Page')
    view = Page()
    with open('tests/templates/cell-magics.ipynb') as f:
        view.render(source=f.read())

        # Old format isn't valid and raises an error
        with pytest.raises((AttributeError, KeyError)):
            view.render(version=3)


def test_notebook_proxy(app):
    # To make cov happy
    from web.components.ipynb import ProxyNotebook
    proxy = ProxyNotebook()
    with pytest.raises(NotImplementedError):
        proxy.set_version(None)
