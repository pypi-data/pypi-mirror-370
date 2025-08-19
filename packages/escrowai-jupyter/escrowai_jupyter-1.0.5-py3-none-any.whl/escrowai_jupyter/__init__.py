from ._version import __version__
from .handlers import setup_handlers
import os
import sys


def _jupyter_server_extension_paths():
    """Deprecated: Use _jupyter_server_extension_points instead."""
    return [{"module": "escrowai_jupyter"}]


def _jupyter_server_extension_points():
    """Modern extension points for Jupyter Server."""
    return [{"module": "escrowai_jupyter"}]


def _jupyter_labextension_paths():
    return [{"src": "labextension", "dest": "escrowai-jupyter"}]


def _jupyter_nbextension_paths():
    return [
        {
            "section": "notebook",
            "src": "static",
            "dest": "escrowai-jupyter",
            "require": "escrowai-jupyter/extension",
        }
    ]


def jupyter_serverproxy_servers():
    """
    Return a dict of server configurations for jupyter-server-proxy.
    This is used by jupyter-server-proxy to start the service.
    """
    return {
        "escrowai-jupyter": {
            "command": [sys.executable, "-m", "escrowai_jupyter.main"],
            "environment": {},
            "launcher_entry": {
                "title": "EscrowAI Jupyter",
                "icon_path": os.path.join(
                    os.path.dirname(__file__), "icons", "escrowai.svg"
                ),
            },
        }
    }


def load_jupyter_server_extension(serverapp):
    if serverapp is None:
        # Called during validation - just return success
        return
    try:
        setup_handlers(serverapp.web_app)
        serverapp.log.info("EscrowAI Jupyter loaded.")
    except Exception as e:
        if hasattr(serverapp, "log"):
            serverapp.log.error(f"Failed to load EscrowAI Jupyter: {e}")
        else:
            print(f"Failed to load EscrowAI Jupyter: {e}")
