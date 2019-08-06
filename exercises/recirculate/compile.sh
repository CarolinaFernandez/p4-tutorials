#!/bin/bash

p4c-bm2-ss --p4v 16 --p4runtime-files $(basename $PWD).p4.p4info.txt $(basename $PWD).p4
