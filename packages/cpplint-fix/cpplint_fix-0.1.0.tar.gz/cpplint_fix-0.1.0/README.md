# cpplint-fix

The [Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html) sets some conventions for how to write C++ code that have often been adopted as a good stylistic standard by C++ developers. As it happens, usually, when it comes to these styles, it's very convenient to have automated tools to detect or even fix any errors, which can then be made part of automated pipelines or pre-commit hooks to enforce the chosen style.

[`cpplint`](https://github.com/cpplint/cpplint) is a Python script that detects and enforces many of the rules in that style guide, especially surrounding things like spaces, comments, indents and so on. This is a useful tool when writing C++ code following the guide.

However, there is one thing `cpplint` does not do: it does not *fix* any of the problems.

`cpplint-fix` is meant as a script that builds on top of `cpplint` (plus a couple other very light dependencies) to fix some of the more trivial style problems detected, the ones that likely don't require any developer intervention and can be safely automated. You can find the list of currently supported codes [here](./CODES.md), though note that some code refer to *multiple* error types (like `whitespace/indent`) and in that case I don't guarantee that they're all covered. I mean to grow the functionality with time as I find new candidates to rules that are manageable, but I also provide a configuration file option to exclude rules or files for which this script just doesn't work within your specific codebase (or maybe that you selected to not enforce on purpose).

Either way, `cpplint-fix` should be a help keeping your C++ code clean and well formatted.

## Installation

You can install `cpplint-fix` using pip directly from the Python Package Index:

```bash
pip intall cpplint-fix
```


## Usage

Run `cpplint-fix` on a file or directory:

```bash
cpplint-fix <input>
```

Where `<input>` is a C++ source file or a directory containing source files.

### Options

- `--output`, `-o`   Output directory for fixed files (optional)
- `--config`, `-c`   Path to a YAML configuration file (optional)
- `--dry-run`        Only print the changes without applying them

### Example

```bash
# Fix all files in the src/ directory and write results to fixed/
cpplint-fix src/ --output fixed/

# Run in dry-run mode (no files are changed)
cpplint-fix src/ --dry-run

# Use a custom configuration file
cpplint-fix src/ --config config.yaml
```

## Configuration


You can provide a YAML configuration file to customize which rules or files to exclude from automatic fixing. The configuration file is written in YAML and supports the following fields:

### Configuration Fields

- `exclude_rules` (list of strings):
	- A list of cpplint error codes (e.g., `whitespace/indent`, `whitespace/blank_line`) to exclude from fixing. If a rule is listed here, `cpplint-fix` will not attempt to fix errors of that type.

- `exclude_files` (list of regex patterns as strings):
	- A list of regular expression patterns (as strings) that match file paths to exclude from fixing. Any file whose path matches one of these patterns will be skipped.

#### Example Configuration

```yaml
exclude_rules:
	- whitespace/indent
	- whitespace/blank_line

exclude_files:
	- ".*test/.*"           # Exclude all files in any 'test' directory
	- ".*main.cpp$"         # Exclude files named 'main.cpp'
```

#### Field Details

- **exclude_rules**: The list should contain cpplint error codes as strings. You can find the list of supported codes in [CODES.md](./CODES.md) or by running `python -m cpplint_fix.edits`.

- **exclude_files**: Each entry should be a valid Python regular expression string. The regex is matched against the full file path. For example, `.*test/.*` will match any file in a directory named `test`.

#### Notes

- If the configuration file is missing or a field is omitted, the default is to not exclude any rules or files.
- Extra fields in the YAML file are not allowed and will cause an error.

For more details, see the docstring in `src/cpplint_fix/config.py`.

## License

See [LICENSE](LICENSE).
