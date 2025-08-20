'''opencos.utils.str_helpers -- Various str helpers for printing, indenting'''

import fnmatch
import re
import shlex
import textwrap

def strip_all_quotes(s: str) -> str:
    '''Returns str with all ' and " removed'''
    return s.replace("'", '').replace('"', '')


def strip_outer_quotes(s: str) -> str:
    '''Returns str with outer pairs of (' or ") removed

    Note this is done safely removing only outmost pairs of single quotes, or double
    quotes. This is used on bare CLI args that may have outer quotes from shlex.quote(arg).
    '''
    ret = str(s)
    while (ret.startswith("'") and ret.endswith("'")) or \
          (ret.startswith('"') and ret.endswith('"')):
        ret = ret[1:-1]
    return ret


def string_or_space(text: str, whitespace: bool = False) -> str:
    '''Returns str of either spaces (len(text)) or returns text.'''
    if whitespace:
        return " " * len(text)
    return text


def sanitize_defines_for_sh(value: object, shlex_quote: bool = False) -> str:
    '''Attempts to make a str for +define+key[=value] safer for using as a shell arg

    Need to sanitize this for shell in case someone sends a +define+foo+1'b0,
    which needs to be escaped as +define+foo+1\'b0, otherwise bash or sh will
    think this is an unterminated string.

    Optionally can use shlex.quote('+define+key=value') via shlex_quote=True
    '''
    if isinstance(value, str):
        value = value.replace("'", "\\" + "'")
    if shlex_quote:
        value = shlex.quote(value)
    return value


def sprint_time(time_value: int) -> str:
    '''Return pretty str for time'''
    s = int(time_value)
    txt = ""
    do_all = False
    # days
    if s >= (24 * 60 * 60): # greater than 24h, we show days
        d = int(s / (24 *60 *60))
        txt += f"{d}d:"
        s -= d * 24 * 60 * 60
        do_all = True
    # hours
    if do_all or s >= (60 *60):
        d = int(s / (60 * 60))
        txt += f"{d:2}:"
        s -= d * 60 * 60
        do_all = True
    # minutes
    d = int(s / 60)
    txt += f"{d:02}:"
    s -= d * 60
    # seconds
    txt += f"{s:02}"
    return txt


def indent_wrap_long_text(
        text: str, width: int = 80, initial_indent: int = 0, indent: int = 4
) -> str:
    """Returns str, wraps text to a specified width and indents subsequent lines."""
    wrapped_lines = textwrap.wrap(
        text, width=width,
        initial_indent=' ' * initial_indent,
        subsequent_indent=' ' * indent
    )
    return '\n'.join(wrapped_lines)


def dep_str2list(value: object) -> list:
    '''Helper for a markup \n or space separated string to be returned as a list'''
    if value is None:
        return []
    if isinstance(value, str):
        return re.split('\n+| +', value) # convert \n separated to list, also split on spaces
    return value


def fnmatch_or_re(pattern: str, string: str) -> bool:
    '''Returns True if pattern/string matches in re.match or fnmatch'''
    matches = []
    # fnmatch check, aka: ./*test
    matches.append(
        bool(fnmatch.fnmatch(name=string, pat=pattern))
    )
    # regex check, aka: ./.*test
    try:
        matches.append(
            bool(re.match(pattern=pattern, string=string))
        )
    except: # pylint: disable=bare-except
        # could have been an illegal/unsupported regex, so don't match.
        pass
    return any(matches)
