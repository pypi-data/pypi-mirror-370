
import argparse
from .core import BTM

def main():
    btm = BTM()
    btm.banner()

    parser = argparse.ArgumentParser(description="Birth Day Teller CLI")
    parser.add_argument('--name', required=True, help="Your name")
    parser.add_argument('--day', required=True, type=int, help="Birth day (1-31)")
    parser.add_argument('--month', required=True, help="Birth month (e.g., jan, feb)")
    parser.add_argument('--year', required=True, type=int, help="Birth year (e.g., 2000)")

    args = parser.parse_args()

    btm.greetings(args.name.title())

    try:
        info = btm.information(args.day, args.month, args.year)
    except ValueError as e:
        print(f"[×] {e}")
        return

    print(f"\n[=] You were born on {info['weekDay']}")
    print("\n\t[Information]")
    for key, value in info.items():
        if key == 'weekDay':
            continue
        print(f"\t{key.title()}: {value}")
