# <img alt="Qualichat" src="branding/logo/qualichat-logo.png" height="150">
<!-- badges -->
[![Downloads](https://pepy.tech/badge/qualichat)](https://pepy.tech/project/qualichat)
<img src="https://img.shields.io/github/stars/qualichat/qualichat" />
<img src="https://img.shields.io/pypi/pyversions/qualichat.svg" >

Open-source linguistic ethnography tool for framing public opinion in mediatized groups.


## Table of Contents

- [Installing](#installing)
- [Quickstart](#quickstart)
- [Links](#links)


### Installing

**Python 3.7.1 or higher is required.**

To install the library, you can just run the following command:
```sh
$ pip install -U qualichat
```


To install a development version, follow these steps:
```sh
$ git clone https://github.com/qualichat/qualichat
$ cd qualichat

# Linux/MacOS
$ python3 -m pip install -U .
# Windows
$ py -3 -m pip install -U .
```

### Quickstart

To use this library, you need a plain chat text file, following this format:

```
[dd/mm/yy hh:mm:ss] <contact name>: <message>
```

For example, see this following sample chat file named `sample-chat.txt`:

```
[01/01/21 07:52:45] Joel: Hello!
[01/01/21 07:52:47] Mary: Hi!
[01/01/21 07:52:49] Joel: How are you guys?
[01/01/21 07:52:52] Mary: We are fine! 😊
How about you?
[01/01/21 07:52:55] Oliva: Everything's great!
[01/01/21 07:52:59] Joel: Cool! I am also fine!
[01/01/21 07:53:03] John left
```

In your code, you will just load the chat using `qualichat.load_chat()`.

```py
chat = qualichat.load_chat('sample-chat.txt')
```


### Links

- **Website:** http://qualichat.com
- **Documentation:** https://qualichat.readthedocs.io
- **Source code:** https://github.com/qualichat/qualichat

