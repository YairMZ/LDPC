#!/bin/bash

FILE=$1
DATE=`date '+%Y-%m-%d'`
PREFIX="last_modified_date: "
STRING="$PREFIX.*$"
SUBSTITUTE="$PREFIX$DATE"
if ! grep -q "$SUBSTITUTE" "$FILE"; then
  if grep -q "$PREFIX" "$FILE"; then
    sed -i '' "s/$(echo "$STRING")/$(echo "$SUBSTITUTE")/" $FILE
  else
    echo "Error!"
    echo "'$PREFIX' doesn't appear in $FILE"
    exit 1
  fi
fi