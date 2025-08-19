

import sys, argparse, pathlib

from .iterm import IPyTerm, version


if sys.version_info < (3, 10):
    raise ImportError('indipyterm requires Python >= 3.10')


def main():
    """The commandline entry point to run the terminal client."""

    parser = argparse.ArgumentParser(usage="indipyterm [options]",
                                     description="Terminal client to communicate to an INDI service.")
    parser.add_argument("--port", type=int, default=7624, help="Port of the INDI server (default 7624).")
    parser.add_argument("--host", default="localhost", help="Hostname/IP of the INDI server (default localhost).")
    parser.add_argument("--blobfolder", help="Optional folder where BLOB's will be saved.")
    parser.add_argument("--version", action="version", version=version)
    args = parser.parse_args()

    if args.blobfolder:
        try:
            blobfolder = pathlib.Path(args.blobfolder).expanduser().resolve()
        except Exception:
            print("Error: If given, the BLOB's folder should be an existing directory")
            return 1
        else:
            if not blobfolder.is_dir():
                print("Error: If given, the BLOB's folder should be an existing directory")
                return 1
    else:
        blobfolder = None

    # run the IPyTerm app
    app = IPyTerm(host=args.host, port=args.port, blobfolder=blobfolder)
    app.run()

    return 0


if __name__ == "__main__":
    sys.exit(main())
