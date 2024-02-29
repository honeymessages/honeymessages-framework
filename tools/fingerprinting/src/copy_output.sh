#!/usr/bin/env bash

SCRIPT_DESTINATION="../../../backend/static/scripts/"
FEATURE_DESTINATION="../../../backend/run/fingerprinting/"

get_abs_filename() {
  # $1 : relative filename
  echo "$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
}

cp ../output/fingerprinting.js $SCRIPT_DESTINATION
echo "Script copied to $(get_abs_filename $SCRIPT_DESTINATION)"

cp ../output/feature_map.json $FEATURE_DESTINATION
cp ../config/features-in-scope.txt $FEATURE_DESTINATION

echo "Map files copied to $(get_abs_filename $FEATURE_DESTINATION)"
