import argparse
import sys
from collections import deque
import re

def output(line):
    print(line)

def grep(lines, params):
    PrimaryLength = max(params.before_context, params.context)
    ResultLength = max(params.after_context, params.context)
    PrimaryDeque = deque()
    ResultDeque = deque()
    Counter = 0
    TmpLength = 0
    for index, line in enumerate(lines):
        line = line.rstrip()
        Search = Find(line, params.pattern, params.ignore_case)
        if (not Search and params.invert) or (Search and not params.invert):
            while ResultDeque:
                Element = ResultDeque.popleft()
                output(Element)
                if Element in PrimaryDeque:
                    PrimaryDeque.remove(Element)
            while PrimaryDeque:
                output(PrimaryDeque.popleft())
            if params.count:
                Counter += 1
                continue
            if params.line_number:
                line = "{}:{}".format(index+1, line)
            output(line)
            TmpLength = ResultLength
            ResultDeque.clear()
        elif params.count:
            continue
        else:
            if params.line_number:
                line = "{}-{}".format(index+1, line)
            if PrimaryLength:
                if PrimaryLength == len(PrimaryDeque):
                    PrimaryDeque.popleft()
                    PrimaryDeque.append(line)
                else:
                    PrimaryDeque.append(line)
            if TmpLength:
                ResultDeque.append(line)
                TmpLength -= 1
    if params.count:
        output(str(Counter))
    while ResultDeque:
        output(ResultDeque.popleft())

def Find(matchString, Expr_, isIgnore):
    Expression = Expr_.replace('*', '.*').replace('?', '.')
    Pattern = None
    if isIgnore:
        Pattern = re.compile(Expression, re.IGNORECASE)
    else:
        Pattern = re.compile(Expression)
    Result = Pattern.search(matchString)
    return Result

def parse_args(args):
    parser = argparse.ArgumentParser(description='This is a simple grep on python')
    parser.add_argument(
        '-v', action="store_true", dest="invert", default=False, help='Selected lines are those not matching pattern.')
    parser.add_argument(
        '-i', action="store_true", dest="ignore_case", default=False, help='Perform case insensitive matching.')
    parser.add_argument(
        '-c',
        action="store_true",
        dest="count",
        default=False,
        help='Only a count of selected lines is written to standard output.')
    parser.add_argument(
        '-n',
        action="store_true",
        dest="line_number",
        default=False,
        help='Each output line is preceded by its relative line number in the file, starting at line 1.')
    parser.add_argument(
        '-C',
        action="store",
        dest="context",
        type=int,
        default=0,
        help='Print num lines of leading and trailing context surrounding each match.')
    parser.add_argument(
        '-B',
        action="store",
        dest="before_context",
        type=int,
        default=0,
        help='Print num lines of trailing context after each match')
    parser.add_argument(
        '-A',
        action="store",
        dest="after_context",
        type=int,
        default=0,
        help='Print num lines of leading context before each match.')
    parser.add_argument('pattern', action="store", help='Search pattern. Can contain magic symbols: ?*')
    return parser.parse_args(args)


def main():
    params = parse_args(sys.argv[1:])
    grep(sys.stdin.readlines(), params)


if __name__ == '__main__':
    main()
