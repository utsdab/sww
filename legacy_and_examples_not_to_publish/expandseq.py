#!/usr/bin/env python

# expandseq.py.py/condenseseq.py.py - two command line utilities that expose the basic
# functionality of the python-module "seqLister.py" functions "expandSeq()"
# and "condenseSeq()".  These functions translate back and forth between a
# condensed form for listing sequences of integers and plain lists of integers.
# Lists of integers in this condensed format are commonly used by various
# computer programs dealing with sequences of images such as render farm
# management tools (like smedge), image sequence viewers (like rv) or "ls"
# commands (like lsseq) to list frames from CG-animation or video footage
# which has been saved as a sequence of individually numbered frames.
#
# The "expandseq.py.py" and "condenseseq.py.py" commands enhance the simple behavior of
# the "expandSeq()" and "condenseSeq()" python functions by adding the ability
# to print out the lists in various forms.  eg.; comma, space or newline
# separators as well as sorting the lists, reversing order, and mixing and
# matching expanded and condensed formats as arguments on the command line.

# Copyright (c) 2008-2012, James Philip Rowell,
# Orange Imagination & Concepts, Inc.
# www.orangeimagination.com
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# - Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
#   - Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in
#     the documentation and/or other materials provided with the
#     distribution.
#
#   - Neither the name of "Orange Imagination & Concepts, Inc."  nor the
#     names of its contributors may be used to endorse or promote
#     products derived from this software without specific prior written
#     permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import argparse
import os

import sys
import usr.bin.seqLister


EXPAND_MODE = True
VERSION = "1.200"


def indexNegNumber(argList):
    i = 0
    argLen = len(argList)
    while i < argLen:
        if len(argList[i]) >= 2:
            if argList[i][0] == '-' and argList[i][1].isdigit():
                return i
        i += 1
    return -1


def main():
    # Redefine the exception handling routine so that it does NOT
    # do a trace dump if the user types ^C while expandseq.py.py or
    # condenseseq.py.py are running.
    #
    old_excepthook = sys.excepthook

    def new_hook(exceptionType, value, traceback):
        if exceptionType != KeyboardInterrupt and exceptionType != IOError:
            old_excepthook(exceptionType, value, traceback)
        else:
            pass

    sys.excepthook = new_hook

    global EXPAND_MODE
    if os.path.basename(sys.argv[0]) == "expandseq.py.py":
        EXPAND_MODE = True
    elif os.path.basename(sys.argv[0]) == "condenseseq.py.py":
        EXPAND_MODE = False
    else:
        print >> sys.stderr, os.path.basename(sys.argv[0]) + ": must be named either expandseq.py.py or condenseseq.py.py"
        sys.exit(1)

    if EXPAND_MODE:
        p = argparse.ArgumentParser(
            description="Expands a list of integers and integer sequences \
	    of the form 'A-B' or 'A-BxN' into a list of integers.  A-BxN means \
	    list every Nth integer starting at A ending at the highest integer \
	    less than or equal to B. Numbers will only be listed once each.\
	    That is; '2-4 1-6' yeilds the list '2 3 4 1 5 6'.  (Also see condenseseq.py.py).",
            usage="%(prog)s [OPTION]... [INTEGER SEQUENCE]...")
    else:
        p = argparse.ArgumentParser(
            description="Condenses a list of integers and/or integer sequences \
	    of the form 'A-B' or 'A-BxN' into the most minimal sequence format \
	    possible to represent the full list of numbers. (Also see expandseq.py.py).",
            usage="%(prog)s [OPTION]... [INTEGER SEQUENCE]...")

    p.add_argument("--version", action="version", version=VERSION)

    p.add_argument("--delimiter", "-d", action="store", type=str,
                   choices=("comma", "space", "newline"),
                   dest="seqDelimiter",
                   metavar="DELIMITER",
                   default="comma",
                   help="List successive numbers delimited by a 'comma' (default) or a 'space' or a 'newline'.")
    if not EXPAND_MODE:  # i.e.; condense
        p.add_argument("--onlyOnes", action="store_true",
                       dest="onlyOnes", default=False,
                       help="only condense sucessive frames, that is, do not list sequences on 2's, 3's, ... N's")
    p.add_argument("--reverse", "-r", action="store_true",
                   dest="reverseList", default=False,
                   help="reverse the order of the list")
    if EXPAND_MODE:
        p.add_argument("--sort", "-s", action="store_true",
                       dest="sortList", default=False,
                       help="sort the resulting list")

    p.add_argument("numSequences", metavar="INTEGER SEQUENCE", nargs="*",
                   help="is a single integer such as 'A', or a range \
	of integers such as 'A-B' (A or B can be negative,\
	and A may be greater than B to count backwards), or \
	a range on N's such as 'A-BxN' where N is a positive integer.")

    sysArgs = sys.argv[1:]  # Copy the command line args (except prog name)
    remainingArgs = []
    result = usr.bin.seqLister.expandSeq(sysArgs, remainingArgs)
    args = p.parse_args(remainingArgs)

    if EXPAND_MODE:
        if args.sortList:
            result.sort()
    else:
        if args.onlyOnes:
            result = usr.bin.seqLister.condenseSeqOnes(result)
        else:
            result = usr.bin.seqLister.condenseSeq(result)

    if args.reverseList:
        result.reverse()

    isFirst = True
    for s in result:
        if args.seqDelimiter == 'space':
            print s,
        elif args.seqDelimiter == 'comma':
            if not isFirst:
                sys.stdout.write(',')
            sys.stdout.write(str(s))
            isFirst = False
        else:  # newline
            print s
    if args.seqDelimiter == 'comma' and not isFirst:
        print ""


if __name__ == '__main__':
    main()
