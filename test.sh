#!/bin/bash
# 200.33.163

echo $1

for i in {1..254}
do
    dig -x "$1.$i" | grep "PTR"
done
