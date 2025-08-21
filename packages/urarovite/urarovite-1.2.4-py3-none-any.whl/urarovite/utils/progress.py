"""Progress bar and visual feedback utilities for Urarovite operations.

This module provides comprehensive progress tracking and visual feedback for
command-line operations, including exponential backoff indicators, validation
progress, and operation status updates.
"""

import sys
import time
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field

try:
    from rich.console import Console
    from rich.progress import (
        Progress,
        TaskID,
        BarColumn,
        TextColumn,
        TimeElapsedColumn,
        TimeRemainingColumn,
        SpinnerColumn,
        MofNCompleteColumn,
    )
    from rich.panel import Panel
    from rich.text import Text
    from rich.live import Live
    from rich.table import Table
    from rich.align import Align

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None
    Progress = None
    TaskID = None


@dataclass
class ProgressConfig:
    """Configuration for progress display."""

    show_progress: bool = True
    show_backoff: bool = True
    show_details: bool = False
    console_width: Optional[int] = None
    disable_in_jupyter: bool = True

    def __post_init__(self):
        """Auto-detect environment and adjust settings."""
        if self.disable_in_jupyter and self._is_jupyter():
            self.show_progress = False

        # Disable if not in a terminal
        if not sys.stdout.isatty():
            self.show_progress = False

    def _is_jupyter(self) -> bool:
        """Check if running in Jupyter notebook."""
        try:
            from IPython import get_ipython

            return get_ipython() is not None
        except ImportError:
            return False


@dataclass
class BackoffStatus:
    """Status tracking for exponential backoff operations."""

    operation: str = ""
    attempt: int = 0
    max_attempts: int = 0
    delay: float = 0.0
    error_type: str = ""
    is_retrying: bool = False
    total_elapsed: float = 0.0
    start_time: float = field(default_factory=time.time)


class ProgressManager:
    """Centralized progress management for Urarovite operations."""

    def __init__(self, config: Optional[ProgressConfig] = None):
        """Initialize progress manager.

        Args:
            config: Progress configuration (uses default if None)
        """
        self.config = config or ProgressConfig()
        self.console = (
            Console() if RICH_AVAILABLE and self.config.show_progress else None
        )
        self._active_progress: Optional[Progress] = None
        self._backoff_status: Dict[str, BackoffStatus] = {}

    def is_enabled(self) -> bool:
        """Check if progress display is enabled."""
        return RICH_AVAILABLE and self.config.show_progress and self.console is not None

    @contextmanager
    def operation(self, description: str, total: Optional[int] = None):
        """Context manager for tracking a long-running operation.

        Args:
            description: Description of the operation
            total: Total number of steps (None for indeterminate progress)

        Example:
            >>> with progress_manager.operation(
            ...     "Validating spreadsheet", total=5
            ... ) as progress:
            ...     for i in range(5):
            ...         progress.update(1, description=f"Step {i + 1}")
        """
        if not self.is_enabled():
            yield _DummyProgress()
            return

        columns = [
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn() if total else TextColumn(""),
            MofNCompleteColumn() if total else TextColumn(""),
            TimeElapsedColumn(),
        ]

        if total:
            columns.append(TimeRemainingColumn())

        progress = Progress(*columns, console=self.console)

        try:
            self._active_progress = progress
            with progress:
                task_id = progress.add_task(description, total=total)
                yield _ProgressTracker(progress, task_id)
        finally:
            self._active_progress = None

    def show_backoff_status(self, operation_id: str, status: BackoffStatus):
        """Display exponential backoff status.

        Args:
            operation_id: Unique identifier for the operation
            status: Current backoff status
        """
        if not self.is_enabled() or not self.config.show_backoff:
            return

        self._backoff_status[operation_id] = status

        if status.is_retrying:
            self._display_backoff_retry(status)
        else:
            # Clear the status when done
            self._backoff_status.pop(operation_id, None)

    def _display_backoff_retry(self, status: BackoffStatus):
        """Display retry status for exponential backoff."""
        if not self.console:
            return

        # Create a retry indicator panel
        retry_text = Text()
        retry_text.append("🔄 ", style="yellow")
        retry_text.append(f"Retrying {status.operation}", style="bold yellow")
        retry_text.append(f" (attempt {status.attempt}/{status.max_attempts})")

        if status.error_type:
            retry_text.append(f"\n   Error: {status.error_type}", style="red")

        if status.delay > 0:
            retry_text.append(
                f"\n   Waiting {status.delay:.1f}s before retry...", style="dim"
            )

        panel = Panel(
            retry_text,
            title="[yellow]Exponential Backoff[/yellow]",
            border_style="yellow",
            padding=(0, 1),
        )

        # If we have an active progress, print above it
        # Otherwise, print directly
        if self._active_progress:
            self.console.print()  # Add some space
            self.console.print(panel)
        else:
            self.console.print(panel)

    def show_validation_summary(self, results: Dict[str, Any]):
        """Display validation results summary.

        Args:
            results: Validation results dictionary
        """
        if not self.is_enabled():
            return

        table = Table(
            title="Validation Results Summary",
            show_header=True,
            header_style="bold magenta",
        )
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")

        # Add key metrics
        if "fixes_applied" in results:
            table.add_row("Fixes Applied", str(results["fixes_applied"]))

        if "flags_found" in results:
            table.add_row("flags Found", str(results["flags_found"]))

        if "errors" in results and results["errors"]:
            table.add_row("Errors", str(len(results["errors"])))

        if "duplicate_created" in results and results["duplicate_created"]:
            table.add_row("Duplicate Created", "✓")

        if "automated_log" in results:
            table.add_row("Status", results["automated_log"])

        self.console.print()
        self.console.print(table)
        self.console.print()

    def show_error(self, error: str, details: Optional[str] = None):
        """Display error message with rich formatting.

        Args:
            error: Main error message
            details: Optional additional details
        """
        if not self.is_enabled():
            # Fallback to plain text
            print(f"ERROR: {error}")
            if details:
                print(f"Details: {details}")
            return

        error_text = Text()
        error_text.append("❌ ", style="red")
        error_text.append("Error: ", style="bold red")
        error_text.append(error)

        if details:
            error_text.append(f"\n   {details}", style="dim")

        panel = Panel(
            error_text, title="[red]Error[/red]", border_style="red", padding=(0, 1)
        )

        self.console.print()
        self.console.print(panel)
        self.console.print()

    def show_success(self, message: str, details: Optional[str] = None):
        """Display success message with rich formatting.

        Args:
            message: Success message
            details: Optional additional details
        """
        if not self.is_enabled():
            # Fallback to plain text
            print(f"SUCCESS: {message}")
            if details:
                print(f"Details: {details}")
            return

        success_text = Text()
        success_text.append("✅ ", style="green")
        success_text.append("Success: ", style="bold green")
        success_text.append(message)

        if details:
            success_text.append(f"\n   {details}", style="dim")

        panel = Panel(
            success_text,
            title="[green]Success[/green]",
            border_style="green",
            padding=(0, 1),
        )

        self.console.print()
        self.console.print(panel)
        self.console.print()


class _ProgressTracker:
    """Internal progress tracker for operations."""

    def __init__(self, progress: Progress, task_id: TaskID):
        self.progress = progress
        self.task_id = task_id

    def update(self, advance: int = 1, description: Optional[str] = None):
        """Update progress.

        Args:
            advance: Number of steps to advance
            description: Optional new description
        """
        if description:
            self.progress.update(self.task_id, description=description, advance=advance)
        else:
            self.progress.update(self.task_id, advance=advance)

    def set_description(self, description: str):
        """Set new description for the progress bar.

        Args:
            description: New description
        """
        self.progress.update(self.task_id, description=description)

    def complete(self):
        """Mark the operation as complete."""
        task = self.progress._tasks[self.task_id]
        if task.total:
            self.progress.update(self.task_id, completed=task.total)


class _DummyProgress:
    """Dummy progress tracker when rich is not available."""

    def update(self, advance: int = 1, description: Optional[str] = None):
        """Dummy update method."""
        pass

    def set_description(self, description: str):
        """Dummy set description method."""
        pass

    def complete(self):
        """Dummy complete method."""
        pass


# Global progress manager instance
_global_progress_manager: Optional[ProgressManager] = None


def get_progress_manager() -> ProgressManager:
    """Get the global progress manager instance.

    Returns:
        Global progress manager instance
    """
    global _global_progress_manager
    if _global_progress_manager is None:
        _global_progress_manager = ProgressManager()
    return _global_progress_manager


def configure_progress(config: ProgressConfig):
    """Configure the global progress manager.

    Args:
        config: Progress configuration
    """
    global _global_progress_manager
    _global_progress_manager = ProgressManager(config)


# Convenience functions for common operations
def show_operation_progress(description: str, total: Optional[int] = None):
    """Context manager for showing operation progress.

    Args:
        description: Description of the operation
        total: Total number of steps

    Returns:
        Progress context manager
    """
    return get_progress_manager().operation(description, total)


def show_backoff_status(operation_id: str, status: BackoffStatus):
    """Show exponential backoff status.

    Args:
        operation_id: Unique operation identifier
        status: Backoff status
    """
    get_progress_manager().show_backoff_status(operation_id, status)


def show_validation_summary(results: Dict[str, Any]):
    """Show validation results summary.

    Args:
        results: Validation results
    """
    get_progress_manager().show_validation_summary(results)


def show_error(error: str, details: Optional[str] = None):
    """Show error message.

    Args:
        error: Error message
        details: Optional details
    """
    get_progress_manager().show_error(error, details)


def show_success(message: str, details: Optional[str] = None):
    """Show success message.

    Args:
        message: Success message
        details: Optional details
    """
    get_progress_manager().show_success(message, details)
