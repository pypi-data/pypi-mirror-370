import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from math import ceil, isinf, isnan
from typing import Literal, cast

import matplotlib.pyplot as plt
import numpy
import pandas
from tqdm.auto import tqdm

from .baseline import calculate_crps_for_miner
from .data import shared_pyth_hermes as price_provider
from .interface import Asset, GenerateSimulationsOutput, SynthMiner

logger = logging.getLogger()

ONE_DAY = 24 * 60 * 60
TWO_DAYS = ONE_DAY * 2


@dataclass(frozen=True)
class TestOutput:
    simulations: GenerateSimulationsOutput
    asset: Asset
    start: datetime
    time_increment: int
    time_length: int
    num_simulations: int
    validate_output: bool


@dataclass(frozen=True)
class PendingTestOutput(TestOutput):
    pass


def run_live(
    miner: SynthMiner,
    asset: Asset,
    *,
    time_increment: int = 60,
    time_length: int = 300,
    num_simulations: int = 100,
    validate_output: bool = True,
) -> PendingTestOutput:
    """
    Run the miner in live mode, predicting future prices.
    You will have to wait before being able to compute the results.

    :param miner: The SynthMiner instance to run.
    :param asset: The asset to predict prices for.
    :param time_increment: The resolution of the predictions in seconds (default is 1min, must be >=60s).
    :param time_length: The total length of the predictions in seconds (default is 5min, must be >=60s).
    :param num_simulations: The number of simulations to run (default is 100, must be >0).
    :param validate_output: Whether to validate the output of the miner (default is True).
    :raises ValueError: If `start` is provided when `live` is True, or if `end` is in the past.
    """

    start = datetime.now()

    results = _run(
        miner=miner,
        asset=asset,
        live=True,
        start=start,
        time_increment=time_increment,
        time_length=time_length,
        num_simulations=num_simulations,
        should_validate_output=validate_output,
    )

    return cast(PendingTestOutput, results)


@dataclass(frozen=True)
class ResolvedTestOutput(TestOutput):
    prices: pandas.Series


def run_historical(
    miner: SynthMiner,
    asset: Asset,
    *,
    start=datetime(2024, 2, 1, 14, 0, 0),
    time_increment: int = 300,
    time_length: int = ONE_DAY,
    num_simulations: int = 300,
    validate_output: bool = True,
) -> ResolvedTestOutput:
    """
    Run the miner in historical mode, predicting prices between the specified start and end times.

    :param miner: The SynthMiner instance to run.
    :param asset: The asset to predict prices for.
    :param start: The start time of the predictions. (default is 1st of February 2024).
    :param time_increment: The resolution of the predictions in seconds (default is 5min, must be >=60s).
    :param time_length: The total length of the predictions in seconds (default is 1day, must be >=60s).
    :param num_simulations: The number of simulations to run (default is 300, must be >0).
    :param validate_output: Whether to validate the output of the miner (default is True).
    :raises ValueError: If `start` + `time_length` is in the future.
    """

    now = datetime.now()
    end = start + timedelta(seconds=time_length)
    if end >= now:
        raise ValueError("`start` + `time_length` is in the future")

    results = _run(
        miner=miner,
        asset=asset,
        live=False,
        start=start,
        time_increment=time_increment,
        time_length=time_length,
        num_simulations=num_simulations,
        should_validate_output=validate_output,
    )

    return cast(ResolvedTestOutput, results)


def _run(
    *,
    # TODO should we accept the class and instanciate it here?
    miner: SynthMiner,
    asset: Asset,
    live: bool,
    start: datetime,
    time_increment: int,
    time_length: int,
    num_simulations: int,
    should_validate_output: bool,
) -> TestOutput:
    if time_increment < 60:
        raise ValueError("`time_increment` must be greater than 60 seconds")
    if time_increment % 60 != 0:
        raise ValueError("`time_increment` must be a multiple of 60 seconds")
    if time_length < 60:
        raise ValueError("`time_length` must be greater than 60 seconds")
    if time_length > TWO_DAYS:
        raise ValueError(f"`time_length` must not be greater {TWO_DAYS} seconds (2 days)")
    if num_simulations <= 0:
        raise ValueError("`num_simulations` must be greater than 0")
    if time_length % time_increment != 0:
        raise ValueError("`time_length` must be a multiple of `time_increment`")

    # TODO is replacing the tzinfo like this correct?
    start = start.replace(second=0, microsecond=0, tzinfo=timezone.utc)

    current_price = _get_current_price(
        asset=asset,
        live=live,
        start=start,
        time_length=time_length,
    )

    simulation_type = "live" if live else "historical"
    logger.info(f"starting {asset} {simulation_type} simulation with current price at {current_price}")

    simulations = miner.generate_simulations(
        asset=asset,
        current_price=current_price,
        start_time=start.isoformat(),
        time_increment=time_increment,
        time_length=time_length,
        num_simulations=num_simulations,
    )

    if should_validate_output:
        expected_point_count = (time_length // time_increment) + 1

        validate_output(
            simulations=simulations,
            num_simulations=num_simulations,
            expected_point_count=expected_point_count,
        )

    if live:
        return PendingTestOutput(
            simulations=simulations,
            asset=asset,
            start=start,
            time_increment=time_increment,
            time_length=time_length,
            num_simulations=num_simulations,
            validate_output=should_validate_output,
        )
    else:
        return ResolvedTestOutput(
            simulations=simulations,
            asset=asset,
            start=start,
            time_increment=time_increment,
            time_length=time_length,
            num_simulations=num_simulations,
            validate_output=should_validate_output,
            prices=prices,  # type: ignore
        )


def _get_current_price(
    *,
    asset: Asset,
    live: bool,
    start: datetime,
    time_length: int,
):
    if live:
        prices = price_provider.get_price_history(
            asset=asset,
            from_=start,
            to=start,
            resolution="minute",
        )

        if len(prices):
            return prices.iloc[0]

        logger.info(f"history endpoint returned no prices for {start.isoformat()}, getting the last price")
        return price_provider.get_last_price(
            asset=asset,
        )

    else:
        end = start + timedelta(seconds=time_length)
        prices = price_provider.get_price_history(
            asset=asset,
            from_=start,
            to=end,
            resolution="minute",
        )

        return prices.iloc[0]


class SimulationFormatError(ValueError):
    """
    Raised when the output of `generate_simulations` does not match the expected format.
    """


def validate_output(
    *,
    simulations: GenerateSimulationsOutput,
    num_simulations: int,
    expected_point_count: int,
):
    point_keys = {"time", "price"}

    if not isinstance(simulations, list):
        raise SimulationFormatError("`generate_simulations` must return a list of simulations")
    if len(simulations) != num_simulations:
        raise SimulationFormatError(f"expected {num_simulations} simulations, got {len(simulations)}")

    for index, simulation in enumerate(simulations):
        if not isinstance(simulation, list):
            raise SimulationFormatError(f"simulation at index {index} is not a list, got {type(simulation)}")
        if len(simulation) != expected_point_count:
            raise SimulationFormatError(f"simulation at index {index} has {len(simulation)} points, expected {expected_point_count}")

        for jndex, point in enumerate(simulation):
            if not isinstance(point, dict):
                raise SimulationFormatError(f"point at index {index}[{jndex}] is not a dict, got {type(point)}")

            keys = set(point.keys())
            if point_keys != keys:
                raise SimulationFormatError(f"point at index {index}[{jndex}] has keys {keys}, expected {point_keys}")

            time = point["time"]
            if not isinstance(time, str):
                raise SimulationFormatError(f"time at index {index}[{jndex}] is not a string, got {type(time)}")
            try:
                datetime.fromisoformat(time)
            except ValueError as error:
                raise SimulationFormatError(f"time at index {index}[{jndex}] is not a valid ISO 8601 string: {time}") from error

            price = point["price"]
            if not isinstance(price, (int, float)) or isinstance(price, bool):
                raise SimulationFormatError(f"price at index {index}[{jndex}] is not a number, got {type(price)}")

            if isnan(price):
                raise SimulationFormatError(f"price at index {index}[{jndex}] is nan")

            if isinf(price):
                sign = "-" if price < 0 else "+"
                raise SimulationFormatError(f"price at index {index}[{jndex}] is {sign}inf")

    return simulations


def visualize_simulations(
    result: PendingTestOutput | ResolvedTestOutput,
    *,
    show_past: Literal[False] | int = 10,
    figsize: tuple[int, int] = (10, 6),
):
    """
    Plot a simulations.

    :param result: The output of the test run.
    :param show_past: The number of `time_interval` to show past prices for. Set to `False` or `0` to disable.
    :param figsize: The size of the figure to plot.
    """

    plt.figure(figsize=figsize)

    if show_past > 0:
        past = price_provider.get_price_history(
            asset=result.asset,
            from_=(result.start - timedelta(seconds=result.time_increment * show_past)).replace(second=0),
            to=result.start,
            resolution="minute",
        )

        plt.plot(past.index, past, color='green', linewidth=2, label='Past Price')

    for index, simulation in enumerate(result.simulations):
        dataframe = pandas.DataFrame(simulation)
        time = pandas.to_datetime(dataframe['time'])
        price = dataframe['price']

        plt.plot(time, price, color='blue', alpha=0.6, linewidth=1, label='Prediction Price' if index == 0 else "")

    if isinstance(result, ResolvedTestOutput):
        plt.plot(result.prices.index, result.prices, color='red', linewidth=2, label='Real Price')

    plt.title(f'Your {result.asset} Simulation', fontsize=16, fontweight='bold')
    plt.xlabel('Time', fontsize=12)
    plt.ylabel('Price', fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.show()


@dataclass(frozen=True)
class ScoredTestOutput(ResolvedTestOutput):
    score: float
    score_details: pandas.DataFrame

    @property
    def score_summary(self) -> str:
        filtered = self.score_details[self.score_details["Increment"] == "Total"]
        filtered = filtered[["Interval", "CRPS"]]

        return filtered.to_string(index=False)


class TargetNotResolvedError(ValueError):
    """
    Raised when the target of the simulations is not resolved yet.
    """


def score_simulations(
    result: PendingTestOutput | ResolvedTestOutput,
    *,
    wait_until_resolved=True,
) -> ScoredTestOutput:
    """
    Score the simulations.

    :param result: The output of the test run.
    :param wait_until_resolved: Whether to wait until the simulations target are resolved.
    """

    if isinstance(result, ScoredTestOutput):
        print(f"Result is already scored!")
        return result

    if isinstance(result, PendingTestOutput):
        end = result.start + timedelta(seconds=result.time_length)
        now = datetime.now(timezone.utc)

        wait_until_next_minute = 60
        wait_extra_seconds_for_api = 10
        delta = ceil((end - now).total_seconds() + wait_until_next_minute + wait_extra_seconds_for_api)
        if delta > 0:
            if not wait_until_resolved:
                raise TargetNotResolvedError(f"simulation targets are not resolved yet, retry in {delta} seconds (include extras to be safe)")

            print(f"Waiting {delta} seconds (include extras to be safe) until the simulations target are resolved. Do an interrupt (Ctrl+C) if you want to stop early.")
            for _ in tqdm(range(delta), desc="Waiting for targets to resolve", unit="s"):
                time.sleep(1)

        prices = price_provider.get_price_history(
            asset=result.asset,
            from_=result.start,
            to=end,
        )

    else:
        prices = result.prices

    simulation_runs = _prepare_simulation_runs(result)
    real_price_path = _prepare_prices(result, prices)

    score, score_details = calculate_crps_for_miner(
        simulation_runs=simulation_runs,
        real_price_path=real_price_path,
        time_increment=result.time_increment,
    )

    return ScoredTestOutput(
        simulations=result.simulations,
        asset=result.asset,
        start=result.start,
        time_increment=result.time_increment,
        time_length=result.time_length,
        num_simulations=result.num_simulations,
        validate_output=result.validate_output,
        prices=prices,
        score=score,
        score_details=pandas.DataFrame(score_details),
    )


def _prepare_simulation_runs(result: TestOutput) -> numpy.ndarray:
    return numpy.array([
        [
            point['price']
            for point in simulation
        ]
        for simulation in result.simulations
    ])


def _prepare_prices(result: TestOutput, prices: pandas.Series) -> numpy.ndarray:
    first = pandas.DataFrame(
        [
            point['time']
            for point in result.simulations[0]
        ],
        columns=['time'],
    )

    first['time'] = pandas.to_datetime(first['time'])

    first = first.merge(
        prices,
        left_on='time',
        right_index=True,
        how='left'
    )

    return numpy.array(first["price"].astype(float).tolist())
