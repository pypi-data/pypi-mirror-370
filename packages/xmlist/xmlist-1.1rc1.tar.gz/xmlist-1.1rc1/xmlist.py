'''Functions for generating XML/HTML'''

import warnings

class DTD(object):

    html401 = ('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN"' ' "http://www.w3.org/TR/html4/strict.dtd">')

    html401_loose = ('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"'
                     ' "http://www.w3.org/TR/html4/loose.dtd">')

    html401_frameset = ('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Frameset//EN"'
                        ' "http://www.w3.org/TR/html4/frameset.dtd">')

    html5 = ('<!DOCTYPE html>')

    xhtml10 = ('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"'
               ' "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">')

    xhtml10_loose = ('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"'
                     ' "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">')

    xhtml10_frameset = ('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Frameset//EN"'
                        ' "http://www.w3.org/TR/xhtml1/DTD/xhtml1-frameset.dtd">')

    xhtml11 = ('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"' ' "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">'),

dtd = type('DeprecatedDict', (dict, ), {'__getitem__': lambda self, k: warnings.warn('xmlist.dtd is deprecated; use xmlist.DTD instead') or dict.__getitem__(self, k)})({
    'HTML 4.01 Strict':    DTD.html401,
    'HTML 4.01 Loose':     DTD.html401_loose,
    'HTML 4.01 Frameset':  DTD.html401_frameset,
    'HTML 5':              DTD.html5,
    'XHTML 1.0 Strict':    DTD.xhtml10,
    'XHTML 1.0 Loose':     DTD.xhtml10_loose,
    'XHTML 1.0 Frameset':  DTD.xhtml10_frameset,
    'XHTML 1.1':           DTD.xhtml11
})

def PROCINS(mode, L):
    return '<?%s?>' % ' '.join(serialize_ex(n, mode) for n in L)

def PROCINC(mode, L): # pragma: no cover
    warnings.warn('xmlist.PROCINC is deprecated; use xmlist.PROCINS instead')
    return PROCINS(mode, L)

def CDATA(mode, L):
    return '<![CDATA[%s]]>' % ''.join(L)

def COMMENT(mode, L):
    return '<!--%s-->' % ''.join(L)

def FRAGMENT(mode, L):
    return ''.join(serialize_ex(n, mode) for n in L)

def DOCTYPE(mode, L):
    try:
        return getattr(DTD, L[0]) + '\n'
    except AttributeError:
        return dtd[L[0]] + '\n'


MODE_HTML = object()
MODE_XML = object()

MODE = MODE_XML

HTMLEMPTY = 'base link meta hr br embed param area col input'.split(' ')


def insert_ws(node, level=0, char='\t'):
    is_text = lambda n: isinstance(n, str) or isinstance(n, int)
    is_elem = lambda n: isinstance(n, list) and is_text(n[0])
    is_attr = lambda n: isinstance(n, tuple)
    is_frag = lambda n: isinstance(n, list) and (n[0] == FRAGMENT)
    is_procins = lambda n: isinstance(n, list) and (n[0] in [PROCINC, PROCINS])
    is_empty = lambda n: is_elem(n) and all(is_attr(ch) for ch in n[1:])
    node_no_attr = [ch for ch in node if not is_attr(ch)]
    if is_procins(node):
        return
    if is_elem(node) and len(node_no_attr) == 2 and is_text(node_no_attr[1]):
        return
    if is_frag(node):
        for n in node[1:]:
            insert_ws(n, level, char)
        return
    for i in range(len(node)-1, 0, -1):
        if not is_attr(node[i]):
            node.insert(i, '\n' + char * (level + 1))
    if not is_empty(node):
        node.append('\n' + char * level)
    for i in range(len(node)-1, 0, -1):
        if is_elem(node[i]):
            insert_ws(node[i], level + 1, char)

def serialize_xml(node):
    return serialize_ex(node, MODE_XML)

def serialize_html(node):
    return serialize_ex(node, MODE_HTML)

def serialize(node): # pragma: no cover
    warnings.warn("xmlist.serialize is deprecated, please use serialize_xml or serialize_html instead")
    return serialize_ex(node, MODE)

def serialize_ex(node, mode):
    entities = '&amp "quot <lt >gt' \
               if MODE == MODE_HTML \
               else '&amp "quot \'apos <lt >gt'

    # text node
    if isinstance(node, str):
        for r in entities.split(' '):
            node = node.replace(r[0], '&'+r[1:]+';')
        return node

    # text node
    elif isinstance(node, int):
        return str(node)

    # attribute node
    elif isinstance(node, tuple):
        return '%s="%s"' % (node[0], serialize_ex(node[1], mode))

    # element node
    if isinstance(node, list) and isinstance(node[0], str):
        name = node[0]
        nodes = [ (isinstance(n, tuple), serialize_ex(n, mode)) for n in node[1:] if n ]
        attrs = ' '.join(n for (isattr, n) in nodes if isattr)
        elems =  ''.join(n for (isattr, n) in nodes if not isattr)
        space = ' ' if attrs else ''

        if mode == MODE_HTML:
            if name in HTMLEMPTY:
                if elems:
                    raise ValueError('%s not empty' % name)
                return '<%s%s%s>' % (name, space, attrs)
            else:
                return '<%s%s%s>%s</%s>' % (name, space, attrs, elems, name)

        elif mode == MODE_XML:
            if elems:
                return '<%s%s%s>%s</%s>' % (name, space, attrs, elems, name)
            else:
                return '<%s%s%s/>' % (name, space, attrs)

        else:
            raise ValueError('mode %r not recognized' % mode)

    # some crazy other type of node like doctype, processing instruction or comment
    elif isinstance(node, list) and callable(node[0]):
        return node[0](mode, node[1:])

    # aah! wtf are you doing
    else:
        raise ValueError(repr(node))

def serialize_ws_xml(node, indent='\t'):
    return serialize_ws_ex(node, MODE_XML, indent)

def serialize_ws_html(node, indent='\t'):
    return serialize_ws_ex(node, MODE_HTML, indent)

def serialize_ws(node, indent='\t'): # pragma: no cover
    warnings.warn("xmlist.serialize_ws is deprecated, please use serialize_ws_xml or serialize_ws_html instead")
    return serialize_ws_ex(node, MODE, indent)

def serialize_ws_ex(node, mode, indent='\t'):
    insert_ws(node, char=indent)
    return serialize_ex(node, mode)
