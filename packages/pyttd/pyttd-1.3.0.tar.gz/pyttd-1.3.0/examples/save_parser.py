#!/usr/bin/env python3
"""
OpenTTD Save File Parser Example

This example demonstrates how to utilize pyttd for extracting data from OpenTTD save files into JSON.

Usage:
    python examples/save_parser.py [path/to/savefile.sav]
"""

import sys
import json
from pathlib import Path
from functools import partial

try:
    from tqdm import tqdm
except Exception:
    tqdm = None

# Add the pyttd package to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pyttd.saveload import (
    load_savefile,
    SaveFileExporter,
    export_savefile_to_json,
    export_savefile_to_string,
)


def main():
    """Main function"""

    if len(sys.argv) < 2:
        print("Usage: python save_parser.py <savefile_path>")
        return

    savefile_path = sys.argv[1]

    if not Path(savefile_path).exists():
        print(f"Error: Savefile not found: {savefile_path}")
        return

    print(f"Loading savefile: {savefile_path}")
    print()

    # Example 1: Basic savefile loading
    print("1. Basic Savefile Loading")
    print("-" * 30)

    try:
        # Helper to make progress bars
        def make_progress(desc: str):
            bar = tqdm(total=100, unit="%", desc=desc) if tqdm else None

            def cb(p: float, stage: str):
                if bar is not None:
                    newn = int(max(0, min(100, p * 100)))
                    if newn >= bar.n:
                        bar.n = newn
                        bar.set_postfix_str(stage)
                        bar.refresh()

            return bar, cb

        # Load with parsed data (human-readable)
        pbar, _progress = make_progress("Parsing (parsed)")
        parsed_data = load_savefile(
            savefile_path, silent=True, parsed=True, progress_callback=_progress
        )
        print(f"Loaded parsed data")
        print(
            f"  - Save version: {parsed_data.meta.save_version if hasattr(parsed_data, 'meta') else 'Unknown'}"
        )
        print(
            f"  - Companies: {parsed_data.companies.count if hasattr(parsed_data, 'companies') else 0}"
        )
        print(
            f"  - Map size: {parsed_data.map.dim_x if hasattr(parsed_data, 'map') else 0}x{parsed_data.map.dim_y if hasattr(parsed_data, 'map') else 0}"
        )

        # Load with raw data
        if pbar is not None:
            pbar.close()
        pbar2, _progress2 = make_progress("Parsing (raw)")
        raw_data = load_savefile(
            savefile_path, silent=True, parsed=False, progress_callback=_progress2
        )
        if pbar2 is not None:
            pbar2.close()
        print(f"Loaded raw data")
        print(
            f"  - Raw chunks: {list(raw_data.keys()) if isinstance(raw_data, dict) else 'structured_data'}"
        )

    except Exception as e:
        print(f"Error loading savefile: {e}")
        return

    print()

    # Example 2: JSON Export
    print("2. JSON Export")
    print("-" * 15)

    try:
        pbar4, _progress4 = make_progress("Export (string)")
        json_string = export_savefile_to_string(
            parsed_data, parsed=True, include_raw=False, pretty=True, progress_callback=_progress4
        )
        if pbar4 is not None:
            pbar4.close()
        print(f"Exported to JSON string")
        print(f"  - JSON length: {len(json_string):,} characters")

        # Export to file (parsed data)
        output_file = Path(savefile_path).with_suffix(".json")
        pbar5, _progress5 = make_progress("Export (parsed file)")
        export_savefile_to_json(
            parsed_data,
            output_file,
            parsed=True,
            include_raw=False,
            pretty=True,
            progress_callback=_progress5,
        )
        if pbar5 is not None:
            pbar5.close()
        print(f"Exported to file: {output_file}")

        # Export raw data to file
        raw_output_file = Path(savefile_path).with_suffix(".raw.json")
        pbar6, _progress6 = make_progress("Export (raw file)")
        export_savefile_to_json(
            raw_data,
            raw_output_file,
            parsed=False,
            include_raw=True,
            pretty=True,
            progress_callback=_progress6,
        )
        if pbar6 is not None:
            pbar6.close()
        print(f"Exported raw data to: {raw_output_file}")

    except Exception as e:
        print(f"Error exporting to JSON: {e}")

    print()

    # Example 3: Game data
    print("3. Game data")
    print("-" * 18)

    try:
        companies = parsed_data.companies.companies
        if companies:
            print(f"Companies:")
            print(f"  - Total companies: {len(companies)}")

            richest_company = max(companies, key=lambda c: c.get("money", 0))
            print(f"  - Richest company: {richest_company.get('name', 'Unknown')}")
            print(f"    Money: ${richest_company.get('money', 0):,}")

            ai_companies = sum(1 for c in companies if c.get("is_ai", False))
            human_companies = len(companies) - ai_companies
            print(f"  - AI companies: {ai_companies}")
            print(f"  - Human companies: {human_companies}")

        game_data = parsed_data.game
        if game_data:
            print(f"Game State:")
            print(f"  - Current date: {game_data.date.formatted}")
            print(f"  - Economy date: {game_data.economy_date.formatted}")
            print(f"  - Price inflation: {game_data.inflation_prices.formatted}")
            print(f"  - Payment inflation: {game_data.inflation_payment.formatted}")
            print(f"  - Interest rate: {game_data.interest_rate}%")
            print(f"  - Max loan: ${game_data.max_loan:,}")

    except Exception as e:
        print(f"Error: {e}")

    print()
    print("\nGenerated files:")
    print(f"  - {Path(savefile_path).with_suffix('.json')} (parsed data)")
    print(f"  - {Path(savefile_path).with_suffix('.raw.json')} (raw data)")


if __name__ == "__main__":
    main()
