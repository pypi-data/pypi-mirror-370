from filecmp import cmp
from os import walk
from os.path import exists, join, relpath
from typing import List


def compare_dir_contents(
    expect_dir: str, result_dir: str, verbose: bool = False
) -> List[str]:
    """
    Make a list of differences that the resulting directory content
    has from the expected content directory content.
    :param expect_dir: Path to a directory with the correct contents we expect from the test subject
    :param result_dir: Path to a directory with the actual contents created by the test subject
    :param verbose: Flag to print file differences or not, default is non-verbose
    :return: A list of strings describing mismatches result_dir has compared to expected_dir, pass if empty
    """
    mismatches = []
    # Traverses all plugin directory contents
    # TestCreateUtil.recursive_check(expect_dir, result_dir, mismatches) # Try this if walk() traversal fails
    for path, dirs, files in walk(expect_dir):
        expect_path = join(expect_dir, path)
        # result_path should have the same path under result_dir as the expect_path has under expect_dir
        result_path = join(result_dir, relpath(expect_path, expect_dir))
        # Assert that the expected directory exists in the result
        if not exists(result_path):
            mismatches.append(f"{result_path} directory not found.")
            continue
        # Iterate over the files in this directory to verify existence & content match
        for _file in files:
            expect_file = join(expect_path, _file)
            result_file = join(result_path, _file)
            # Assert that the expected file exists in the result
            if not exists(result_file):
                mismatches.append(f"{result_file} file not found.")
                continue
            # Files both exist, now we compare the contents
            if not cmp(expect_file, result_file):
                mismatches.append(f"{result_file} does not match expected content.")
                continue
            if verbose:
                print(f"{result_file} matches expected content!")
    # If all files exist and match, mismatches should be empty
    return mismatches
