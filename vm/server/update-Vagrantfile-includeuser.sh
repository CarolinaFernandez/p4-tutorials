#!/bin/bash

file="Vagrantfile"
filem="${file}.bak"
cp -p $file $filem
[[ -z $(grep "config\.ssh\.username" $filem) ]] && sed '/\ \ config.ssh.forward_x11.*/a\ \ config.ssh.username = "p4"' $filem > $file
rm -f $filem
