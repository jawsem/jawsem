#!/bin/bash
dep=$1
echo $dep
cd $dep
7z e *.rar
exit 0

