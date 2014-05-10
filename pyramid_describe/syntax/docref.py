# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: Philip J Grabner <grabner@cadit.com>
# date: 2014/05/06
# copy: (C) Copyright 2014-EOT Cadit Inc., All Rights Reserved.
#------------------------------------------------------------------------------

import six
import os.path
import docutils
from docutils import nodes
from docutils.parsers.rst import roles
from docutils.writers.html4css1 import HTMLTranslator

from ..writers.rst import RstTranslator
from ..describer import tag

#------------------------------------------------------------------------------
# TODO: provide a better implementation here...
# todo: or move to using inline-style declaration? (that way it does not
#       polute *everything* in the application):
#         .. role:: class(literal)
#         .. role:: meth(literal)
#         .. role:: func(literal)
roles.register_generic_role('class', nodes.literal)
roles.register_generic_role('meth', nodes.literal)
roles.register_generic_role('func', nodes.literal)
# /TODO
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def undecorate(path):
  # this is very dim-witted implementation, but it works...
  # todo: is there a way to get rid of the need for this?...
  #       perhaps by using entry.path instead of entry.dpath...
  for char in '{}<>':
    path = path.replace(char, '')
  return path

#------------------------------------------------------------------------------
def normalizeDecoratedPath(path, node):
  curpath = '/'
  while node.parent:
    node = node.parent
    if isinstance(node, nodes.section) \
        and 'classes' in getattr(node, 'attributes', '') \
        and 'endpoint' in node.attributes.get('classes', ''):
      curpath = node.attributes.get('dpath', '') \
        or node.attributes.get('path', '') \
        or curpath
      break
  return os.path.normpath(os.path.join(curpath, path))

#------------------------------------------------------------------------------
# doc.link
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
class pyrdesc_doc_link(nodes.reference): pass
roles.register_generic_role('doc.link', pyrdesc_doc_link)

#------------------------------------------------------------------------------
class DocLink(object):
  _name = 'doc.link'
  def __init__(self, spec, node):
    '''
    Valid `spec` format EBNF := [ METHOD ':' ] PATH
    '''
    if not spec or not isinstance(spec, six.string_types):
      raise ValueError('Invalid pyramid-describe "%s" target: %r' % (self._name, spec))
    specv = spec.split(':')
    if len(specv) > 2:
      raise ValueError('Invalid pyramid-describe "%s" target: %r' % (self._name, spec))
    self.dpath  = normalizeDecoratedPath(specv.pop(), node)
    self.path   = undecorate(self.dpath)
    self.method = specv.pop() if specv else None
  def _escapeTextRoleArg(self, text):
    # todo: anything else need escaping?...
    return '`' + text.replace('\\', '\\\\').replace('`', '\\`') + '`'
  @property
  def args(self):
    args = [self.dpath]
    if self.method:
      args.insert(0, self.method)
    return args
  def __str__(self):
    return ':' + self._name + ':' + self._escapeTextRoleArg(':'.join(self.args))
def pyrdesc_doc_link_rst_visit(self, node):
  self._pushOutput()
def pyrdesc_doc_link_rst_depart(self, node):
  link = DocLink(self._popOutput().data(), node)
  self.output.separator()
  self.output.append(str(link))
  self.output.separator()
RstTranslator.visit_pyrdesc_doc_link = pyrdesc_doc_link_rst_visit
RstTranslator.depart_pyrdesc_doc_link = pyrdesc_doc_link_rst_depart

#------------------------------------------------------------------------------
def pyrdesc_doc_link_html_visit(self, node):
  # todo: make this 'doc-' prefix configurable...
  atts = {'class': 'doc-link'}
  link = DocLink(node.astext(), node)
  if not link.method:
    atts['href']  = '#endpoint-' + tag(link.path)
    atts['class'] += ' endpoint'
  else:
    atts['href'] = '#method-' + tag(link.path) + '-' + tag(link.method)
    atts['class'] += ' method'
  self.body.append(self.starttag(node, 'a', '', **atts))
def pyrdesc_doc_link_html_depart(self, node):
  self.body.append('</a>')
  if not isinstance(node.parent, nodes.TextElement):
    self.body.append('\n')
HTMLTranslator.visit_pyrdesc_doc_link = pyrdesc_doc_link_html_visit
HTMLTranslator.depart_pyrdesc_doc_link = pyrdesc_doc_link_html_depart

#------------------------------------------------------------------------------
# doc.copy
#------------------------------------------------------------------------------

# todo: support something like
#         :doc.copy:`METHOD:PATH:Parameters` -- copies title & all params
#         :doc.copy:`METHOD:PATH:Parameters[.*]` -- copies all params only
#         :doc.copy:`METHOD:PATH:Parameters[(foo|bar)]` -- copies 'foo' & 'bar' params only

# TODO: doc.copy's are currently child nodes of nodes.paragraph... which it
#       really shouldn't be. instead, it should be a nodes.container (or
#       something similar. one of the problems this causes is that the HTML
#       output wraps the imported nodes with a redundant <p>...</p>. ugh.

#------------------------------------------------------------------------------
class pyrdesc_doc_copy(nodes.reference): pass
roles.register_generic_role('doc.copy', pyrdesc_doc_copy)

#------------------------------------------------------------------------------
class DocCopy(DocLink):
  _name = 'doc.copy'
  def __init__(self, spec, node):
    '''
    Valid `spec` format EBNF := [ METHOD ':' ] PATH [ ':' SECTION ]
    '''
    if not spec or not isinstance(spec, six.string_types):
      raise ValueError('Invalid pyramid-describe "%s" target: %r' % (self._name, spec))
    specv = spec.split(':')
    if len(specv) > 3:
      raise ValueError('Invalid pyramid-describe "%s" target: %r' % (self._name, spec))
    self.sections = specv.pop().split(',') if len(specv) > 2 else None
    super(DocCopy, self).__init__(':'.join(specv), node)
  @property
  def args(self):
    args = [self.dpath]
    if self.method or self.sections:
      args.insert(0, self.method or '')
    if self.sections:
      args.append(','.join(self.sections))
    return args
def pyrdesc_doc_copy_rst_visit(self, node):
  self._pushOutput()
def pyrdesc_doc_copy_rst_depart(self, node):
  copy = DocCopy(self._popOutput().data(), node)
  self.output.separator()
  self.output.append(str(copy))
  self.output.separator()
RstTranslator.visit_pyrdesc_doc_copy = pyrdesc_doc_copy_rst_visit
RstTranslator.depart_pyrdesc_doc_copy = pyrdesc_doc_copy_rst_depart

#------------------------------------------------------------------------------
def walk(node):
  yield node
  # TODO: should this just be ``for child in node:`` ?
  for child in getattr(node, 'children', []):
    for sub in walk(child):
      yield sub

#------------------------------------------------------------------------------
def locatePath(node, path, up=True):
  # TODO: doc.copy's should probably be de-referenced on the parse-side instead
  #       of the render-side, since that would centralize where that kind of
  #       processing needs to occur... *AND* it would remove the need for this
  #       function, which is a *very* odd one...
  if not node:
    return None
  if up:
    path = 'endpoint-' + tag(path)
    while node.parent:
      node = node.parent
    return locatePath(node, path, False)
  for sub in walk(node):
    if isinstance(sub, nodes.section) \
        and 'endpoint' in getattr(sub, 'attributes', {}).get('classes', []) \
        and path in sub.attributes.get('ids', []):
      return sub
  return None

#------------------------------------------------------------------------------
def locateMethod(node, path, method):
  if not node:
    return None
  if not method:
    # TODO: fallback to 'GET'?
    return node
  nid = 'method-' + tag(path) + '-' + tag(method)
  for sub in walk(node):
    # todo: the `method.lower()` feels a bit weird to me... it's a bit of
    #       an abstraction barrier violation. i should 
    if isinstance(sub, nodes.section) \
        and 'method' in getattr(sub, 'attributes', {}).get('classes', []) \
        and nid in sub.attributes.get('ids', []):
      return sub
  return None

#------------------------------------------------------------------------------
def locateSection(node, path, method, section):
  if not node:
    return None
  nid = section.lower() + '-method-' + tag(path) + '-' + tag(method)
  for sub in walk(node):
    if isinstance(sub, nodes.section) \
        and section.lower() in getattr(sub, 'attributes', {}).get('classes', []) \
        and nid in sub.attributes.get('ids', []):
      return sub
  return None

#------------------------------------------------------------------------------
def pyrdesc_doc_copy_html_visit(self, node):
  text  = node.astext()
  copy  = DocCopy(text, node)
  cnode = locatePath(node, copy.path)
  if not cnode:
    raise ValueError('Could not locate "doc.copy" path target for "%s"' % (text,))
  cnode = locateMethod(cnode, copy.path, copy.method)
  if not cnode:
    raise ValueError('Could not locate "doc.copy" method target for "%s"' % (text,))
  if not copy.sections:
    # TODO: should this just be ``for idx, child in enumerate(cnode):`` ?
    for idx, child in enumerate(cnode.children):
      # todo: why is this check for 'html.MetaBody.meta' necessary???
      #       i.e. how is it being excluded during the normal walk of
      #       the remote node but not here?...
      from docutils.parsers.rst.directives import html
      if ( idx == 0 and isinstance(child, nodes.title) ) \
          or isinstance(child, html.MetaBody.meta):
        continue
      child.walkabout(self)
    raise nodes.SkipNode
  # todo: here, the :doc.copy: is controlling order, but that probably
  #       shouldn't be the case, since order of sections is not
  #       preserved by the numpydoc parsing.
  for section in copy.sections:
    snode = locateSection(cnode, copy.path, copy.method, section)
    if not snode:
      continue
    snode.walkabout(self)
  raise nodes.SkipNode
def pyrdesc_doc_copy_html_depart(self, node):
  pass
HTMLTranslator.visit_pyrdesc_doc_copy = pyrdesc_doc_copy_html_visit
HTMLTranslator.depart_pyrdesc_doc_copy = pyrdesc_doc_copy_html_depart

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------