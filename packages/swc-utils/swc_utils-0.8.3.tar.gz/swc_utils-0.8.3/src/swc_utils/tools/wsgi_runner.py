import sys
import time
import signal
import subprocess
import multiprocessing
from swc_utils.exceptions.package_exceptions import MissingDependencyError
from swc_utils.other.decorators import deprecated

try:
    from flask import Flask
except ImportError:
    raise MissingDependencyError("flask")


class KillSignalHandler:
    kill_received = False

    def __init__(self, exit_on_signal: bool = True):
        self._register_signal_handlers()
        self._extra_handlers = []
        self._exit_on_signal = exit_on_signal

    def add_handler(self, handler):
        """
        Add a custom signal handler to be called on SIGINT or SIGTERM.
        :param handler: A callable that takes no arguments.
        """
        self._extra_handlers.append(handler)

    def _register_signal_handlers(self):
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        self.kill_received = True
        print(f"Received signal {signum}. Shutting down gracefully...")

        for handler in self._extra_handlers:
            try:
                handler()
            except Exception as e:
                print(f"Error in signal handler: {e}")

        if self._exit_on_signal:
            exit(0)


class WsgiRunner:
    def __init__(self, host: str, port: int or str, debug: bool = False):
        """
        WSGI runner for Flask applications.
        :param host: Host address to bind the server to.
        :param port: Port number to bind the server to.
        :param debug: Whether to run the server in debug mode.
        """

        self.host = host
        self.port = int(port) if isinstance(port, str) else port
        self.debug = debug

    def _build_command(self, application_pointer: str, backend: str, extra_options: dict, port_offset: int = 0):
        command = [
            "gunicorn",
            "-b", f"{self.host}:{self.port + port_offset}",
            "-k", backend
        ]

        for key, value in extra_options.items():
            command.extend([f"--{key}", str(value)])

        command.append(application_pointer)
        return command

    def run_internal(self, application: Flask, *args, **kwargs):
        """
        Run the Flask application internally.
        :param application: Flask application instance.
        :param args: Extra arguments to pass to the run method.
        :param kwargs: Extra keyword arguments to pass to the run method.
        """
        application.run(host=self.host, port=self.port, debug=self.debug, *args, **kwargs)

    def run_gunicorn(
            self,
            application_pointer: str = "__init__:app",
            backend: str = "gevent",
            extra_options: dict = None,
            runner_count: int = 1
    ):
        """
        Run the Flask application using Gunicorn.
        :param application_pointer: The application module pointer to the Flask app. For example: "app:app" or "__init__:app".
        :param backend: The backend to use for Gunicorn. Default is "gevent".
        :param extra_options: Extra options to pass to Gunicorn. Default is `{limit-request-line: 0, limit-request-field_size: 0, timeout: 120}`.
        :param runner_count: Number of Gunicorn workers to spawn. Default is 1. The port will be incremented for each worker.
        :return:
        """

        try:
            import gunicorn

            if backend == "gevent":
                import gevent
        except ImportError:
            raise MissingDependencyError(["gunicorn", "gevent"], alt_source="web_production")

        if extra_options is None:
            extra_options = {
                "limit-request-line": 0,
                "limit-request-field_size": 0,
                "timeout": 120
            }

        signal_handler = KillSignalHandler(exit_on_signal=False)
        processes = list()

        def shutdown():
            for process in processes:
                print(f"Shutting down process {process.pid}...")
                process.send_signal(signal.SIGKILL)
                process.wait()

        def terminate():
            for process in processes:
                print(f"Terminating process {process.pid}...")
                process.terminate()
                process.wait()

        signal_handler.add_handler(shutdown)

        try:
            for i in range(runner_count):
                processes.append(
                    subprocess.Popen(self._build_command(application_pointer, backend, extra_options, i))
                )

            while True:
                time.sleep(1)
                if signal_handler.kill_received:
                    while any(p.poll() is None for p in processes):
                        time.sleep(1)
                    print("All processes shut down. Shutting down thread handler...")
                    break

        except Exception as e:
            print(f"Error while running Gunicorn: {e}")
            terminate()
            sys.exit(1)

        finally:
            sys.exit(0)

    @deprecated
    def run_threaded_gunicorn(
            self, threads: int,
            application_pointer: str = "__init__:app", backend: str = "gevent", extra_options: dict = None
    ):
        def thread_func():
            wsgi = self.__class__(self.host, self.port + i, self.debug)
            wsgi.run_gunicorn(application_pointer, backend, extra_options)

        for i in range(threads):
            thread = multiprocessing.Process(target=thread_func)
            thread.start()

    @deprecated
    def run_multiprocess_gunicorn(
            self, processes: int,
            application_pointer: str = "__init__:app", backend: str = "gevent", extra_options: dict = None
    ):
        processes = min(processes, multiprocessing.cpu_count())

        def process_func(wsgi_args, gunicorn_args):
            wsgi = self.__class__(*wsgi_args)
            wsgi.run_gunicorn(*gunicorn_args)

        for i in range(processes):
            process = multiprocessing.Process(target=process_func, args=(
                (self.host, self.port + i, self.debug),
                (application_pointer, backend, extra_options)
            ))
            process.start()
