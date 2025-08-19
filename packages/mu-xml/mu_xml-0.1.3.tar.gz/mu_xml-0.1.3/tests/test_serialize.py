from __future__ import annotations

from mu import html
from mu import sgml
from mu import xhtml
from mu import xml


class TestSerializeXml:
    def test_empty_element(self):
        assert xml(["div"]) == "<div/>"


class TestAttributeFormatting:
    def test_escaping(self):
        # escape double quotes (required with foo="bar")
        assert xml(["_", {"foo": '"hi"'}]) == '<_ foo="&quot;hi&quot;"/>'
        # note that one would expect this to be output as &apos;
        # but not a problem
        assert xml(["_", {"foo": "'hi'"}]) == '<_ foo="&#x27;hi&#x27;"/>'
        # always escape &
        assert xml(["_", {"foo": "Q&A"}]) == '<_ foo="Q&amp;A"/>'
        # always escape < and >
        assert xml(["_", {"foo": "<foo/>"}]) == '<_ foo="&lt;foo/&gt;"/>'


class TestElementTextFormatting:
    def test_escaping(self):
        pass


class TestCreateNode:
    def test_empty_element(self):
        assert xml(["foo"]) == "<foo/>"

    def test_element_with_attributes(self):
        assert xml(["foo", {"a": 10, "b": 20}]) == '<foo a="10" b="20"/>'

    def test_element_without_attributes(self):
        assert xml(["foo", {}]) == "<foo/>"

    def test_element_with_content(self):
        assert xml(["foo", "bla"]) == "<foo>bla</foo>"

    def test_element_with_content_and_attributes(self):
        assert xml(["foo", {"a": 10, "b": 20}, "bla"]) == '<foo a="10" b="20">bla</foo>'

    def test_element_seq(self):
        assert xml(["a"], ["b"], ["c"]) == "<a/><b/><c/>"


class TestDoc:
    def test_doc_with_empty_element(self):
        assert xml(["foo", ["bar"]]) == "<foo><bar/></foo>"

    def test_doc_with_text_newlines(self):
        assert (
            xml(["foo", ["bar", "foo", "\n", "bar", "\n"]])
            == "<foo><bar>foo\nbar\n</bar></foo>"
        )


class TestDocWithNamespaces:
    def test_doc_with_empty_element(self):
        assert (
            xml(["x:foo", ["y:bar", {"m:a": 10, "b": 20}]])
            == '<x:foo><y:bar b="20" m:a="10"/></x:foo>'
        )


class TestDocWithSpecialNodes:
    def test_doc_with_comments(self):
        # FIXME no -- allowed
        assert xml(["$comment", "bla&<>"]) == "<!-- bla&<> -->"

    def test_doc_with_cdata(self):
        # FIXME no ]]> allowed, could escape as ]]&gt;
        #       (in normal content already handled by always escaping >)
        assert xml(["$cdata", "bla&<>"]) == "<![CDATA[bla&<>]]>"

    def test_doc_with_processing_instruction(self):
        # FIXME no ?> allowed
        assert (
            xml(["$pi", 'xml version="1.0" encoding="UTF-8"'])
            == '<?xml version="1.0" encoding="UTF-8"?>'
        )

    def test_doc_with_invalid_special_node(self):
        assert xml(["$foo", "bla"]) == ""


class TestTagFormatting:
    # FIXME html, xhtml have particular rules re self-closing or not
    #       these elements are:
    #       area, base, br, col, command, embed, hr, img, input, keygen,
    #       link, meta, param, source, track, wbr
    def test_empty_elements(self):
        assert xml(["img"]) == "<img/>"
        assert xml(["img", {"src": "foo"}]) == '<img src="foo"/>'


# https://github.com/weavejester/hiccup/blob/master/test/hiccup/compiler_test.clj


class TestCompile:
    def test_normal_tag_with_attrs(self):
        assert xml(["p", {"id": 1}]) == '<p id="1"/>'

    def test_void_tag_with_attrs(self):
        assert xml(["br", {"id": 1}]) == '<br id="1"/>'

    def test_normal_tag_with_content(self):
        assert xml(["p", "x"]) == "<p>x</p>"

    def test_void_tag_with_content(self):
        assert xml(["br", "x"]) == "<br>x</br>"

    def test_normal_tag_without_attrs(self):
        assert xml(["p", {}]) == "<p/>"

    def test_void_tag_without_attrs(self):
        assert xml(["br", {}]) == "<br/>"
        assert xml(["br", None]) == "<br/>"


# https://github.com/weavejester/hiccup/blob/master/test/hiccup/core_test.clj


class TestTagNames:
    def test_basic_tags(self):
        assert html(["div"]) == "<div></div>"

    def test_tag_syntax_sugar(self):
        assert html(["div#foo"]) == '<div id="foo"></div>'
        assert html(["div.foo"]) == '<div class="foo"></div>'
        assert html(["div.foo", "bar", "baz"]) == '<div class="foo">barbaz</div>'
        assert (
            html(["div.foo", ["$text", "bar", "baz"]])
            == '<div class="foo">barbaz</div>'
        )
        assert html(["div.a.b"]) == '<div class="a b"></div>'
        assert html(["div.a.b.c"]) == '<div class="a b c"></div>'
        assert html(["div#foo.bar.baz"]) == '<div class="bar baz" id="foo"></div>'
        assert html(["div.bar.baz#foo"]) == '<div class="bar baz" id="foo"></div>'


class TestTagContents:
    def test_empty_tags(self):
        assert xml(["div"]) == "<div/>"
        assert html(["div"]) == "<div></div>"
        assert xml(["h1"]) == "<h1/>"
        assert xml(["script"]) == "<script/>"
        assert xml(["text"]) == "<text/>"
        assert xml(["a"]) == "<a/>"
        assert xml(["iframe"]) == "<iframe/>"
        assert xml(["title"]) == "<title/>"
        assert xml(["section"]) == "<section/>"
        assert xml(["select"]) == "<select/>"
        assert xml(["object"]) == "<object/>"
        assert xml(["video"]) == "<video/>"

    def test_void_tags(self):
        assert xml(["br"]) == "<br/>"
        assert html(["br"]) == "<br>"
        assert xml(["link"]) == "<link/>"
        assert html(["link"]) == "<link>"
        assert xml(["colgroup", {"span": 2}]) == '<colgroup span="2"/>'
        assert html(["colgroup", {"span": 2}]) == '<colgroup span="2"></colgroup>'

    def test_containing_text(self):
        assert html(["text", "Lorem Ipsum"]) == "<text>Lorem Ipsum</text>"

    def test_contents_are_concatenated(self):
        assert xml(["body", "foo", "bar"]) == "<body>foobar</body>"
        assert xml(["body", ["p"], ["br"]]) == "<body><p/><br/></body>"
        assert html(["body", ["p"], ["br"]]) == "<body><p></p><br></body>"

    def test_seqs_are_expanded(self):
        assert html(["body", "foo", "bar"]) == "<body>foobar</body>"
        assert html([["p", "a"], ["p", "b"]]) == "<p>a</p><p>b</p>"

    def test_tags_can_contain_tags(self):
        assert xml(["div", ["p"]]) == "<div><p/></div>"
        assert html(["div", ["p"]]) == "<div><p></p></div>"
        assert html(["p", ["span", ["a", "foo"]]]) == "<p><span><a>foo</a></span></p>"


class TestTagAttributes:
    def test_tag_with_blank_attribute_map(self):
        assert xml(["xml", {}]) == "<xml/>"
        assert html(["xml", {}]) == "<xml></xml>"
        assert xml(["xml", None]) == "<xml/>"
        assert html(["xml", None]) == "<xml></xml>"

    def test_tag_with_populated_attribute_map(self):
        assert xml(["xml", {"a": 123}]) == '<xml a="123"/>'
        assert xml(["xml", {"a": 1, "b": 2, "c": 3}]) == '<xml a="1" b="2" c="3"/>'
        assert xml(["img", {"id": 1}]) == '<img id="1"/>'
        assert xml(["xml", {"a": ["kw", "foo", 3]}]) == '<xml a="kw foo 3"/>'

    def test_attribute_values_are_escaped(self):
        assert xml(["div", {"id": "<>&"}]) == '<div id="&lt;&gt;&amp;"/>'

    def test_nil_attributes(self):
        assert xml(["span", {"class": None}]) == "<span/>"

    def test_resolve_attribute_conflict(self):
        pass

    def test_tag_with_vector_class(self):
        assert html(["div", {"class": ["bar"]}, "baz"]) == '<div class="bar">baz</div>'
        assert (
            html(["div.foo", {"class": ["foo", "bar"]}, "baz"])
            == '<div class="foo bar">baz</div>'
        )


class TestRenderModes:
    def test_closed_tag(self):
        assert xml(["p"], ["br"]) == "<p/><br/>"
        assert xhtml(["p"], ["br"]) == "<p></p><br />"
        assert html(["p"], ["br"]) == "<p></p><br>"
        assert sgml(["p"], ["br"]) == "<p><br>"

    def test_boolean_attributes(self):
        assert (
            xml(["input", {"type": "checkbox", "checked": True}])
            == '<input checked="checked" type="checkbox"/>'
        )
        assert (
            xml(["input", {"type": "checkbox", "checked": False}])
            == '<input type="checkbox"/>'
        )
        assert (
            sgml(["input", {"type": "checkbox", "checked": True}])
            == '<input checked type="checkbox">'
        )
        assert (
            sgml(["input", {"type": "checkbox", "checked": False}])
            == '<input type="checkbox">'
        )
