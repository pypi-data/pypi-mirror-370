# SPDX-FileCopyrightText: 2025 Justus Perlwitz
#
# SPDX-License-Identifier: MIT

{ lib
, buildPythonPackage
, fetchPypi

, hatchling
, pyright
, pytest
, ruff
, pytestCheckHook
, typing-extensions
}:

buildPythonPackage rec {
  pname = "playsound3";
  version = "3.2.4";
  pyproject = true;

  build-system = [
    hatchling
  ];

  src = fetchPypi {
    inherit pname version;
    hash = "sha256-p6f3EQL9ipQzefWvKahycVEZQaGYZB11Y7EIhIGkXg0=";
  };

  nativeCheckInputs = [
    pyright
    pytest
    ruff
    pytestCheckHook
    typing-extensions
  ];

  disabledTestPaths = [
    # urllib.error.URLError: <urlopen error [Errno 8] nodename nor servname provided, or not known>
    "tests/test_functionality.py"
  ];

  doCheck = true;
  # https://github.com/sjmikler/playsound3/blob/main/.github/workflows/check-code-quality.yaml
  preCheck = ''
    ruff check .
    ruff format . --check
    pyright playsound3
  '';
}
