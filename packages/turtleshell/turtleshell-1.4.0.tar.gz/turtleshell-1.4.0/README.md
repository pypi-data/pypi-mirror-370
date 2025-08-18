# TurtleShell

Convenience wrapper around Python turtle standard library.

## Development
1. Do all this in a virtual environment, e.g.:
    ```
    python3 -m venv venv
    source /venv/bin/activate
    pip install pytest bumpver build twine
    ```

2. Test:
    ```
    pytest
    ```

3. Push.

4. Update package version:
    ```
    bumpver update --minor
    ```

5. Push.

6. Build/check package:
    ```
    python -m build; twine check dist/*
    ```

7. Upload to Test PyPI, install, and test:
    ```
    twine upload -r testpypi dist/*
    pip install -i https://test.pypi.org/simple turtleshell
    ```

8. Upload to PyPI:
    ```
    twine upload dist/*
    ```