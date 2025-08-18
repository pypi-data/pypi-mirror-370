# Copyright (C) 2024 Bryan L. Fordham
#
# This file is part of RoboTooter.
#
# RoboTooter is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# RoboTooter is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with RoboTooter. If not, see <https://www.gnu.org/licenses/>.

import argparse
import sys

from robotooter import RoboTooter
from robotooter.bots.base_bot import BaseBot
from robotooter.rt import load_robo_tooter

parser = argparse.ArgumentParser()
parser.add_argument('-b', '--bot')
parser.add_argument('-w', '--working-dir', dest='working_dir', default='~/.robotooter')

subparsers = parser.add_subparsers(help='subcommand help', dest='command', required=False)

subparsers.add_parser('info', help='Display info about the local setup')
subparsers.add_parser('configure', help='Configure the local setup')
subparsers.add_parser('version', help='Display the current version')
subparsers.add_parser('help', help='Display this help message')
subparsers.add_parser('list', help='List current bots')
subparsers.add_parser('create', help='Create a new bot')

plugins_parser = subparsers.add_parser('plugins', help='Manage plugins')
plugins_subparsers = plugins_parser.add_subparsers(
    dest='plugin_action',
    help='Plugin management commands'
)
register_parser = plugins_subparsers.add_parser('register', help='Register a new plugin')
register_parser.add_argument('-p', '--plugin', help='Name of the plugin to register')

remove_parser = plugins_subparsers.add_parser('remove', help='Remove a plugin')
remove_parser.add_argument('-p', '--plugin', help='Name of the plugin to remove')

list_plugin_parser = plugins_subparsers.add_parser('list', help='List plugins')

list_parser = plugins_subparsers.add_parser('help', help='Print this help message')

def require_bot(robo: RoboTooter, bot_name:str) -> BaseBot|None:
    return robo.load_bot(bot_name)


def find_bot_param(arguments: list[str]) -> tuple[str | None, list[str]]:
    return find_param(arguments, ['-b', '--bot'])


def find_working_dir(arguments: list[str]) -> tuple[str | None, list[str]]:
    return find_param(arguments, ['-w', '--working-dir'])


def find_param(arguments: list[str], flags: list[str]) -> tuple[str | None, list[str]]:
    i = -1
    flag_value = None
    for p in flags:
        if p in arguments:
            i = arguments.index(p)
        if i > -1:
            break
    if i > -1:
        flag_value = arguments[i+1]
        del arguments[i+1]
        del arguments[i]
    return flag_value, arguments


def main(arguments: list[str] | None = None) -> None:
    if arguments:
        bot_name, arguments = find_bot_param(arguments)
        if bot_name:
            wd, arguments = find_working_dir(arguments)
            rt = load_robo_tooter(wd)
            bot = require_bot(rt, bot_name)
            if not bot:
                print(f"{bot_name} is not a valid bot")
                sys.exit(1)
            bot.parse_and_run(arguments)
            return

    args, remainder = parser.parse_known_args(arguments)
    rt = load_robo_tooter(args.working_dir)

    match args.command:
        case 'info':
            from robotooter.cli.info import run_info
            run_info(rt)

        case 'configure':
            from robotooter.cli.configure import run_configure
            run_configure(rt)

        case 'version':
            print(rt.__version__)

        case 'help':
            parser.print_help()

        case 'create':
            from robotooter.cli.create_bot import run_create_bot
            run_create_bot(rt)

        case 'list':
            all_plugins = rt.list_all_bots()
            if not all_plugins:
                print("No plugins found")
            if not all_plugins:
                print("No bots are currently configured")
                return
            for b_config in all_plugins:
                if not b_config:
                    continue
                print(b_config.bot_name)
                print(f"  {b_config.username}")
                print(f"  {b_config.bot_class}")

        case 'plugins':
            match args.plugin_action:
                case 'register':
                    rt.register_plugin(args.plugin)
                    print(f"{args.plugin} plugin registered")
                case 'remove':
                    rt.unregister_plugin(args.plugin)
                    print(f"{args.plugin} plugin removed")
                case 'list':
                    plugin_info = rt.list_current_plugins()
                    if plugin_info['filters']:
                        print("Plugin filters:")
                        for f in plugin_info['filters']:
                            print(f)
                    if plugin_info['bots']:
                        print("Plugin bots:")
                        for b in plugin_info['bots']:
                            print(b)
                case 'help':
                    parser.print_help()
                case _:
                    parser.print_help()


        case _:
            parser.print_help()

def call_cli() -> None:
    main(sys.argv[1:])

if __name__ == '__main__':
    call_cli()
