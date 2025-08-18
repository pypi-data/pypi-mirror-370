# Python Bootwrap

![Python + Bootstrap = Bootwrap](https://github.com/mmgalushka/bootwrap/raw/main/docs/bootwrap-equation.png)

[![Continuous Integration Status](https://github.com/mmgalushka/bootwrap/workflows/CI/badge.svg)](https://github.com/mmgalushka/bootwrap/actions)
[![Code Coverage Percentage](https://codecov.io/gh/mmgalushka/bootwrap/branch/main/graphs/badge.svg)](https://codecov.io/gh/mmgalushka/bootwrap)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/763657a471ff424c85a5b894ddb750d0)](https://www.codacy.com/gh/mmgalushka/bootwrap/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=mmgalushka/bootwrap&amp;utm_campaign=Badge_Grade)
[![Project License](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/mmgalushka/bootwrap/blob/main/LICENSE)
[![Project Documentation](https://img.shields.io/badge/docs-up--to--date-success)](https://mmgalushka.github.io/bootwrap/)

**Bootwrap** is a Python library for rapid developing of web-based user interfaces (WebUI). It helps creating WebUI using Python code only and can be used in conjunction with different web-development frameworks such as [Flask](https://palletsprojects.com/p/flask/). Under the hood, this library wraps one of the most popular front-end toolkit [Bootstrap](https://getbootstrap.com/).

As a showcase of what this library is capable of please check the documentation. The entire [documentation](https://mmgalushka.github.io/bootwrap/) web interface is created using the **Bootwrap**.

## Installing

Install and update using [pip](https://pip.pypa.io/en/stable/quickstart/):

```bash
~$ pip install bootwrap
```

Bootwrap package has no external dependencies!

## Why & where you might use Bootwrap?

The vast majority of web applications consist of frontend and backend. If you are a small team or even a solo developer you need to divide resources and time to focus on both parts. This often results in switching between different platforms such as Python and [React](https://reactjs.org/), [AngularJs](https://angular.io/), Flask templates (HTML, CSS, JS), etc. But what if your main focus is the backend and you also don't want to compromise on the quality of your WebUI. In this case, the Bootwrap library is for you! It will help you develop WebUI without leaving the Python ecosystem and not waste your time on HTML, CSS, and Javascript. To understand its capability just clone the project and run the [demo application](demo/demo.md) ":pig: PiggyBank".

![Screenshots Collage](demo/collage.png)

For more information also read the Bootwrap [documentation](https://mmgalushka.github.io/bootwrap/).

## Hello World Application

The following code will create three pages application with a top-level menu bar for navigations. Since this application is based on [Flask](https://palletsprojects.com/p/flask/) make sure that you installed it as well.

```Python
from flask import Flask
from markupsafe import Markup
from bootwrap import Page, Menu, Image, Anchor, Button, Text

app = Flask(__name__, static_folder='docs', static_url_path='')

LOGO = 'https://github.com/mmgalushka/bootwrap/blob/main/docs/logo.png?raw=true'
FAVICON = 'https://raw.githubusercontent.com/mmgalushka/bootwrap/main/docs/favicon.ico'

class MyMenu(Menu):
    def __init__(self):
        super().__init__(
            logo=Image(LOGO, width=32, alt='Logo'),
            brand=Text('Bootwrap').as_strong().as_light().ms(2),
            anchors=[
                Anchor('Home').link('/'),
                Anchor('About').link('/about')
            ], 
            actions=[
                Button('Sign In').as_outline().as_light().link('/signin')
            ]
        )

class MyPage(Page):
    def __init__(self, container):
        super().__init__(
            favicon = FAVICON,
            title='Hello World Application',
            menu=MyMenu(),
            container=container
        )

@app.route('/')
def home():
    return Markup(MyPage(container=Text('Home').as_heading(1)))

@app.route('/about')
def about():
    return Markup(MyPage(container=Text('About').as_heading(1)))

@app.route('/signin')
def signin():
    return Markup(MyPage(container=Text('Sign In').as_heading(1)))

if __name__ == '__main__':
    app.run(debug=True)
```

Use the following command to launch the application.

```bash
$ flask run
  * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

The result should look like.

![Simple Example](https://github.com/mmgalushka/bootwrap/raw/main/docs/multi-pages-app.png)

## Contributing

For information on how to set up a development environment and how to make a contribution to Bootwrap, see the [contributing guidelines](CONTRIBUTING.md).

## Links

- Documentation: [https://mmgalushka.github.io/bootwrap/](https://mmgalushka.github.io/bootwrap/)
- PyPI Releases: [https://pypi.org/project/bootwrap/](https://pypi.org/project/bootwrap/)
- Source Code: [https://github.com/mmgalushka/bootwrap](https://github.com/mmgalushka/bootwrap/)
- Issue Tracker: [https://github.com/mmgalushka/bootwrap/issues](https://github.com/mmgalushka/bootwrap/)
