[![CircleCI](https://circleci.com/gh/w3f/academy-games.svg?style=svg&circle-token=291abfc40771bd8f4372f3cb372cb321a2e47e35)](https://circleci.com/gh/w3f/academy-games)

# Polkadot Blockchain Academy Games

The academy uses a centralized wallet app:

 - [Wallet](./academy_wallet)
 - [Endcard](./academy_endcard)

Currently consists of the following experiments:

 - [Cournot Game](./academy_cournot)
 - [Guessing Game](./academy_guess)
 - [Prisoner Dilema](./academy_prisoner)
 - [Public Good](./academy_publicgood)
 - [Ultimatum Game](./academy_ultimatum)

All currency collected can the be used in a final auction:

 - [Auction](./academy_auction)

## How To Trigger the deployment pipeline

- for the helm chart, see https://github.com/w3f/polkadot-experiments#how-to-trigger-the-deployment-pipeline
- define a new image version [here](https://github.com/w3f/academy-games/blob/main/helmfile.d/config/otree-values.yaml.gotmpl#L1) and tag the new release accordingly
