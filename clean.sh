#!/bin/bash
# Usage: clean.sh [target]

if [ $# -eq 0 ]
	then
		echo "rm -rf GMLs content heatmaps models webgraphs"
		rm -rf GMLs content heatmaps models webgraphs
	else
		for var in "$@"
		do
			echo "rm -rf GMLs/$var.txt content/$var.txt heatmaps/${var}_$var.html models/$var.txt webgraphs/$var"
		    rm -rf "GMLs/$var.txt" "content/$var.txt" "heatmaps/${var}_$var.html" "models/$var.txt" "webgraphs/$var"
		done
fi
