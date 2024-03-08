#!/usr/bin/env python3

from sys import argv
from argparse import ArgumentParser, Namespace

FG = [ "\033[30m", "\033[31m", "\033[32m",
       "\033[33m", "\033[34m", "\033[35m",
       "\033[36m", "\033[37m", "\033[m" ]


def parse_command_arguments(cmd_args: list[str]) -> Namespace:
	parser = ArgumentParser(description="...todo...")

	parser.add_argument("-m", "--max", type=int, default=10)
	parser.add_argument("-e", "--exclude", type=str, default="")

	return parser.parse_args()


def main(cmd_args: list[str]) -> None:
	args = parse_command_arguments(cmd_args)
	excluded = list(map(int, args.exclude.split(",")))
	n = args.max
	already_used = []

	print(" "*3, end=f"{FG[3]} ")
	for ih in range(1, n + 1):  print(f"{ih:>3}", end=" ")
	print(FG[-1])

	for ir in range(1, n + 1):
		print(f"{FG[3]}{ir:>3}{FG[-1]}", end=" ")

		for ic in range(1, n + 1):
			if ir in excluded or ic in excluded or (ir, ic) in already_used or ir == ic:
				print(" "*3, end=" ")
				continue

			r = ir * ic
			clr = FG[2] if r % 2 == 0 else FG[1]
			print(f"{clr}{r:>3}{FG[-1]}", end=" ")

			already_used += [(ir, ic), (ic, ir)]
		print()


if __name__ == "__main__":
	main(argv[1:])
