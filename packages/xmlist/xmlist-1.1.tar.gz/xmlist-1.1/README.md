# xmlist

`xmlist` is a module for generating XML, which it represents by lists and
tuples.

## using xmlist

    doc = ['html',
        ('xmlns', 'http://www.w3.org/1999/xhtml'),
        ['head', ['title', 'Hello, world!']],
        ['body',
            ['h1', 'Hello, world!'],
            ['p', 'xmlist is a module for generating XML']]]
    xml = xmlist.serialize(doc)

## hacking on xmlist

Create a venv and install the package with the `-e`/`--editable` flag. The
`dev` group pulls in requirements for setuptools, tox and various pytest
packages.

    python -m venv .venv
    python -m pip install -e . --group dev

## testing xmlist

Running the tests for your current Python:

    python -m pytest -v

Running the tests in other Pythons:

    python -m tox
