from invoke.context import Context

BLACK = "uv run black"
ISORT = "uv run isort"
BASEDPYRIGHT = "uv run basedpyright"


def run_python_typecheck(c: Context, warn: bool = False) -> bool:
    result = c.run(f"{BASEDPYRIGHT}", warn=warn)
    return bool(result and result.ok)


def run_typescript_typecheck(c: Context, warn: bool = False) -> bool:
    with c.cd("ui"):
        result = c.run("npm run typecheck", warn=warn)
    return bool(result and result.ok)


def run_python_format(c: Context, check: bool = False, warn: bool = False) -> bool:
    if check:
        black_result = c.run(f"{BLACK} . --check --diff", warn=warn)
        isort_result = c.run(f"{ISORT} . --check-only --diff", warn=warn)
        return bool(black_result and black_result.ok and isort_result and isort_result.ok)
    else:
        c.run(f"{BLACK} .", warn=warn)
        c.run(f"{ISORT} .", warn=warn)
        return True


def run_typescript_format(c: Context, check: bool = False, warn: bool = False) -> bool:
    with c.cd("ui"):
        if check:
            result = c.run("npm run format:check", warn=warn)
            return bool(result and result.ok)
        else:
            c.run("npm run format", warn=warn)
            return True
