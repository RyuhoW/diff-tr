import argparse
import json
from trace_parser import TraceParser
from trace_comparator import TraceComparator, Diff


def format_diff_human_readable(diff: Diff) -> str:
    """差分を人間が読みやすい形式にフォーマットする"""
    path_str = ".".join(diff.path)
    if diff.type == "added":
        return f"[+] Added: {path_str} = {diff.new_value}"
    elif diff.type == "removed":
        return f"[-] Removed: {path_str} (was {diff.old_value})"
    elif diff.type == "modified":
        return f"[~] Modified: {path_str}\n  - {diff.old_value}\n  + {diff.new_value}"
    return ""


def main():
    parser = argparse.ArgumentParser(
        description="Compare two Terraform trace logs for semantic differences."
    )
    parser.add_argument("trace_file_1", help="Path to the first trace log file.")
    parser.add_argument("trace_file_2", help="Path to the second trace log file.")
    parser.add_argument(
        "--output-format",
        choices=["human", "json"],
        default="human",
        help="The output format for the diff report.",
    )
    args = parser.parse_args()

    print(f"Parsing {args.trace_file_1}...")
    with open(args.trace_file_1, "r") as f1:
        parser1 = TraceParser(f1)
        trace1 = parser1.parse()

    print(f"Parsing {args.trace_file_2}...")
    with open(args.trace_file_2, "r") as f2:
        parser2 = TraceParser(f2)
        trace2 = parser2.parse()

    print("Comparing traces...")
    comparator = TraceComparator(trace1, trace2)
    diffs = comparator.compare()

    if not diffs:
        print("No semantic differences found.")
        return

    if args.output_format == "human":
        for diff in diffs:
            print(format_diff_human_readable(diff))
    elif args.output_format == "json":
        print(json.dumps([d.__dict__ for d in diffs], indent=2))


if __name__ == "__main__":
    main()
