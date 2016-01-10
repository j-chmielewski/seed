import sys
from os.path import expanduser, join
from collections import namedtuple

from git import Repo
from git.exc import NoSuchPathError
from colorama import init, Fore, Style
import argparse


SEED_LIST = join(expanduser('~'), '.seedlist')
SeedData = namedtuple('SeedData', ['repository', 'tag'])


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', help='Command to run')

    return parser


def list_seeds():
    repos = []
    with open(SEED_LIST, 'r') as seed_list:
        for path in seed_list:
            try:
                repos.append(Repo(path.strip()))
            except NoSuchPathError:
                print("{}WARN: Path {} is not a valid git repository{}".format(Fore.RED, path.strip(), Style.RESET_ALL))

    seeds = {}
    for repo in repos:
        for tag in repo.tags:
            if str(tag).startswith('seed'):
                seeds[tag.commit] = tag

    for commit, tag in seeds.items():
        print("{}{}\t{}{}\t{}{}{}".format(Fore.CYAN, commit, Fore.YELLOW, str(tag), Fore.WHITE, tag.tag.message, Style.RESET_ALL))

    return seeds


def add_seed():
    # TODO
    print("Add seed")


if __name__ == '__main__':
    init()
    parser = build_parser()
    args = parser.parse_args()

    switcher = {
        'list': list_seeds,
        'add': add_seed
    }
    command = switcher.get(args.command, parser.print_help)
    command()

