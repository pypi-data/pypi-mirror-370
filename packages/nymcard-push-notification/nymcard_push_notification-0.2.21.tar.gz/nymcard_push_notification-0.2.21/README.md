# push-notifications
Push Notifications Django Application

```
{
  "callback_url": "http://localhost:8003/wow",
  "pattern": "consumer/registration/*"
}
```

build steps

Ensure twine and build are Installed

```
pip install twine build
```

Build the Package

```
python -m build
```


Upload to PyPI using twine

```
twine upload dist/*
```