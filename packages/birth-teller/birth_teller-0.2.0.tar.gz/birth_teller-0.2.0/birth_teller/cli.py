
import argparse
from .core import BTM


def main():
    btm = BTM()
    btm.banner()

    parser = argparse.ArgumentParser(description="Birth Day Teller CLI")
    parser.add_argument('-n', '--name', help="Your name")
    parser.add_argument('-d', '--day', required=True, type=int, help="Birth day (1-31)")
    parser.add_argument('-m', '--month', required=True, help="Birth month (e.g., jan, feb)")
    parser.add_argument('-y', '--year', required=True, type=int, help="Birth year (e.g., 2000)")

    args = parser.parse_args()

    name = args.name.title() if args.name else "User"
    btm.greetings(name)

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
