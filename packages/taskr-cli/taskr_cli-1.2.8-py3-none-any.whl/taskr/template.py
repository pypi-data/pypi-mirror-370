template = """from taskr import runners, utils
from importlib.metadata import version

# Taskr config settings

## The default task to run, when typing just 'taskr'
DEFAULT = "all"

## If you want people to only use taskr in a VENV, set this to True. If not, set to
## false or delete it
VENV_REQUIRED = True

# If you want an environment variable file to be loaded before every task
# Files needs to be in the form of var_name=value
ENVS = ".env"

#Builds a wheel
def build() -> bool:
    return runners.run(["python -m build --wheel -n;", "echo 'Artifact:'; ls dist/"])


# Remove build artifacts, cache, etc.
def clean() -> bool:
    retValue = utils.cleanBuilds()

    if retValue:
        retValue = utils.cleanCompiles()

    return retValue


# Run tests, optionally a subset
def test(subset: Optional[str] = None) -> bool:
    cmd = "python -m pytest tests/ -v "
    if subset:
        cmd += f"-k {subset}"

    return runners.run(cmd)

# Run formatting
def fmt() -> bool:
    return runners.run("python -m ruff format src/ tests/")

# lint
def lint() -> bool:
    return runners.run("ruff check --unsafe-fixes --fix src/* tests/*")


# Check types
def types() -> bool:
    return runners.run("python -m mypy src/*.py ")


# Runs all static analysis tools
def check() -> bool:
    return runners.run_conditional(fmt, lint, types)


# Runs a server based on a passed in variable
def run_server(env: str = "dev") -> bool:
    ENVS = {"ENV": env}
    return runners.run("python server.py", ENVS)


# Bump a version file (any file)
def bump(version: str = "") -> bool:
    return utils.bumpVersion(version=version, filename="pyproject.toml")


# Some non python tasks

# Squash the branch
def squish() -> None:
    runners.run(
        [
            'git reset --soft $(git merge-base HEAD master) && git commit -m "$(git log --format=%B master..HEAD)"',
            "git commit --amend",
        ]
    )

# Tag the branch
def tag(ver: str = "") -> bool:
    if ver == "":
        ver = version("package-name")

    return runners.run([f"git tag v{ver};", "git push --tags"])

"""
