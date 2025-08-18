from typing import TYPE_CHECKING
from pathlib import Path
from enum import Enum
from datetime import datetime, timedelta, UTC

from typer import Typer, Option, Argument, Exit, secho, colors, confirm

from rich import print as rprint
from rich.console import Console
from rich.progress import (Progress, SpinnerColumn, TextColumn, BarColumn,
                           TimeElapsedColumn, TimeRemainingColumn)

from ..app import app, app_state
from ...providers import available_providers
from ...providers.provider import Provider

from ...utils.rich.date_column import DateColumn
from pynecore.core.ohlcv_file import OHLCVReader, OHLCVWriter

__all__ = []

app_data = Typer(help="OHLCV related commands")
app.add_typer(app_data, name="data")

# Create an enum from it
AvailableProvidersEnum = Enum('Provider', {name.upper(): name.lower() for name in available_providers})

# Available intervals (The same fmt as described in timeframe.period)
TimeframeEnum = Enum('Timeframe', {name: name for name in ('1', '5', '15', '30', '60', '120', '240', '1D', '1W')})

# Trick to avoid type checking errors
DateOrDays = datetime if TYPE_CHECKING else str


def parse_date_or_days(value: str) -> datetime | str:
    """
    Parse a date or a number of days
    """
    if value == 'continue':
        return value
    if not value:
        return datetime.now(UTC).replace(second=0, microsecond=0)
    try:
        # Is it a date?
        return datetime.fromisoformat(str(value))
    except ValueError:
        try:
            # Not a date, maybe it's a number of days
            days = int(value)
            if days < 0:
                secho("Error: Days cannot be negative", err=True, fg=colors.RED)
                raise Exit(1)
            return (datetime.now(UTC) - timedelta(days=days)).replace(second=0, microsecond=0)
        except ValueError:
            secho(f"Error: Invalid date fmt or days number: {value}", err=True, fg=colors.RED)
            raise Exit(1)


@app_data.command()
def download(
        provider: AvailableProvidersEnum = Argument(..., case_sensitive=False, show_default=False,  # type: ignore
                                                    help="Data provider"),
        symbol: str | None = Option(None, '--symbol', '-s', show_default=False,
                                    help="Symbol (e.g. BYBIT:BTC/USDT:USDT)"),
        list_symbols: bool = Option(False, '--list-symbols', '-ls',
                                    help="List available symbols of the provider"),
        timeframe: TimeframeEnum = Option('1D', '--timeframe', '-tf', case_sensitive=False,  # type: ignore
                                          help="Timeframe in TradingView fmt"),
        time_from: DateOrDays = Option("continue", '--from', '-f',  # type: ignore
                                       callback=parse_date_or_days, formats=[],
                                       metavar="[%Y-%m-%d|%Y-%m-%d %H:%M:%S|NUMBER]|continue",
                                       help="Start date or days back from now, or 'continue' to resume last download,"
                                            " or one year if no data"),
        time_to: DateOrDays = Option(datetime.now(UTC).replace(second=0, microsecond=0), '--to', '-t',  # type: ignore
                                     callback=parse_date_or_days, formats=[],
                                     metavar="[%Y-%m-%d|%Y-%m-%d %H:%M:%S|NUMBER]",
                                     help="End date or days from start date"),
        show_info: bool = Option(False, '--symbol-info', '-si', help="Show symbol info"),
        force_save_info: bool = Option(False, '--force-save-info', '-fi', help="Force save symbol info"),
        truncate: bool = Option(False, '--truncate', '-tr',
                                help="Truncate file before downloading, all data will be lost"),
):
    """
    Download historical OHLCV data
    """
    # Import provider module from
    provider_module = __import__(f"pynecore.providers.{provider.value}", fromlist=[''])
    provider_class = getattr(provider_module, [p for p in dir(provider_module) if p.endswith('Provider')][0])

    try:
        # If list_symbols is True, we show the available symbols then exit
        if list_symbols:
            with Progress(SpinnerColumn(), TextColumn("{task.description}"), transient=True) as progress:
                progress.add_task(description="Fetching market data...", total=None)
                provider_instance: Provider = provider_class(symbol=symbol, config_dir=app_state.config_dir)
                symbols = provider_instance.get_list_of_symbols()
            with (console := Console()).pager():
                for s in symbols:
                    console.print(s)
            return

        if not symbol:
            secho("Error: Symbol is required!", err=True, fg=colors.RED)
            raise Exit(1)

        # Create provider instance
        provider_instance: Provider = provider_class(symbol=symbol, timeframe=timeframe.value,
                                                     ohlv_dir=app_state.data_dir)

        # Download symbol info if not exists
        if force_save_info or not provider_instance.is_symbol_info_exists():
            with Progress(SpinnerColumn(finished_text="[green]✓"), TextColumn("{task.description}")) as progress:
                # Get symbol info task
                task = progress.add_task(description="Fetching symbol info...", total=1)
                sym_info = provider_instance.get_symbol_info(force_update=force_save_info)

                # Complete task
                progress.update(task, completed=1)

                # Print symbol info
                if show_info:
                    rprint(sym_info)
        else:  # We have symbol info, just show it
            sym_info = provider_instance.get_symbol_info()
            if show_info:
                rprint(sym_info)

        # Open the OHLCV file and start downloading
        with provider_instance as ohlcv_writer:
            # Truncate file if overwrite is True
            if truncate:
                ohlcv_writer.seek(0)
                ohlcv_writer.truncate()

            # If the start date is "continue" (default), we resume from the last download
            if time_from == "continue":
                if ohlcv_writer.end_timestamp:  # Resume from last download
                    time_from = datetime.fromtimestamp(ohlcv_writer.end_timestamp, UTC)
                    # We need to add one interval to the start date to avoid downloading the same data
                    time_from += timedelta(seconds=ohlcv_writer.interval)
                else:  # No data, download one year as default
                    time_from = datetime.now(UTC) - timedelta(days=365)

            # We need to remove timezone info
            time_from = time_from.replace(tzinfo=None)
            time_to = time_to.replace(tzinfo=None)

            # We cannot download data from the future otherwise it would take very long
            if time_to > datetime.now(UTC).replace(tzinfo=None):
                time_to = datetime.now(UTC).replace(tzinfo=None)

            # Check time range
            if time_to < time_from:
                secho("Error: End date (to) must be greater than start date (from)!", err=True, fg=colors.RED)
                raise Exit(1)

            # If the start date is before the start of the existing file, we truncate the file
            if ohlcv_writer.start_timestamp:
                if time_from < ohlcv_writer.start_datetime.replace(tzinfo=None):
                    secho(f"The start date (from: {time_from}) is before the start of the "
                          f"existing file ({ohlcv_writer.start_datetime.replace(tzinfo=None)}).\n"
                          f"If you continue, the file will be truncated.",
                          fg=colors.YELLOW)
                    confirm("Do you want to continue?", abort=True)
                    # Truncate file
                    ohlcv_writer.seek(0)
                    ohlcv_writer.truncate()

            total_seconds = int((time_to - time_from).total_seconds())

            # Get OHLCV data
            with Progress(
                    SpinnerColumn(finished_text="[green]✓"),
                    TextColumn("{task.description}"),
                    DateColumn(time_from),
                    BarColumn(),
                    TimeElapsedColumn(),
                    "/",
                    TimeRemainingColumn(),
            ) as progress:
                task = progress.add_task(
                    description="Downloading OHLCV data...",
                    total=total_seconds,
                )

                def cb_progress(current_time: datetime):
                    """ Callback to update progress """
                    elapsed_seconds = int((current_time - time_from).total_seconds())
                    progress.update(task, completed=elapsed_seconds)

                # Start downloading
                provider_instance.download_ohlcv(time_from, time_to, on_progress=cb_progress)

    except (ImportError, ValueError) as e:
        secho(str(e), err=True, fg=colors.RED)
        raise Exit(2)


@app_data.command()
def convert_to(
        provider: AvailableProvidersEnum = Argument(..., case_sensitive=False, show_default=False,  # type: ignore
                                                    help="Data provider"),
        symbol: str | None = Option(None, '--symbol', '-s', show_default=False,
                                    help="Symbol (e.g. BYBIT:BTCUSDT:USDT)"),
        timeframe: TimeframeEnum = Option('1D', '--timeframe', '-tf', case_sensitive=False,  # type: ignore
                                          help="Timeframe in TradingView fmt"),
        fmt: Enum('Format', {'csv': 'csv', 'json': 'json'}) = Option(  # noqa # type: ignore
            'csv', '--format', '-f',
            case_sensitive=False,
            help="Output format"),
        as_datetime: bool = Option(False, '--as-datetime', '-dt',
                                   help="Save timestamp as datetime instead of UNIX timestamp"),
):
    """
    Convert downloaded data from pyne's OHLCV format to another format
    """
    # Import provider module from
    provider_module = __import__(f"pynecore.providers.{provider.value}", fromlist=[''])
    provider_class = getattr(provider_module, [p for p in dir(provider_module) if p.endswith('Provider')][0])
    ohlcv_path = provider_class.get_ohlcv_path(symbol, timeframe.value, app_state.data_dir)

    with Progress(SpinnerColumn(finished_text="[green]✓"), TextColumn("{task.description}")) as progress:
        # Convert
        with OHLCVReader(str(ohlcv_path)) as ohlcv_reader:
            if fmt.value == 'csv':
                task = progress.add_task(description="Converting to CSV...", total=1)
                ohlcv_reader.save_to_csv(str(ohlcv_path.with_suffix('.csv')), as_datetime=as_datetime)

            elif fmt.value == 'json':
                task = progress.add_task(description="Converting to JSON...", total=1)
                ohlcv_reader.save_to_json(str(ohlcv_path.with_suffix('.json')), as_datetime=as_datetime)

        # Complete task
        progress.update(task, completed=1)


@app_data.command()
def convert_from(
        file_path: Path = Argument(..., help="Path to CSV file to convert"),
        provider: str = Option("custom", '--provider', '-p',
                               help="Data provider, can be any name"),
        symbol: str | None = Option(None, '--symbol', '-s', show_default=False,
                                    help="Symbol (e.g. BYBIT:BTCUSDT:USDT)"),
        timeframe: TimeframeEnum = Option('1D', '--timeframe', '-tf', case_sensitive=False,  # type: ignore
                                          help="Timeframe in TradingView fmt"),
        fmt: Enum('Format', {'csv': 'csv', 'json': 'json'}) | None = Option(  # noqa # type: ignore
            None, '--fmt', '-f',
            case_sensitive=False,
            help="Output fmt"),
        tz: str = Option('UTC', '--timezone', '-tz',
                         help="Timezone"),
):
    """
    Convert data from other sources to pyne's OHLCV format
    """
    with Progress(SpinnerColumn(finished_text="[green]✓"), TextColumn("{task.description}")) as progress:
        ohlcv_path = Provider.get_ohlcv_path(symbol, timeframe.value, app_state.data_dir, provider)
        if fmt is None:
            fmt = file_path.suffix[1:]  # noqa
        else:
            fmt = fmt.value
        # Convert
        with OHLCVWriter(ohlcv_path) as ohlcv_writer:
            if fmt == 'csv':
                task = progress.add_task(description="Converting from CSV...", total=1)
                ohlcv_writer.load_from_csv(file_path, tz=tz)

            elif fmt == 'json':
                task = progress.add_task(description="Converting from JSON...", total=1)
                ohlcv_writer.load_from_json(file_path, tz=tz)
            else:
                secho(f"Error: Invalid format: {fmt}", err=True, fg=colors.RED)
                raise Exit(1)

            # Complete task
            progress.update(task, completed=1)
