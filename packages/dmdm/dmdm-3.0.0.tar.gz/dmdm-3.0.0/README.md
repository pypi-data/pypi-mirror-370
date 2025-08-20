#  Django MarkDown Mail

[![PyPI version](https://badge.fury.io/py/dmdm.svg)](https://pypi.org/project/dmdm)
[![Tests](https://github.com/nim65s/dmdm/actions/workflows/test.yml/badge.svg)](https://github.com/nim65s/dmdm/actions/workflows/test.yml)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/nim65s/dmdm/main.svg)](https://results.pre-commit.ci/latest/github/nim65s/dmdm/main)
[![codecov](https://codecov.io/gh/nim65s/dmdm/branch/main/graph/badge.svg?token=CUHNXAVJPO)](https://codecov.io/gh/nim65s/dmdm)
[![Maintainability](https://api.codeclimate.com/v1/badges/6737a84239590ddc0d1e/maintainability)](https://codeclimate.com/github/nim65s/dmdm/maintainability)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Write your email in markdown, and send them in txt & html.

## Requirements

- Python 3.10+
- Django 2.0+
- [nmdmail](https://github.com/nim65s/nmdmail)

## Install

`python -m pip install dmdm`

## Usage

This replaces django's `django.core.email.send_mail`, but the mail will have an html alternative rendered from the text
part with markdown. You can also provide a custom `css` and even images (that will be inlined) located in `image_root`.


```python
from dmdm import send_mail

def send_mail(
    subject: str,
    message: str,
    from_email: str,
    recipient_list: List[str],
    context: Optional[Dict] = None,
    request: Optional[HttpRequest] = None,
    fail_silently: bool = False,
    css: Optional[str] = None,
    image_root: str = ".",
    auth_user: Optional[str] = None,
    auth_password: Optional[str] = None,
    connection: Optional[BaseEmailBackend] = None,
    reply_to: Optional[List[str]] = None,
) -> int
```

If you want to write your markdown in a template, just put the name of the template in `message` and add a `context`
(which can be `{}`) and eventually a `request`:

```python
send_mail(
    subject,
    "test_email_template.md",
    from_email,
    recipient_list,
    {"template_variable": "value"},
)
```
