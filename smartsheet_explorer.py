from ast import parse
import copy
import os
import sys
import argparse
from tracemalloc import start
import smartsheet
from pptree import *


def init_client():
    token_name = "SMARTSHEET_ACCESS_TOKEN"
    token = os.getenv(token_name)
    if token == None:
        sys.exit(f"{token_name} not set")
    client = smartsheet.Smartsheet(token)
    client.errors_as_exceptions(True)
    return client


def parse_args():
    parser = argparse.ArgumentParser(
        description="Explore Smartsheet Workspaces")
    parser.add_argument('workspace_id')
    parser.add_argument('--output', choices=['tree', 'csv'], default='tree')
    parser.add_argument('--starting_folder_id', type=int,
                        help='Displays folders starting with and contained by this folder')
    parser.add_argument('--depth', type=int, default=0,
                        help='Depth from starting point to print (csv output only)')

    return parser.parse_args()


def find_folder_in(workspace, folder_id_to_find):
    search_domain = copy.copy(workspace.folders)

    i = 0
    while i < len(search_domain):
        folder = search_domain[i]
        if folder.id == folder_id_to_find:
            return folder
        search_domain += folder.folders
        i += 1

    return None


def print_csv(starting_folder, depth):
    starting_folder.depth = 0
    list = [starting_folder]
    i = 0
    while i < len(list):
        current = list[i]
        if current.depth == depth:
            print(f'"{current.name}","{current.id}"')
        else:
            for f in current.folders:
                f.name = f'{current.name}/{f.name}'
                f.depth = current.depth + 1
            list += current.folders
        i += 1


args = parse_args()
client = init_client()

workspace = client.Workspaces.get_workspace(
    workspace_id=args.workspace_id, load_all=True, include=["folders"])


if args.starting_folder_id == None:
    top = workspace
else:
    top = find_folder_in(workspace, args.starting_folder_id)
    if top == None:
        sys.exit("Folder not found")

if args.output == 'tree':
    print_tree(top, childattr="folders")
else:
    print_csv(top, args.depth)
