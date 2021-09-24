{
  description = "Polkadot Experiment Platform";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-21.05";

    pypi-deps-db.url = "github:DavHau/pypi-deps-db";
    pypi-deps-db.inputs.nixpkgs.follows = "nixpkgs";
    pypi-deps-db.inputs.mach-nix.follows = "mach-nix";

    mach-nix.url = "github:DavHau/mach-nix/3.3.0";
    mach-nix.inputs.nixpkgs.follows = "nixpkgs";
    mach-nix.inputs.pypi-deps-db.follows = "pypi-deps-db";
  };

  outputs = { self, nixpkgs, mach-nix, ... }: let

    mkPython = lib: lib.mkPython {
      requirements = builtins.readFile ./requirements.txt;
      _.otree.propagatedBuildInputs.mod = pySelf: oldAttrs: oldVal: oldVal ++ [ pySelf.psycopg2 ];
    };

    mkShell = _: lib: (mkPython lib).env;

    mkScript = system: lib:
      nixpkgs.legacyPackages.${system}.writeScriptBin "polkadot-experiments" ''
        cd ${self} && ${mkPython lib}/bin/otree $@
      '';
  in {
    devShell = builtins.mapAttrs mkShell mach-nix.lib;
    defaultPackage = builtins.mapAttrs mkScript mach-nix.lib;
  };
}
