# Prospector profile utils

It contains some utility Prospector profiles.

## Usage

```bash
pip install prospector-profile-utils
```

Then, in your `.prospector.yaml` file, you can use the profiles like this:

```yaml
inherits:
  - utils:base
  - utils:c2cwsgiutils
  - utils:no-design-checks
```

It provide also an alternate base witch activate less strict checks:

```yaml
inherits:
  - utils:base-less-strict
```

Additional available profiles:

- `utils:fix`: Disables specific rules that are known to have reliability issues.
- `utils:autofix`: Enables automatic fixing capabilities for supported rules.
- `utils:tests`: Specifically designed for test files validation, recommended to use in combination with the `utils:fix` or `utils:pre-commit` profiles.
- `utils:pre-commit`: Specifically designed for pre-commit hooks.

## pre-commit profile

I use the `utils:tests` and `utils:pre-commit` profiles with the following precommit configuration to have the ruff checks with auto-fix on all the files with a specific profile for the tests.

```yaml
repos:
  - repo: https://github.com/PyCQA/prospector
    rev: v<rev>
    hooks:
      - id: prospector
        args:
          - --die-on-tool-error
          - --output-format=pylint
          - --profile=utils:pre-commit
          - --profile=.prospector.yaml
        additional_dependencies:
          - prospector-profile-duplicated==<rev> # pypi
          - prospector-profile-utils==<rev> # pypi
      - id: prospector
        args:
          - --die-on-tool-error
          - --output-format=pylint
          - --profile=utils:pre-commit
          - --profile=utils:tests
        additional_dependencies:
          - prospector-profile-utils==<rev> # pypi
```

## Contributing

Install the pre-commit hooks:

```bash
pip install pre-commit
pre-commit install --allow-missing-config
```
