from __future__ import annotations

import time
from typing import Mapping, Optional, Sequence

PORT = 8002
HOST = "127.0.0.1"


if __name__ == "__main__":
    from flask import Flask

    app = Flask(__name__)

    @app.route("/")
    def home():
        return "hello"

    app.run(port=PORT, host=HOST)


class FlaskOtelTest:
    def environment_variables(self) -> Mapping[str, str]:
        return {}

    def requirements(self) -> Sequence[str]:
        return (
            "flask",
            "opentelemetry-distro",
            "opentelemetry-exporter-otlp-proto-grpc",
            "opentelemetry-instrumentation-flask",
        )

    def wrapper_command(self) -> str:
        return "opentelemetry-instrument"

    def on_start(self) -> Optional[float]:
        import http.client

        # TODO: replace this sleep with a liveness check!
        time.sleep(10)

        conn = http.client.HTTPConnection(HOST, PORT)
        conn.request("GET", "/")
        print("response:", conn.getresponse().read().decode())
        conn.close()

        # The return value of on_script_start() tells oteltest the number of seconds to wait for the script to complete.
        # In this case, we indicate 30 (seconds), which, once elapsed, will cause the script to be terminated, if it's
        # still running. If we return `None` then the script will run indefinitely.
        return 30

    def on_stop(self, telemetry, stdout: str, stderr: str, returncode: int) -> None:
        from oteltest.telemetry import count_spans

        assert count_spans(telemetry)

    def is_http(self) -> bool:
        return False
