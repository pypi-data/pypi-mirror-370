def register(subparsers):
    p = subparsers.add_parser("echo", help="Sample plugin: echo arguments")
    p.add_argument("words", nargs="*")
    p.set_defaults(_run=lambda args: print(" ".join(args.words)))

# Auto-entry point (cli detects _run, but we don't hook in here to avoid interference)
