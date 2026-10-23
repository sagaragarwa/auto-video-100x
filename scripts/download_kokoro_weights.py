import os
import sys

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_venv_site = os.path.join(_root, ".venv", "Lib", "site-packages")
if os.path.exists(_venv_site) and _venv_site not in sys.path:
    sys.path.insert(0, _venv_site)
if _root not in sys.path:
    sys.path.insert(0, _root)

from omnichannel_powerhouse.kokoro_engine import (
    MODEL_URL, VOICES_URL, MODEL_FILE, VOICES_FILE, download_file_with_resume
)

print("Starting download of Kokoro-82M ONNX model weights and voices...", flush=True)
download_file_with_resume(VOICES_URL, VOICES_FILE, expected_min_bytes=10000000)
download_file_with_resume(MODEL_URL, MODEL_FILE, expected_min_bytes=50000000)
print("SUCCESS: Kokoro-82M model weights secured!", flush=True)
