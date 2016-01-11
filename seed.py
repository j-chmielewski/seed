import sys
from subprocess import call
from os.path import expanduser, join

from git import Git, Repo
from git.exc import NoSuchPathError
from colorama import init, Fore, Style


SEED_LIST = join(expanduser('~'), '.seedlist')


class Seed(object):

    def __init__(self, seed_list=SEED_LIST):
        self.seed_list = seed_list

    def print_help(self):
        print('TODO: help message')

    def get_seeds(self):
        repos = []
        with open(self.seed_list, 'r') as seed_list:
            for path in seed_list:
                try:
                    repos.append(Repo(path.strip()))
                except NoSuchPathError:
                    print("{}WARN: Path {} is not a valid git repository{}".format(Fore.RED, path.strip(), Style.RESET_ALL))

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
            print("{}Missing arguments, seed plant failed{}\n".format(Fore.RED, Style.RESET_ALL))
            self.print_help()
            sys.exit(1)

        seeds = self.get_seeds()
        tagref = seeds.get(seed_id, None)
        if not tagref:
            print("{}Seed id {} not found\n".format(Fore.RED, seed_id, Style.RESET_ALL))
            sys.exit(1)

        git = Git(tagref.repo.working_dir)
        current_commit = str(Repo(tagref.repo.working_dir).commit())
        print("{}Current commit: {}{}".format(Fore.GREEN, current_commit, Style.RESET_ALL))
        dirty = tagref.repo.is_dirty()

        print("{}Working directory {}{}".format(Fore.GREEN, 'dirty' if dirty else 'clean', Style.RESET_ALL))
        if dirty:
            print("{}--> git stash{}".format(Fore.YELLOW, Style.RESET_ALL))
            git.stash()

        print("{}--> git checkout {}{}".format(Fore.YELLOW, seed_id, Style.RESET_ALL))
        git.checkout(seed_id)

        try:
            print("{}Copying seed directory: {}{}".format(Fore.GREEN, tagref.repo.working_dir, Style.RESET_ALL))
            call(["cp", "-r", tagref.repo.working_dir, target_dir])
        except OSError as error:
            print("{}Copying directory failed:\n{}{}".format(Fore.RED, error, Style.RESET_ALL))
        finally:
            if dirty:
                print("{}--> git stash apply{}".format(Fore.YELLOW, Style.RESET_ALL))
                git.stash('apply')

            print("{}--> git checkout {}{}".format(Fore.YELLOW, current_commit, Style.RESET_ALL))
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
        seed.print_help()
        exit(1)
