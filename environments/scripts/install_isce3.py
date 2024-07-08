#!/opt/conda/bin/python
# The shebang should reflect the base environment (see BASE_ENV_PREFIX)

import argparse
import os
import pathlib
import signal
import subprocess
import sys

BASE_ENV_PREFIX = pathlib.Path('/opt/conda')  # Conda base environment prefix
CMAKE_CACHE_NAME = 'CMakeCache.txt'  # The filename for the CMake cache, assumed to be in the build dir
ENV_PREFIX_VAR = 'CONDA_PREFIX'  # The environment varialbe for the active Conda environment prefix
KEYBOARD_INTERRUPT_ES = 130  # Exit status to use for keyboard interrupt
ERROR_ES = 1  # Exit status to use for other caught errors

YES_RESPONSES = {'yes', 'ye', 'y'}  # Query responses that count as "yes" (lowercase, stripped)
NO_RESPONSES = {'no', 'n', ''}      # Query responses that count as "no" (lowercase, stripped)

OPTIONS: argparse.Namespace


def get_defaults(instance_type: str) -> argparse.Namespace:
    """Return the default options for the given instance type
    Does not depend on OPTIONS."""
    defaults = argparse.Namespace()
    
    home_dir = get_home_dir()
    this_repo_dir = get_this_repo_dir()
    
    match instance_type:
        case 'GPU':
            defaults.repo_dir = home_dir / 'isce3'
            defaults.env_name = 'isce3_src'
        case 'CPU':
            defaults.repo_dir = home_dir / 'isce3_cpu'
            defaults.env_name = 'isce3_src_cpu'
        case _:
            raise NotImplementedError(f"unknown instance type: {instance_type}")
    
    defaults.assume_yes = False
    
    defaults.version = 'develop'
    defaults.repo_url = 'https://github.com/isce-framework/isce3.git'
    defaults.fetch = True
    defaults.merge = True
    
    defaults.build_dir = defaults.repo_dir / 'build'
    defaults.clear_cmake_cache = True
    defaults.cmake_build_type = 'Release'
    defaults.make_jobs = None  # None means infinity
    
    defaults.envs_dir = home_dir / '.local' / 'envs'
    defaults.env_def_file = this_repo_dir / 'environments' / 'env_files' / 'isce3_src_conda_env.yml'
    
    defaults.conda_exec = BASE_ENV_PREFIX / 'condabin' / 'conda'
    defaults.mamba_exec = BASE_ENV_PREFIX / 'condabin' / 'mamba'
    defaults.git_exec = BASE_ENV_PREFIX / 'bin' / 'git'
    defaults.cmake_exec = defaults.envs_dir / defaults.env_name / 'bin' / 'cmake'
    defaults.make_exec = pathlib.Path('/usr/bin/make')
    
    return defaults


def main() -> None:
    global OPTIONS
    OPTIONS = get_options()
    
    if OPTIONS.env_prefix.exists():
        if OPTIONS.env_prefix.is_dir():
            if OPTIONS.env_prefix.samefile(BASE_ENV_PREFIX):
                print("You may not install ISCE3 into the base environment.")
                return
            active_prefix = get_env_prefix()
            if active_prefix is not None and active_prefix.samefile(OPTIONS.env_prefix):
                print("You may not install ISCE3 into the active environment.")
                print("Switch to a different environment (or deactivate Conda) and try again.")
                return
        else:
            print(f"There is a non-directory at {OPTIONS.env_prefix}.")
            if query("Would you like to remove it?"):
                run_command(['rm', '-f', OPTIONS.env_prefix],
                            f"error: removing non-directory at {OPTIONS.env_prefix} failed")
            else:
                return
    
    prev_version = get_prev_version()
    print(f"Going to install: {OPTIONS.version_str}")
    if prev_version is None:
        print(f"No {OPTIONS.instance_type} version of ISCE3 is currently installed.")
    else:
        print(f"Currently installed: {prev_version}")
    if not query("Would you like to proceed?"):
        return
    
    if repo_exists():
        print(f"ISCE3 repo found at {OPTIONS.repo_dir}")
        if OPTIONS.version is not None:
            if not working_tree_is_clean():
                print("There are uncommitted changes in the ISCE3 repo")
                print("If you would like to install from your working tree, use -v without specifying a version")
                if query("Would you like to discard uncommitted changes?"):
                    print("Discarding uncommitted changes")
                    discard_uncommitted_changes()
                else:
                    return
        if OPTIONS.fetch:
            print("Fetching new refs...")
            fetch_refs()
    else:
        print(f"ISCE3 repo not found at {OPTIONS.repo_dir}")
        ensure_available_repo_dir()
        print("Cloning ISCE3 repo...")
        clone_repo()
    if OPTIONS.version is not None:
        print(f"Checking out version {OPTIONS.version_str}")
        check_out_version()
    if OPTIONS.merge:
        branch_path = current_branch_path()
        if branch_path is not None:
            upstream = get_upstream_branch(branch_path)
            if upstream is not None:
                print(f"Merging upstream branch {upstream} into {OPTIONS.version_str}")
                # Passing in the upstream branch to override merge.defaultToUpstream configuration
                merge_into_current_branch(upstream)
            else:
                print(f"Branch {OPTIONS.version_str} has no upstream branch; skipping merge")
        else:
            print(f"{OPTIONS.version_str} is not a branch; skipping merge")
    
    print("Setting up Conda environments directory")
    set_up_envs_dir()
    print("Creating Conda environment (this will take a while)")
    create_env()
    print("Adding Conda environment to the ipykernel...")
    add_env()
    print("Setting environment variables in Conda environment")
    set_env_vars()
    
    make_build_dir()
    if OPTIONS.clear_cmake_cache:
        clear_cmake_cache()
    print("Building Make files...")
    build_make_files()
    print("Installing ISCE3 (this will take a while)")
    install()
    print(f"Successfully installed ISCE3 to Conda environment at {OPTIONS.env_prefix}")


def get_options() -> argparse.Namespace:
    """Return the options for the current instance type from the command-line arguments.
    Catch any usage errors or help requests and exit after handling them appropriately.
    Does not depend on OPTIONS."""
    instance_type = get_instance_type()
    print(f"Detected {instance_type} instance.")
    defaults = get_defaults(instance_type)
    parser = argparse.ArgumentParser(
        description="Install or switch versions of ISCE3",
        epilog=f"Note: Some of the above defaults were based on your detected instance type ({instance_type})",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument(
        '--assume-yes', '--yes', '-y',
        action='store_const',
        const=True,
        help="assume yes for any interactive queries")
    
    repo_group = parser.add_argument_group('ISCE3 Git repository')
    repo_group.add_argument(
        '--version', '-v',
        nargs='?',
        const=None,  # Used if option is present but value is omitted; None means working tree
        help="version (a tree-ish) to install (working tree if value is omitted)")
    repo_group.add_argument(
        '--repo-url', '-u',
        help="URL from which to clone the repo if it doesn't already exist")
    repo_group.add_argument(
        '--repo-dir', '-R',
        type=resolved_path,
        help="repo directory (the directory containing .git)")
    repo_group.add_argument(
        '--fetch',
        action=argparse.BooleanOptionalAction,
        help="fetch new refs before checking out the version")
    repo_group.add_argument(
        '--merge',
        action=argparse.BooleanOptionalAction,
        help="if version is a branch with an upstream branch, merge the upstream")
    
    env_group = parser.add_argument_group('ISCE3 Conda environment')
    env_group.add_argument(
        '--envs-dir', '-E',
        type=resolved_path,
        help="parent directory of the environment prefix")
    env_group.add_argument(
        '--env-name', '-n',
        help="environment name")
    env_group.add_argument(
        '--env-def-file', '-f',
        type=extant_file,
        help="environment definition file")
    
    build_group = parser.add_argument_group('build')
    build_group.add_argument(
        '--build-dir', '-B',
        type=resolved_path,
        help="build directory")
    build_group.add_argument(
        '--clear-cmake-cache',
        action=argparse.BooleanOptionalAction,
        help="clear the CMake cache before building")
    build_group.add_argument(
        '--cmake-build-type', '-t',
        help="CMAKE_BUILD_TYPE value to use when building")
    build_group.add_argument(
        '--make-jobs', '-j',
        nargs='?',
        const=None,  # Used if option is present but value is omitted; None means infinity
        type=int,
        help="number of job slots Make has when building (infinity if value is omitted)")
    
    exec_group = parser.add_argument_group('executables')
    exec_group.add_argument(
        '--conda-exec',
        type=extant_file,
        help="Conda executable")
    mamba_exec_group = exec_group.add_mutually_exclusive_group()
    mamba_exec_group.add_argument(
        '--mamba-exec',
        type=extant_file,
        help="Mamba executable")
    mamba_exec_group.add_argument(
        '--no-mamba',
        action='store_const',
        const=None,
        help="do not use Mamba (use Conda instead)",
        dest='mamba_exec')
    exec_group.add_argument(
        '--git-exec',
        type=extant_file,
        help="Git executable")
    exec_group.add_argument(
        '--cmake-exec',
        type=extant_file,
        help="CMake executable")
    exec_group.add_argument(
        '--make-exec',
        type=extant_file,
        help="Make executable")
    
    # Setting defaults.version to True to detect default and print additional message
    default_version = defaults.version
    defaults.version = True
    parser.set_defaults(**vars(defaults))
    # Not catching exceptions because argparse handles invalid args nicely
    options = parser.parse_args()
    
    if options.version is True:
        print(f"Using default version ({default_version}). Use -v to override this with any tree-ish.")
        options.version = default_version
    options.version_str = '<working tree>' if options.version is None else options.version
    options.env_prefix = options.envs_dir / options.env_name
    options.instance_type = instance_type
    if options.mamba_exec is None:
        options.mamba_exec = options.conda_exec
    return options



def repo_exists() -> bool:
    """Return whether the ISCE3 repository exists in its intended directory."""
    return (OPTIONS.repo_dir / '.git').exists()


def working_tree_is_clean() -> bool:
    """Return whether the ISCE3 repository working tree has no uncommitted changes."""
    # When a CPU instance is initially spun up, git diff-index indicates uncommitted changes when there are none
    # Running git diff beforehand seems to fix this issue
    args = [str(OPTIONS.git_exec), 'diff']
    run_command(args, "error: checking for uncommitted changes in the ISCE3 Git repo failed", cwd=OPTIONS.repo_dir)
    
    args = [str(OPTIONS.git_exec), 'diff-index', '--quiet', 'HEAD']
    cp = subprocess.run(args, capture_output=True, cwd=OPTIONS.repo_dir, text=True)
    # --quiet implies --exit-code, which makes it so an exit status of 1 indicates differences
    if cp.returncode == 0:
        return True
    elif cp.returncode == 1:
        return False
    else:
        eprint("error: checking for uncommitted changes in the ISCE3 Git repo failed")
        eprint("below are some details about the command that failed")
        eprint_completed_process(cp)
        sys.exit(ERROR_ES)

        
def discard_uncommitted_changes() -> None:
    """Discard uncommitted changes in the ISCE3 Git repo."""
    args = [OPTIONS.git_exec, 'reset', '--hard']
    run_command(args, "error: discarding uncommitted changes failed", cwd=OPTIONS.repo_dir)
        

def fetch_refs() -> None:
    """Fetch new refs in the ISCE3 repository from the default remote."""
    # Use --all because we can't know in advance which remote to use in the case of an unfetched commit hash
    args = [OPTIONS.git_exec, 'fetch', '--all']
    run_command(args, "error: pulling the ISCE3 Git repo failed", cwd=OPTIONS.repo_dir)


def ensure_available_repo_dir() -> None:
    """Exit with a helpful error message if the intended ISCE3 repository is not available for use."""
    if OPTIONS.repo_dir.exists():
        eprint(f"error: the intended ISCE3 repo path ({OPTIONS.repo_dir}) is occupied")
        eprint(f"try removing it or moving it to another location")
        eprint("to use another directory, change REPO_DIR at the top of this file")
        sys.exit(ERROR_ES)


def clone_repo() -> None:
    """Clone the ISCE3 repository to its indended directory."""
    args = [OPTIONS.git_exec, 'clone', OPTIONS.repo_url, OPTIONS.repo_dir]
    run_command(args, f"error: cloning the ISCE3 Git repo to {OPTIONS.repo_dir} failed")


def check_out_version() -> None:
    """Check out the ISCE3 repository's desired version.
    The version must not be the working tree."""
    args = [OPTIONS.git_exec, 'checkout', OPTIONS.version]
    run_command(args, "error: checking out the given ISCE3 version failed", cwd=OPTIONS.repo_dir)


def current_branch_path() -> str | None:
    """Return the path to the current branch relative to the .git directory.
    If there is no current branch, return None."""
    args = [OPTIONS.git_exec, 'symbolic-ref', '-q', 'HEAD']
    cp = subprocess.run(args, capture_output=True, cwd=OPTIONS.repo_dir, text=True)
    # -q makes it so a nonzero exit code with no standard error implies no current branch
    if cp.returncode < 0 or (cp.returncode > 0 and cp.stderr):
        eprint("error: finding the path of the branch for the ISCE3 version failed")
        eprint("below are some details about the command that failed")
        eprint_completed_process(cp)
        sys.exit(ERROR_ES)
    if cp.returncode > 0:
        return None
    return cp.stdout.strip()


def get_upstream_branch(branch_path: str) -> str | None:
    """Return the name of the upstream branch for the given branch (a path relative to the .git directory).
    If the given branch has no upstream branch, return None."""
    args = [OPTIONS.git_exec, 'for-each-ref', '--format=%(upstream:short)', branch_path]
    upstream_branch = run_command(args, "error: finding the upstream branch for the ISCE3 version failed", cwd=OPTIONS.repo_dir).strip()
    return upstream_branch if upstream_branch else None


def merge_into_current_branch(branch: str) -> None:
    """Merge the given branch into the current branch."""
    args = [OPTIONS.git_exec, 'merge', branch]
    run_command(args, (f"error: merging branch {branch} into ISCE3 version branch failed\n"
                       "if you made any local commits, you may need to resolve merge conflicts"), cwd=OPTIONS.repo_dir)



def set_up_envs_dir() -> None:
    """Create the Conda environments directory and configure Conda to recognize it."""
    args = ['mkdir', '-p', OPTIONS.envs_dir]
    run_command(args, f"error: creating {OPTIONS.envs_dir} directory failed")
    args = [OPTIONS.conda_exec, 'config', '--append', 'envs_dirs', OPTIONS.envs_dir]
    run_command(args, f"error: adding {OPTIONS.envs_dir} as a Conda environment directory failed")


def create_env() -> None:
    """Create the ISCE3 Conda environment."""
    args = [OPTIONS.mamba_exec, 'env', 'create', '-f', OPTIONS.env_def_file, '-p', OPTIONS.env_prefix, '--force']
    run_command(args, "error: creating the ISCE3 Conda environment failed")


def add_env() -> None:
    """Update the ipykernel to recognize the ISCE3 Conda environment."""
    args = [BASE_ENV_PREFIX / 'bin' / 'python', '-m', 'ipykernel', 'install', '--user', '--name', OPTIONS.env_name, '--display-name', OPTIONS.env_name]
    run_command(args, "error: udating the ipykernel to add the ISCE3 Conda environment failed", env_prefix=OPTIONS.env_prefix)

    
def set_env_vars() -> None:
    """Set the necessary environment variables in the ISCE3 Conda environment."""
    env_vars = {
        'ISCE3_BUILD_DIR': str(OPTIONS.build_dir),
        'CUDAHOSTCXX': 'x86_64-conda-linux-gnu-g++',
        'CC': 'x86_64-conda-linux-gnu-gcc',
        'CXX': 'x86_64-conda-linux-gnu-g++',
        'PYTHONPATH': f"{OPTIONS.build_dir / 'packages'}:{get_var('PYTHONPATH', BASE_ENV_PREFIX)}",
        'LD_LIBRARY_PATH': f"{OPTIONS.build_dir / 'lib64'}:{get_var('LD_LIBRARY_PATH', BASE_ENV_PREFIX)}",
    }
    args = [OPTIONS.conda_exec, 'env', 'config', 'vars', 'set', '-p', OPTIONS.env_prefix]
    args += [f'{k}={v}' for k, v in env_vars.items()]
    run_command(args, "error: setting environment variables in the ISCE3 Conda environment failed")


    
def make_build_dir() -> None:
    """Create the build directory if it doesn't already exist."""
    args = ['mkdir', '-p', OPTIONS.build_dir]
    run_command(args, f"error: creating build directory {OPTIONS.build_dir} failed")


def clear_cmake_cache() -> None:
    """Clear the CMake cache for the ISCE3 build."""
    cmake_cache = OPTIONS.build_dir / CMAKE_CACHE_NAME
    if not cmake_cache.exists():
        return
    if not cmake_cache.is_file():
        eprint(f"error: the expected CMake cache file path ({cmake_cache}) is occupied by a non-file")
        eprint(f"try removing it or moving it to another location")
        sys.exit(ERROR_ES)
    args = ['rm', '-f', cmake_cache]
    run_command(args, f"error: clearing the cmake cache (removing {cmake_cache}) failed")


def build_make_files() -> None:
    """Build the files required for Make to install ISCE3."""
    args = [OPTIONS.cmake_exec, f'-DCMAKE_BUILD_TYPE={OPTIONS.cmake_build_type}', f'-DCMAKE_INSTALL_PREFIX={OPTIONS.build_dir}', OPTIONS.repo_dir]
    # Unsure if cwd or env_prefix is necessary
    run_command(args, "error: building ISCE3 Make files with CMake failed", cwd=OPTIONS.build_dir, env_prefix=OPTIONS.env_prefix)


def install() -> None:
    """Run the Make target `install' to install ISCE3."""
    if OPTIONS.make_jobs is None:
        args = [OPTIONS.make_exec, '-j', 'install']
    else:
        args = [OPTIONS.make_exec, '-j', str(OPTIONS.make_jobs), 'install']
    # Unsure if env_prefix is necessary
    run_command(args, "error: installing ISCE3 with Make target `install' failed", cwd=OPTIONS.build_dir, env_prefix=OPTIONS.env_prefix)


    
def get_env_prefix() -> pathlib.Path | None:
    """Return the active Conda environment prefix.
    If Conda is inactive, return None."""
    return pathlib.Path(os.environ[ENV_PREFIX_VAR]) if ENV_PREFIX_VAR in os.environ else None


def get_prev_version() -> str | None:
    """Return the previously installed ISCE3 version.
    If the version cannot be determined or doesn't exist, return None."""
    args = ['python', '-c', "import isce3; print(isce3.__version__)"]
    version = run_command(args, env_prefix=OPTIONS.env_prefix, exit=False)
    return None if version is None else version.strip()

    
def get_instance_type() -> str:
    """Return the instance type corresponding to the running environment.
    Does not depend on OPTIONS."""
    args = ['command', '-v', 'nvcc']
    cp = subprocess.run(args, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    return 'GPU' if cp.returncode == 0 else 'CPU'


def get_var(var: str, env_prefix: pathlib.Path) -> str:
    """Return the stripped value of the environment variable in the given Conda environment.
    If the variable is not set, return the empty string."""
    args = ['python', '-c', f"import os; print(os.environ[{repr(var)}] if {repr(var)} in os.environ else '')"]
    return run_command(
        args,
        f"error: reading environment variable {var} from Conda environment {env_prefix} failed",
        env_prefix=env_prefix).strip()


def get_home_dir() -> pathlib.Path:
    """Return the user's home directory.
    Does not depend on OPTIONS."""
    try:
        return pathlib.Path.home()
    except RuntimeError:
        eprint("error: home directory could not be resolved")
        sys.exit(ERROR_ES)


def get_this_repo_dir() -> pathlib.Path:
    """Return the sds-ondemand repo directory.
    Does not depend on OPTIONS."""
    # If the location of the install_isce3.py script is changed, this function should be updated accordingly.
    return get_this_file().parent.parent.parent


def get_this_file() -> pathlib.Path:
    """Return the path to this file (install_isce3.py)."""
    try:
        return pathlib.Path(sys.argv[0]).resolve(strict=True)
    except FileNotFoundError:
        eprint("error: path to install_isce3.py script could not be resolved")
        sys.exit(ERROR_ES)
    except RuntimeError:
        eprint("error: infinite loop encountered while resolving path to install_isce3.py script")
        sys.exit(ERROR_ES)



def run_command(args: list[str], error_message: str | None = None, cwd: pathlib.Path | None = None,
                env_prefix: pathlib.Path | None = None, exit: bool = True) -> str | None:
    """Run the command given by args and return its output if successful.
    Otherwise, if exit is True, exit with the given error message and additional details, and if exit is False, return None.
    cwd overrides the current working directory when the command is run.
    env_prefix overrides the Conda environment in which the command is run.
    """
    if env_prefix is not None:
        args = [OPTIONS.mamba_exec, 'run', '-p', env_prefix] + args
    cp = subprocess.run(args, capture_output=True, cwd=cwd, text=True)
    if cp.returncode != 0:
        if not exit:
            return None
        if error_message is not None:
            eprint(error_message)
        eprint("below are some details about the command that failed")
        eprint_completed_process(cp)
        sys.exit(ERROR_ES)
    return cp.stdout


def query(prompt: str) -> bool:
    """Query to user interactively for a yes/no; return True for yes and False for no."""
    if OPTIONS.assume_yes:
        return True
    if '' in YES_RESPONSES:
        options = "Y/n"
    elif '' in NO_RESPONSES:
        options = "y/N"
    else:
        options = "y/n"
    while True:
        response = input(f"{prompt} [{options}] ").strip().lower()
        if response in YES_RESPONSES:
            return True
        if response in NO_RESPONSES:
            return False


def eprint(*args, **kwargs) -> None:
    """Print to standard error.
    file must not be specified as a keyword argument."""
    print(*args, file=sys.stderr, **kwargs)

    
def eprint_completed_process(cp: subprocess.CompletedProcess) -> None:
    """Print the given completed process to standard error in a human-readable way."""
    eprint(f"Command: {cp.args}")
    if cp.returncode < 0:
        signal = signal_num_to_signal(-cp.returncode)
        if signal is None:
            eprint(f"Died with: unknown signal number {-cp.returncode}")
        else:
            eprint(f"Died with: {signal}")
    elif cp.returncode > 0:
        eprint(f"Exit status: {cp.returncode} (failure)")
    else:
        eprint("Exit status: 0 (success)")
    
    if cp.stdout is None:
        eprint("stdout not captured")
    else: 
        eprint(f"=== BEGIN stdout ===")
        eprint(cp.stdout)
        eprint(f"==== END stdout ====")
    
    if cp.stderr is None:
        eprint("stderr not captured")
    else:
        eprint(f"=== BEGIN stderr ===")
        eprint(cp.stderr)
        eprint(f"==== END stderr ====")



def resolved_path(path: str) -> pathlib.Path:
    """Convert a path string to its resolved Path object.
    If the path doesn't exist, resolve as far as possible.
    Does not depend on OPTIONS."""
    try:
        return pathlib.Path(path).resolve()
    except RuntimeError:
        eprint(f"error: infinite loop encountered while resolving {path}")
        sys.exit(ERROR_ES)


def extant_file(path: str) -> pathlib.Path:
    """Convert a path string for an extant file to its resolved Path object.
    If the path doesn't correspond to a file, exit with a helpful error message.
    Does not depend on OPTIONS."""
    try:
        result = pathlib.Path(path).resolve(strict=True)
    except FileNotFoundError:
        eprint(f"error: {path} does not exist")
        sys.exit(ERROR_ES)
    except RuntimeError:
        eprint(f"error: infinite loop encountered while resolving {path}")
        sys.exit(ERROR_ES)
    if not result.is_file():
        eprint(f"error: {path} is not a file")
        sys.exit(ERROR_ES)
    return result


def signal_num_to_signal(signal_num: int) -> signal.Signals | None:
    """Return the signal corresponding to the given signal number.
    If the signal number is invalid, return None."""
    try:
        return signal.Signals(signal_num)
    except ValueError:
        return None



if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        eprint()
        sys.exit(KEYBOARD_INTERRUPT_ES)
