#!/usr/bin/env bash

# This script removes all text between solutions tags "# BEGIN SOLUTION" and "# END SOLUTION"
# as well as "// BEGIN SOLUTION" and "// END SOLUTION" 
# 
# WARNING: Copy to intended directory before usage.
#
# Arguments:
# 	1. filename - name of the file to edit
# Sample usage: './remove_solution.sh hw01-sol.Rmd'

INFILE=$1
OUTFILE=${INFILE//-sol}

sed '/# BEGIN SOLUTION/,/# END SOLUTION/d' $INFILE > $OUTFILE
sed -i '.bak' '/\/\/ BEGIN SOLUTION/,/\/\/ END SOLUTION/d' $OUTFILE

rm -f ${OUTFILE}.bak