# -*- coding: utf-8 -*-

import pytest

import xmlist

#
# XML serialization
#

def test_serialize_xml_empty_elem():
    assert xmlist.serialize_xml(['foo']) == '<foo/>'

def test_serialize_xml_sub_elem():
    assert xmlist.serialize_xml(['html', ['head'], ['body']]) == '<html><head/><body/></html>'

def test_serialize_xml_attr():
    assert xmlist.serialize_xml(['a', ('b', 'c')]) == '<a b="c"/>'

def test_serialize_xml_text():
    assert xmlist.serialize_xml(['a', 'foo']) == '<a>foo</a>'

def test_serialize_xml_int_long():
    assert xmlist.serialize_xml(['a', ['int', 0xff], ['long', 0x7fffffffffffffffff]]) \
        == '<a><int>255</int><long>2361183241434822606847</long></a>'

def test_serialize_xml_unicode():
    assert xmlist.serialize_xml(['a', u'ælbåtŕöšś']) == u'<a>ælbåtŕöšś</a>'

def test_serialize_xml_unicode_2():
    assert xmlist.serialize_xml(['spam', u'\u20ac 99']) == u'<spam>\u20ac 99</spam>'

def test_serialize_xml_br():
    assert xmlist.serialize_xml(['body', ['br']]) == '<body><br/></body>'

def test_serialize_html_br():
    assert xmlist.serialize_html(['html', ['br']]) == '<html><br></html>'

#
# HTML special cases
#

def test_serialize_html_br_nonempty():
    with pytest.raises(ValueError) as exc:
        xmlist.serialize_html(['html', ['br', 'foo']])
    assert str(exc.value) == 'br not empty'

def test_serialize_wrong():
    with pytest.raises(ValueError) as exc:
        xmlist.serialize_ex(['foo'], 'whatever')
    assert str(exc.value) == 'mode \'whatever\' not recognized'

#
# Feed Me Weird Things (tm)
#

def test_serialize_xml_procins():
    assert xmlist.serialize_xml(['spam', [xmlist.PROCINS, 'albatross', ('spanish_inquisition', 'unexpected')]]) \
        == '<spam><?albatross spanish_inquisition="unexpected"?></spam>'

def test_serialize_xml_fragment():
    assert xmlist.serialize_xml(['spam', [xmlist.FRAGMENT, ['albatross']]]) == '<spam><albatross/></spam>'

def test_serialize_xml_comment():
    assert xmlist.serialize_xml(['spam', [xmlist.COMMENT, 'foo bar <quux>']]) == '<spam><!--foo bar <quux>--></spam>'

def test_serialize_xml_cdata():
    assert xmlist.serialize_xml(['spam', [xmlist.CDATA, '<albatross/>']]) == '<spam><![CDATA[<albatross/>]]></spam>'

def test_serialize_xml_doctype():
    assert xmlist.serialize_xml([xmlist.FRAGMENT, [xmlist.DOCTYPE, 'html5'], ['html']]) == '<!DOCTYPE html>\n<html/>'

def test_serialize_xml_doctype_deprecated():
    with pytest.warns(UserWarning):
        assert xmlist.serialize_xml([xmlist.FRAGMENT, [xmlist.DOCTYPE, 'HTML 5'], ['html']]) == '<!DOCTYPE html>\n<html/>'

def test_serialize_xml_wtf_are_you_doing():
    with pytest.raises(ValueError) as exc:
        assert xmlist.serialize_xml(['wtf', [13, 'albatross']])
    assert exc.value.args[0] == '[13, \'albatross\']'

#
# XML with more whitespace
#

def test_serialize_ws_xml_elem():
    assert xmlist.serialize_ws_xml(['foo', ['bar']]) == '<foo>\n\t<bar/>\n</foo>'

def test_serialize_ws_xml_text():
    assert xmlist.serialize_ws_xml(['spam', 'albatross']) == '<spam>albatross</spam>'

def test_serialize_ws_xml_procins():
    assert xmlist.serialize_ws_xml(['foo', [xmlist.PROCINS, 'a', ('b', 'c')]]) == '<foo>\n\t<?a b="c"?>\n</foo>'

def test_serialize_ws_xml_fragment():
    assert xmlist.serialize_ws_xml(['foo', ['quux', [xmlist.FRAGMENT, ['bar']]]]) \
        == '<foo>\n\t<quux>\n\t\t<bar/>\n\t</quux>\n</foo>'

def test_serialize_ws_xml_fragment_2():
    assert xmlist.serialize_ws_xml([xmlist.FRAGMENT, ['spam', ['albatross'], ['albatross', ('inquisition', 'spanish')]]]) \
        == '<spam>\n\t<albatross/>\n\t<albatross inquisition="spanish"/>\n</spam>'

def test_serialize_ws_html_procins():
    assert xmlist.serialize_ws_html(['p', 'a', [xmlist.PROCINS, 'spam', 'albatross', 'foo', 'bar'], 'b']) \
        == '<p>\n\ta\n\t<?spam albatross foo bar?>\n\tb\n</p>'

def test_serialize_ws_html_procins_2():
    assert xmlist.serialize_ws_html([xmlist.PROCINS, 'foo', 'bar']) == '<?foo bar?>'

def test_serialize_ws_html_elem():
    assert xmlist.serialize_ws_html(['body', ['p', 'a', ['br'], 'b']]) \
        == '<body>\n\t<p>\n\t\ta\n\t\t<br>\n\t\tb\n\t</p>\n</body>'

def test_serialize_ws_html_text():
    assert xmlist.serialize_ws_html(['ul', ['li', 'item 1'], ['li', 'item 2'], ['li', 'item 3']]) \
        == '<ul>\n\t<li>item 1</li>\n\t<li>item 2</li>\n\t<li>item 3</li>\n</ul>'
