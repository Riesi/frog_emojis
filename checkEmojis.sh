#!/usr/bin/env bash

# Enables globstar to recursively go through folders
shopt -s globstar
errArr=()
for f in ./svg/**/*.svg 
do
  echo "Checking '$f'"
  
  # Checking if file contains space in path
  if [[ $f == *\ * ]] ; then
    errArr+=("$f contains a space!")
  fi
  
  # Save first few lines of file into variable to make parsing faster
  headfile=$(head -n 50 "$f")
  # Gets everything in between the viewBox quotes
  vbStr=${headfile}
  vbStr=${vbStr##*viewBox=\"}
  vbStr=${vbStr%%\"*}

  # sets x, y, width, height params
  vbArr=($vbStr)
  vbX=${vbArr[0]}
  vbY=${vbArr[1]}
  vbW=${vbArr[2]}
  vbH=${vbArr[3]}

  # Check that viewbox' x and y are 0
  if [[ $vbX != 0 || $vbY != 0 ]] ; then
    errArr+=("$f has viewBox' x: $vbX and y: $vbY")
  fi

  # Check that viewbox' width and height are equal
  if [[ $vbW != $vbH ]] ; then
    errArr+=("$f has viewbox -width: $vbW and -height: $vbH")
  fi

  # Check if normal width/height parameters exist and
  # if yes, compare them with viewBox height/width
  svgTags=${headfile}
  svgTags=${svgTags##*\<svg}
  svgTags=${svgTags%%\>*}
  
  # Width comparison
  if [[ $svgTags == *width* ]] ; then
    w=${svgTags##*width=\"}
    w=${w%%\"*}
    if [[ $w != $vbW ]] ; then
      errArr+=("$f has width: $w but viewbox-width: $vbW")
    fi
  fi

  # Height comparison
  if [[ $svgTags == *height* ]] ; then
    h=${svgTags##*height=\"}
    h=${h%%\"*}
    if [[ $h != $vbH ]] ; then
      errArr+=("$f has height: $h but viewbox-height: $vbH")
    fi
  fi
  
  # Check that svg is not 1 line
  if [[ $(wc -l < "$f") == 0 ]] ; then
    errArr+=("$f is only one line!")
  fi
done

# Results
# If the error Array is not empty, print everything from it and error out
# Otherwise exit normally
echo "--------------------"
if [[ ${#errArr[@]} != 0 ]] ; then
  for errMess in "${errArr[@]}"
  do
    echo $errMess
  done
  exit 1
fi
echo "No Errors!"
