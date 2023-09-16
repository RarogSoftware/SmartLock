import sys

if sys.implementation.name == 'micropython':
    # inspired by https://github.com/micropython/micropython-lib
    import os
    import sys
    from pathlib import Path
    from fnmatch import fnmatch
    from micropython import const

    from unittest import TestRunner, TestResult, TestSuite


    def _run_file(runner: TestRunner, file_name: str, *extra_paths: list[str]):
        module_name = file_name.rsplit(".", 1)[0]
        original_module = {k: v for k, v in sys.modules.items()}
        original_path = sys.path[:]
        try:
            for path in reversed(extra_paths):
                if path:
                    sys.path.insert(0, path)

            suite = TestSuite(module_name)
            suite._load_module(__import__(module_name))
            return runner.run(suite)
        finally:
            sys.path[:] = original_path
            sys.modules.clear()
            sys.modules.update(original_module)


    _DIR_TYPE = const(0x4000)


    def _run_directory(directory: str, pattern: str, project_dir: str, runner: TestRunner = TestRunner()):
        result = TestResult()
        for file_name, file_type, *_ in os.ilistdir(directory):
            if file_name in ("..", ".", "__pycache__"):
                continue
            elif file_type == _DIR_TYPE:
                result += _run_directory(
                    directory="/".join((directory, file_name)),
                    pattern=pattern,
                    project_dir=project_dir,
                    runner=runner
                )
            elif fnmatch(file_name, pattern):
                result += _run_file(runner, file_name, directory, project_dir)
        return result


    directory = Path(__file__).parent

    result = _run_directory(
        directory=directory.absolute(),
        pattern="test*.py",
        project_dir=directory.parent.absolute()
    )

    sys.exit(result.failuresNum + result.errorsNum)

elif sys.implementation.name == "cpython":
    from test.micropython_mocks import get_micropython_mocks

    mocks = get_micropython_mocks()
    for key in mocks:
        sys.modules[key] = mocks[key]
