# Copyright 2024 Efabless Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
{
  stdenv,
  lib,
  nix-gitignore,
  buildPythonPackage,
  setuptools,
  setuptools_scm,

  # Tools
  klayout-gdsfactory,
  magic-vlsi,
  netgen,
  ciel,
  xschem,
  ngspice,
  xyce,
  
  # Python
  matplotlib,
  numpy,
  scipy,
  pillow,
  tkinter,
  rich,
}: let

  self = buildPythonPackage rec {
      pname = "cace";
      format = "pyproject";

      version_file = builtins.readFile ./cace/__version__.py;
      version_list = builtins.match ''.+''\n__version__ = '([^']+)'.+''\n.+''$'' version_file;
      version = builtins.head version_list;

      src = [
        ./README.md
        ./pyproject.toml
        (nix-gitignore.gitignoreSourcePure "__pycache__" ./cace)
        ./requirements.txt
      ];
      
      unpackPhase = ''
        echo $src
        for file in $src; do
          BASENAME=$(python3 -c "import os; print('$file'.split('-', maxsplit=1)[1], end='$EMPTY')")
          cp -r $file $PWD/$BASENAME
        done
        ls -lah
      '';

      buildInputs = [
        setuptools
        setuptools_scm
      ];
      
      includedTools = if stdenv.hostPlatform.isDarwin
        then
      ([
        klayout-gdsfactory
        magic-vlsi
        netgen
        ngspice
        xschem
      ])
        else
      ([
        klayout-gdsfactory
        magic-vlsi
        netgen
        ngspice
        xschem
        xyce
      ]);

      propagatedBuildInputs = [
        # Python
        matplotlib
        numpy
        scipy
        pillow
        ciel
        tkinter
        rich
      ]
      ++ self.includedTools;

      computed_PATH = lib.makeBinPath self.propagatedBuildInputs;

      # Make PATH available to CACE subprocesses
      makeWrapperArgs = [
        "--prefix PATH : ${self.computed_PATH}"
      ];

      meta = with lib; {
        description = "Circuit Automatic Characterization Engine";
        homepage = "https://github.com/fossi-foundation/cace";
        mainProgram = "cace";
        license = licenses.asl20;
        platforms = platforms.linux ++ platforms.darwin;
      };
    };
  in
    self
