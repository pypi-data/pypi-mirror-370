# Synth on CrunchDAO

Participate to the [Synth Subnet](https://github.com/mode-network/synth-subnet) directly via the CrunchDAO Platform, making it easier to have your code enter the protocol at no cost!

- [Synth on CrunchDAO](#synth-on-crunchdao)
- [Install](#install)
- [Your first model](#your-first-model)
- [Test it locally](#test-it-locally)
  - [Running using historical data](#running-using-historical-data)
  - [Running using live data](#running-using-live-data)
  - [Visualize the simulations](#visualize-the-simulations)
  - [Score the simulations](#score-the-simulations)
- [Accessing more data (for training only)](#accessing-more-data-for-training-only)

# Install

```bash
pip install synth-crunch
```

# Your first model

You may use the following code as a baseline submission, which has been adapted from the [official Synth Subnet example](https://github.com/mode-network/synth-subnet/blob/f66ea914bd62cd4c173da98ba1061a287242dbba/synth/miner/simulations.py#L10).

```python
from typing import Any

# Import the types
from synth_crunch import SynthMiner, Asset

# Import baseline functions
from synth_crunch.baseline import simulate_crypto_price_paths, convert_prices_to_time_format


class MyMiner(SynthMiner):

    def __init__(self):
        # Initialize your state in the constructor:
        # - load your model
        # - warmup your code

        pass

    def generate_simulations(
        self,
        asset: Asset,  # can only be "BTC", "ETH", "XAU" or "SOL"
        current_price: float,
        start_time: str,
        time_increment: int,
        time_length: int,
        num_simulations: int,
    ) -> list[list[dict[str, Any]]]:
        """
        Generate simulated price paths.

        Parameters:
            asset (str): The asset to simulate.
            current_price (float): The current price of the asset to simulate.
            start_time (str): The start time of the simulation. Defaults to current time.
            time_increment (int): Time increment in seconds.
            time_length (int): Total time length in seconds.
            num_simulations (int): Number of simulation runs.

        Returns:
            list[list[dict[str, Any]]]: A simulations list that contains a list of points, defined as {"time": str, "price": float}.
        """

        if start_time == "":
            raise ValueError("Start time must be provided.")

        sigma = 0.1
        if asset == "BTC":
            sigma *= 3
        elif asset == "ETH":
            sigma *= 1.25
        elif asset == "XAU":
            sigma *= 0.5
        elif asset == "SOL":
            sigma *= 0.75

        simulations = simulate_crypto_price_paths(
            current_price=current_price,
            time_increment=time_increment,
            time_length=time_length,
            num_simulations=num_simulations,
            sigma=sigma,
        )

        predictions = convert_prices_to_time_format(
            prices=simulations.tolist(),
            start_time=start_time,
            time_increment=time_increment,
        )

        return predictions
```

# Test it locally

Your miner can test on either historical or live data.

We recommend using historical data for quick iterations because you can be scored immediately. 

When you are ready to use the brand new data, use the live data. However, you will have to wait before you can be scored.

Once you have generated your simulations, they are validated to ensure that you are ready for the network.

## Running using historical data

```python
from datetime import datetime

# Import the function
from synth_crunch import test_historical

# Run the tester
result = test_historical(
    # You must instantiate your miner.
    MyMiner(),

    # Specify which asset you want to run with: "BTC," "ETH," "XAU," or "SOL".
    "BTC",

    # Customize the start date (default to 1st of February 2024 at 02:00 PM).
    start=datetime(2024, 2, 1, 14),

    # Customize the time increment between two predictions (default to 5min).
    time_increment=300,

    # Customize the duration of a simulation; it must be a divisor of the time increment (default to 24h).
    time_length=86400,

    # Customize the number of simulations to run (default to 300).
    num_simulations=300,
)
```

> [!TIP]
> Using the same `start` and `time_increment` parameters will make subsequent execution faster because the prices will be cached in memory.

## Running using live data

```python
# Import the function
from synth_crunch import test_live

# Run the tester
result = test_live(
    # You must instantiate your miner.
    MyMiner(),

    # Specify which asset you want to run with: "BTC," "ETH," "XAU," or "SOL".
    "BTC",

    # Customize the time increment between two predictions (default to 1min).
    time_increment=60,

    # Customize the duration of a simulation; it must be a divisor of the time increment (default to 5min).
    time_length=300,

    # Customize the number of simulations to run (default to 100).
    num_simulations=100,
)
```

> [!NOTE]
> The longer your `time_length` is, the longer you will have to wait to score your simulations.

## Visualize the simulations

It's easy to plot your simulations in one line.

```python
# Import the function
from synth_crunch import visualize_simulations

visualize_simulations(
    result,

    # Show a line with the price before your simulations with up to `n * time_interval` points. Set to `False` to disable it.
    show_past=10,

    # Customize the figure size (default to (10, 6)).
    figsize=(10, 6),
)
```

The code will produce the following:

![visualization](./assets/visualization.png)

## Score the simulations

Your simulations will be scored using [Synth Subnet's scoring function](https://github.com/mode-network/synth-subnet/blob/d076dc3bcdf93256a278dfec1cbe72b0c47612f6/synth/validator/crps_calculation.py#L5).

If you run a test using live data, you will have to wait for the targets to resolve before you can score them. The function will wait by default (`time.sleep(x)`) until the time comes. If you do not want to wait, an error will be raised instead.

```python
# Import the function
from synth_crunch import score_simulations

# Score your results
scored_result = score_simulations(
    result,

    # Use sleep to wait until the targets are resolved (default to True).
    wait_until_resolved=True,
)

print("My miner score is:", scored_result.score)
print()

print("More details:")
print(scored_result.score_summary)
```

> [!WARNING]
> This will not be your score on the leaderboard. When multiple miners are scored to generate a leaderboard, [the scores are first subtracted from the lowest miner's score. Then, the prompt score is used to compute the rewards.](https://github.com/mode-network/synth-subnet/blob/d076dc3bcdf93256a278dfec1cbe72b0c47612f6/synth/validator/reward.py#L180)

# Accessing more data (for training only)

For this competition, you may use any data you wish for your training.

The library exposes a mini Python client, which allows you to easily access asset prices from [Pyth](https://pyth.network/) with up to one year at a time.

> [!IMPORTANT]  
> The Pyth data is only available for training. This is because no Internet connection is possible when running on the platform.

```python
from datetime import datetime

# Import the function
from synth_crunch import pyth

prices = pyth.get_price_history(
    # Specify which asset you want to get data of: "BTC," "ETH," "XAU," or "SOL".
    asset="BTC",

    # Start time of the data.
    from_=datetime(2024, 1, 1),

    # End time of the data (up to 1 year).
    to=datetime(2024, 1, 2),

    # Data resolution, must be one of: "minute", "2minute", "5minute", "15minute", "30minute", "hour", "2hour", "4hour", "6hour", "12hour", "day", "week", "month".
    resolution="minute",
)
```

The prices are represented using a `pandas.Series` of `float`, using `datetime` as index.

> [!WARNING]
> Pyth limits the number of data points that can be returned at once. If you are requesting a large amount of data, you may need to change the `resolution` (e.g. for a year, the smallest resolution is `"hour"`).
