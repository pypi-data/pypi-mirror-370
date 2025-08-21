"""
Tests for the Scheduler class.
"""

import time
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from apilinker.core.scheduler import Scheduler


class TestScheduler:
    """Test suite for Scheduler class."""

    def setup_method(self):
        """Set up test environment before each test."""
        self.scheduler = Scheduler()

    def test_add_interval_schedule(self):
        """Test adding an interval schedule."""
        # Add interval schedule
        self.scheduler.add_schedule(
            type="interval",
            minutes=5
        )
        
        # Verify scheduler configuration
        assert self.scheduler.schedule_type == "interval"
        assert self.scheduler.schedule_config["minutes"] == 5
        
        # Verify schedule info
        info = self.scheduler.get_schedule_info()
        assert "Every 5 minutes" in info

    def test_add_cron_schedule(self):
        """Test adding a cron schedule."""
        # Add cron schedule
        self.scheduler.add_schedule(
            type="cron",
            expression="0 */6 * * *"
        )
        
        # Verify scheduler configuration
        assert self.scheduler.schedule_type == "cron"
        assert self.scheduler.schedule_config["expression"] == "0 */6 * * *"
        
        # Verify schedule info
        info = self.scheduler.get_schedule_info()
        assert "Cron: 0 */6 * * *" in info

    def test_add_once_schedule(self):
        """Test adding a one-time schedule."""
        # Create future datetime
        future_time = datetime.now() + timedelta(hours=1)
        
        # Add one-time schedule
        self.scheduler.add_schedule(
            type="once",
            datetime=future_time
        )
        
        # Verify scheduler configuration
        assert self.scheduler.schedule_type == "once"
        assert self.scheduler.schedule_config["datetime"] == future_time
        
        # Verify schedule info
        info = self.scheduler.get_schedule_info()
        assert "Once at" in info

    def test_invalid_schedule_type(self):
        """Test adding an invalid schedule type."""
        # Try to add invalid schedule type
        with pytest.raises(ValueError, match="Unsupported schedule type"):
            self.scheduler.add_schedule(type="invalid")

    def test_invalid_interval_schedule(self):
        """Test adding an invalid interval schedule."""
        # Try to add interval schedule without time unit
        with pytest.raises(ValueError, match="Interval schedule must specify"):
            self.scheduler.add_schedule(type="interval")

    def test_invalid_cron_schedule(self):
        """Test adding an invalid cron schedule."""
        # Try to add cron schedule without expression
        with pytest.raises(ValueError, match="Cron schedule must specify"):
            self.scheduler.add_schedule(type="cron")
        
        # Try to add cron schedule with invalid expression
        with pytest.raises(ValueError, match="Invalid cron expression"):
            self.scheduler.add_schedule(type="cron", expression="invalid")

    def test_invalid_once_schedule(self):
        """Test adding an invalid one-time schedule."""
        # Try to add one-time schedule without datetime
        with pytest.raises(ValueError, match="One-time schedule must specify"):
            self.scheduler.add_schedule(type="once")

    @patch("threading.Thread")
    def test_start_without_schedule(self, mock_thread):
        """Test starting the scheduler without a schedule."""
        # Try to start scheduler without adding schedule
        with pytest.raises(ValueError, match="Schedule not configured"):
            self.scheduler.start(lambda: None)
        
        # Verify thread was not started
        mock_thread.assert_not_called()

    @patch("threading.Thread")
    def test_start_and_stop(self, mock_thread):
        """Test starting and stopping the scheduler."""
        # Set up a mock thread
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance
        
        # Add schedule
        self.scheduler.add_schedule(
            type="interval",
            seconds=1
        )
        
        # Start scheduler with callback
        callback_mock = MagicMock()
        self.scheduler.start(callback_mock)
        
        # Verify thread was started
        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()
        assert self.scheduler.running is True
        
        # Stop scheduler
        self.scheduler.stop()
        
        # Verify thread was joined
        mock_thread_instance.join.assert_called_once()
        assert self.scheduler.running is False

    @patch("time.sleep", side_effect=lambda x: None)  # Skip actual sleeping
    def test_scheduler_loop_interval(self, mock_sleep):
        """Test scheduler loop with interval schedule."""
        # Create a callback mock
        callback = MagicMock()
        
        # Configure scheduler for short interval
        self.scheduler.add_schedule(
            type="interval",
            seconds=1
        )
        
        # Start the scheduler loop directly (simulated)
        self.scheduler.running = True
        
        # Run loop for a short time (simulated)
        def stop_after_runs():
            # Let it run for 3 "cycles"
            if callback.call_count >= 3:
                self.scheduler.running = False
        
        callback.side_effect = stop_after_runs
        
        # Run the scheduler loop
        self.scheduler._scheduler_loop(callback)
        
        # Verify callback was called
        assert callback.call_count == 3

    def test_calculate_next_run(self):
        """Test calculating the next run time."""
        now = datetime.now()
        
        # Test interval schedule
        self.scheduler.add_schedule(
            type="interval",
            minutes=5
        )
        
        next_run = self.scheduler._calculate_next_run()
        expected_time = now + timedelta(minutes=5)
        
        # Allow for small differences in test execution time
        assert abs((next_run - expected_time).total_seconds()) < 5
        
        # Test with last_run set
        self.scheduler.last_run = now
        next_run = self.scheduler._calculate_next_run()
        expected_time = now + timedelta(minutes=5)
        
        assert abs((next_run - expected_time).total_seconds()) < 5
