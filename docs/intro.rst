Introduction
============

Welcome to the Qualichat's documentation.


Prerequisites
-------------

Qualichat works with Python 3.7.1 or higher. Support for earlier versions is not provided.
Python 2.7 is not supported. Python 3.6 or lower is not supported due to one of the dependencies
(`pandas <https://github.com/pandas-dev/pandas>`_) not supporting Python 3.6.


Installing
----------

Work in Progress.


Basic Concepts
--------------

Before using Qualichat, you will need a plain text file
containing a chat following this format: ::

    [dd/mm/yy hh:mm:ss] <contact name>: <message>

You can load the text file using :meth:`qualichat.load_chat()`:

.. code-block:: python3

    import qualichat

    chat = qualichat.load_chat('chat.txt')

To generate graphs, just use :meth:`qualichat.GraphGenerator`:

.. code-block:: python3

    import qualichat

    chat = qualichat.load_chat('chat.txt')
    graphs = qualichat.GraphGenerator(chat)
