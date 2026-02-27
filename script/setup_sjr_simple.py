#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SJR Data Import Helper - Simplified Version
Helps users import Scimago Journal Rank data
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def show_instructions():
    """Display download instructions"""
    print("\n" + "=" * 60)
    print("How to Download SJR Data")
    print("=" * 60)

    print("\nStep 1: Visit Scimago Website")
    print("  Open: https://www.scimagojr.com/")

    print("\nStep 2: Navigate to Journal Rankings")
    print("  Click 'Journal Rankings' button")

    print("\nStep 3: Configure Filters (Recommended)")
    print("  - Year: Select latest year (e.g., 2024)")
    print("  - Areas: Select relevant areas (or 'All Areas')")
    print("    Common options:")
    print("      * Medicine")
    print("      * Computer Science")
    print("      * Engineering")
    print("      * Neuroscience")
    print("      * Or select 'All Areas' for everything")

    print("\nStep 4: Export Data")
    print("  - Click 'Export' button")
    print("  - Select 'CSV' format")
    print("  - Wait for download to complete")

    print("\nStep 5: Save File")
    print(f"  Save to: {PROJECT_ROOT}/cache/sjr_2024.csv")
    print("  Or anywhere else, just specify the path when importing")

    print("\n" + "=" * 60)


# Alias for the function
show_download_instructions = show_instructions


def import_data(csv_path: str, year: int = 2024):
    """Display download instructions"""
    print("\n" + "=" * 60)
    print("How to Download SJR Data")
    print("=" * 60)

    print("\nStep 1: Visit Scimago Website")
    print("  Open: https://www.scimagojr.com/")

    print("\nStep 2: Navigate to Journal Rankings")
    print("  Click 'Journal Rankings' button")

    print("\nStep 3: Configure Filters (Recommended)")
    print("  - Year: Select latest year (e.g., 2024)")
    print("  - Areas: Select relevant areas (or 'All Areas')")
    print("    Common options:")
    print("      * Medicine")
    print("      * Computer Science")
    print("      * Engineering")
    print("      * Neuroscience")
    print("      * Or select 'All Areas' for everything")

    print("\nStep 4: Export Data")
    print("  - Click 'Export' button")
    print("  - Select 'CSV' format")
    print("  - Wait for download to complete")

    print("\nStep 5: Save File")
    print(f"  Save to: {PROJECT_ROOT}/cache/sjr_2024.csv")
    print("  Or anywhere else, just specify the path when importing")

    print("\n" + "=" * 60)


def import_data(csv_path: str, year: int = 2024):
    """Import SJR data from CSV file"""
    from script.impact_filter import ImpactFactorFilter

    csv_file = Path(csv_path)

    if not csv_file.exists():
        print(f"\n[ERROR] File not found: {csv_file}")
        print("\nPlease check:")
        print("  1. File path is correct")
        print("  2. File was downloaded from Scimago")
        print("  3. File is in CSV format")
        return False

    print(f"\nImporting SJR data ({year})...")
    print(f"File: {csv_file}")
    print("This may take a few minutes for large files...\n")

    try:
        filter_engine = ImpactFactorFilter()
        filter_engine.import_sjr_csv(csv_file, year)

        # Verify import
        import sqlite3
        conn = sqlite3.connect(filter_engine.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM journals WHERE year = ?', (year,))
        count = cursor.fetchone()[0]
        conn.close()

        if count > 0:
            print(f"\n[SUCCESS] Imported {count} journals")
            print(f"\nYou can now use --min-sjr parameter!")
            print(f"Example: python paper_search.py \"[AI]\" --pubmed-mode --min-sjr 2.0")
            return True
        else:
            print(f"\n[ERROR] Import failed or empty data")
            return False

    except Exception as e:
        print(f"\n[ERROR] Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_status():
    """Check current database status"""
    from script.impact_filter import ImpactFactorFilter

    filter_engine = ImpactFactorFilter()

    import sqlite3
    conn = sqlite3.connect(filter_engine.db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM journals')
    count = cursor.fetchone()[0]

    if count > 0:
        cursor.execute('SELECT year FROM journals GROUP BY year ORDER BY year DESC')
        years = [row[0] for row in cursor.fetchall()]
        conn.close()

        print(f"\n[OK] Database contains {count} journals")
        print(f"  Years: {', '.join(map(str, years))}")
        return True
    else:
        conn.close()
        print("\n[INFO] Database is empty")
        return False


def main():
    """Main function"""
    print("\n" + "=" * 60)
    print("SJR Data Import Helper")
    print("=" * 60)

    # Check current status
    has_data = check_status()

    if has_data:
        print("\nDatabase already has data!")
        print("Do you want to import more data? (y/N): ", end='')
        try:
            choice = input().strip().lower()
            if choice != 'y':
                print("Cancelled")
                return
        except:
            print("\nCancelled")
            return

    # Show instructions
    show_download_instructions()

    print("\n" + "=" * 60)
    print("Options:")
    print("=" * 60)
    print("1. I have downloaded the CSV file")
    print("2. Show download instructions again")
    print("3. Exit")

    try:
        choice = input("\nEnter choice (1/2/3): ").strip()
    except:
        print("\nExit")
        return

    if choice == '1':
        csv_path = input("\nEnter CSV file path: ").strip()

        # Handle path
        csv_file = Path(csv_path)
        if not csv_file.is_absolute():
            # Relative path
            csv_file = PROJECT_ROOT / csv_file

        year_input = input("Enter data year (default 2024): ").strip()
        if not year_input:
            year = 2024
        else:
            try:
                year = int(year_input)
            except:
                print("[ERROR] Invalid year, using 2024")
                year = 2024

        import_data(str(csv_file), year)

    elif choice == '2':
        show_download_instructions()
        print("\nWhen ready, run this script again and choose option 1")
    else:
        print("\nExit")


if __name__ == '__main__':
    # Command line mode
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
        year = int(sys.argv[2]) if len(sys.argv) > 2 else 2024
        import_data(csv_path, year)
    else:
        # Interactive mode
        main()
