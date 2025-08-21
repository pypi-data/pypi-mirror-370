# SPDX-FileCopyrightText: 2025 Justus Perlwitz
#
# SPDX-License-Identifier: MIT
{ python3
, python3Packages
}:
let
  pypkgs-build-requirements = {
    pyright = [ "setuptools" ];
  };
  playsound3 = python3Packages.callPackage ./playsound3.nix { };
in
python3Packages.buildPythonApplication {
  pname = "pomoglorbo";
  version = "2025.8.21";
  pyproject = true;

  src = ./.;

  build-system = with python3Packages; [
    hatchling
  ];

  dependencies = with python3Packages; [
    playsound3
    prompt-toolkit
  ];

  doCheck = true;
  nativeCheckInputs = with python3Packages; [
    ruff
    mypy
    reuse
    pythonImportsCheckHook
  ];
  checkPhase = ''
    runHook preCheck

    reuse lint
    ruff format --check .
    ruff check .
    mypy .

    runHook postCheck
  '';
  pythonImportsCheck = [
    "pomoglorbo"
  ];
  passthru = { inherit playsound3; };
}
