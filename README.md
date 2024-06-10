# habits.txt

[![PyPI version](https://badge.fury.io/py/habits.txt.svg)](https://badge.fury.io/py/habits.txt)

habits.txt is a plain text habit tracker.

[Features](#features) | [Installation](#installation) | [Concepts](#concepts) | [Format](#format) | [Directives](#directives) | [Examples](examples)

## Features

- [x] Track habits in a plain text file
- [x] Track boolean (done/not done) habits or measurable habits/metrics (e.g. weight)
- [x] Custom and complex frequencies for habits (daily, on Monday and Friday, on the 1st every month, etc...)
- [x] Get stats about your habits with the CLI or with charts opening in your browser

## Installation

```bash
pip install habits.txt
```

You can then use the CLI with:

```bash
hbtxt --help
```

Alternatively, you can use the executable provided by the latest release.

## Concepts

### Time-bound

A habit is time-bound. It has a start date, and eventually an end date.
It means with habits.txt, you can track habits for a specific period of time. When you want to stop tracking a habit, you can just stop tracking it.

### Frequency

A habit is defined by a frequency, else it's called a task. The minimum frequency supported by habits.txt is daily (it doesn't support intra-day habits).

### Boolean or Measurable

A habit can be boolean or measurable. A boolean habit is either done or not done. A measurable habit has a value.

## Format

Habits are tracked in what I call a "journal" which is just a plain text file. A journal contains "directives".

A directive is composed of a date, a directive type, a habit name, and other metadata specific to the directive type. For example, here is a sample directive:

```
2024-01-01 track "Read 5 pages a day" (* * *)
```

You can comment lines in your journal by starting them with a `#` character.
You can't add comments at the end of a line.

```
# Start tracking a habit
2024-01-01 track "Read 5 pages a day" (* * *)
```

**New in `1.1.0`**: You can now add custom metadata to your directives. The metadata should be key-value pairs separated by a colon, and should not include spaces.

```
2024-01-01 track "Read 5 pages a day" (* * *) metadata1:value1 metadata2:value2
```

## Directives

### track

To start tracking a habit, you use the `track` directive and specify the frequency of the habit enclosed in parentheses.
Optionally, you can make the habit measurable by specifying the "measurable" keyword.

The frequency follows a simplified [cron](https://en.wikipedia.org/wiki/Cron) syntax, omitting the minute and the hour.

Example:

```
2024-01-01 track "Read 5 pages a day" (* * *)
2024-01-01 track "Exercise" (* * 1,3,5) measurable
```

### untrack

To stop tracking a habit, you use the `untrack` directive.

Example:

```
2024-02-01 untrack "Read 5 pages a day"
```

### record

To record a habit, you use the `record` directive and specify a value.

The allowed values are `yes`, `no`, or a number. You should not mix boolean and numeric values for the same habit.

**New in `1.1.0`**: If you add custom metadata to a record directive, be sure to add it before the value, because the value should be the last element of the line.

You can write directives but omit the directive type, it will default to `record` (as it is supposed to be the most common directive).

Example:

```
2024-01-01 record "Read 5 pages a day" 5
2024-01-01 record "Workout" yes
2024-01-01 "Weight" 70.5
2024-01-01 record "Meditation" meta:value yes
```

## Examples

`habits.journal`:

```txt
2024-01-01 track "Reading" (* * *)
2024-01-01 track "Exercise" (* * 1,3,5)
2024-01-01 track "Weight" (* * 1) measurable
2024-01-01 track "Meditation" (* * *) meta:value

# Record habits
2024-01-01 record "Reading" yes
2024-01-01 record "Exercise" no
2024-01-01 record "Weight" 70.5
2024-01-01 record "Meditation" place:home yes
```

Once your journal is ready, you can use the CLI to interact with it.

```bash
# Set the journal file as default journal
hbtxt config set journal /path/to/habits.journal

# Fill the habits for today interactively
hbtxt fill -i
Exercise (2024-01-01): yes

# Filter habit records
hbtxt filter -n "Exercise"
2024-01-01 Exercise yes

hbtxt filter -m "place:home"
2024-01-01 Meditation place:home yes

# Get information about the other available commands
hbtxt --help

# Get information about a given command
hbtxt chart --help

# Get information about the available config options
hbtxt config set --help
```
