# Sisyphus tests

These tests only check functions that work on plain values or on temporary
files. They don't need root, Portage or a network connection, and they never
touch the real configuration in /etc/sisyphus.

Run them from the top of the source tree:

```
python3 -m pytest tests
```

You need pytest and the Python packages Sisyphus already uses (colorama,
animation, GitPython, rich, requests, urllib3, python-gnupg, typer), because
importing any Sisyphus module loads all of them. GitPython also needs the
git program installed.
