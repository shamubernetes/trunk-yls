#!/usr/bin/env bash

if [ -z "$1" ]; then
  echo "Usage: $0 <file>"
  exit 1
fi

if [ ! -f "$1" ]; then
  echo "File not found: $1"
  exit 1
fi

echo_message() {
  echo '
  [
  {
    "message": "'"$1"'",
    "code": "'"$2"'",
    "severity": "Error",
    "range": {
      "start": {
        "line": 0,
        "character": 0
      },
      "end": {
        "line": 0,
        "character": 0
      }
    }
  }
]'
}

top_comment=$(yq 'head_comment' "$1")

# check if the file has a top comment
if [ "$top_comment" == "null" ]; then
  echo_message "No YLS Comment found at the top of the file" "no-comment"
  exit 1
fi

# check if top comment starts with "yaml-language-server"
if ! echo "$top_comment" | grep -q "^yaml-language-server"; then
  echo_message "YLS not found in top comment" "no-yls"
  exit 1
fi

# check if schema is present in the top comment
#shellcheck disable=SC2016
if ! echo "$top_comment" | grep -q '$schema='; then
  echo_message "Schema not found in top comment" "no-schema"
  exit 1
fi

# check if schema has `kubernetes-schemas` in it
if echo "$top_comment" | grep -q "kubernetes-schemas"; then
  echo_message "kubernetes-schemas is not allowed in the schema" "wrong-schema"
  exit 1
fi

exit 0
