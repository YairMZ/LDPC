#!/bin/bash

FILE=$1
DATE=`date '+%Y-%m-%d'`
PREFIX="last_modified_date: "
STRING="$PREFIX.*$"
SUBSTITUTE="$PREFIX$DATE"
if ! grep -q "$SUBSTITUTE" "$FILE"; then
  sed -i '' "1,/$(echo "$STRING")/ s/$(echo "$STRING")/$(echo "$SUBSTITUTE")/" $FILE
fi