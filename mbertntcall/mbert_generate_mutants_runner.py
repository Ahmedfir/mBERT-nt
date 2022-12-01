import logging
import os
import sys
from os import makedirs
from os.path import join, isfile, expanduser, isdir
from pathlib import Path

from cbnt.locs_request import MbertFileRequest
from mbertntcall.output_mutants_mbert_ext_request_impl import OutputMutatedClasses

log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler(sys.stdout))


def get_args():
    import argparse
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-project_name', dest='project_name', default=None,
                        help='project name - by default the repo name.')
    parser.add_argument('-repo_path', dest='repo_path', help='target repo/project path.')
    parser.add_argument('-target_classes', dest='target_classes', help="classes to mutate separated by ','.")
    parser.add_argument('-output_dir', dest='output_dir', help="classes to mutate separated by ','.",
                        default='mbert_output')
    parser.add_argument('-mutated_classes_output_path', dest='mutated_classes_output_path',
                        default='mbert_mutated_classes')
    parser.add_argument('-java_home', dest='java_home', help='java home path', default=os.getenv("JAVA_HOME"))
    parser.add_argument('-all_lines', dest='all_lines', default=True)
    parser.add_argument('-max_processes', dest='max_processes', default=16)
    parser.add_argument('-force_reload', dest='force_reload', default=False)

    args = parser.parse_args()

    if args.repo_path is None or not isdir(
            expanduser(args.repo_path)) or args.target_classes is None or len(
            args.target_classes.split(',')) == 0:
        parser.print_help()
        raise AttributeError

    if args.java_home is None or not isdir(args.java_home):
        print("could not load JAVA_HOME automatically.")
        parser.print_help()
        raise AttributeError

    return args


def create_mbert_request(files, mutated_classes_output_dir: str, repo_path, output_dir: str,
                         max_processes_number: int = 4) -> OutputMutatedClasses:
    reqs = {MbertFileRequest(file) for file in files}
    return OutputMutatedClasses(mutated_classes_output_dir, max_processes_number, reqs, repo_path, output_dir)


def create_request(repo_path, target, output_dir, mutated_classes_output_path, class_files,
                   max_processes) -> OutputMutatedClasses:
    for c in class_files:
        if not isfile(join(repo_path, c)):
            log.error('target_classes should contain the path to the file from the project_path'
                      'such as project_path/target_class is the full path to the target_class.')
            raise AttributeError
    output_dir = join(expanduser(output_dir), target)
    mutated_classes_output_path = join(expanduser(mutated_classes_output_path), target)
    if not isdir(output_dir):
        makedirs(output_dir)
    if not isdir(mutated_classes_output_path):
        makedirs(mutated_classes_output_path)

    return create_mbert_request(class_files, mutated_classes_output_path, repo_path, output_dir, max_processes)


if __name__ == '__main__':
    args = get_args()
    job_name = Path(args.repo_path).name if args.project_name is None else args.project_name
    files = args.target_classes.split(',')

    request: OutputMutatedClasses = create_request(expanduser(args.repo_path), job_name,
                                                   expanduser(args.output_dir),
                                                   expanduser(args.mutated_classes_output_path),
                                                   files, args.max_processes)

    request.call(expanduser(args.java_home))