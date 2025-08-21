# SPDX-FileCopyrightText: 2023-2025 Justus Perlwitz
#
# SPDX-License-Identifier: MIT

{
  description = "Pomoglorbo";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs/25.05";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        packages = rec {
          pomoglorbo = pkgs.callPackage ./build.nix { };
          playsound3 = pomoglorbo.playsound3;
          default = pomoglorbo;
        };

        devShells.default = pkgs.mkShell {
          buildInputs = [ pkgs.reuse pkgs.nix-tree ];
        };
      });
}
