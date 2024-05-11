# habits.txt

habits.txt is a plain text habit tracker.

## Concepts

### Time-bound

A habit is time-bound. It has a start date, and eventually an end date.
It means with habits.txt, you can track habits for a specific period of time. When you want to stop tracking a habit, you can just stop tracking it.

### Frequency

A habit is defined by a frequency, else it's called a task. The minimum frequency supported by habits.txt is daily (it doesn't support intra-day habits).

### Boolean or Numeric

A habit can be boolean or numeric. A boolean habit is either done or not done. A numeric habit is a value, like the number of pages read in a day.


## Format

Habits are tracked in what I call a "journal" which is just a plain text file. A journal contains "directives".

A directive is composed of a date, a directive type, a habit name, and other metadata specific to the directive type. For example, here is a sample directive:

```
2024-01-01 track "Read 5 pages a day"
```

You can comment lines in your journal by starting them with a `#` character.
You can't add comments at the end of a line.

```
# Start tracking a habit
2024-01-01 track "Read 5 pages a day"
```


## Directives

### track

To start tracking a habit, you use the `track` directive and specify the frequency of the habit.

The frequency follows a simplified [cron](https://en.wikipedia.org/wiki/Cron) syntax, omitting the minute and the hour.

Example:
```
2024-01-01 track "Read 5 pages a day" * * *
2024-01-01 track "Exercise" * * 1,3,5
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

You can write directives but omit the directive type, it will default to `record`.

Example:
```
2024-01-01 record "Read 5 pages a day" 5
2024-01-01 record "Workout" yes
2024-01-01 "Weight" 70.5
```
