#!/bin/bash

# Return the full path of a file
# Will work for soft links

[[ ! $# -eq 1 ]] && echo "$0 <file>" && exit 1
f=`cd \`dirname $1\`; pwd`/`basename $1`
[[ -e $f ]] && echo $f || (echo -e "Error!\n$f\nDo not exist!\n" 1>&2 && exit 1 )
