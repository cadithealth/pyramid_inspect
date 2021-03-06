=========================
Application Documentation
=========================

This document is intended to assist you in using our API. A quote:

::

    There is nothing in the programming field more despicable than an
    undocumented program.
    
      -- Edward Yourdon

-------------
API Lifecycle
-------------

* Beta

* Public

* Deprecated

---------
Endpoints
---------

The available endpoints are broken down into General_ purpose, Item_ specific,
and Miscellaneous_ endpoints.

```````
General
```````

General purpose endpoints:

::::::
\/
::::::

@PUBLIC

Serves the homepage.

::::::
/about
::::::

@PUBLIC

Serves the glorious "about us" page.

``````
Item
``````

Endpoints that apply to an ITEM_ID:

::::::::::
/{ITEM_ID}
::::::::::

@PUBLIC

Provides RESTful access to the URL-specified item.

::::::::::::::::::::
/{ITEM_ID}/subaction
::::::::::::::::::::

@PUBLIC

Executes a sub-action.

`````````````
Miscellaneous
`````````````

Other:

::::::::::::::::::
/{ITEM_ID}/chatter
::::::::::::::::::

@PUBLIC

Generates chatter.

---------
Copyright
---------

See: `http://creativecommons.org/licenses/by/4.0/
<http://creativecommons.org/licenses/by/4.0/>`_.
