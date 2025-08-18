from pathlib import Path
import subprocess as sp
import logging
from cpplint_fix.parser import CPPLTestsuite
from cpplint_fix.source import SourceFile
from cpplint_fix.edits import Edits, FailedEditError
from cpplint_fix.config import CPPLFixConfig

logger = logging.getLogger(__name__)

def run_cpplint(root: Path) -> CPPLTestsuite:
    """Run cpplint on the given root directory and return the parsed results."""
    if root.is_dir():
        cmd = ["cpplint", "--output=junit", "--recursive", "./"]
    else:
        fname = root.name
        cmd = ["cpplint", "--output=junit", fname]
        root = root.parent  # Use the parent directory as the working directory
    proc = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE, cwd=root)
    _, stderr = proc.communicate()
    
    return CPPLTestsuite.from_string(stderr.decode("utf-8"))

def fix_files(input: Path, output: Path | None, dry_run: bool = False, 
               config: CPPLFixConfig | None = None) -> None:
    """Run cpplint on the input files and apply fixes to the output files/folder."""
    
    # Check if input is a file or folder
    root_dir = input if input.is_dir() else input.parent
       

    cppl_testsuite = run_cpplint(input)
    if config is None:
        config = CPPLFixConfig()
    
    if not cppl_testsuite.testcases:
        logger.info("No test cases found in cpplint output.")
        return
    
    for testcase in cppl_testsuite.testcases:
        # All paths are relative to the input directory
        fpath = root_dir / testcase.fpath

        # Check if any exclusion rules apply
        if any(pattern.match(str(fpath)) for pattern in config.exclude_files):
            logger.info(f"Excluding file {fpath} based on configuration.")
            continue

        logger.info(f"Processing file: {fpath}")
        src = SourceFile.from_file(fpath)
        edits_count = 0
        for failure in testcase.failures:

            if failure.code in config.exclude_rules:
                logger.info(f"Excluding rule {failure.code} for file {fpath}")
                continue

            edit_class = Edits.get(failure.code)
            if edit_class is None:
                logger.warning(f"No edits found for error code: {failure.code}")
                continue

            edit = edit_class(failure)
            if dry_run:
                logger.info(f"Dry run: would apply edit {edit} to {fpath}")
                continue
            try:
                edit.apply(src)
                edits_count += 1
            except FailedEditError as e:
                logger.error(f"Failed to apply edit {edit} to {fpath}: {e}")
                continue
        
        if dry_run:
            continue

        if output is not None:
            dest_path = output / fpath.name
            src.to_file(dest_path)
            logger.info(f"Fixed file written to: {dest_path}")
        elif edits_count > 0:
            logger.info(f"Applying edits to source file: {fpath}")
            src.apply_edits()