
import sys
from typing import Any, Union, List
from pret.render import stub_component
from pret.marshal import js, make_stub_js_module, marshal_as

__version__ = "10.1.0"
_py_package_name = "pret-markdown"
_js_package_name = "react-markdown"
_js_global_name = "Markdown"

make_stub_js_module("Markdown", "pret-markdown", "react-markdown", __version__, __name__)

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

props_mapping = {
 "allowed_elements": "allowedElements",
 "allow_element": "allowElement",
 "disallowed_elements": "disallowedElements",
 "rehype_plugins": "rehypePlugins",
 "remark_plugins": "remarkPlugins",
 "remark_rehype_options": "remarkRehypeOptions",
 "skip_html": "skipHtml",
 "unwrap_disallowed": "unwrapDisallowed",
 "url_transform": "urlTransform"
}

@stub_component(js.Markdown.default, props_mapping)
def Markdown(*children, allowed_elements: Any, allow_element: Any, components: Any, disallowed_elements: Any, key: Union[str, int], rehype_plugins: Any, remark_plugins: Any, remark_rehype_options: Any, skip_html: Any, unwrap_disallowed: Any, url_transform: Any):
    """"""
@stub_component(js.Markdown.MarkdownHooks, props_mapping)
def MarkdownHooks(*children, allowed_elements: Any, allow_element: Any, components: Any, disallowed_elements: Any, fallback: Any, key: Union[str, int], rehype_plugins: Any, remark_plugins: Any, remark_rehype_options: Any, skip_html: Any, unwrap_disallowed: Any, url_transform: Any):
    """"""


@marshal_as(js.Markdown.defaultUrlTransform)
def default_url_transform(value: str=None):
    """"""

@marshal_as(js.Markdown.MarkdownAsync)
def markdown_async(options: Any=None):
    """"""
