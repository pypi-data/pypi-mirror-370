from datetime import datetime
from pathlib import Path

import sys
import argparse
import logging
import os

from amqmonitoring.client import AMQPListener
from amqmonitoring.reader import FindInDictValues, SimplePrinter
from amqmonitoring.monitor import ExchangeMonitor
from amqmonitoring.cli import CLIInterface
from amqmonitoring.gui import GUIInterface


def arg_parser():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog='amqmonitoring',
        description='Monitor AMQP traces and exchanges'
    )

    # Mode selection
    parser.add_argument(
        '-g', '--gui',
        help="Launch GUI mode for exchange monitoring",
        action='store_true'
    )
    
    # Legacy trace monitoring options
    parser.add_argument(
        '-f', '--find-by-dict',
        help="Path to the json instructions (legacy mode)",
        dest="instructions_path",
        required=False,
        default=None
    )
    parser.add_argument(
        '-s', '--store',
        help="Path where the JSON messages outputs will be stored (legacy mode)",
        required=False,
        default='results'
    )
    parser.add_argument(
        '-q', '--queue',
        help="Name of the queue to listen (legacy mode)",
        required=False,
        default='trace'
    )
    
    # Connection options
    parser.add_argument(
        '--host',
        help="RabbitMQ host",
        default=os.getenv('RABBITMQ_HOST', 'localhost')
    )
    parser.add_argument(
        '--port',
        help="RabbitMQ port",
        type=int,
        default=int(os.getenv('RABBITMQ_PORT', '5672'))
    )
    parser.add_argument(
        '--username',
        help="RabbitMQ username",
        default=os.getenv('RABBITMQ_USER', 'guest')
    )
    parser.add_argument(
        '--password',
        help="RabbitMQ password",
        default=os.getenv('RABBITMQ_PASSWORD', 'guest')
    )

    return parser.parse_args()


def setup_logging(storage_path: Path, file_name: str):
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)-8s: %(message)s',
        filename=storage_path / f"{file_name}.log",
    )

    # Set up logging to console
    console = logging.StreamHandler(stream=sys.stderr)
    console.setFormatter(
        logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
    )
    logging.getLogger('').addHandler(console)


def run_legacy_mode(args, storage_path: Path, file_name: str):
    """Run the legacy trace monitoring mode."""
    logger = logging.getLogger(__name__)
    logger.info("Running in legacy trace monitoring mode")
    
    if args.instructions_path:
        # Init finder processor
        processor = FindInDictValues(
            path_to_instructions=Path(args.instructions_path),
            json_path=storage_path / f"{file_name}.json",
        )
    else:
        processor = SimplePrinter(
            json_path=storage_path / f"{file_name}.json"
        )

    # Create and start the listener
    listener = AMQPListener(
        host=args.host, port=str(args.port), queue_name=args.queue
    )
    listener.connect(user=args.username, password=args.password)

    try:
        listener.start_listening(callback=processor.process_message)
    finally:
        processor.save_traces()


def run_monitor_mode(args, gui_mode: bool = False):
    """Run the new exchange monitoring mode."""
    logger = logging.getLogger(__name__)
    
    # Create monitor
    monitor = ExchangeMonitor(
        host=args.host,
        port=args.port,
        username=args.username,
        password=args.password
    )
    
    if gui_mode:
        logger.info("Starting GUI mode")
        interface = GUIInterface(monitor)
        interface.start()
    else:
        logger.info("Starting CLI mode")
        interface = CLIInterface(monitor)
        interface.start()


def main():
    """Main entry point for the application."""
    start_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"AMQP_Traces_{start_date}"

    args = arg_parser()
    storage_path = Path(args.store)
    storage_path.mkdir(parents=True, exist_ok=True)

    # Setup logging
    setup_logging(storage_path, file_name)
    logger = logging.getLogger(__name__)
    
    # Determine mode
    if args.gui:
        # GUI mode
        run_monitor_mode(args, gui_mode=True)
    elif args.instructions_path or args.queue != 'trace':
        # Legacy trace monitoring mode
        run_legacy_mode(args, storage_path, file_name)
    else:
        # CLI monitoring mode (default)
        run_monitor_mode(args, gui_mode=False)


if __name__ == '__main__':
    main()
