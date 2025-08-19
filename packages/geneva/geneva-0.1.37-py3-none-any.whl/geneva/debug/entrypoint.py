# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

# a debugging entrypoint for reproducing task errors locally
import argparse
import json
import logging
import pdb  # noqa: T100

import geneva.cloudpickle as cloudpickle
from geneva import LanceCheckpointStore
from geneva.apply import ScanTask
from geneva.debug.logger import CheckpointStoreErrorLogger
from geneva.transformer import UDF

_LOG = logging.getLogger(__name__)


def run_udf_task_with_debug(
    task: ScanTask,
    udf: UDF,
) -> None:
    batches = task.to_batches()
    while True:
        try:
            batch = next(batches)
        except StopIteration:
            _LOG.info("End of task %s", task)
            break
        except Exception as e:
            _LOG.error(f"Error reading task {task}: {e}")
            pdb.post_mortem()
            break

        try:
            udf(batch)
        except Exception as e:
            _LOG.error(f"Error running UDF {udf} on batch {batch}: {e}")
            pdb.post_mortem()
            break


def register_debug_parser(subparsers: argparse._SubParsersAction) -> None:
    debug_parser = subparsers.add_parser(
        "debug", description="Run a UDF task with debugging"
    )
    debug_parser.add_argument(
        "-c",
        "--checkpoint",
        type=str,
        metavar="URI",
        help="URI to the job checkpoint store",
        required=True,
    )
    debug_parser.add_argument(
        "-j",
        "--job",
        type=str,
        metavar="ID",
        help="The id of the job to debug",
        required=True,
    )
    debug_env_group = debug_parser.add_mutually_exclusive_group(required=True)
    debug_env_group.add_argument(
        "--docker", metavar="IMAGE", help="Docker image to run the task in"
    )
    debug_env_group.add_argument(
        "--local", action="store_true", default=False, help="Run the task locally"
    )
    debug_parser.set_defaults(func=run_debug)


def run_debug(args: argparse.Namespace) -> None:
    checkpoint_store = LanceCheckpointStore(args.checkpoint_store)
    error_logger = CheckpointStoreErrorLogger(args.job_id, checkpoint_store)

    error_keys = list(error_logger.list_errors())
    for key in error_keys:
        _LOG.info(f"Found error {key}")

    while (key := input("Enter error key to debug: ")).lower() not in {
        "exit",
        "quit",
        "q",
    }:
        try:
            error_row = error_logger.get_error_row(key)
        except KeyError:
            _LOG.error(f"Error {key} not found")
            continue

        task_json = error_row["task"][0].as_py()
        udf_data = error_row["udf"][0].as_py()

        task_dict = json.loads(task_json)
        task = ScanTask(**task_dict)
        udf = cloudpickle.loads(udf_data)

        _LOG.info(f"Running task {task} with UDF {udf}")
        run_udf_task_with_debug(task, udf)
