#!/bin/bash

file="Vagrantfile"
filem="${file}.bak"
cp -p $file $filem
[[ ! -z $(grep "config\.ssh\.username" $filem) ]] && sed '/config.ssh.username = "p4"/d' $filem > $file
rm -f $filem
