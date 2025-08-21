"""
Scheduler for running API syncs on defined intervals or cron schedules.
"""

import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Optional, TypeVar, cast

from croniter import croniter

logger = logging.getLogger(__name__)

# Type variables for callbacks
T = TypeVar("T")
R = TypeVar("R")


class Scheduler:
    """
    Scheduler for running API sync operations on defined schedules.

    This class handles scheduling of sync operations based on:
    - Interval: Run every N minutes/hours
    - Cron: Run according to cron expression
    - One-time: Run once at a specific time
    """

    def __init__(self) -> None:
        self.schedule_type: Optional[str] = None
        self.schedule_config: Dict[str, Any] = {}
        self.running: bool = False
        self.thread: Optional[threading.Thread] = None
        self.last_run: Optional[datetime] = None
        logger.debug("Initialized Scheduler")

    def add_schedule(self, type: str, **kwargs) -> None:
        """
        Configure the schedule for sync operations.

        Args:
            type: Type of schedule ('interval', 'cron', or 'once')
            **kwargs: Schedule-specific parameters
        """
        self.schedule_type = type
        self.schedule_config = kwargs

        # Validate schedule config based on type
        if type == "interval":
            if not any(k in kwargs for k in ["seconds", "minutes", "hours", "days"]):
                raise ValueError(
                    "Interval schedule must specify seconds, minutes, hours, or days"
                )

        elif type == "cron":
            if "expression" not in kwargs:
                raise ValueError("Cron schedule must specify an expression")

            # Validate cron expression
            try:
                croniter(kwargs["expression"], datetime.now())
            except Exception as e:
                raise ValueError(f"Invalid cron expression: {str(e)}")

        elif type == "once":
            if "datetime" not in kwargs:
                raise ValueError("One-time schedule must specify a datetime")

        else:
            raise ValueError(f"Unsupported schedule type: {type}")

        logger.info(f"Added {type} schedule: {kwargs}")

    def get_schedule_info(self) -> str:
        """Get human-readable description of the current schedule."""
        if not self.schedule_type:
            return "No schedule configured"

        if self.schedule_type == "interval":
            interval_parts = []
            for unit in ["seconds", "minutes", "hours", "days"]:
                if unit in self.schedule_config:
                    value = self.schedule_config[unit]
                    if value == 1:
                        interval_parts.append(
                            f"1 {unit[:-1]}"
                        )  # Remove 's' for singular
                    else:
                        interval_parts.append(f"{value} {unit}")

            return f"Every {', '.join(interval_parts)}"

        elif self.schedule_type == "cron":
            return f"Cron: {self.schedule_config['expression']}"

        elif self.schedule_type == "once":
            return f"Once at {self.schedule_config['datetime']}"

        return "Unknown schedule"

    def _calculate_next_run(self) -> datetime:
        """Calculate the next scheduled run time based on configuration."""
        now = datetime.now()

        if self.schedule_type == "interval":
            interval = timedelta(
                seconds=self.schedule_config.get("seconds", 0),
                minutes=self.schedule_config.get("minutes", 0),
                hours=self.schedule_config.get("hours", 0),
                days=self.schedule_config.get("days", 0),
            )

            if self.last_run:
                return self.last_run + interval
            else:
                return now + interval

        elif self.schedule_type == "cron" and "expression" in self.schedule_config:
            cron = croniter(self.schedule_config["expression"], now)
            return cast(datetime, cron.get_next(datetime))

        elif self.schedule_type == "once" and "datetime" in self.schedule_config:
            return cast(datetime, self.schedule_config["datetime"])

        # Default fallback
        return now + timedelta(hours=1)

    def _scheduler_loop(
        self, callback: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> None:
        """
        Main scheduler loop that runs the callback at scheduled times.

        Args:
            callback: Function to call on schedule
            *args, **kwargs: Arguments to pass to the callback
        """
        self.running = True

        # One-time run for "once" schedule type
        if self.schedule_type == "once":
            target_time = self.schedule_config["datetime"]
            now = datetime.now()

            if target_time > now:
                # Sleep until target time
                sleep_seconds = (target_time - now).total_seconds()
                logger.info(f"Scheduled to run once in {sleep_seconds:.1f} seconds")

                # Wait for scheduled time or until stopped
                time_elapsed = 0
                while self.running and time_elapsed < sleep_seconds:
                    time.sleep(min(1, sleep_seconds - time_elapsed))
                    time_elapsed += 1

                if self.running:
                    self.last_run = datetime.now()
                    try:
                        logger.info("Running scheduled sync")
                        callback(*args, **kwargs)
                    except Exception as e:
                        logger.error(f"Error in scheduled sync: {str(e)}")
            else:
                logger.warning("One-time schedule is in the past, not running")

            self.running = False
            return

        # Recurring schedule (interval or cron)
        while self.running:
            # Calculate next run time
            next_run = self._calculate_next_run()
            now = datetime.now()

            if next_run > now:
                # Sleep until next run time
                sleep_seconds = (next_run - now).total_seconds()
                logger.info(f"Next sync scheduled in {sleep_seconds:.1f} seconds")

                # Wait for next run time or until stopped
                time_elapsed = 0
                while self.running and time_elapsed < sleep_seconds:
                    time.sleep(min(1, sleep_seconds - time_elapsed))
                    time_elapsed += 1

            # Run the callback if still running
            if self.running:
                self.last_run = datetime.now()
                try:
                    logger.info("Running scheduled sync")
                    callback(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error in scheduled sync: {str(e)}")

    def start(self, callback: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        """
        Start the scheduler with the provided callback function.

        Args:
            callback: Function to call on schedule
            *args, **kwargs: Arguments to pass to the callback
        """
        if not self.schedule_type:
            raise ValueError("Schedule not configured")

        if self.running:
            logger.warning("Scheduler is already running")
            return

        # Set running flag before starting thread
        self.running = True

        # Start the scheduler in a separate thread
        self.thread = threading.Thread(
            target=self._scheduler_loop,
            args=(callback,) + args,
            kwargs=kwargs,
            daemon=True,
        )
        self.thread.start()
        logger.info("Scheduler started")

    def stop(self) -> None:
        """Stop the scheduler."""
        if not self.running:
            logger.warning("Scheduler is not running")
            return

        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
            self.thread = None

        logger.info("Scheduler stopped")
