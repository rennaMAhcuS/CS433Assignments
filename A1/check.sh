#!/usr/bin/bash

num=3

if [[ $# -gt 1 ]]; then
    echo "Usage: ./check.sh <num-of-tests>"
    exit 1
elif [[ $# -eq 1 ]]; then
    num=$1
fi

for (( i = 0 ; i <= num ; i++ )); do
    echo "Test $i"
    echo "expected: $(cat outputs/output$i.txt)"
    echo "got: $(python3 solve.py inputs/input$i.smt2)"
    echo "-------------------------------------"
done
