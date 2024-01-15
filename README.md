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

Before using the library, it's necessary to download the Spacy language model. You can do this by running:

```sh
$ python -m spacy download en_core_web_sm
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

## Compatibility Note
### Python 3.12 Compatibility:

As of the current release, Qualichat has been extensively tested on Python versions up to 3.11. While we strive to ensure compatibility with newer versions of Python, please note that Python 3.12 is a recent release and might have limited coverage in terms of library support and testing. As such, you may encounter unexpected issues or incompatibilities when using Qualichat with Python 3.12.

We recommend using Python 3.7.1 or higher, but not exceeding version 3.11 for the most stable experience. We appreciate any feedback or contributions regarding compatibility with newer Python versions, including Python 3.12.

### Quickstart

To use this library, you need a plain chat text file, following this format:

```
[dd/mm/yy hh:mm:ss] <contact name>: <message>
```

After inserting a chat file (e.g., _chat.txt), you can execute the program with the following command:

```sh
python -m qualichat load <path-to-chat-file>
```

For example:

```sh
python -m qualichat load _chat.txt
```

For example, see this following sample chat file named `_chat.txt`:

```
[01/01/2021 07:52:45] Joel: Hello!
[01/01/2021 07:52:47] Mary: Hi!
[01/01/2021 07:52:49] Joel: How are you guys?
[01/01/2021 07:52:52] Mary: We are fine! 😊
How about you?
[01/01/2021 07:52:55] Oliva: Everything's great!
[01/01/2021 07:52:59] Joel: Cool! I am also fine!
[01/01/2021 07:53:03] John left
```

In a terminal, you will just load the chat using the command mentioned before:

```sh
python -m qualichat load _chat.txt
```


### Links

- **Website:** http://qualichat.com
- **Documentation:** https://qualichat.readthedocs.io
- **Source code:** https://github.com/qualichat/qualichat

