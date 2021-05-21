.. currentmodule:: qualichat

API Reference
=============

The following section outlines the API of Qualichat.


Version Related Info
--------------------

There are two main ways to query version information about the library.

.. data:: version_info

    A named tuple that is similar to :obj:`py:sys.version_info`.

    Just like :obj:`py:sys.version_info` the valid values for ``releaselevel`` are
    `alpha`, `beta`, `candidate` and `final`.

.. data:: __version__

    A string representation of the version. e.g. ``'1.0.0a'``. This is based
    off of :pep:`440`.


.. _loaders:

Chat Loaders
------------

.. autofunction:: load_chat


Chat Analyzers
--------------

.. warning::
    These classes are not supposed to be instantiated by yourself. To maintain
    compatibility with the library, choose to use one of the :ref:`loaders`.

.. autoclass:: qualichat.chat.Qualichat()
    :members:

Models
------

.. autoclass:: qualichat.models.Actor()
    :members:
    
.. autoclass:: qualichat.models.Message()
    :members:

.. autoclass:: qualichat.models.SystemMessage()
    :members:
