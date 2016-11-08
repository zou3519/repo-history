#!/bin/bash
# Usage: clean.sh [target]

if [ $# -eq 0 ]
	then
		rm -rf GMLs content heatmaps models webgraphs
	else
		for var in "$@"
		do
		    rm -rf "GMLs/$var.txt" "content/$var.txt" "heatmaps/$var_$var.html" "models/$var" "webgraphs/$var"
		done
fi
