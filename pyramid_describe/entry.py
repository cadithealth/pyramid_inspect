# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: Philip J Grabner <grabner@cadit.com>
# date: 2013/09/10
# copy: (C) Copyright 2013 Cadit Health Inc., All Rights Reserved.
#------------------------------------------------------------------------------

from .util import adict

#------------------------------------------------------------------------------
class Entry(adict):
  '''
  Represents an entry in the describe hierarchy. Entries can have the
  following attributes:

  :Attributes:

  name : str
    The name of the entry, relative to the `parent` entry.

  dname : str
    The "decorated" version of `name`.

  path : str
    The full path to this entry.

  dpath : str
    The "decorated" version of `path`.

  ipath : str
    The python implementation resolver path, if it can be determined. 

  itype : { 'class', 'instance', 'method', 'function', 'unknown' }
    The python implementation type, if it can be determined.

  parent : { Entry, None }
    A reference to the parent Entry, or ``None`` if this is
    the root Entry.

  view : { callable, pyramid_controllers.Controller }
    The actual pyramid view handler referenced by this entry.

  method : str
    The name of the HTTP method for RESTful verb entries.

  parents : generator
    A generator of entry parents, starting with the closest first.

  rparents : generator
    A reversed version of `parents`, ie. starting at the root first.

  doc : { str, dict }
    The documentation for this entry. During initial loading, is
    populated by the `view`'s ``__doc__`` attribute (i.e. the pydoc
    string). Parsers may extend and replace this attribute to empower
    it with structural information, such as accepted parameters,
    return values, etc.

  isController : bool
    True IFF the `view` is a Controller.

  isMethod : bool
    True IFF the `parent` is a RestController and this is
    a RESTful verb handler.

  isEndpoint : bool
    True IFF it is an endpoint that is capable of handling
    requests. this is always true if `handler` is defined,
    but not necessarily the case if `controller` is defined.
    the latter is only the case IFF an @index has been defined
    for the controller.

  isStub : bool
    True IFF the dispatcher will only send requests to this
    controller if it is returned from a @lookup method, i.e.
    the controller's `expose` attribute is False.

  isRest : bool
    True IFF the `view` is an instance of RestController.

  isDynamic : bool
    True IFF the `view` is not an inspectable class; i.e.  it is not
    an instantiated method, and is dynamically instantiated when
    handling a request.

  '''

  @property
  def parents(self):
    entry = self
    while entry.parent:
      yield entry.parent
      entry = entry.parent

  @property
  def rparents(self):
    if self.parent:
      for parent in self.parent.rparents:
        yield parent
      yield self.parent

  def __eq__(self, other):
    # note: not quite sure exactly why, but the line
    #       describer.DescriberData.tree_entries:
    #         "if entry.parent and entry.parent not in fullset:"
    #       causes a 'RuntimeError: maximum recursion' error if this
    #       is not here...
    return self is other

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
