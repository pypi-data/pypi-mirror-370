from pathlib import Path
import argparse as ap
from typing import Protocol
from cpplint_fix.wrapper import fix_files
from cpplint_fix.config import CPPLFixConfig
import logging

class MainArgs(Protocol):
    input: Path
    output: Path | None
    config: Path | None
    dry_run: bool


def main():
    parser = ap.ArgumentParser(description="Run cpplint and apply fixes to source files.")
    parser.add_argument("input", type=Path, help="Input directory containing source files, or single file")
    parser.add_argument("--output", "-o", type=Path, default=None, 
                        help="Output directory for fixed files (optional)")
    parser.add_argument("--config", "-c", type=Path, default=None,
                        help="Path to the configuration file (optional)")
    parser.add_argument("--dry-run", action="store_true",
                        help="If set, only print the changes without applying them")
    
    args: MainArgs = parser.parse_args() # type: ignore
    
    input_path = args.input
    output_path = args.output
    
    logger = logging.getLogger("cpplint_fix")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    logger.addHandler(handler)
    handler.setFormatter(formatter)
    
    config: CPPLFixConfig | None = None    
    if args.config:
        config_path: Path = args.config
        if not config_path.exists():
            logger.error(f"Configuration file {config_path} does not exist.")
            return
        
        with config_path.open('r') as f:
            config_content = f.read()
        
        try:
            config = CPPLFixConfig.model_validate_yaml(config_content)
            logger.info("Configuration loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return

    fix_files(input_path, output_path, dry_run=args.dry_run, config=config)

if __name__ == "__main__":
    main()