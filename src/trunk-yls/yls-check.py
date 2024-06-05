#!/usr/bin/env python3

import sys
import os
import json
from ruamel.yaml import YAML

def echo_message(line, message, code):
    return {
        "message": message,
        "code": code,
        "severity": "Error",
        "range": {
            "start": {
                "line": line,
                "character": 0
            },
            "end": {
                "line": line,
                "character": 0
            }
        }
    }

def read_yaml_documents(file_path):
    yaml = YAML()
    with open(file_path, 'r') as file:
        documents = list(yaml.load_all(file))
    return documents

def get_top_comment(document):
    if hasattr(document, 'ca') and document.ca.comment and document.ca.comment[1]:
        return document.ca.comment[1][0].value.strip()
    return None


def main():
    if len(sys.argv) < 2:
        print("Usage: {} <file1> <file2> ...".format(sys.argv[0]))
        sys.exit(1)

    file_paths = sys.argv[1:]
    messages = []

    for file_path in file_paths:
        if not os.path.isfile(file_path):
            print(f"File not found: {file_path}")
            continue

        documents = read_yaml_documents(file_path)

        for doc in documents:
            if doc is None:
                continue

            line_num = doc.lc.line if hasattr(doc, 'lc') else 0
            top_comment = get_top_comment(doc)
            if top_comment is None:
                messages.append(
                    echo_message(line_num,
                                 "No YLS Comment found beginning document",
                                 "no-comment"))
                continue

            if not top_comment.startswith("# yaml-language-server"):
                messages.append(
                    echo_message(line_num, "YLS not found in top comment",
                                 "no-yls"))
                continue

            if '$schema=' not in top_comment:
                messages.append(
                    echo_message(line_num, "Schema not found in top comment",
                                 "no-schema"))
                continue

            if "kubernetes-schemas" in top_comment:
                messages.append(
                    echo_message(
                        line_num,
                        "kubernetes-schemas is not allowed in the schema",
                        "wrong-schema"))
                continue

    if messages:
        print(json.dumps(messages, indent=2))

if __name__ == "__main__":
    main()
