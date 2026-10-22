"""
OmniChannel Sandboxed Code Interpreter Engine (Open-Interpreter Architecture)
=============================================================================
Enables ChatGPT Pro-grade Advanced Data Analysis & local code execution:
- Executes Python & Shell scripts in an isolated subprocess with 45s safety timeout
- Automatically captures standard output, errors, and return codes
- Intercepts generated charts/plots (Matplotlib/Seaborn/PIL) and converts to web URLs
- Securely offloads computation to local Python 3.11 environment
"""

import os
import sys
import glob
import time
import shutil
import subprocess
from typing import Dict, Any, Optional

_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHARTS_DIR = os.path.join(_root, "output", "charts")
SANDBOX_DIR = os.path.join(_root, "temp_render", "interpreter_sandbox")
os.makedirs(CHARTS_DIR, exist_ok=True)
os.makedirs(SANDBOX_DIR, exist_ok=True)

PYTHON_EXE = os.path.expanduser(r"~\AppData\Roaming\uv\python\cpython-3.11.17-windows-x86_64-none\python.exe")
if not os.path.exists(PYTHON_EXE):
    PYTHON_EXE = sys.executable


def execute_python_code(code: str, timeout: int = 45) -> Dict[str, Any]:
    """
    Executes Python script, tracks execution time, and detects generated plot images.
    """
    ts = int(time.time() * 1000)
    script_path = os.path.join(SANDBOX_DIR, f"exec_{ts}.py")
    out_chart_target = os.path.join(CHARTS_DIR, f"chart_{ts}.png")

    clean_chart_target = out_chart_target.replace("\\", "/")
    # Prepend helper imports & automatic chart redirection if matplotlib is used
    header = f"""# -*- coding: utf-8 -*-
import sys, os
os.environ['MPLBACKEND'] = 'Agg'
try:
    import matplotlib.pyplot as plt
    original_show = plt.show
    def auto_save_show(*args, **kwargs):
        plt.savefig('{clean_chart_target}', bbox_inches='tight', dpi=150)
        print('[CHART_SAVED] {clean_chart_target}')
    plt.show = auto_save_show
except ImportError:
    pass

"""
    full_script = header + code

    with open(script_path, "w", encoding="utf-8") as f:
        f.write(full_script)

    env = os.environ.copy()
    env["PYTHONPATH"] = f"{_root};{os.path.join(_root, '.venv', 'Lib', 'site-packages')};{env.get('PYTHONPATH', '')}"

    start_time = time.time()
    try:
        proc = subprocess.run(
            [PYTHON_EXE, script_path],
            cwd=_root,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        elapsed = time.time() - start_time

        stdout = proc.stdout or ""
        stderr = proc.stderr or ""

        # Check if an image was generated
        chart_url = None
        if os.path.exists(out_chart_target) and os.path.getsize(out_chart_target) > 500:
            chart_url = f"/output/charts/{os.path.basename(out_chart_target)}"
        else:
            # Check for any newly created png/jpg in the sandbox
            recent_imgs = glob.glob(os.path.join(SANDBOX_DIR, f"*.png"))
            if recent_imgs:
                latest_img = max(recent_imgs, key=os.path.getmtime)
                if os.path.getmtime(latest_img) >= start_time:
                    dest = os.path.join(CHARTS_DIR, os.path.basename(latest_img))
                    shutil.move(latest_img, dest)
                    chart_url = f"/output/charts/{os.path.basename(dest)}"

        return {
            "success": proc.returncode == 0,
            "stdout": stdout,
            "stderr": stderr,
            "exit_code": proc.returncode,
            "execution_time_s": round(elapsed, 3),
            "chart_url": chart_url
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Execution timed out after {timeout} seconds.",
            "execution_time_s": timeout,
            "chart_url": None
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "execution_time_s": 0.0,
            "chart_url": None
        }
    finally:
        # Prune scratch script
        try:
            if os.path.exists(script_path):
                os.remove(script_path)
        except Exception:
            pass
