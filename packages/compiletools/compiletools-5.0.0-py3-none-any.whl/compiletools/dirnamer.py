""" Wrapper around appdirs that intercepts user_cache_dir 
    and uses the CTCACHE environment variable and other ct config files 
"""
import sys
import os
import appdirs
import configargparse
import compiletools.configutils

user_data_dir = appdirs.user_data_dir
user_config_dir = appdirs.user_config_dir
site_config_dir = appdirs.site_config_dir


def add_arguments(cap):
    cap.add_argument(
        "--CTCACHE",
        default="None",
        help="Location to cache the magicflags and deps. None means no caching.",
    )


def _verbose_write(output, verbose=0, newline=False):
    if verbose > 0:
        sys.stdout.write(output)
        if newline:
            sys.stdout.write("\n")


def _verbose_write_found(cachedir, verbose=0):
    _verbose_write("Using CTCACHE=", verbose=verbose)
    _verbose_write(cachedir, verbose=verbose)
    if cachedir == "None":
        _verbose_write(". Disk caching is disabled.", verbose=verbose)
    if verbose > 0:
        sys.stdout.write("\n")


def user_cache_dir(
    appname="ct",
    appauthor=None,
    version=None,
    opinion=True,
    args=None,
    argv=None,
    exedir=None,
):
    if args is None:
        verbose = 0
    else:
        verbose = args.verbose
    # command line > environment variables > config file values > defaults

    cachedir = compiletools.configutils.extract_value_from_argv(key="CTCACHE", argv=argv)
    if cachedir:
        _verbose_write(
            "Highest priority CTCACHE is the command line.",
            verbose=verbose,
            newline=True,
        )
        _verbose_write_found(cachedir, verbose=verbose)
        return cachedir

    _verbose_write(
        "CTCACHE not on commandline. Falling back to environment variables.",
        verbose=verbose,
        newline=True,
    )
    try:
        cachedir = os.environ["CTCACHE"]
        _verbose_write_found(cachedir, verbose=verbose)
        return cachedir

    except KeyError:
        pass

    _verbose_write(
        "CTCACHE not in environment variables. Falling back to config files.",
        verbose=verbose,
        newline=True,
    )

    cachedir = compiletools.configutils.extract_item_from_ct_conf(
        "CTCACHE", exedir=exedir, verbose=verbose
    )
    if cachedir:
        _verbose_write_found(cachedir, verbose=verbose)
        return cachedir

    _verbose_write(
        "CTCACHE not in config files.  Falling back to python-appdirs (which on linux wraps XDG variables).",
        verbose=verbose,
        newline=True,
    )
    cachedir = appdirs.user_cache_dir(appname, appauthor, version, opinion)
    _verbose_write_found(cachedir, verbose=verbose)
    return cachedir


def main(argv=None):
    cap = compiletools.apptools.create_parser("Cache directory naming tool", argv=argv, include_config=False)
    add_arguments(cap)
    args = cap.parse_args(args=argv)
    print(compiletools.dirnamer.user_cache_dir(args=args))
