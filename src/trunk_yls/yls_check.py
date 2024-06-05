#!/usr/bin/env python3

import sys
import os
import json
import argparse
from urllib.parse import urlparse
from ruamel.yaml import YAML


def echo_message(line, char_start, char_end, message, code):

    return {
        "message": message,
        "code": code,
        "severity": "Error",
        "range": {
            "start": {
                "line": line,
                "character": char_start
            },
            "end": {
                "line": line,
                "character": char_end
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


def read_config(config_path):
    yaml = YAML()
    with open(config_path, 'r') as file:
        config = yaml.load(file)
    return config.get('excluded_domains', [])


def extract_domain_from_schema(schema):
    parsed_url = urlparse(schema)
    return parsed_url.netloc


def main():
    parser = argparse.ArgumentParser(description='Process YAML files.')
    parser.add_argument('--config', type=str, help='Path to the config file')
    parser.add_argument('files',
                        metavar='file',
                        type=str,
                        nargs='+',
                        help='YAML files to process')
    args = parser.parse_args()

    excluded_domains = []
    config_file = args.config if args.config else 'trunk-yls.yaml'

    if os.path.isfile(config_file):
        excluded_domains = read_config(config_file)
    elif args.config:
        print(f"Config file not found: {config_file}")
        sys.exit(1)

    file_paths = args.files
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
                    echo_message(line_num, 0, 0,
                                 "No YLS Comment found beginning document",
                                 "no-comment"))
                continue

            if not top_comment.startswith("# yaml-language-server"):
                messages.append(
                    echo_message(line_num, 0, 0,
                                 "YLS not found in top comment", "no-yls"))
                continue

            if '$schema=' not in top_comment:
                startLen = len("# yaml-language-server")
                endLen = len(top_comment)
                messages.append(
                    echo_message(line_num, startLen, endLen,
                                 "Schema not found in top comment",
                                 "no-schema"))
                continue
            schema_part = top_comment.split('$schema=')[1].strip()
            domain = extract_domain_from_schema(schema_part)

            if domain in excluded_domains:
                messages.append(
                    echo_message(line_num, 32, len(schema_part)+32,
                                 f"{domain} is not allowed in the schema",
                                 "wrong-schema"))
                continue

    if messages:
        print(json.dumps(messages, indent=2))


if __name__ == "__main__":
    main()
