#!/bin/bash
# Lottery program for drawing prize winners after the race.
#
# :copyright: (c) 2016 Jim Enkel
# :license: BSD, see LICENSE for more details.
#
# return a random line from a $1, save state and
# only return the same line once.

# create a tmp file to contain all that already have been returned
tmpfile=/tmp/alreadyrandomized
touch $tmpfile

# check number of lines in input file and tmp file
lines_tmp=`cat $tmpfile | wc -l`
lines_file=`cat $1 | wc -l`

# if the tmp file contains the same number of rows as the input file
# every line in $1 has been returned once. Time to rm the tmp file
# and start over again
if [ "$lines_tmp" -eq "$lines_file" ]; then
  echo "end of file, remove $tmpfile"
  exit
fi

# get a random line, if exists in $tmpfile, get a new line
function printaline {
 line=`shuf -n1 $1`
 if grep --quiet "$line" $tmpfile; then
   printaline $1
 else
   echo $line >> $tmpfile
   echo $line
 fi
}

# start
printaline $1

# end of file
