# Copyright 2023-2024 Luminary Cloud, Inc. All Rights Reserved.
import io
import logging
from time import time, sleep

from .._proto.api.v0.luminarycloud.simulation.simulation_pb2 import (
    GetSimulationResponse,
    GetSimulationRequest,
    GetSimulationGlobalResidualsRequest,
    GetSimulationGlobalResidualsResponse,
    Simulation,
)
from .._client import Client

logger = logging.getLogger(__name__)


def wait_for_simulation(
    client: Client,
    simulation: Simulation,
    *,
    print_residuals: bool = False,
    interval_seconds: float = 5,
    timeout_seconds: float = float("inf"),
) -> Simulation.SimulationStatus.ValueType:
    """
    Waits until simulation is completed, failed, or suspended.

    Parameters
    ----------
    client: Client
        A Luminary Cloud Client (see client.py)
    simulation: Simulation
        The simulation to wait for.
    print_residuals: bool
        If true, residual values for the latest completed iteration will be printed.
        Frequency is based on interval_seconds.
    interval_seconds: float
        Number of seconds between polls. Default is five seconds.
    timeout_seconds: float
        Number of seconds before the operation times out. Default is infinity.

    Raises
    ------
    TimeoutError
    """
    deadline = time() + timeout_seconds
    # latest_iter is used to avoid printing the same iteration's residuals multiple times
    latest_printed_iter = -1
    while True:
        response: GetSimulationResponse = client.GetSimulation(
            GetSimulationRequest(id=simulation.id)
        )
        status = response.simulation.status
        if print_residuals and status != Simulation.SIMULATION_STATUS_PENDING:
            try:
                latest_printed_iter = _print_residuals(client, simulation.id, latest_printed_iter)
            except:
                # printing residuals is non-critical, so we catch all exceptions
                print(f"Current simulation status is: {Simulation.SimulationStatus.Name(status)}\n")

        if status in [
            Simulation.SIMULATION_STATUS_COMPLETED,
            Simulation.SIMULATION_STATUS_FAILED,
            Simulation.SIMULATION_STATUS_SUSPENDED,
        ]:
            return status
        if time() >= deadline:
            logger.error("`wait_for_simulation` timed out.")
            raise TimeoutError
        sleep(max(0, min(interval_seconds, deadline - time())))


def _print_residuals(client: Client, simulation_id: str, last_printed_iter: int) -> int:
    residuals: GetSimulationGlobalResidualsResponse = client.GetSimulationGlobalResiduals(
        GetSimulationGlobalResidualsRequest(id=simulation_id)
    )
    with io.StringIO(residuals.csv_file.full_contents.decode()) as stream:
        if last_printed_iter < 0:  # we haven't printed the header yet
            first_line = stream.readline().strip().split(",")
            header = "\t".join("{:>18}".format(s) for s in first_line)
            print(header)  # TODO: avoid printing, replace with a logger or something better

        last_line = stream.readlines()[-1].strip().split(",")
        latest_iter = int(last_line[0])
        # only print if this is a later iteration than we have previously seen
        if latest_iter > last_printed_iter:
            row = "\t".join(["{:>18}".format(s) for s in last_line])
            print(row)  # TODO: avoid printing, replace with a logger or something better
            return latest_iter

        return last_printed_iter
