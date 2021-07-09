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

.. autofunction:: load_chats


Chat Analyzers
--------------

.. warning::
    These classes are not supposed to be instantiated by yourself. To maintain
    compatibility with the library, choose to use one of the :ref:`loaders`.

.. autoclass:: qualichat.core.Qualichat()
    :members:

.. autoclass:: qualichat.chat.Chat()
    :members:


Features
--------

.. autofunction:: qualichat.features.generate_chart

.. autoclass:: qualichat.features.BaseFeature
    :members:

.. autoclass:: qualichat.features.MessagesFeature
    :members:

.. autoclass:: qualichat.features.ActorsFeature
    :members:

.. autoclass:: qualichat.features.TimeFeature
    :members:

.. autoclass:: qualichat.features.NounsFeature
    :members:

.. autoclass:: qualichat.features.VerbsFeature
    :members:


Abstract Base Classes
---------------------

An :term:`abstract base class` (also known as an ``abc``) is a class that models can inherit
to get their behaviour. **Abstract base classes should not be instantiated**.

.. autoclass:: qualichat.abc.BaseMessage()
    :members:


Enumerations
------------

This library provides some enumerations for certain types. All time formats below are 24-hour
format.

.. class:: qualichat.enums.MessageType

    Specifies the type of :class:`.Message`. This is used to denote if a
    message is to be interpreted as a system message or a regular message.

    .. attribute:: default

        The default message type. This is the same as regular messages.

    .. attribute:: gif_omitted

        System message when a GIF image was sent but omitted.

    .. attribute:: image_omitted

        System message when an image was sent but omitted.

    .. attribute:: video_omitted

        System message when a video was sent but omitted.

    .. attribute:: audio_omitted

        System message when an audio was sent but omitted.

    .. attribute:: sticker_omitted

        System message when a sticker was sent but omitted.

    .. attribute:: document_omitted

        System message when a document (PDF, XML, etc.) was sent but omitted.

    .. attribute:: contact_card_omitted

        System message when a contact card was sent but omitted.

    .. attribute:: deleted_message

        System message when the message was deleted.

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

.. class:: qualichat.enums.SubPeriod

    Represents the sub-period in which a message was sent.

    .. attribute:: resting

        If the message was sent between ``00:00`` and ``05:59``.

    .. attribute:: transport_morning

        If the message was sent between ``06:00`` and ``08:59``.

    .. attribute:: work_morning

        If the message was sent between ``09:00`` and ``11:59``.

    .. attribute:: lunch

        If the message was sent between ``12:00`` and ``14:59``.

    .. attribute:: work_evening

        If the message was sent between ``15:00`` and ``17:59``.

    .. attribute:: transport_evening

        If the message was sent between ``18:00`` and ``20:59``.

    .. attribute:: second_office_hour

        If the message was sent between ``21:00`` and ``23:59``.


Models
------

Models are classes created by the library to represent an element of the chat. 
They are not intended to be instantiated by the user of the library.

.. warning::

    The classes listed below are **not intended to be created by users** and
    are also **read-only**.

    For example, this means that you should not make your own :class:`.Actor` instances
    or should you modify the :class:`.Actor` instance yourself.

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
