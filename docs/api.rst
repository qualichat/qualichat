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


Abstract Base Classes
---------------------

An :term:`abstract base class` (also known as an ``abc``) is a class that models can inherit
to get their behaviour. **Abstract base classes should not be instantiated**.

.. autoclass:: qualichat.abc.Message()
    :members:


Enumerations
------------

This library provides some enumerations for certain types. All time formats below are 24-hour
format.

.. class:: qualichat.enums.Period

    Represents the period in which a message was sent.

    .. attribute:: dawn

        If the message was sent between ``00:00`` and ``05:59``.

    .. attribute:: morning

        If the message was sent between ``06:00`` and ``11.59``.

    .. attribute:: evening

        If the message was sent between ``12:00`` and ``17:59``.

    .. attribute:: night

        If the message was sent between ``18:00`` and ``23:59``.


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


Graphs
------

.. autoclass:: GraphGenerator
    :members:


Models
------

Models are classes created by the library to represent an element of the chat. 
They are not intended to be instantiated by the user of the library.

.. warning::

    The classes listed below are **not intended to be created by users** and
    are also **read-only**.

    For example, this means that you should not make your own :class:`.Actor` instances
    nor should you modify the :class:`.Actor` instance yourself.

Actors
~~~~~~

.. autoclass:: qualichat.models.Actor()
    :members:

Messages
~~~~~~~~
    
.. autoclass:: qualichat.models.Message()
    :members:
    :inherited-members:

.. autoclass:: qualichat.models.SystemMessage()
    :members:
    :inherited-members:
