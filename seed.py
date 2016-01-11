#!/usr/bin/env python

import sys
from subprocess import call
from os.path import expanduser, join

from git import Git, Repo
from git.exc import NoSuchPathError
from colorama import init, Fore, Style


SEED_LIST = join(expanduser('~'), '.seedlist')
HELP_STRING = """
Usage:

seed <command> [<args>]

Commands:

\tlist\t\t\t\tlists available seeds
\tplant <seed_id> <target_dir>\tplants specified seed in target_dir
"""


def cprint(message, color=Style.RESET_ALL):
    print("{}{}{}".format(color, message, Style.RESET_ALL))


class Seed(object):

    def __init__(self, seed_list=SEED_LIST):
        self.seed_list = seed_list

    def print_help(self):
        print(HELP_STRING)

    def rage_quit(self, message):
        cprint(message, Fore.RED)
        self.print_help()
        sys.exit(1)

    def get_seeds(self):
        repos = []
        with open(self.seed_list, 'r') as seed_list:
            for path in seed_list:
                try:
                    repos.append(Repo(path.strip()))
                except NoSuchPathError:
                    cprint("WARN: Path {} is not a valid git repository".format(path.strip()), Fore.RED)

        seeds = {}
        for repo in repos:
            for tag in repo.tags:
                if str(tag).startswith('seed'):
                    seeds[str(tag.commit)] = tag

        return seeds

    def print_seeds(self):
        seeds = self.get_seeds()
        for commit, tag in seeds.items():
            print("{}{}\t{}{}\t{}{}{}".format(Fore.CYAN, commit, Fore.YELLOW, str(tag), Fore.WHITE, tag.tag.message, Style.RESET_ALL))

    def plant_seed(self, seed_id=None, target_dir=None):
        if not seed_id or not target_dir:
            self.rage_quit("Missing arguments, seed plant failed")

        seeds = self.get_seeds()
        tagref = seeds.get(seed_id, None)
        if not tagref:
            self.rage_quit("Seed id {} not found".format(seed_id))

        git = Git(tagref.repo.working_dir)
        current_commit = str(Repo(tagref.repo.working_dir).commit())
        cprint("Current commit: {}".format(current_commit), Fore.GREEN)
        dirty = tagref.repo.is_dirty()

        cprint("Working directory {}".format('dirty' if dirty else 'clean'), Fore.GREEN)
        if dirty:
            cprint("--> git stash", Fore.YELLOW)
            git.stash()

        cprint("--> git checkout {}".format(seed_id), Fore.YELLOW)
        git.checkout(seed_id)

        try:
            cprint("Copying seed directory: {}".format(tagref.repo.working_dir), Fore.GREEN)
            call(["cp", "-r", tagref.repo.working_dir, target_dir])
        except OSError as error:
            cprint("Copying directory failed:\n{}".format(error), Fore.RED)
        finally:
            if dirty:
                cprint("--> git stash apply", Fore.YELLOW)
                git.stash('apply')

            cprint("--> git checkout {}".format(current_commit), Fore.YELLOW)
            git.checkout(current_commit)


if __name__ == '__main__':
    init()
    seed = Seed()
    if len(sys.argv) < 2:
        seed.print_help()
        sys.exit(1)

    command = sys.argv[1]
    if command == 'list':
        seed.print_seeds()
    elif command == 'plant':
        seed.plant_seed(*sys.argv[2:])
    else:
        seed.rage_quit("Unknown command {}".format(command))
        sys.exit(1)
