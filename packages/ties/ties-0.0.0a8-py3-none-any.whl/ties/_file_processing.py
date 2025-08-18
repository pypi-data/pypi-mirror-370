"""A CLI tool to duplicate and sync file content with advanced transformations."""

import hashlib
import importlib
import sys
from pathlib import Path
from typing import Any

from ._consts import DEFAULT_SCRIPT_DIR, Colors, cprint


def get_content_hash(content: bytes) -> str:
    """Calculate the SHA256 hash of a byte string."""
    return hashlib.sha256(content).hexdigest()


def get_file_hash(filepath: Path) -> str:
    """Calculate the SHA256 hash of a file's content."""
    try:
        content = filepath.read_bytes()
        return get_content_hash(content)
    except FileNotFoundError:
        return ""


def get_source_content(group_config: dict, script_dir: Path) -> bytes:
    """
    Get the final source content.

    By handling single source, concatenation,
    or a custom transform function.
    """
    # Normalize 'source'/'sources' to a list
    sources = _resolve_sources(group_config)
    source_paths = [Path(s) for s in sources]

    # --- Custom Transform Logic ---
    transforms = _resolve_transforms(group_config)
    if len(transforms) > 0:
        # Validate all sources are text files for transforms
        for src_path in source_paths:
            if not is_text_file(src_path):
                raise TypeError(
                    f"Source file for transform must be a text file: {src_path}"
                )

        source_contents = [p.read_text(encoding="utf-8") for p in source_paths]
        for transform in transforms:
            cprint(f"  -> Using custom transform: {transform}", Colors.BLUE)
            module_spec = transform
            try:
                module_path_str, func_name = module_spec.split(":")

                # Add the script directory to the path for importing
                sys.path.insert(0, str(script_dir.resolve()))

                module = importlib.import_module(module_path_str)
                transform_func = getattr(module, func_name)

                # Restore sys.path
                sys.path.pop(0)

                result = transform_func(*source_contents)
                source_contents = [result]

            except (ValueError, ImportError, AttributeError, FileNotFoundError) as e:
                raise RuntimeError(
                    f"Failed to load transform '{module_spec}' from '{script_dir}': {e}"
                ) from e
            except Exception as e:
                raise RuntimeError(
                    f"Error executing transform '{module_spec}': {e}"
                ) from e

        return result.encode("utf-8")

    # --- Single Source Logic ---
    if len(source_paths) == 1:
        return source_paths[0].read_bytes()

    # --- Concatenation Logic ---
    cprint(f"  -> Concatenating {len(source_paths)} sources...", Colors.BLUE)
    final_content = bytearray()
    for i, src_path in enumerate(source_paths):
        if not is_text_file(src_path):
            raise TypeError(
                f"Source file for concatenation is not a text file: {src_path}"
            )
        final_content.extend(src_path.read_bytes())
        if i < len(source_paths) - 1:
            final_content.extend(b"\n")  # Add a newline between concatenated files

    return bytes(final_content)


def _resolve_sources(group_config: dict[str, Any]) -> list[str]:
    if "source" in group_config:
        sources = [group_config["source"]]
    elif "sources" in group_config:
        sources = group_config["sources"]
    else:
        raise ValueError("Each 'tie' group must contain a 'source' or 'sources' key.")
    return sources


def _resolve_transforms(group_config: dict[str, Any]) -> list[str]:
    if "transform" in group_config:
        transforms = [group_config["transform"]]
    elif "transforms" in group_config:
        transforms = group_config["transforms"]
    else:
        transforms = []
    return transforms


def process_files(config: dict, mode: str) -> bool:
    """
    Process files.

    Generic function to either 'check' or 'fix' files based on the mode.
    """
    if mode == "check":
        cprint("--- 🕵️  Ties Check ---", Colors.MAGENTA, bold=True)
    else:
        cprint("--- ✨ Ties Fix ---", Colors.MAGENTA, bold=True)

    ties = config.get("tie", [])
    global_script_dir = config.get("script_dir", DEFAULT_SCRIPT_DIR)

    discrepancies = 0
    errors = 0
    fixed_count = 0

    for i, group in enumerate(ties):
        group_name = group.get("name", f"Group #{i + 1}")
        cprint(f"\nProcessing '{group_name}':", bold=True)
        try:
            # Determine script_dir: per-tie override > global > default
            local_script_dir = group.get("script_dir", global_script_dir)
            script_dir_path = Path(local_script_dir)

            expected_content = get_source_content(group, script_dir_path)
            expected_hash = get_content_hash(expected_content)

            targets = normalize_targets(group)

            for target_str in targets:
                target_path = Path(target_str)
                target_hash = get_file_hash(target_path)

                if expected_hash != target_hash:
                    discrepancies += 1
                    if mode == "check":
                        cprint(f"  ❌ '{target_path}' is out of sync.", Colors.YELLOW)
                    else:  # mode == 'fix'
                        cprint(f"  🔧 Fixing '{target_path}'...", Colors.CYAN)
                        try:
                            target_path.parent.mkdir(parents=True, exist_ok=True)
                            target_path.write_bytes(expected_content)
                            fixed_count += 1
                        except OSError as e:
                            cprint(f"    ❌ Error writing to file: {e}", Colors.RED)
                            errors += 1
                elif mode == "fix":
                    cprint(f"  ✅ '{target_path}' is already in sync.", Colors.GREEN)

        except (ValueError, TypeError, RuntimeError) as e:
            cprint(
                f"  ❌ Error processing group '{group_name}': {e}",
                Colors.RED,
                bold=True,
            )
            errors += 1

    return final_summary(mode, discrepancies, fixed_count, errors)


def normalize_targets(group: dict[str, Any]) -> list[str]:
    """Normalize 'target'/'targets' to a list."""
    if "target" in group:
        targets = [group["target"]]
    elif "targets" in group:
        targets = group.get("targets", [])
    else:
        raise ValueError("Each 'tie' group must contain a 'target' or 'targets' key.")

    return targets


def final_summary(mode: str, discrepancies: int, fixed_count: int, errors: int) -> bool:
    """Print the result and return conclusion."""
    if mode == "check":
        if discrepancies > 0:
            cprint(f"\nFound {discrepancies} discrepancies.", Colors.RED, bold=True)
            cprint("Run 'ties fix' to resolve.", Colors.CYAN)
            return False
        cprint("\n✅ All files are in sync.", Colors.GREEN, bold=True)
        return True

    # mode == 'fix'
    if fixed_count > 0:
        cprint(f"\nSuccessfully fixed {fixed_count} file(s).", Colors.GREEN)
    if errors > 0:
        cprint(f"\nEncountered {errors} error(s).", Colors.RED, bold=True)
        return False
    if fixed_count == 0 and errors == 0:
        cprint(
            "\n✅ All files were already in sync. No changes needed.",
            Colors.GREEN,
            bold=True,
        )

    return errors == 0


def is_text_file(file_path: Path) -> bool:
    """Check if a file is likely a text file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            f.read(1024)
        return True
    except (OSError, UnicodeDecodeError):
        return False
