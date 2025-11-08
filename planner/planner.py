from bisect import bisect_left
from datetime import timedelta
from math import ceil, inf
from typing import Any, NamedTuple

import pandas as pd

# All time values are in minutes
# Storing them as ints/float is MUCH simpler
# than using std types (thanks python)0)


class TimePeriod:
    start: int
    end: int

    def __init__(self, start: int, end: int) -> None:
        if end <= start:
            raise ValueError(
                f"time period end {end} must be greater than start {start}"
            )
        self.start = start
        self.end = end

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, TimePeriod):
            return False
        return self.start < other.start

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TimePeriod):
            return False
        return self.start == other.start and self.end == other.end

    def contains(self, other: object) -> bool:
        if not isinstance(other, TimePeriod):
            return False
        return self.start <= other.start and self.end >= other.end


class Group:
    name: str
    count: int
    next_available: int
    limit: TimePeriod
    activity: str

    def __init__(self, name: str, count: int, activity: str, limit: TimePeriod) -> None:
        if count <= 0:
            raise ValueError(f"group count must be positive, got {count}")
        self.name = name
        self.count = count
        self.next_available = limit.start
        self.limit = limit
        self.activity = activity


class Court:
    name: str
    time_available: list[TimePeriod]

    def __init__(self, name: str, available: list[TimePeriod]) -> None:
        self.name = name
        self.time_available = available
        self.time_available.sort()

    def book_period(self, period: TimePeriod) -> bool:
        idx = bisect_left(self.time_available, period)
        if idx >= len(self.time_available):
            return False
        if (
            self.time_available[idx].start > period.start
            or self.time_available[idx] < period.end
        ):
            return False

        if period == self.time_available[idx]:
            self.time_available.pop(idx)
        elif period.end == self.time_available[idx].end:
            self.time_available[idx].end = period.start
        elif period.start == self.time_available[idx].start:
            self.time_available[idx].start = period.end
        else:
            end = self.time_available[idx].end
            self.time_available[idx].end = period.start
            self.time_available.insert(idx + 1, TimePeriod(period.end, end))
        return True

    def unbook_period(self, period: TimePeriod):
        idx: int = bisect_left(self.time_available, period)
        if (idx > 0 and self.time_available[idx - 1].contains(period)) or (
            idx < len(self.time_available) and self.time_available[idx].contains(period)
        ):
            return

        insert: TimePeriod = period
        if idx > 0 and self.time_available[idx - 1].end >= period.start:
            insert.start = self.time_available[idx - 1].start
            self.time_available.pop(idx - 1)
            idx -= 1

        while (
            idx < len(self.time_available)
            and self.time_available[idx].end <= insert.end
        ):
            self.time_available.pop(idx)

        self.time_available.insert(idx, insert)


class TimetableEntry(NamedTuple):
    group_idx: int
    court_idx: int
    period: TimePeriod


class Solver:
    groups: list[Group]
    courts: list[Court]
    rest_time: int
    evaluate_time: int
    stage_limits: list[int]
    activity_durations: dict[str, float]

    def __init__(
        self,
        groups: list[Group],
        courts: list[Court],
        rest_time: int,
        evaluate_time: int,
        stage_limits: list[int],
        activity_durations: dict[str, float],
    ) -> None:
        self.groups = groups
        self.courts = courts
        self.rest_time = rest_time
        self.evaluate_time = evaluate_time
        self.stage_limits = stage_limits
        self.activity_durations = activity_durations

    def find_timetable(self) -> list[TimetableEntry] | None:
        if len(self.courts) == 0 or len(self.groups) == 0:
            return None

        timetable: list[TimetableEntry] = []
        if self._find_timetable_recursive(0, timetable) is not None:
            return None
        return timetable

    def _get_performace_time(self, group: Group) -> int:
        if group.activity not in self.activity_durations:
            raise ValueError(
                f"unknown activity '{group.activity}'")
        elif group.count <= 0:
            raise ValueError(f"performer count must be positive, got {group.count}")
        return ceil(
            group.count * self.activity_durations[group.activity]
            + self.evaluate_time
        )

    def _find_timetable_recursive(
        self, idx: int, timetable: list[TimetableEntry]
    ) -> TimetableEntry | None:
        """
        recursively builds timetable, records it on success
        returns None on success, or information about group that couldn't get a place in timetable
        """
        if idx >= len(self.groups):
            # everyone placed, we got a valid timetable
            return None

        group: Group = self.groups[idx]
        stage_idx: int = len(self.stage_limits)
        for i in range(0, len(self.stage_limits)):
            if self.stage_limits[i] < group.count:
                stage_idx = i
        has_next_stage: bool = stage_idx == len(self.stage_limits)

        duration: int = self._get_performace_time(group)

        fail_result = TimetableEntry(
            period=TimePeriod(group.next_available, group.limit.end), group_idx=idx, court_idx=0
        )
        for start in range(group.next_available, group.limit.end):
            if start + duration > group.limit.end:
                return fail_result
            booked_period: TimePeriod = TimePeriod(start, start + duration)
            for court_idx in range(0, len(self.courts)):
                court = self.courts[court_idx]
                if not court.book_period(booked_period):
                    continue
                prev_count = group.count
                prev_next_available = group.next_available
                if has_next_stage:
                    group.count = self.stage_limits[stage_idx]
                group.next_available = start + duration + self.rest_time
                result = self._find_timetable_recursive(
                    idx + 1 if has_next_stage else idx, timetable
                )

                if result is None:
                    timetable.append(
                        TimetableEntry(period=booked_period, group_idx=idx, court_idx=court_idx)
                    )
                    return None

                group.count = prev_count
                group.next_available = prev_next_available
                court.unbook_period(booked_period)
                if result.group_idx == idx:
                    # we are blocking ourselves, can't solve this by moving forward
                    # someone else up the stack has to move
                    return fail_result
                elif (
                    booked_period.end < result.period.start
                    or booked_period.start >= result.period.end
                ):
                    # we are not the ones blocking, skip to the last group that booked
                    # a relevant period
                    return result
                # otherwise, try other values
        # nothing found
        return fail_result


def generate_schedule(args: dict) -> dict[str, Any] | None:
    OPTIONS_KEY = 'options'
    LAST_UPLOAD_KEY = 'lastUploadPath'
    WINDOW_KEY = 'window'
    DATE_KEY = 'date'

    if OPTIONS_KEY not in args or not isinstance(args[OPTIONS_KEY], dict):
        return None
    options = args[OPTIONS_KEY]
    if LAST_UPLOAD_KEY not in options or not isinstance(options[LAST_UPLOAD_KEY], str):
        return None

    if WINDOW_KEY not in args or not isinstance(args[WINDOW_KEY], dict):
        return None
    window = args['window']
    if DATE_KEY not in window or not isinstance(window[DATE_KEY], str):
        return None

    date = window[DATE_KEY]
    rest_time = int(args.get('restTime', 0))
    evaluate_time = int(args.get('evaluateTime', 0))

    info = parse_excel(options[LAST_UPLOAD_KEY])
    planner = Solver(info.groups, info.courts, rest_time, evaluate_time, info.stage_limits, info.activity_durations)

    timetable = planner.find_timetable()
    if timetable is None:
        return None

    result: dict[str, Any] = {'date': date, 'slots': []}
    for slot in timetable:
        result['slots'].append({
            'start': str(timedelta(minutes=slot.period.start)),
            'end': str(timedelta(minutes=slot.period.end)),
            'courtId': planner.courts[slot.court_idx].name,
            'groupId': planner.groups[slot.group_idx].name,
            'item': planner.groups[slot.group_idx].activity,
            'judge': '',
            'comment': ''
        })
    return result

class InputInfo(NamedTuple):
    activity_durations: dict[str, float]
    courts: list[Court]
    groups: list[Group]
    stage_limits: list[int]


def parse_excel(path: str) -> InputInfo:
    books = pd.read_excel(path, sheet_name=None)

    activity_durations: dict[str, float] = { str(getattr(row, 'Название')): int(getattr(row, 'Длительность')) for row in books['Упражнения'].itertuples() }
    stage_limits: list[int] = [ int(getattr(row, 'МаксимумУчастников')) for row in books['Этапы'].iterrows() ]

    min_start: float = inf
    max_end: int = 0
    courts_dict: dict[str, list[TimePeriod]] = {}
    for row in books['Корты'].itertuples():
        id = str(getattr(row, 'Корт'))
        start = ceil(pd.to_timedelta(getattr(row, 'Открытие')).total_seconds() / 60)
        end = int(pd.to_timedelta(getattr(row, 'Закрытие')).total_seconds() / 60)
        courts_dict.setdefault(id, []).append(TimePeriod(start, end))
        min_start = min(min_start, start)
        max_end = max(max_end, end)
    courts = [Court(name, periods) for name, periods in courts_dict.items()]

    books['Группы'].fillna({'МинимальноеВремяНачала': int(min_start), 'МаксимальноеВремяОкончания': max_end})
    groups: list[Group] = []
    for row in books['Группы'].itertuples():
        name = str(getattr(row, 'ИмяГруппы'))
        count = int(getattr(row, 'КоличествоУчастников'))
        activity = str(getattr(row, 'Упражнение'))
        start = int(getattr(row, 'МинимальноеВремяНачала'))
        end = int(getattr(row, 'МаксимальноеВремяОкончания'))
        groups.append(Group(name, count, activity, TimePeriod(start, end)))

    return InputInfo(groups=groups, courts=courts, activity_durations=activity_durations, stage_limits=stage_limits)
