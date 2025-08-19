import asyncio
import logging
import os
import signal
import time
import yaml
import sys
import json
import random
import string
from cryptography.fernet import Fernet
from pathlib import Path
from setproctitle import setproctitle
from typing import Optional, Dict, Tuple, Callable, Awaitable, Mapping
from .exceptions import (
    CheckException,
    IgnoreResultException,
    IgnoreCheckException,
    IncompleteResultException,
    NoCountException,
)
from . import logger
from .net.package import Package
from .protocol import AgentcoreProtocol
from .asset import Asset
from .config import encrypt, decrypt, get_config
from .response import UploadFile, FileType

HEADER_FILE = """
# WARNING: InfraSonar will make `password` and `secret` values unreadable but
# this must not be regarded as true encryption as the encryption key is
# publicly available.
#
# Example configuration for `myprobe` collector:
#
#  myprobe:
#    config:
#      username: alice
#      password: "secret password"
#    assets:
#    - id: 12345
#      config:
#        username: bob
#        password: "my secret"
""".lstrip()

AGENTCORE_HOST = os.getenv('AGENTCORE_HOST', '127.0.0.1')
AGENTCORE_PORT = int(os.getenv('AGENTCORE_PORT', 8750))
INFRASONAR_CONF_FN = \
    os.getenv('INFRASONAR_CONF', '/data/config/infrasonar.yaml')
MAX_CHECK_TIMEOUT = float(os.getenv('MAX_CHECK_TIMEOUT', 300))
DRY_RUN = os.getenv('DRY_RUN', '')
OUTPUT_TYPE = os.getenv('OUTPUT_TYPE', 'JSON').upper()

# Index in path
ASSET_ID, CHECK_ID = range(2)

# Index in names
ASSET_NAME_IDX, CHECK_NAME_IDX = range(2)

# This is the InfraSonar encryption key used for local configuration files.
# Note that this is not intended as a real security measure but prevents users
# from reading a passwords directly from open configuration files.
FERNET = Fernet(bytes(os.getenv(
    'ENCRYPTION_KEY',
    '4DFfx9LZBPvwvCpwmsVGT_HzjgiGUHduP1kq_L2Fbjw='), encoding='utf-8'))

MAX_PACKAGE_SIZE = int(os.getenv('MAX_PACKAGE_SIZE', 500))
if 1 > MAX_PACKAGE_SIZE > 2000:
    sys.exit('Value for MAX_PACKAGE_SIZE must be between 1 and 2000')

MAX_PACKAGE_SIZE *= 1000

EDR = """
asset:
  name: "foo.local"
  check: "wmi"
  config:
    address: "192.168.1.2"
"""

dry_run = None

if DRY_RUN:
    with open(DRY_RUN, "r") as fp:
        dry_run = yaml.safe_load(fp)
    if not isinstance(dry_run, dict):
        sys.exit(f'Invalid yaml file {DRY_RUN}; example: {EDR}')
    assert OUTPUT_TYPE in ('JSON', 'PPRINT'), \
        f'Invalid output type `{OUTPUT_TYPE}`; Must be JSON or PPRINT'


class Probe:
    """This class should only be initialized once."""

    def __init__(
        self,
        name: str,
        version: str,
        checks: Mapping[str, Callable[[Asset, dict, dict], Awaitable[dict]]],
        config_path: str = INFRASONAR_CONF_FN
    ):
        """Initialize a Infrasonar probe.

        Args:
            name: (str):
                Probe name
            version: (str):
                Probe version
            checks (dictionary):
                Dictionary of awaitable functions indexed by its (check) name
            config_path (str):
                Location of the configuration file. Defaults to
                `/data/config/infrasonar.yaml`.
        """
        setproctitle(name)
        logger.setup_logger()
        start_msg = 'starting' if dry_run is None else 'dry-run'
        logging.warning(f'{start_msg} probe collector: {name} v{version}')
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.name: str = name
        self.version: str = version
        self._checks_funs: Mapping[
            str,
            Callable[[Asset, dict, dict], Awaitable[dict]]] = checks
        self._config_path: Path = Path(config_path)
        self._connecting: bool = False
        self._protocol: Optional[AgentcoreProtocol] = None
        self._retry_next: int = 0
        self._retry_step: int = 1
        self._local_config: Optional[dict] = None
        self._local_config_mtime: Optional[float] = None
        self._checks_config: Dict[
            Tuple[int, int],
            Tuple[Tuple[str, str], dict]] = {}
        self._checks: Dict[Tuple[int, int], asyncio.Future] = {}
        self._dry_run: Optional[Tuple[Asset, dict]] = \
            None if dry_run is None else self._load_dry_run_assst(dry_run)
        self._on_close: Callable[[], Awaitable[None]] | None = None

        if not os.path.exists(config_path):
            try:
                parent = os.path.dirname(config_path)
                if not os.path.exists(parent):
                    os.mkdir(parent)
                with open(self._config_path, 'w') as fp:
                    fp.write(HEADER_FILE)
            except Exception:
                logging.exception(f"cannot write file: {config_path}")
                exit(1)
            logging.warning(f"created a new configuration file: {config_path}")
        try:
            self._read_local_config()
        except Exception:
            logging.exception(f"configuration file invalid: {config_path}")
            exit(1)

    def _load_dry_run_assst(self, dry_run: dict) -> Tuple[Asset, dict]:
        asset = dry_run.get('asset')

        if not isinstance(asset, dict):
            logging.error(
                f'Missing or invalid `asset` in {DRY_RUN}; example: {EDR}')
            exit(1)

        asset_name = asset.get('name')
        if not isinstance(asset_name, str):
            logging.error(
                f'Missing or invalid `name` in {DRY_RUN}; example: {EDR}')
            exit(1)

        asset_id = asset.get('id', 0)
        if not isinstance(asset_id, int):
            logging.error(
                f'Invalid optional `id` in {DRY_RUN}; '
                'Asset id must be type int')
            exit(1)

        check_key = asset.get('check')
        if not isinstance(check_key, str):
            logging.error(
                f'Missing or invalid `check` in {DRY_RUN}; example: {EDR}')
            exit(1)

        if check_key not in self._checks_funs:
            available = ', '.join(self._checks_funs.keys())
            logging.error(
                f'Unknown check `{check_key}` in {DRY_RUN}; '
                f'Available checks: {available}')
            exit(1)

        config = asset.get('config', {}) or {}
        if not isinstance(config, dict):
            logging.error(
                f'Invalid `config` in {DRY_RUN}; example: {EDR}')
            exit(1)

        return Asset(asset_id, asset_name, check_key), config

    def is_connected(self) -> bool:
        return self._protocol is not None and self._protocol.is_connected()

    def is_connecting(self) -> bool:
        return self._connecting

    def set_on_close(self, on_close: Callable[[], Awaitable[None]]):
        self._on_close = on_close

    def _stop(self, signame, *args):
        logging.warning(
            f'signal \'{signame}\' received, stop {self.name} probe')
        if self._on_close is not None and self.loop is not None:
            self.loop.run_until_complete(self._on_close())
        else:
            for task in asyncio.all_tasks():
                task.cancel()

    async def _start(self):
        initial_step = 2
        step = 2
        max_step = 2 ** 7

        while True:
            if not self.is_connected() and not self.is_connecting():
                asyncio.ensure_future(self._connect(), loop=self.loop)
                step = min(step * 2, max_step)
            else:
                step = initial_step
            for _ in range(step):
                await asyncio.sleep(1)

    def start(self, loop: Optional[asyncio.AbstractEventLoop] = None):
        """Start a Infrasonar probe

        Args:
            loop (AbstractEventLoop, optional):
                Can be used to run the client on a specific event loop.
                If this argument is not used, a new event loop will be
                created. Defaults to `None`.
        """
        signal.signal(signal.SIGINT, self._stop)
        signal.signal(signal.SIGTERM, self._stop)

        self.loop = loop if loop else asyncio.new_event_loop()
        if self._dry_run is None:
            try:
                self.loop.run_until_complete(self._start())
            except asyncio.exceptions.CancelledError:
                self.loop.run_until_complete(self.loop.shutdown_asyncgens())
                self.loop.close()
        else:
            self.loop.run_until_complete(self._do_dry_run())

    async def _do_dry_run(self):
        assert self._dry_run is not None
        asset, config = self._dry_run
        timeout = MAX_CHECK_TIMEOUT
        asset_config = self._asset_config(asset.id, config.get('_use'))
        fun = self._checks_funs[asset.check]
        ts = time.time()

        logging.debug(f'run check (dry-run); {asset}')
        success, failed, no_count = None, None, False

        try:
            try:
                res = await asyncio.wait_for(
                    fun(asset, asset_config, config), timeout=timeout)
                if not isinstance(res, dict):
                    raise TypeError(
                        'expecting type `dict` as check result '
                        f'but got type `{type(res).__name__}`')
            except asyncio.TimeoutError:
                raise CheckException('timed out')
            except asyncio.CancelledError:
                raise CheckException('cancelled')
            except (IgnoreCheckException,
                    IgnoreResultException,
                    CheckException):
                raise
            except Exception as e:
                # fall-back to exception class name
                if 'alpha' in self.version:
                    logger.exception(
                        'NOTE: exception is visible because this is an '
                        'alpha version and debug logging is enabled')
                error_msg = str(e) or type(e).__name__
                raise CheckException(error_msg)

        except IgnoreResultException:
            logging.info(f'ignore result; {asset}')

        except IgnoreCheckException:
            # log as warning; the user is able to prevent this warning by
            # disabling the check if not relevant for the asset;
            logging.warning(f'ignore check; {asset}')

        except IncompleteResultException as e:
            logging.warning(
                'incomplete result; '
                f'{asset} error: `{e}` severity: {e.severity}')
            success, failed = e.result, e.to_dict()

        except NoCountException as e:
            no_count = True
            if not e.is_exception:
                logging.debug(f'run check ok ({e}); {asset}')
                success, failed = e.result, None
            else:
                logging.warning(
                    'incomplete no count result; '
                    f'{asset} error: `{e}` severity: {e.severity}')
                success, failed = e.result, e.to_dict()

        except CheckException as e:
            logging.error(
                'check error; '
                f'{asset} error: `{e}` severity: {e.severity}')
            success, failed = None, e.to_dict()
        else:
            logging.debug(f'run check ok; {asset}')
            success, failed = res, None

        framework = {
            'duration': time.time() - ts,
            'timestamp': int(ts),
        }
        if no_count:
            framework['no_count'] = True

        response = {
            'result': success,
            'error': failed,
            'framework': framework
        }

        print('-'*80, file=sys.stderr)
        if OUTPUT_TYPE == 'PPRINT':
            import pprint
            pprint.pprint(response, indent=2)
        else:
            output = json.dumps(response, indent=2)
            print(output)
        print('', file=sys.stderr)
        if self._on_close is not None:
            await self._on_close()

    async def _connect(self):
        assert self.loop is not None
        conn = self.loop.create_connection(
            lambda: AgentcoreProtocol(
                self._on_set_assets,
                self._on_unset_assets,
                self._on_upsert_asset,
            ),
            host=AGENTCORE_HOST,
            port=AGENTCORE_PORT
        )
        self._connecting = True

        try:
            _, self._protocol = await asyncio.wait_for(conn, timeout=10)
        except Exception as e:
            error_msg = str(e) or type(e).__name__
            logging.error(f'connecting to agentcore failed: {error_msg}')
        else:
            pkg = Package.make(
                AgentcoreProtocol.PROTO_REQ_ANNOUNCE,
                data=[self.name, self.version]
            )
            if self._protocol and self._protocol.transport:
                try:
                    await self._protocol.request(pkg, timeout=10)
                except Exception as e:
                    logging.error(e)
        finally:
            self._connecting = False

    def send(
            self,
            path: tuple,
            result: Optional[dict],
            error: Optional[dict],
            ts: float,
            no_count: bool = False):
        asset_id, _ = path
        framework = {
            'duration': time.time() - ts,
            'timestamp': int(ts),
        }
        if no_count:
            framework['no_count'] = True

        check_data = {
            'result': result,
            'error': error,
            'framework': framework
        }
        pkg = Package.make(
            AgentcoreProtocol.PROTO_FAF_DUMP,
            partid=asset_id,
            data=[path, check_data]
        )

        data = pkg.to_bytes()
        if len(data) > MAX_PACKAGE_SIZE:
            e = CheckException(f'data package too large ({len(data)} bytes)')
            logging.error(f'check error; asset_id `{asset_id}`; {str(e)}')
            self.send(path, None, e.to_dict(), ts)
        elif self._protocol and self._protocol.transport:
            self._protocol.transport.write(data)

    def close(self):
        if self._protocol and self._protocol.transport:
            self._protocol.transport.close()
        self._protocol = None

    async def upload_file(self, name: str, blob: bytes,
                          timeout: int = 10) -> UploadFile:
        pkg = Package.make(
            AgentcoreProtocol.PROTO_REQ_UPLOAD_FILE,
            data={"name": name, "blob": blob}
        )
        if not self._protocol:
            raise ConnectionError('no connection')

        resp = await self._protocol.request(pkg, timeout=timeout)
        return UploadFile(
            id=resp['id'],
            size=resp['size'],
            name=resp['name'],
            type=FileType.get(resp['type']),
            created=resp['created']
        )

    async def download_file(self, file_id: int, timeout: int = 10) -> bytes:
        pkg = Package.make(
            AgentcoreProtocol.PROTO_REQ_DOWNLOAD_FILE,
            data={"id": file_id}
        )
        if not self._protocol:
            raise ConnectionError('no connection')

        resp = await self._protocol.request(pkg, timeout=timeout)
        return resp

    def _read_local_config(self):
        mtime = self._config_path.stat().st_mtime
        if mtime == self._local_config_mtime:
            return

        with open(self._config_path, 'r') as fp:
            config = yaml.safe_load(fp)

        if config:
            # First encrypt everything
            changed = encrypt(config, FERNET)

            # Re-write the file
            if changed:
                try:
                    tmp_file = self.tmp_file(str(self._config_path))
                    with open(tmp_file, 'w') as fp:
                        fp.write(HEADER_FILE)
                        fp.write(yaml.dump(config))
                    os.unlink(self._config_path)
                    os.rename(tmp_file, self._config_path)
                except Exception:
                    # This can happen when for example a read-only ConfigMap
                    # is used in Kubernetes. In this case we do not want to
                    # crash when we cannot write the file to disk.
                    logging.warning(f"failed to write `{self._config_path}`")
                else:
                    mtime = self._config_path.stat().st_mtime

            # Now decrypt everything so we can use the configuration
            decrypt(config, FERNET)
        else:
            config = {}

        for probe in config.values():
            if 'use' in probe:
                for section in ('assets', 'config'):
                    if section in probe:
                        logging.warning(
                            f'both `{section}` and `use` in probe section')

        self._local_config_mtime = mtime
        self._local_config = config

    def _asset_config(self, asset_id: int, use: Optional[str]) -> dict:
        try:
            self._read_local_config()
        except Exception:
            logging.warning('new config file invalid, keep using previous')

        assert self._local_config is not None
        return get_config(self._local_config, self.name, asset_id, use)

    def _on_unset_assets(self, asset_ids: list):
        asset_ids_set = set(asset_ids)
        new_checks_config = {
            path: config
            for path, config in self._checks_config.items()
            if path[ASSET_ID] not in asset_ids_set}
        self._set_new_checks_config(new_checks_config)

    def _on_upsert_asset(self, asset: list):
        asset_id, checks = asset
        new_checks_config = {
            path: config
            for path, config in self._checks_config.items()
            if path[ASSET_ID] != asset_id}
        new = {
            tuple(path): (names, config)
            for path, names, config in checks
            if names[CHECK_NAME_IDX] in self._checks_funs}
        new_checks_config.update(new)
        self._set_new_checks_config(new_checks_config)

    def _on_set_assets(self, assets: list):
        new_checks_config = {
            tuple(path): (names, config)
            for path, names, config in assets
            if names[CHECK_NAME_IDX] in self._checks_funs}
        self._set_new_checks_config(new_checks_config)

    def _set_new_checks_config(self, new_checks_config: dict):
        desired_checks = set(new_checks_config)

        for path in set(self._checks):
            if path not in desired_checks:
                # the check is no longer required, pop and cancel the task
                self._checks.pop(path).cancel()
            elif new_checks_config[path] != self._checks_config[path] and \
                    self._checks[path].cancelled():
                # this task is desired but has previously been cancelled;
                # now the config has been changed so we want to re-scheduled.
                del self._checks[path]

        # overwite check_config
        self._checks_config = new_checks_config

        # start new checks
        for path in desired_checks - set(self._checks):
            self._checks[path] = asyncio.ensure_future(
                self._run_check_loop(path)
            )

    @staticmethod
    def _next_ts(asset_id: int, check_id: int, interval: int,
                 ts: float) -> float:
        """Return a timestamp for the next run for a check on the given asset.
        It calculates a value between the range 0..interval based on both the
        asset and check and adds a value between 0..1 based on just the asset.
        """
        w = ((asset_id + check_id) % interval) - (ts % interval)
        return \
            ts + (w if w >= 0 else (w + interval)) + (asset_id % 32 * 0.03125)

    async def _run_check_loop(self, path: tuple):
        asset_id, check_id = path
        (asset_name, check_key), config = self._checks_config[path]
        interval = config.get('_interval')
        fun = self._checks_funs[check_key]
        asset = Asset(asset_id, asset_name, check_key)

        my_task = self._checks[path]
        assert isinstance(interval, int) and interval > 0

        while True:
            ts = self._next_ts(asset_id, check_id, interval, time.time())

            try:
                while True:
                    wait = ts - time.time()
                    if wait < 0.0:
                        # very small negative values are possible when the
                        # previous wait was very close to 10.0 seconds.
                        # We only need to log if the time difference is
                        # serious off schedule.
                        if wait < -4.0:
                            logging.error(
                                'scheduled timestamp in the past; '
                                'maybe the computer clock has been changed '
                                'or the event loop had a blocking task; '
                                f'(off by {wait:.1f} seconds)')
                        break

                    w = min(wait, 10.0)
                    await asyncio.sleep(w)

                    (asset_name, _), config = self._checks_config[path]
                    i: int = config.get('_interval')  # type: ignore

                    if w == wait:
                        break

                    if i != interval:
                        # calculate new interval; this is helpful when we
                        # change from a large interval to a short interval;
                        ts = self._next_ts(asset_id, check_id, i, time.time())
                        interval = i

            except asyncio.CancelledError:
                logging.info(f'cancelled; {asset}')
                break

            timeout = min(0.8 * interval, MAX_CHECK_TIMEOUT)

            if asset.name != asset_name:
                # asset_id and check_key are truly immutable, name is not
                asset = Asset(asset_id, asset_name, check_key)

            asset_config = self._asset_config(asset.id, config.get('_use'))

            logging.debug(f'run check; {asset}')

            try:
                try:
                    res = await asyncio.wait_for(
                        fun(asset, asset_config, config), timeout=timeout)
                    if not isinstance(res, dict):
                        raise TypeError(
                            'expecting type `dict` as check result '
                            f'but got type `{type(res).__name__}`')
                except asyncio.TimeoutError:
                    raise CheckException('timed out')
                except asyncio.CancelledError:
                    if my_task is self._checks.get(path):
                        # cancelled from within, just raise
                        raise CheckException('cancelled')
                    logging.warning(f'cancelled; {asset}')
                    break
                except (IgnoreCheckException,
                        IgnoreResultException,
                        CheckException):
                    raise
                except Exception as e:
                    # fall-back to exception class name
                    if 'alpha' in self.version:
                        logger.exception(
                            'NOTE: exception is visible because this is an '
                            'alpha version and debug logging is enabled')
                    error_msg = str(e) or type(e).__name__
                    raise CheckException(error_msg)

            except IgnoreResultException:
                logging.info(f'ignore result; {asset}')

            except IgnoreCheckException:
                # log as warning; the user is able to prevent this warning by
                # disabling the check if not relevant for the asset;
                logging.warning(f'ignore check; {asset}')
                break

            except IncompleteResultException as e:
                logging.warning(
                    'incomplete result; '
                    f'{asset} error: `{e}` severity: {e.severity}')
                self.send(path, e.result, e.to_dict(), ts)

            except NoCountException as e:
                if not e.is_exception:
                    logging.debug(f'run check ok ({e}); {asset}')
                    self.send(path, e.result, None, ts, no_count=True)
                else:
                    logging.warning(
                        'incomplete result (no count); '
                        f'{asset} error: `{e}` severity: {e.severity}')
                    self.send(path, e.result, e.to_dict(), ts, no_count=True)

            except CheckException as e:
                logging.error(
                    'check error; '
                    f'{asset} error: `{e}` severity: {e.severity}')
                self.send(path, None, e.to_dict(), ts)

            else:
                logging.debug(f'run check ok; {asset}')
                self.send(path, res, None, ts)

    @staticmethod
    def tmp_file(filename: str) -> str:
        letters = string.ascii_lowercase
        tmp = ''.join(random.choice(letters) for i in range(10))
        return f'{filename}.{tmp}'
