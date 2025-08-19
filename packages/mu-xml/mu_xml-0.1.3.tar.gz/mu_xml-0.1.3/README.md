# Mu-XML

Represent XML using Python data structures. This does for Python what the [Hiccup](https://github.com/weavejester/hiccup) library by James Reeves did for the Clojure language.

Warning: this library is still alpha. So expect breaking changes.


## Install

```shell
pip install mu-xml
# or
uv add mu-xml
```


## Usage

To render a Mu data structure as XML markup use the `xml` function.

```python
from mu import xml

xml(["p", "Hello, ", ["b", "World"], "!"])
```

Returns the string `<p>Hello, <b>World</b>!</p>`

Note that serializing to a string will not guarantee well-formed XML.


## Documentation

XML is a tree data structure made up of various node types such as element, attribute, or text nodes.

However, writing markup in code is tedious and error-prone. Mu allows creating markup with Python code and basic Python data structures.


### Element nodes

An element node is made up of a tag, an optional attribute dictionary and zero or more content nodes which themselves can be made up of other elements.

```python
el = ["p", {"id": 1}, "this is a paragraph."]
```

You can access the individual parts of an element node using the following accessor functions.

```python
import mu

mu.tag(el)            # "p"
mu.attrs(el)          # {"id": 1}
mu.content(el)        # ["this is a paragraph."]
mu.get_attr("id", el) # 1
```

To render this as XML markup:

```python
from mu import xml

xml(el)    # <p id="1">this is a paragraph.</p>
```

Use the provided predicate functions to inspect a node.

```python
import mu

mu.is_element(el)       # is this a valid element node?
mu.is_special_node(el)  # is this a special node? (see below)
mu.is_empty(el)         # does it have child nodes?
mu.has_attrs(el)        # does it have attributes?
```


### Special nodes

XML has a few syntactic constructs that you usually don't need. But if you do need them, you can represent them in Mu as follows.

```python
["$comment", "this is a comment"]
["$pi", "foo", "bar"]
["$cdata", "<foo>"]
["$raw", "<foo/>"]
["$text" "<foo>"]
```

These will be rendered as:

```xml
<!-- this is a comment -->
<?foo bar?>
<![CDATA[<foo>]]>
<foo/>
&lt;foo&gt;
```

Nodes with tag names that start with `$` are reserved for other applications. The `xml()` function will drop special nodes that it does not recognize.

A `$cdata` node will not escape it's content as is usual in XML and HTML. A `$raw` node is very useful for adding string content that already contains markup.

A `$comment` node will ensure that the forbidden `--` is not part of the comment text.


### Namespaces

Mu does not enforce XML rules. You can use namespaces but you have to provide the namespace declarations as is expected by [XML Namespaces](https://www.w3.org/TR/xml-names).

```python
["svg", dict(xmlns="http://www.w3.org/2000/svg"),
  ["rect", dict(width=200, height=100, x=10, y=10)]
]
```

```xml
<svg xmlns="http://www.w3.org/2000/svg">
  <rect height="100" width="200" x="10" y="10"/>
</svg>
```

The following uses explicit namespace prefixes and is semantically identical to the previous example.

```python
["svg:svg", {"xmlns:svg": "http://www.w3.org/2000/svg"},
  ["svg:rect", {"width": 200, "height": 100, "x": 10, "y": 10}]
]
```

```xml
<svg:svg xmlns:svg="http://www.w3.org/2000/svg">
  <svg:rect widht="200" height="100" x="10" y="10"/>
</svg:svg>
```


### Object nodes

Object nodes may appear in two positions inside a Mu data structure.

1) In the content position of an element node (e.g. `["p", {"class": "x"}, obj]`) or,
2) In the tag position of an element node (e.g. `[obj, {"class": "x"}, "content"]`)

Object nodes can be derived from the `mu.Node` class. See the example below.

```python
from mu import Node, xml

class UL(Node):
    def __init__(self, **attrs):
        super().__init__("ul", **attrs)

    def __call__(self, *nodes, **attrs):
        nodes = [["li", node] for node in nodes]
        return super().__call__(*nodes, **attrs)
```

Let's use this class in a Mu data structure.

```python
xml(["div", UL(), "foo"])
```

```xml
<div><ul/>foo</div>
```

Here the `UL()` object is in the content position so no information is passed to it to render a list. This may not be what you wanted to achieve.

To produce a list the object must be in the tag position of an element node.

```python
xml(["div", [UL(), {"class": ("foo", "bar")}, "item 1", "item 2", "item 3"]])
```

```xml
<div>
  <ul class="foo bar">
    <li>item 1</li>
    <li>item 2</li>
    <li>item 3</li>
  </ul>
</div>
```

You can also provide some initial content and attributes in the object node constructor.

```python
xml(["div", [UL(id=1, cls=("foo", "bar")), "item 1", "item 2", "item 3"]])
```

Note that we cannot use the reserved `class` keyword, instead use `cls` to get a `class` attribute.

```xml
<div>
  <ol class="foo bar" id="1">
    <li>item 1</li>
    <li>item 2</li>
    <li>item 3</li>
  </ol>
</div>
```


### Expand nodes

In some cases you may want to use the `mu.expand` function to only expand object nodes to a straightforward data structure.

```python
from mu import expand

expand(["div", [OL(), {"class": ("foo", "bar")}, "item 1", "item 2", "item 3"]])
```

```python
["div",
  ["ol", {"class": ("foo", "bar")},
    ["li", "item 1"],
    ["li", "item 2"],
    ["li", "item 3"]]]
```


### Serializing Python data structures

```python
mu.dumps(["a",True,3.0])
```

```python
mu.loads(['_', {'as': 'array'},
  ['_', 'a'],
  ['_', {'as': 'boolean', 'value': 'true()'}],
  ['_', {'as': 'float'}, 3.0]])
```

```python
mu.dumps(dict(a="a",b=True,c=3.0))
```

```python
mu.loads(['_', {'as': 'object'},
  ['a', 'a'],
  ['b', {'as': 'boolean', 'value': 'true()'}],
  ['c', {'as': 'float'}, 3.0]])
```

When `dumps()` encounters a Python object it will call it's `mu()` method if it exists otherwise it will not be part of the serialized result. A function object will be called and it's return value becomes part of the serialized result.


## Develop

- Install [uv](https://github.com/astral-sh/uv).
- `uv tool add ruff`
- Maybe install `Ruff` VS Code extension

Run linter.

```shell
uvx ruff check
```

Run formatter.

```shell
uvx ruff format
```


Run tests.

```shell
uv run pytest
```

Or with coverage and missing lines.

```shell
uv run pytest --cov-report term-missing --cov=mu
```


## Related work

- [weavejester/hiccup](https://github.com/weavejester/hiccup)
- [nbessi/pyhiccup](https://github.com/nbessi/pyhiccup)
- [SXML](https://en.wikipedia.org/wiki/SXML)
