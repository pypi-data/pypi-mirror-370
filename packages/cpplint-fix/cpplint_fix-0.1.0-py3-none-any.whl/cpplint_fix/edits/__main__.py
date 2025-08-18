from cpplint_fix.edits import Edits

if __name__ == "__main__":
    # Print out all available edit codes
    print("## Supported edit codes:\n")
    codes = sorted(Edits.codes())
    for code in codes:
        print(f"- `{code}`")