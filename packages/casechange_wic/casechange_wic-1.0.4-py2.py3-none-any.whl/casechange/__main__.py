import sys

from casechange import case_change

def main():
    if len(sys.argv) < 2:
        print("Usage: casechange <mode> <text>")
        sys.exit(1)
    mode = sys.argv[1]
    text = sys.argv[2]
    print(case_change(text, mode))

if __name__ == "__main__":
    main()
