# Contributing

Thanks for taking the time to contribute to **cocon_client**!

## Development setup

1. Fork the repository and clone your fork.
2. Create and activate a Python 3.11+ virtual environment.
3. Install the project in editable mode:

   ```bash
   pip install -e .
   ```

4. Before committing, ensure the code still parses:

   ```bash
   python -m py_compile $(git ls-files '*.py')
   ```

## Adding new models to `parser.py`

The client parses notification payloads into typed dataclasses defined in
[`parser.py`](./cocon_client/parser.py). To add support for a new model:

1. **Create a dataclass** that represents the payload structure.
2. **Register the dataclass** with the JSON key returned by the server using the
   `@register_model("YourKey")` decorator.
3. If the payload needs special handling, implement a `from_dict` classmethod
   that converts the raw dictionary into the dataclass.
4. **Expose the model** in `cocon_client/__init__.py` by importing it and
   adding it to `__all__` so it is available to users of the package.
5. Update documentation and examples as appropriate.

## Submitting changes

- Keep commits focused and include descriptive messages.
- Ensure documentation is updated for any new features.
- Open a pull request against the `main` branch and describe your changes and
  how to test them.

Happy hacking!

