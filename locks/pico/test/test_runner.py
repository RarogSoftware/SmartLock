# ------------------------------------------------------------------------------
#  Copyright (c) 2023, Pawel Przytarski                                        -
#                                                                              -
#   Licensed under the Apache License, Version 2.0 (the "License");            -
#   you may not use this file except in compliance with the License.           -
#   You may obtain a copy of the License at                                    -
#   http://www.apache.org/licenses/LICENSE-2.0                                 -
# ------------------------------------------------------------------------------
import gc

config = dict()


# inspired by https://github.com/micropython/micropython-lib
def run_tests():
    import os
    import sys
    from pathlib import Path
    from fnmatch import fnmatch
    from micropython import const
    from unittest import TestRunner, TestSuite, TestResult

    def _load_file(runner: TestRunner, file_name: str, *extra_paths: list[str]):
        module_name = file_name.rsplit(".", 1)[0]
        original_module = {k: v for k, v in sys.modules.items()}
        original_path = sys.path[:]
        try:
            suite = TestSuite(module_name)
            for path in reversed(extra_paths):
                if path:
                    sys.path.insert(0, path)
            print(f"Running {module_name}")
            suite._load_module(__import__(module_name))
            return runner.run(suite)
        finally:
            pass
            sys.path[:] = original_path
            sys.modules.clear()
            sys.modules.update(original_module)

    _DIR_TYPE = const(0x4000)

    def _load_directory(directory: str, pattern: str, project_dir: str, runner: TestRunner = TestRunner()):
        files_to_scan = []
        result = TestResult()
        # if you wonder if this is needed, yes it is os.ilistdir have some bug, which makes it not work in recursive scenarios
        for file_name, file_type, *_ in os.ilistdir(directory):
            files_to_scan.append((file_name, file_type))
        for file_name, file_type, *_ in files_to_scan:
            if file_name in ("..", ".", "__pycache__"):
                continue
            elif file_type == _DIR_TYPE:
                _load_directory(
                    directory=directory + "/" + file_name,
                    pattern=pattern,
                    project_dir=project_dir,
                    runner=runner
                )
            elif fnmatch(file_name, pattern):
                result = result + _load_file(runner, file_name, directory, project_dir)
        return result

    print(f'Memory stats: alloc: {gc.mem_alloc()} free: {gc.mem_free()}')

    directory = Path(__file__).parent

    result = _load_directory(
        directory=directory.absolute(),
        pattern="test*.py",
        project_dir=directory.parent.absolute()
    )

    print(f'Memory stats: alloc: {gc.mem_alloc()} free: {gc.mem_free()}')

    sys.exit(result.failuresNum + result.errorsNum)
