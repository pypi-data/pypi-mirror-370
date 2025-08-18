"""
CLI argument validation logic.

Ensures mutually exclusive or required arguments are properly used
and triggers formatted JSON errors if rules are violated.
"""


def validate_args(args, ptjsonlib):
    """
    Validates combinations and presence of CLI arguments.

    Raises a JSON-formatted error via ptjsonlib if invalid usage is detected.
    """

    if len(args.url_list) > 1 and args.json:
        ptjsonlib.end_error("Cannot test more than 1 domain while --json parameter is present", "ERROR")
    if (args.grouping or args.grouping_complete) and args.json:
        ptjsonlib.end_error("Cannot use -g or -gc parameters while --json parameter is present", args.json)
    if args.grouping and args.grouping_complete:
        ptjsonlib.end_error("Cannot use both -g and -gc parameters together", args.json)

    if args.output_parts and not args.output:
        ptjsonlib.end_error("Missing --output parameter", args.json)
    if args.input and args.file:
        ptjsonlib.end_error("Cannot use --input and --list parameter together", args.json)
    if args.domain and not args.file:
        ptjsonlib.end_error("--list required to use with --domain", args.json)
    if not args.input and not args.file:
        ptjsonlib.end_error("--input or --list parameter required", args.json)
    if (args.extension_yes or args.extension_no) and not args.file:
        ptjsonlib.end_error("--list required for usage of --extension-yes / --extension-no parameters", args.json)
    if args.extension_yes and args.extension_no:
        ptjsonlib.end_error("Cannot combine --extension-yes together with --extension-no", args.json)
