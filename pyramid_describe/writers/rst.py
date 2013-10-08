# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: Philip J Grabner <grabner@cadit.com>
# date: 2013/10/02
# copy: (C) Copyright 2013 Cadit Health Inc., All Rights Reserved.
#------------------------------------------------------------------------------

import re, textwrap
from docutils import core, utils, nodes, writers
import docutils.writers

#------------------------------------------------------------------------------
def rstEscape(text, context=None):
  if context in ('`',):
    if re.match('^[a-zA-Z0-9]+$', text):
      return text
    text = text.replace('\\', '\\\\').replace(context, '\\' + context)
    return context + text + context
  if context in (':',):
    if context not in text and '\\' not in text:
      return text
    return text.replace('\\', '\\\\').replace(context, '\\' + context)
  # TODO
  return text

#------------------------------------------------------------------------------
def rstTicks(text):
  return rstEscape(text, context='`')

#------------------------------------------------------------------------------
DEFAULT_SECTION_CHARS = '''=-`:'"~^_*+#<>'''
DEFAULT_TEXT_WIDTH    = 79
DEFAULT_INDENT        = ' '*4

#------------------------------------------------------------------------------
# default settings:
#   footnote_backlinks:              1
#   record_dependencies:             DependencyList(None, [])
#   language_code:                   'en'
#   traceback:                       True
#   strip_comments:                  None
#   toc_backlinks:                   'entry'
#   dump_internals:                  None
#   datestamp:                       None
#   report_level:                    2
#   strict_visitor:                  None
#   _destination:                    None
#   halt_level:                      4
#   strip_classes:                   None
#   title:                           None
#   error_encoding_error_handler:    'backslashreplace'
#   debug:                           None
#   dump_transforms:                 None
#   warning_stream:                  None
#   text_width:                      79
#   exit_status_level:               5
#   config:                          None
#   section_chars:                   '=-`:\'"~^_*+#<>'
#   dump_pseudo_xml:                 None
#   expose_internals:                None
#   source_link:                     None
#   output_encoding_error_handler:   'strict'
#   source_url:                      None
#   input_encoding:                  None
#   _disable_config:                 None
#   id_prefix:                       ''
#   sectnum_xform:                   1
#   error_encoding:                  'UTF-8'
#   output_encoding:                 'utf-8'
#   generator:                       None
#   explicit_title:                  False
#   _source:                         None
#   input_encoding_error_handler:    'strict'
#   auto_id_prefix:                  'id'
#   strip_elements_with_classes:     None
#   _config_files:                   []
#   dump_settings:                   None
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
class Writer(writers.Writer):

  supported = ('reStructuredText', 'text', 'txt', 'rst')
  'Formats this writer supports.'

  settings_spec = (
    '"Docutils Canonical reStructuredText" Writer Options',
    None,
    (('Specify the order of over/underline characters.',
      ['--section-chars'],
      {'dest': 'section_chars', 'action': 'store',
       'default': DEFAULT_SECTION_CHARS}),
     ('Set the default indentation text.',
      ['--indent'],
      {'dest': 'indent', 'action': 'store',
       'default': DEFAULT_INDENT}),
     ('Set the text wrapping width.',
      ['--text-width'],
      {'dest': 'text_width', 'action': 'store', 'type': 'int',
       'default': DEFAULT_TEXT_WIDTH}),
     ('Output an explicit `title` directive (even if inferrable).',
      ['--explicit-title'],
      {'dest': 'explicit_title', 'action': 'store_true',
       'default': False}),
     ),)

  config_section = 'rst writer'
  config_section_dependencies = ('writers',)

  output = None
  'Final translated form of `document`.'

  def __init__(self):
    writers.Writer.__init__(self)
    self.translator_class = RstTranslator

  def translate(self):
    self.visitor = visitor = self.translator_class(self.document)
    self.document.walkabout(visitor)
    # todo: translate EOL's here?...
    self.output = visitor.output.data()

#------------------------------------------------------------------------------
def collapseLines(value, step):
  if not step:
    return value
  if step != '\n':
    return value + [step]
  if not value:
    return value
  if len(value) > 2 and value[-1] == '\n' and value[-2] == '\n':
    return value
  return value + [step]

#------------------------------------------------------------------------------
class Output:
  def __init__(self):
    self.lines = []
  def emptyline(self):
    # todo: improve this
    self.lines.append('\n')
    self.lines.append('\n')
  def newline(self):
    # todo: improve this
    if len(self.lines) > 0 and self.lines[-1] != '\n':
      self.lines.append('\n')
  def append(self, data):
    self.lines.append(data)
  def extend(self, data):
    self.lines.extend(data)
  def data(self):
    return ''.join(reduce(collapseLines, self.lines, []))

#------------------------------------------------------------------------------
class RstTranslator(nodes.GenericNodeVisitor):

  inline_format = {
    'inline'                          : ('{}',       None),
    'emphasis'                        : ('*{}*',     None),
    'strong'                          : ('**{}**',   None),
    'interpreted_or_phrase_ref'       : ('`{}`',     None),
    'title_reference'                 : ('`{}`',     None),
    'literal'                         : ('``{}``',   None),
    'inline_internal_target'          : ('_{}',      rstTicks),
    'footnote_reference'              : ('[{}]_',    None),
    'substitution_reference'          : ('|{}|',     None),
    'reference'                       : ('{}_',      rstTicks),
    'anonymous_reference'             : ('{}__',     rstTicks),
    }

  #----------------------------------------------------------------------------
  def __init__(self, document):
    nodes.NodeVisitor.__init__(self, document)
    self.settings = document.settings
    self.output   = Output()
    self.stack    = []
    self.level    = 0

  #----------------------------------------------------------------------------
  def _pushStack(self):
    self.stack.append(self.output)
    self.output = Output()

  #----------------------------------------------------------------------------
  def _popStack(self):
    ret = self.output
    self.output = self.stack.pop()
    return ret

  #----------------------------------------------------------------------------
  def _putAttributes(self, node):
    title = None
    wtitle = False
    if isinstance(node, nodes.document):
      title = self.settings.title
      if title is not None:
        wtitle = True
    if not title:
      title = node.get('title')
    if title is not None:
      wtitle = self.settings.explicit_title or wtitle
      if not wtitle and isinstance(node, nodes.document):
        # check to see if the `document` title is different than
        # the inferred title, in which case we force-show the title
        # todo: is this really the best way to determine the inferred title?
        # todo: is checking for the first `title` node sufficient?
        # todo: there must be a way to use the rst parser code, no?...
        for subnode in node:
          if isinstance(subnode, nodes.title):
            if node.get('title') != subnode.astext():
              wtitle = True
            break
      if wtitle:
        self.output.emptyline()
        self.output.append('.. title:: ' + node['title'])
        self.output.emptyline()
    if node['classes']:
      self.output.emptyline()
      self.output.append('.. class:: ' + ' '.join(node['classes']))
      self.output.emptyline()
    if node['ids']:
      # note: only generating an `id` node IFF they are not generated
      # todo: this is *not* the best way to determine whether or not
      #       the node['ids'] is completely generated!...
      dids = self.document.ids
      nids = node['ids']
      node['ids'] = []
      for id in nids:
        # todo: there is a weirdness that if the id references the document,
        #       then self.document.ids lookup points to a `section` node...
        #       look into what i misunderstood here.
        rnode = self.document.ids.get(id)
        if isinstance(node, nodes.document) and isinstance(rnode, nodes.section):
          rnode = node
        if rnode is node:
          del self.document.ids[id]
      self.document.set_id(node)
      nids_ng = set(nids) - set(node['ids'])
      if nids_ng:
        self.output.emptyline()
        self.output.append('.. id:: ' + ' '.join(sorted(nids_ng)))
        self.output.emptyline()
      self.document.ids = dids
      node['ids'] = nids

  #----------------------------------------------------------------------------
  def default_visit(self, node):
    if isinstance(node, nodes.Inline):
      self._pushStack()
    else:
      self._putAttributes(node)

  #----------------------------------------------------------------------------
  def default_departure(self, node):
    if isinstance(node, nodes.Inline):
      text = self._popStack().data()
      fmt = self.inline_format[node.__class__.__name__]
      if fmt[1]:
        text = fmt[1](text)
      self.output.append(fmt[0].format(text))

  #----------------------------------------------------------------------------
  def depart_document(self, node):
    self.output.newline()

  #----------------------------------------------------------------------------
  def visit_Text(self, node):
    self.output.append(node.astext())

  #----------------------------------------------------------------------------
  def visit_title(self, node):
    self._pushStack()

  #----------------------------------------------------------------------------
  def depart_title(self, node):
    sclen = len(self.settings.section_chars)
    over  = self.level < sclen
    lsym  = self.settings.section_chars[self.level % sclen]
    text  = self._popStack().data()
    if len(text) > 0 and text == text[0] * len(text) and re.match('[^a-zA-Z0-9]', text[0]):
      text = re.sub('([^a-zA-Z0-9])', '\\\\\\1', text)
    width = max(6, len(text))
    self.output.emptyline()
    if over:
      self.output.append(lsym * width)
      self.output.newline()
    self.output.append(text)
    self.output.newline()
    self.output.append(lsym * width)
    self.output.newline()

  #----------------------------------------------------------------------------
  def visit_section(self, node):
    self._putAttributes(node)
    self.level += 1

  #----------------------------------------------------------------------------
  def depart_section(self, node):
    self.level -= 1

  #----------------------------------------------------------------------------
  def visit_paragraph(self, node):
    self._pushStack()

  #----------------------------------------------------------------------------
  def depart_paragraph(self, node):
    text = self._popStack().data()
    self.output.emptyline()
    # todo: do textwrapping rules change in rST?...
    self.output.append(
      '\n'.join(textwrap.wrap(text, width=self.settings.text_width)))
    self.output.newline()

  #----------------------------------------------------------------------------
  def visit_literal_block(self, node):
    self._pushStack()

  #----------------------------------------------------------------------------
  def depart_literal_block(self, node):
    text = self._popStack().data()
    self.output.emptyline()
    cmd = '::'
    if 'code' in node['classes']:
      cmd = '.. code-block::'
      if len(node['classes']) > 1:
        classes = node['classes'][:]
        classes.remove('code')
        cmd += ' ' + ' '.join(sorted(classes))
    self.output.append(cmd)
    self.output.emptyline()
    self.output.append(self.settings.indent
                       + text.replace('\n', '\n' + self.settings.indent))
    self.output.newline()

  #----------------------------------------------------------------------------
  def visit_target(self, node):
    if isinstance(node.parent, nodes.TextElement) and node.referenced <= 1:
      # note: this is a little weird, but `target`s exist both when a link
      # is inlined AND when generated as 
      return
    self.output.emptyline()
    self.output.append('.. _{name}: {uri}'.format(
      name = rstEscape(node['names'][0], context='`'),
      uri  = rstEscape(node['refuri'])))
    self.output.newline()

  #----------------------------------------------------------------------------
  def depart_target(self, node):
    pass

  #----------------------------------------------------------------------------
  def depart_reference(self, node):
    # todo: this is a bit of a hack... if this is an inline reference,
    #       i'm artificially inserting the "TEXT <URI>" output, and
    #       expecting the default handler to wrap it in "`...`_" --
    #       instead, there should be a helper method.
    sibs = list(node.parent)
    idx  = sibs.index(node)
    if idx + 1 < len(sibs) \
        and isinstance(sibs[idx + 1], nodes.target) \
        and node['name'] in sibs[idx + 1]['names'] \
        and sibs[idx + 1].referenced == 1:
      text = self._popStack().data()
      self._pushStack()
      self.output.append('{text} <{uri}>'.format(
        text = text,
        uri  = rstEscape(node['refuri'])))
    return self.default_departure(node)

  #----------------------------------------------------------------------------
  def visit_meta(self, node):
    sibs = list(node.parent)
    idx  = sibs.index(node)
    if idx == 0 or type(sibs[idx - 1]) is not type(node):
      self.output.emptyline()
      self.output.append('.. meta::')
      self.output.newline()
    self.output.append('{indent}:{name}: {content}'.format(
      indent  = self.settings.indent,
      name    = rstEscape(node['name'], context=':'),
      content = rstEscape(node['content']),
      ))
    self.output.newline()

  #----------------------------------------------------------------------------
  def depart_meta(self, node):
    pass

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------