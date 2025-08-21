from watchdog.events import PatternMatchingEventHandler, FileModifiedEvent
from mindustry_campaign_stats.presenters import to_json, to_table
from mindustry_campaign_stats.__version__ import __version__
from mindustry_campaign_stats.constants import Planet
from mindustry_campaign_stats.settings import load
from mindustry_campaign_stats.stats import compute
from argparse import ArgumentParser, Namespace
from watchdog.observers import Observer
from rich.console import Console
from threading import Timer
from time import sleep
import os

console = Console()


def show(args: Namespace) -> None:
    if not args.json and args.refresh:
        console.clear()

    with open(args.filename, 'rb') as fp:
        settings_parsed = load(fp)

    computed_stats = compute(settings_parsed, args.planet)

    if args.json:
        console.out(
            to_json(computed_stats, args.pretty if not args.refresh else False),
            end='\n'
        )
    else:
        console.print(
            to_table(computed_stats)
        )


def cli() -> None:
    arg_parser = ArgumentParser(
        description='CLI tool to read Mindustry\'s campaign global stats.'
    )

    arg_parser.add_argument(
        'filename',
        help='The settings.bin file to load'
    )

    arg_parser.add_argument(
        'planet',
        help='Which campaign to retrieve stats for',
        type=Planet,
        choices=list(Planet)
    )

    arg_parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'parkitect-blueprint-reader {__version__}'
    )

    arg_parser.add_argument(
        '-j', '--json',
        help='Output JSON instead of a table',
        action='store_true'
    )

    arg_parser.add_argument(
        '-p', '--pretty',
        help='Pretty-print JSON output',
        action='store_true'
    )

    arg_parser.add_argument(
        '-r', '--refresh',
        help='Listen for file changes',
        action='store_true'
    )

    args = arg_parser.parse_args()

    show(args)

    if args.refresh:
        class SettingsModifiedHandler(PatternMatchingEventHandler):
            def __init__(self, *args, **kvargs):
                super().__init__(*args, **kvargs)

                self.timer = None

            def on_modified(self, event: FileModifiedEvent):
                if self.timer:
                    self.timer.cancel()

                self.timer = Timer(2.0, lambda args: show(args), args=[args])
                self.timer.start()

        observer = Observer()

        observer.schedule(
            SettingsModifiedHandler(patterns=[os.path.basename(args.filename)], ignore_directories=True),
            os.path.dirname(args.filename) or './',
            recursive=False
        )

        observer.start()

        try:
            while True:
                sleep(1)
        except KeyboardInterrupt:
            observer.stop()

        observer.join()
