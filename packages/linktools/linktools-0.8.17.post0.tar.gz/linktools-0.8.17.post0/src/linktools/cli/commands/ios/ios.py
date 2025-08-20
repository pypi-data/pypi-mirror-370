#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Optional

from linktools.cli import CommandMain, IOSCommand, IOSNamespace


class Command(IOSCommand):
    """
    Manage multiple iOS devices effortlessly with go-ios commands
    """

    _GENERAL_COMMANDS = [
        "list",
        "help",
        "version",
    ]

    @property
    def main(self):
        return CommandMain(self, show_log_level=False, show_log_time=False)

    def init_arguments(self, parser) -> None:
        parser.add_argument("ios_args", nargs="...", metavar="args", help="go-ios args")

    def run(self, args: IOSNamespace) -> Optional[int]:
        if args.ios_args and args.ios_args[0] not in self._GENERAL_COMMANDS:
            device = args.device_selector.select()
            process = device.popen(*args.ios_args, capture_output=False)
            return process.call()

        ios = args.device_selector.bridge
        process = ios.popen(*args.ios_args, capture_output=False)
        return process.call()


command = Command()
if __name__ == "__main__":
    command.main()
