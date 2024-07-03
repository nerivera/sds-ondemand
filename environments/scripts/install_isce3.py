# TODO: decide whether to include shebang (would be /opt/conda/bin/python)
# TODO: fix alignment of comments
# TODO: check to make sure everything that uses run_command is actually hard
# to guess in the case of an error. Or maybe add a parameter to run_command.

# Check instance type
# Check for existing installation
# Check S3 for existing tarball using boto3
# If nonexistent, clone git repo, etc. (same as in ipynb)

# Standard module dependencies only. Add other dependencies to import_nonstandard().
import os
import signal
import subprocess
import sys

REPO_URL = 'https://github.com/isce-framework/isce3.git'  # ISCE3 repository URL (HTTPS or SSH)
DEFAULT_VERSION = 'develop'                               # Version of ISCE3 to install if unspecified
REPO_DIR = '/home/jovyan/isce3'                           # ISCE3 repository directory
ENV_NAME = 'isce3_src'                                    # ISCE3 Conda environment name
ENV_PREFIX = f'/home/jovyan/.local/envs/{ENV_NAME}'       # ISCE3 Conda environment prefix
BUILD_DIR = os.path.join(REPO_DIR, 'build')               # ISCE3 build directory

# Environment definition file to use for creating the ISCE3 Conda environment
ENV_DEF_FILE = '/home/jovyan/sds-ondemand/environments/env_files/isce3_src_conda_env.yml'

DEFAULT_TO_YES = True               # Whether to default to yes in an interactive query
YES_RESPONSES = {"yes", "ye", "y"}  # Query responses that count as "yes"
NO_RESPONSES = {"no", "n"}          # Query responses that count as "no"

CMAKE_CACHE_REL = 'CMakeCache.txt'  # The path to the CMake cache relative to BUILD_DIR
CLEAR_CMAKE_CACHE = True            # If True, the CMake cache is deleted before building
CMAKE_BUILD_TYPE = 'Release'        # -DCMAKE_BUILD_TYPE flag passed to CMake when building
MAKE_NUM_JOBS = 0                   # -j option passed to Make when installing (0 means infinity)

ENV_PREFIX_VAR = 'CONDA_PREFIX'  # Environment variable for the active Conda environment prefix
BASE_ENV_PREFIX = '/opt/conda'       # Conda base environment prefix

CONDA_CREATE_EXEC = 'mamba'    # Executable to use for creating a Conda environment
CONDA_ADD_EXEC = 'mamba'       # Executable to use for adding a Conda environment to the ipykernel
CONDA_ACTIVATE_EXEC = 'conda'  # Executable to use for activating a Conda environment
GIT_EXEC = 'git'               # Executable to use for Git
CMAKE_EXEC = 'cmake'           # Executable to use for CMake
MAKE_EXEC = 'make'             # Executable to use for Make

INVALID_ARGS_ES = 2  # Exit status to use for invalid arguments
ERROR_ES = 1         # Exit status to use for other errors

def import_nonstandard() -> None:
    """Import all dependencies for this script that aren't standard modules.
    This function may only depend on standard modules."""
    pass

def eprint(*args, **kwargs) -> None:
    """Print to standard error.
    file should not be specified as a keyword argument."""
    print(*args, file=sys.stderr, **kwargs)

def signal_num_to_signal(signal_num: int) -> signal.Signals | None:
    """Return the signal corresponding to the given signal number.
    Return None if the signal number is invalid."""
    try:
        return signal.Signals(signal_num)
    except ValueError:
        return None

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

def is_parent(parent: str | bytes | os.PathLike, child: str | bytes | os.PathLike) -> bool:
    """Return whether parent is a parent path of child, accounting for symbolic links."""
    parent_norm = os.path.abspath(os.path.realpath(parent))
    child_norm = os.path.abspath(os.path.realpath(child))
    common_parent = os.path.commonpath([parent_norm])
    common_both = os.path.commonpath([parent_norm, child_norm])
    return common_parent == common_both

def query(prompt: str) -> bool:
    """Query to user interactively for a yes/no; return True for yes and False for no."""
    options = "Y/n" if DEFAULT_TO_YES else "y/N"
    while True:
        response = input(f"{prompt} [{options}] ").strip().lower()
        if not response:
            return DEFAULT_TO_YES
        if response in YES_RESPONSES:
            return True
        if response in NO_RESPONSES:
            return False

def get_version() -> str:
    """Return the requested ISCE3 version if the arguments seem valid.
    Otherwise, exit with a helpful error message.
    This function may only depend on standard modules."""
    num_args = len(sys.argv) - 1
    if num_args == 0:
        print(f"using default ISCE3 version: {DEFAULT_VERSION}")
        print("to use another version, pass it in as a command-line argument")
        return DEFAULT_VERSION
    if num_args == 1:
        version = sys.argv[1]
        if len(version) == 0 or version[0] == '-':
            eprint("error: invalid version")
            eprint("the version should be something recognized by `git checkout', like a version, commit, or branch")
            sys.exit(INVALID_ARGS_ES)
        return version
    eprint("error: too many arguments")
    eprint(f"usage: python {sys.argv[0]} [<version>]")
    sys.exit(INVALID_ARGS_ES)

def get_instance_type() -> str | None:
    """Return the instance type corresponding to the running environment.
    If the instance type cannot be determined, return None."""
    # TODO: implement
    return "CPU"

def conda_is_active() -> bool:
    """Return whether this script is being run from an active Conda environment."""
    return ENV_PREFIX_VAR in os.environ

def get_env() -> str:
    """Return the environment prefix for the active Conda environment."""
    return os.environ[ENV_PREFIX_VAR]

def ensure_base_env() -> None:
    """Return only if this script is being run from the Conda base environment.
    Otherwise, exit with a helpful error message.
    This function may only depend on standard modules."""
    if not conda_is_active():
        eprint("error: Conda must be active to run this script")
        eprint("try running `conda activate'")
        sys.exit(ERROR_ES)
    if not os.path.isdir(BASE_ENV_PREFIX):
        eprint(f"error: Conda base environment ({BASE_ENV_PREFIX}) not found")
        eprint(f"either your Conda installation is corrupted or it's in an unexpected place"
               " in which case you can try changing BASE_ENV_PREFIX at the top of this file")
        sys.exit(ERROR_ES)
    prefix = get_env()
    if not os.path.isdir(prefix):
        eprint("error: corrupted Conda environment")
        eprint(f"either the {ENV_PREFIX_VAR} environment variable was changed"
               " or the active Conda environment's prefix directory was removed")
        sys.exit(ERROR_ES)
    if not os.path.samefile(prefix, BASE_ENV_PREFIX):
        eprint(f"error: this script must be run from the Conda base environment ({BASE_ENV_PREFIX})")
        eprint("try running `conda activate'")
        sys.exit(ERROR_ES)

def current_installation_details() -> tuple[str | None, str | None]:
    """Return the currently installed version and instance type (respecitvely) of ISCE3.
    If an insatllation is detected but an instance type cannot be determined, return (version, None).
    If an installation is not detected, return (None, None)."""
    # TODO: implement
    return ("develop", "CPU")

def run_command(args: list[str], error_message: str, cwd: str = None) -> str:
    """Run the command given by args and return its output if successful.
    Otherwise, exit with the given error message and additional details.
    cwd overrides the current working directory when the command is run."""
    cp = subprocess.run(args, capture_output=True, cwd=cwd, text=True)
    if cp.returncode != 0:
        eprint(error_message)
        eprint("this is probably not a trivial error, but below are some details about the command that failed")
        eprint_completed_process(cp)
        sys.exit(ERROR_ES)
    return cp.stdout

def create_env() -> None:
    """Create the ISCE3 Conda environment and return if successful.
    Otherwise, exit with a helpful error message."""
    args = [CONDA_CREATE_EXEC, 'env', 'create', '-f', ENV_DEF_FILE, '-p', ENV_PREFIX, '--force']
    run_command(args, "error: creating the ISCE3 Conda environment failed")

def add_env() -> None:
    """Update the ipykernel to recognize the ISCE3 Conda environment and return if successful.
    Otherwise, exit with a helpful error message."""
    args = [CONDA_ADD_EXEC, 'run', '-p', ENV_PREFIX,
            'python', '-m', 'ipykernel', 'install', '--user', '--name', ENV_NAME, '--display-name', ENV_NAME]
    run_command(args, "error: udating the ipykernel to add the ISCE3 Conda environment failed")

def activate_env() -> None:
    """Activate the ISCE3 Conda environment and return if successful.
    Otherwise, exit with a helpful error message."""
    args = [CONDA_ACTIVATE_EXEC, 'activate', ENV_PREFIX]
    # TODO: remove below once it's working with above line
    # args = ['source', os.path.join(BASE_ENV_PREFIX, 'bin/activate'), ENV_PREFIX]
    run_command(args, "error: activating the ISCE3 Conda environment failed")

def repo_exists() -> bool:
    """Return whether the ISCE3 repository exists in its intended directory."""
    return os.path.isdir(os.path.join(REPO_DIR, '.git'))

def ensure_clean_working_tree() -> None:
    """Return if the ISCE3 repository working tree has no uncommitted changes.
    Otherwise, exit with a helpful error message."""
    args = [GIT_EXEC, 'diff-index', '--quiet', 'HEAD']
    cp = subprocess.run(args, capture_output=True, cwd=REPO_DIR, text=True)
    # --quiet implies --exit-code, which makes it so an exit status of 1 indicates differences
    if cp.returncode == 1:
        eprint("error: there are uncommitted changes in the ISCE3 Git repo")
        if is_parent(REPO_DIR, BUILD_DIR):
            eprint("you may need to ensure that the build directory is in the .gitignore file")
        sys.exit(ERROR_ES)
    if cp.returncode != 0:
        eprint("error: checking for uncommitted changes in the ISCE3 Git repo failed")
        eprint("this is probably not a trivial error, but below are some details about the command that failed")
        eprint_completed_process(cp)
        sys.exit(ERROR_ES)

def fetch_refs() -> None:
    """Fetch new refs in the ISCE3 repository from the default remote and return if successful.
    Otherwise, exit with a helpful error message."""
    # use --all because the version may be a new branch that hasn't been fetched yet, and we can't know which
    # remote to use in that case
    args = [GIT_EXEC, 'fetch', '--all']
    run_command(args, "error: pulling the ISCE3 Git repo failed", cwd=REPO_DIR)

def ensure_available_repo_dir() -> None:
    """Return if the intended ISCE3 repository is available for use.
    Otherwise, exit with a helpful error message."""
    if os.path.lexists(REPO_DIR):
        eprint(f"error: the intended ISCE3 repo path ({REPO_DIR}) is occupied")
        eprint(f"try removing it or moving it to another location")
        eprint("to use another directory, change REPO_DIR at the top of this file")
        sys.exit(ERROR_ES)

def clone_repo() -> None:
    """Clone the ISCE3 repository to its indended directory and return if successful.
    Otherwise, exit with a helpful error message."""
    args = [GIT_EXEC, 'clone', REPO_URL, REPO_DIR]
    run_command(args, f"error: cloning the ISCE3 Git repo to {REPO_DIR} failed", cwd=REPO_DIR)

def check_out_version(version: str) -> None:
    """Check out the given ISCE3 repository version corresponding and return if successful.
    Otherwise, exit with a helpful error message."""
    args = [GIT_EXEC, 'checkout', version]
    run_command(args, "error: checking out the given ISCE3 version failed", cwd=REPO_DIR)

def current_branch_path() -> str | None:
    """Return the path to the current branch relative to REPO_DIR/.git, or None if there is no current branch.
    Exit with a helpful error message if the underlying Git command is terminated by a signal."""
    args = [GIT_EXEC, 'symbolic-ref', '-q', 'HEAD']
    cp = subprocess.run(args, capture_output=True, cwd=REPO_DIR, text=True)
    # -q makes it so a nonzero exit code with no standard error implies no current branch
    if cp.returncode < 0 or (cp.returncode > 0 and cp.stderr):
        eprint("error: finding the path of the branch for the ISCE3 version failed")
        eprint("this is probably not a trivial error, but below are some details about the command that failed")
        eprint_completed_process(cp)
        sys.exit(ERROR_ES)
    if cp.returncode > 0:
        return None
    return cp.stdout.strip()

def get_upstream_branch(branch_path: str) -> str | None:
    """Return the name of the upstream branch for the given branch (a path relative to REPO_DIR/.git), or None if there isn't one.
    Exit with a helpful error message if the underlying Git command fails."""
    args = [GIT_EXEC, 'for-each-ref', '--format=%(upstream:short)', branch_path]
    upstream_branch = run_command(args, "error: finding the upstream branch for the ISCE3 version failed", cwd=REPO_DIR).strip()
    return upstream_branch if upstream_branch else None

def merge_into_current_branch(branch: str) -> None:
    """Merge the given branch into the current branch and return if successful.
    Otherwise, exit with a helpful error message."""
    args = [GIT_EXEC, 'merge', branch]
    run_command(args, (f"error: merging branch {branch} into ISCE3 version branch failed\n"
                       "if you made any local commits, you may need to resolve merge conflicts"))

def make_build_dir() -> None:
    """Create the build directory if it doesn't already exist and return if successful.
    Otherwise, exit with a helpful error message."""
    args = ['mkdir', '-p', BUILD_DIR]
    run_command(args, f"error: creating build directory {BUILD_DIR} failed")

def clear_cmake_cache() -> None:
    """Clear the CMake cache (BUILD_DIR/CMakeCache.txt) and return if successful.
    Otherwise, exit with a helpful error message."""
    cmake_cache = os.path.join(BUILD_DIR, CMAKE_CACHE_REL)
    if not os.path.lexists(cmake_cache):
        return
    if not os.path.isfile(cmake_cache):
        eprint(f"error: the expected CMake cache file path ({cmake_cache}) is occupied by a non-file")
        eprint(f"try removing it or moving it to another location")
        sys.exit(ERROR_ES)
    args = ['rm', '-f', cmake_cache]
    run_command(args, f"error: clearing the cmake cache (removing {cmake_cache}) failed")

def build_make_files() -> None:
    """Build the files required for Make to install ISCE3 and return if successful.
    Otherwise, exit with a helpful error message."""
    args = [CMAKE_EXEC, f'-DCMAKE_BUILD_TYPE={CMAKE_BUILD_TYPE}', f'-DCMAKE_INSTALL_PREFIX={BUILD_DIR}', REPO_DIR]
    # TODO: unsure if cwd is necessary
    run_command(args, "error: building ISCE3 Make files with CMake failed", cwd=BUILD_DIR)

def install() -> None:
    """Run the Make target `install' to install ISCE3 and return if successful.
    Otherwise, exit with a helpful error message."""
    if MAKE_NUM_JOBS == 0:
        args = [MAKE_EXEC, '-j', 'install']
    else:
        args = [MAKE_EXEC, '-j', str(MAKE_NUM_JOBS), 'install']
    run_command(args, "error: installing ISCE3 with Make target `install' failed", cwd=BUILD_DIR)

def main() -> None:
    # TODO: change to more general parse_args returning dict. Look into libraries that do this?
    # Maybe one of these args can be a "don't prompt me interactively" flag like -y or -f
    version = get_version()
    instance_type = get_instance_type()
    ensure_base_env()
    import_nonstandard()
    
    current_version, current_instance_type = current_installation_details()
    print(f"Going to install: {version}")
    if current_version is None:
        print("No version of ISCE3 is currently installed.")
    else:
        if current_instance_type is None:
            print(f"Currently installed: {current_version} (unknown instance type)")
        else:
            print(f"Currently installed: {current_version} ({current_instance_type} instance)")
    if not query("Would you like to proceed?"):
        return
    
    if repo_exists():
        ensure_clean_working_tree()
        fetch_refs()
    else:
        ensure_available_repo_dir()
        clone_repo()
    
    check_out_version(version)
    
    branch_path = current_branch_path()
    if branch_path is not None:
        upstream = get_upstream_branch(branch_path)
        if upstream is not None:
            # Passing in the upstream branch to override merge.defaultToUpstream configuration
            merge_into_current_branch(upstream)
    
    create_env()
    add_env()
    activate_env()
    
    make_build_dir()
    if CLEAR_CMAKE_CACHE:
        clear_cmake_cache()
    build_make_files()
    install()
    # TODO: is deactivating Conda and returning to source directory necessary?

if __name__ == '__main__':
    main()
