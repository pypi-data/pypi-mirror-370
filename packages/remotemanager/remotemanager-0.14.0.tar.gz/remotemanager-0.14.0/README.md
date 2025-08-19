# remotemanager

Modular serialisation and management package for handling the running of functions on remote machines

Based off of the BigDFT RemoteRunner concept, remotemanager represents an improvement and expansion on the concepts based there.

Primary usage is via a `Dataset`, which connects to a remote machine via `URL`

You can think of the `Dataset` as a "container" of sorts for a calculation, to which "runs" are attached. These runs are then executed on the remote machine described by the provided `URL`

## Installation

A quick install of the latest stable release can be done via `pip install remotemanager`

For development, you can clone this repo and install via `cd remotemanager && pip install -e .[dev]`

Tip: You can clone a specific branch with `git clone -b devel`.

If you want to build the docs locally a `pandoc` install is required.

You can install all required python packages with the `[dev]` or `[docs]` optionals.

## HPC

Remotemanager exists to facilitate running on High Performance Compute machines (supercomputers). Script generation is ideally done via the `BaseComputer` module.

Existing Computers can be found at [this repository](https://gitlab.com/l_sim/remotemanager-computers). For creating a new machine class, see the [documentation](https://l_sim.gitlab.io/remotemanager/).

## Documentation

See the [documentation](https://l_sim.gitlab.io/remotemanager/) for further information, tutorials and api documentation.

## Quickstart

This section will run through running a very basic function on a machine.

It roughly echoes the [quickstart](https://l_sim.gitlab.io/remotemanager/tutorials/A1_Quickstart.html) page found in the
docs.

### Function Definition

Start by defining your "calculation" as a python function.

```python
def multiply(a, b):
    import time

    time.sleep(1)

    return a * b
```

### Remote Connection

We need to be able to connect to a remote machine to run this function.

Assuming you can connect to a machine with a string like `ssh user@host` or just `ssh machine`, you can directly create
a connection.

Use the `URL` module for this.

```python
from remotemanager import URL

connection = URL("ssh@machine")
```

### Commands

You can execute commands on this machine using the `cmd` method:

```python
connection.cmd("pwd")
>> > "/home/user"
```

### Running Functions

To execute your function on the specified machine, create a `Dataset`

```python
from remotemanager import Dataset

ds = Dataset(function=multiply, url=connection, name="test")
```

#### Adding Runs

You can specify the inputs that your function should use by adding `Runner` instances to the `Dataset`

```python
ds.append_run({"a": 10, "b": 7})
```

#### Running

Now run your `Dataset` with `run()`.

You can wait for completion with `wait()`

```python
ds.run()

ds.wait(1, 10)
```

Here, we are waiting for a maximum of 10s, and checking for results every 1s

### Results

Result collection is done in two stages.

Once a run is complete, we must first fetch the results with `fetch_results`.

Then we can access the results at the `results` property

```python
ds.fetch_results()

ds.results

>> > [70]
```

## sanzu

The `sanzu` functionality allows you to tag a jupyter cell for remote running.

The cell will be converted into a function, set off to the specified remote machine, and executed there.

For detailed information, see the
relevant [section of the docs](https://l_sim.gitlab.io/remotemanager/tutorials/D2_Jupyter_Magic.html)

To use this functionality, first enable the magic:

```python
%load_ext
remotemanager
```

You should then create a `URL` instance for your machine:

```python
from remotemanager import URL

connection = URL(...)
```

And now we can execute any cell on this machine by using the `%%sanzu` protocol:

```python
%%sanzu
url = connection
%%sargs
a = 10
%%sargs
b = 7

a * b

>> > 70
```

This can be useful for doing file operations on the remote machine, however it is possible to access your results.

### Accessing Sanzu Results

A sanzu run will inject a `magic_dataset` object into the jupyter runtime.

This is the `Dataset` that was used to execute the most recent cell, so you can access the information from there.

For our last run, we can see our results here:

```python
print(magic_dataset.results)

>> > [70]
```
