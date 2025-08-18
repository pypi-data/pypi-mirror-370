# (Fork) 0.0.13 (2025-08-17)

- Merged in the latest changes from upstream (version 0.17)
- Added `tox.ini` for local tox tests

# 0.17 (2025-??-??)

- General: Replace poetry with hatchling (thanks to @LecrisUT)
- General: Drop support for Python 3.6 and 3.7 (thanks to @LecrisUT)
- General: Officially support Python 3.13 (thanks to @mauvilsa)
- General: Publish packages to PyPI with digital attestations (thanks to @mauvilsa)
- Google: Fix multi-line parameter definitions (thanks to @coolbeevip)
- Attrdoc: Remove use of deprecated ast classes (thanks to @fedepell)

# (Fork) 0.0.12 (2025-01-13)

- Tweaked how to calculate the size of a `Docstring` object

# (Fork) 0.0.11 (2025-01-12)

- Added calculation of the size of a `Docstring` object

# (Fork) 0.0.10 (2025-01-10)

- For numpy style, raise `ParseError` when a section with non-empty contents is detected
  but nothing can be parsed

# (Fork) 0.0.9 (2024-06-26)

- Switched to pprint to show details of a `Docstring` object

# (Fork) 0.0.8 (2024-06-23)

- Added support for parsing attributes from Sphinx-style docstrings
- Dropped support for Python 3.6 because it doesn't support data classes

# (Fork) 0.0.7 (2024-06-22)

- Made "Attributes" a separate section from "Parameters" (for Google, Numpy, and Sphinx
  styles)

# (Fork) 0.0.6 (2024-06-22)

- Merged in the latest changes from upstream (version 0.16)

# 0.16 (2024-03-15)

- Parser: add a new property, `description`, that combines short and long
  descriptions into a single string (thanks to @pR0Ps)
- General: support Python 3.12 (thanks to @mauvilsa)

# (Fork) 0.0.5 (2023-19-18)

- Google: Fix parsing issue of return section (which would not parse `dict[str, Any] | None: Something` correctly)

# (Fork) 0.0.4 (2023-08-28)

- Numpy: Add many_yields property

# (Fork) 0.0.3 (2023-08-28)

- Google, Numpy, Sphinx: Make "Yields" an official parsed section (`DocstringYields`)
  - This corresponds to a PR in the upstream repo that was open
    since June 2023 (https://github.com/rr-/docstring_parser/pull/79)


# (Fork) 0.0.2 (2023-08-26)

- Google: Added capability to parse the yields section


# (Fork) 0.0.1 (2023-08-18)

- Google: Fixed a bug where union style return types (such as `int | str`) are not parsed correctly (https://github.com/rr-/docstring_parser/issues/81)

# 0.15 (2022-09-05)

- Parser: add a new function, `parse_from_object`, that supports scattered
  docstrings (thanks to @mauvilsa)

# 0.14.1 (2022-04-27)

- Parser: fix autodetection (regression from 0.14)

# 0.14 (2022-04-25)

- Numpydoc: Improved support for Example / Examples section

# 0.13 (2021-11-17)

- Google: Added support for Example / Examples section

# 0.12 (2021-10-15)

- General: Added support for lone `:rtype:` meta information (thanks to @abergou)

# 0.11 (2021-09-30)

- General: Started tracking changes
- General: Added ability to combine function docstrings (thanks to @abergou)
- ReST: Added support for `:type:` and `:rtype:` (thanks to @abergou)
