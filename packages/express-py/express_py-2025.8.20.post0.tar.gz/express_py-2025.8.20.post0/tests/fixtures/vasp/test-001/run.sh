#!/usr/bin/env bash

module add vasp/535-g-485-ompi-110

mpirun --allow-run-as-root -np 1 vasp &> vasp.out
