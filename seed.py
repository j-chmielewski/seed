import sys
from os.path import expanduser, join

from git import Repo
from git.exc import NoSuchPathError
from colorama import init, Fore, Style


SEED_LIST = join(expanduser('~'), '.seedlist')

def print_help():
    print('TODO: help message')


def get_seeds():
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

    return seeds


def print_seeds():
    seeds = get_seeds()
    for commit, tag in seeds.items():
        print("{}{}\t{}{}\t{}{}{}".format(Fore.CYAN, commit, Fore.YELLOW, str(tag), Fore.WHITE, tag.tag.message, Style.RESET_ALL))


def add_seed():
    # TODO
    print("{}Add seed: not implemented{}".format(Fore.RED, Style.RESET_ALL))


def plant_seed(seed_id=None):
    if not seed_id:
        print("{}Missing seed id{}\n".format(Fore.RED, Style.RESET_ALL))
        print_help()
        sys.exit(1)


if __name__ == '__main__':
    init()
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)

    command = sys.argv[1]
    if command == 'list':
        print_seeds()
    elif command == 'add':
        add_seed(*sys.argv[2:])
    elif command == 'plant':
        plant_seed(*sys.argv[2:])
    else:
        print_help()
        exit(1)
