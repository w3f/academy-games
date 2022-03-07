{
  description = "Polkadot Experiment Platform";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-21.11";

    pypi-deps-db.url = "github:DavHau/pypi-deps-db";
    pypi-deps-db.inputs.nixpkgs.follows = "nixpkgs";
    pypi-deps-db.inputs.mach-nix.follows = "mach-nix";

    mach-nix.url = "github:DavHau/mach-nix/3.4.0";
    mach-nix.inputs.nixpkgs.follows = "nixpkgs";
    mach-nix.inputs.pypi-deps-db.follows = "pypi-deps-db";
  };

  outputs = { self, nixpkgs, mach-nix, ... }: let
    # Build python environment with mach-nix and patched otree
    mkPython = lib: lib.mkPython {
      requirements = builtins.readFile ./requirements.txt;
      _.otree = {
        patches = [ ./.nix/otree-login-logging.patch ];
        propagatedBuildInputs.mod = pyPkgs: _: old: old ++ [ pyPkgs.psycopg2 ];
      };
    };

    # Build python env and return as shell
    mkShell = _: lib: (mkPython lib).env;

    # Build otree instance script from python env
    mkScript = system: lib:
      nixpkgs.legacyPackages.${system}.writeScriptBin "polkadot-experiments" ''
        cd ${self} && ${mkPython lib}/bin/otree $@
      '';
  in {
    devShell = builtins.mapAttrs mkShell mach-nix.lib;
    defaultPackage = builtins.mapAttrs mkScript mach-nix.lib;
  };
}
