#!/usr/bin/env python3
"""
Download all 2023 demonstration data from FragDenStaat (authenticated)
"""
import requests
from pathlib import Path
import sys

# User credentials
EMAIL = "davidpomerenke@mailbox.org"
PASSWORD = "y@4!3t9dJRXNyq"

# Base paths
REPO_ROOT = Path(__file__).parent
RAW_DATA = REPO_ROOT / "data" / "raw"

# File definitions: (city_name, url, filename, file_type)
FILES_TO_DOWNLOAD = [
    # XLSX Files (15 cities)
    ("Berlin", "https://media.frag-den-staat.de/files/foi/876068/auswertung-name-name-ifg17-24.xlsx", "2023_2023.xlsx", "xlsx"),
    ("Mainz", "https://media.frag-den-staat.de/files/foi/896277/anfrageltranspg-18032024-name.xlsx", "2023_2023.xlsx", "xlsx"),
    ("Magdeburg", "https://media.frag-den-staat.de/files/foi/918325/versammlungen2023.xlsx", "2023_2023.xlsx", "xlsx"),
    ("München", "https://media.frag-den-staat.de/files/foi/875514/versammlungsliste-mnchen-2023-fragdenstaat299704.xlsx", "2023_2023.xlsx", "xlsx"),
    ("Erfurt", "https://media.frag-den-staat.de/files/foi/879576/versammlungenimjahr2023.xlsx", "2023_2023.xlsx", "xlsx"),
    ("Dresden", "https://media.frag-den-staat.de/files/foi/885327/versammlungsuebersicht-dd-03-bis-12-2023.xlsx", "2023_2023.xlsx", "xlsx"),
    ("Köln", "https://media.frag-den-staat.de/files/foi/888437/versammlungen2023.xlsx", "2023_2023.xlsx", "xlsx"),
    ("Bremen", "https://media.frag-den-staat.de/files/foi/887952/bersicht-angemeldeteversammlungen2023-bremen.xlsx", "2023_2023.xlsx", "xlsx"),
    ("Karlsruhe", "https://media.frag-den-staat.de/files/foi/887639/tabelleauskunftlifgab2023.xlsx", "2023_2023.xlsx", "xlsx"),
    ("Dortmund", "https://media.frag-den-staat.de/files/foi/887260/versammlungen2023ppdortmund.xlsx", "2023_2023.xlsx", "xlsx"),
    ("Kiel", "https://media.frag-den-staat.de/files/foi/884966/demos2023-versand.xlsx", "2023_2023.xlsx", "xlsx"),
    ("Freiburg", "https://media.frag-den-stadt.de/files/foi/883305/versammlungen-2023.xlsx", "2023_2023.xlsx", "xlsx"),
    ("Wiesbaden", "https://media.frag-den-staat.de/files/foi/879458/fragdenstaat2023.xlsx", "2023_2023.xlsx", "xlsx"),
    ("Duisburg", "https://media.frag-den-stadt.de/files/foi/877319/versammlungsbersicht2023.xlsx", "2023_2023.xlsx", "xlsx"),

    # Saarbrücken - Two files (XLSX and XLS)
    ("Saarbrücken", "https://media.frag-den-staat.de/files/foi/912566/kopievonanfrageforschungs-studieversammlungslagen2023-anfragevom10-06-2024.xlsx", "2023_2023a.xlsx", "xlsx"),
    ("Saarbrücken", "https://media.frag-den-staat.de/files/foi/911731/kopievonstatistikversammlung.xls", "2023_2023b.xls", "xls"),

    # PDFs (2 cities)
    ("Wuppertal", "https://media.frag-den-stadt.de/files/foi/889263/mappe1.pdf", "2023.pdf", "pdf"),
    ("Potsdam", "https://media.frag-den-staat.de/files/foi/883323/aw06-03-24.pdf", "2023a.pdf", "pdf"),
    ("Potsdam", "https://media.frag-den-stadt.de/files/foi/883238/versammlungen2023inpotsdam.pdf", "2023b.pdf", "pdf"),
]

def login():
    """Authenticate with FragDenStaat and return session"""
    session = requests.Session()

    # Get CSRF token
    login_url = "https://fragdenstaat.de/account/login/"
    response = session.get(login_url)
    csrf_token = session.cookies.get('csrftoken')

    if not csrf_token:
        print("ERROR: Could not get CSRF token")
        return None

    # Login
    login_data = {
        'username': EMAIL,
        'password': PASSWORD,
        'csrfmiddlewaretoken': csrf_token,
    }
    headers = {'Referer': login_url}

    response = session.post(login_url, data=login_data, headers=headers)

    # Check if login successful
    if 'sessionid' in session.cookies:
        print(f"✓ Authenticated as {EMAIL}")
        return session
    else:
        print("ERROR: Login failed")
        return None

def download_file(session, url, output_path):
    """Download a file from authenticated URL"""
    try:
        response = session.get(url, timeout=60)

        if response.status_code == 200:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(response.content)
            size_kb = len(response.content) / 1024
            return True, size_kb
        else:
            return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, str(e)

def main():
    print("="*80)
    print("DOWNLOADING 2023 DEMONSTRATION DATA FROM FRAGDENSTAAT")
    print("="*80)
    print()

    # Authenticate
    session = login()
    if not session:
        sys.exit(1)

    print()
    print("Starting downloads...")
    print()

    # Download all files
    success_count = 0
    fail_count = 0

    for city, url, filename, file_type in FILES_TO_DOWNLOAD:
        output_path = RAW_DATA / city / filename

        print(f"📥 {city:15} {filename:20} ... ", end="", flush=True)

        success, result = download_file(session, url, output_path)

        if success:
            print(f"✓ ({result:.1f} KB)")
            success_count += 1
        else:
            print(f"✗ FAILED: {result}")
            fail_count += 1

    print()
    print("="*80)
    print(f"DOWNLOAD SUMMARY: {success_count} succeeded, {fail_count} failed")
    print("="*80)

    if fail_count > 0:
        print("\nSome downloads failed. Check URLs and authentication.")
        sys.exit(1)
    else:
        print("\n✓ All files downloaded successfully!")
        print(f"\nFiles saved to: {RAW_DATA}")
        return 0

if __name__ == "__main__":
    sys.exit(main())
