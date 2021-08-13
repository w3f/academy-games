{
  description = "Polkadot Experiment Platform";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-21.05";

    pypi-deps-db.url = "github:DavHau/pypi-deps-db";

    mach-nix.url = "github:DavHau/mach-nix/3.3.0";
    mach-nix.inputs.nixpkgs.follows = "nixpkgs";
    mach-nix.inputs.pypi-deps-db.follows = "pypi-deps-db";
  };

  outputs = { self, mach-nix, ... }: let
    requirements = builtins.readFile ./requirements.txt;
  in {
    devShell = builtins.mapAttrs
      (_: lib: lib.mkPythonShell {
        inherit requirements;
        _.otree.propagatedBuildInputs.mod = pySelf: oldAttrs: oldVal: oldVal ++ [ pySelf.psycopg2 ];
      }) mach-nix.lib;
  };
}
