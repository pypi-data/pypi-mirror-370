import json
import logging

from pathlib import Path

from amqmonitoring.utils import read_dict_file, pjson

logger = logging.getLogger(__name__)


class SimplePrinter:
    def __init__(self, json_path: Path):
        self.messages: dict[dict, dict[dict, list[str]]] = {}
        self.json_path: Path = json_path

    def process_message(self, ch, method, properties, body):
        message = body.decode('utf-8')
        message_dict = json.loads(message)

        r_exchange = properties.headers.get('exchange_name')
        r_queue = properties.headers.get('routed_queues')[0]
        r_routine = properties.headers.get('routing_keys')[0]

        if r_exchange not in self.messages:
            self.messages[r_exchange] = {}
        if r_routine not in self.messages[r_exchange]:
            self.messages[r_exchange][r_routine] = []

        self.messages[r_exchange][r_routine].append(message_dict)
        logger.info(f"E: {r_exchange} R: {r_routine} Q: {r_queue} \n{body}")

        # Acknowledge the message (remove from queue).
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def save_traces(self):
        if self.messages:
            self.json_path.parent.mkdir(exist_ok=True, parents=True)
            with open(self.json_path, 'w', encoding='UTF-8') as _fh:
                json.dump(self.messages, _fh, indent=4)
            logger.info(f"Traces saved to `{self.json_path}`.")




class FindInDictValues(SimplePrinter):

    def __init__(self, path_to_instructions: Path, json_path: Path):
        super().__init__(json_path=json_path)

        self.instructions: dict = read_dict_file(path_to_instructions)
        self.tracking_count = 0

        for track_exchange, track_routines in self.instructions.items():
            self.tracking_count += len(track_routines)

        self.already_discovered = []

    @property
    def missing(self) -> str:
        return (f"{self.tracking_count - len(self.already_discovered)}"
                f" from {self.tracking_count}")

    def process_message(self, ch, method, properties, body):
        """
        Process received message - this function just prints the message

        Args:
            ch: Channel object
            method: Method frame
            properties: Properties
            body: Message body
        """
        message = body.decode('utf-8')
        message_dict = json.loads(message)
        logger.debug(f"{ch} - {method} - {properties}:\n{message}")

        r_exchange = properties.headers.get('exchange_name')
        r_queue = properties.headers.get('routed_queues')[0]
        r_routine = properties.headers.get('routing_keys')[0]

        if r_exchange in self.instructions.keys():
            for exchange, routines_queues in self.instructions.items():
                if r_exchange != exchange:
                    continue

                if exchange not in self.messages:
                    self.messages[exchange] = {}
                if r_routine not in self.messages[exchange]:
                    self.messages[exchange][r_routine] = []

                self.messages[exchange][r_routine].append(message_dict)

                if r_queue in routines_queues and r_routine in routines_queues:
                    if f"{r_exchange}__{r_routine}" in self.already_discovered:
                        logger.info(f"Missing: {self.missing}"
                                    f" | ->\t E: {r_exchange}"
                                    f" R: {r_routine} Q: {r_queue}")
                    else:
                        logger.info(
                            f"✓ Missing: {self.missing}"
                                    f" | ->\t E: {r_exchange}"
                                    f" R: {r_routine} Q: {r_queue}"
                                    f"\n{pjson(message_dict)}")
                        self.already_discovered.append(
                            f"{r_exchange}__{r_routine}")
            else:
                logger.warning(
                    f"𐄂 Missing: {self.missing}"
                    f" | ->\t E: {r_exchange}"
                    f" R: {r_routine} Q: {r_queue}"
                    f"\n{pjson(message_dict)}"
                )

        else:
            logger.info(f"Missing: {self.missing}"
                        f" | ->\t E: {r_exchange}"
                        f" R: {r_routine} Q: {r_queue}")

        # Acknowledge the message (remove from queue)
        ch.basic_ack(delivery_tag=method.delivery_tag)
