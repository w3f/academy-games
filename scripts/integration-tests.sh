#!/bin/bash

source /scripts/common.sh
source /scripts/bootstrap-helm.sh


run_tests() {
    echo Running tests...

    wait_pod_ready otree
}

teardown() {
    helm delete otree
}

main(){
    trap teardown EXIT

    /scripts/build-helmfile.sh

    run_tests
}

main
