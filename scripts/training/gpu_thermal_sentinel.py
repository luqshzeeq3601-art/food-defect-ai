"""GPU Thermal Safety Sentinel & Real-Time Monitor.

Continuously tracks NVIDIA GPU temperature, VRAM usage, and power draw during
deep learning training. Automatically suspends training if temperature reaches
safety limit (84°C) to prevent thermal degradation, resuming once cooled (< 72°C).
"""

import csv
import datetime
import subprocess
import time
from pathlib import Path

import psutil

TARGET_PID = 17768  # Active training process PID
SAFETY_MAX_TEMP = 84  # Celsius throttle cutoff
BASE_DIR = Path(__file__).resolve().parents[2]
LOG_CSV = BASE_DIR / "reports" / "gpu_thermal_telemetry.csv"


def query_gpu_metrics() -> dict[str, float] | None:
    """Query real-time temperature, power, and memory from nvidia-smi."""
    cmd = [
        "nvidia-smi",
        "--query-gpu=temperature.gpu,fan.speed,power.draw,utilization.gpu,memory.used,memory.total",
        "--format=csv,noheader,nounits",
    ]
    try:
        out = subprocess.check_output(cmd, encoding="utf-8").strip()
        parts = [p.strip() for p in out.split(",")]
        return {
            "temp": float(parts[0]),
            "fan": float(parts[1]) if parts[1] != "[N/A]" else 0.0,
            "power": float(parts[2]),
            "util": float(parts[3]),
            "mem_used": float(parts[4]),
            "mem_total": float(parts[5]),
        }
    except Exception:
        return None


def run_sentinel(pid: int = TARGET_PID) -> None:
    """Run continuous thermal guard loop."""
    print("==================================================")
    print(f"GPU THERMAL SENTINEL ACTIVE (Target PID: {pid})")
    print(f"Safety Cutoff: >= {SAFETY_MAX_TEMP}°C | Safe Resume: <= {SAFE_RESUME_TEMP}°C")
    print(f"Telemetry Log: {LOG_CSV}")
    print("==================================================")

    LOG_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "temp_c", "fan_pct", "power_w", "gpu_util_pct", "vram_mb", "status"])

    is_suspended = False

    while True:
        # Check if process is still alive
        if not psutil.pid_exists(pid):
            print(f"[SENTINEL] Training process PID {pid} has completed or terminated.")
            break

        try:
            proc = psutil.Process(pid)
            if proc.status() == psutil.STATUS_ZOMBIE or not proc.is_running():
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            break

        metrics = query_gpu_metrics()
        if metrics:
            temp = metrics["temp"]
            power = metrics["power"]
            vram = metrics["mem_used"]
            now_str = datetime.datetime.now().strftime("%H:%M:%S")

            status = "NORMAL"

            # Thermal Safety Cutoff Check
            if temp >= SAFETY_MAX_TEMP and not is_suspended:
                print(f"\n[ALERT {now_str}] GPU Temp {temp}°C exceeded safety cutoff ({SAFETY_MAX_TEMP}°C)!")
                print(f"  -> Suspending PID {pid} to cool GPU...")
                try:
                    proc.suspend()
                    is_suspended = True
                    status = "SAFETY_SUSPENDED"
                except Exception as e:
                    print(f"  -> Suspend error: {e}")

            elif is_suspended:
                if temp <= SAFE_RESUME_TEMP:
                    print(f"\n[RECOVERY {now_str}] GPU cooled to {temp}°C (<= {SAFE_RESUME_TEMP}°C).")
                    print(f"  -> Resuming training PID {pid}...")
                    try:
                        proc.resume()
                        is_suspended = False
                        status = "RESUMED"
                    except Exception as e:
                        print(f"  -> Resume error: {e}")
                else:
                    status = "COOLING"

            # Log to CSV
            with open(LOG_CSV, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([now_str, temp, metrics["fan"], power, metrics["util"], vram, status])

            # Terminal heartbeat every 15s
            state_label = "COOLING (PAUSED)" if is_suspended else "ACTIVE"
            print(
                f"[{now_str}] Temp: {temp:4.1f}°C | Power: {power:5.1f}W | "
                f"VRAM: {vram:4.0f}/{metrics['mem_total']:4.0f}MB | State: {state_label}",
                end="\r",
                flush=True,
            )

        time.sleep(5)

    print("\n[SENTINEL] GPU Monitoring finished safely.")


if __name__ == "__main__":
    import sys
    target = int(sys.argv[1]) if len(sys.argv) > 1 else TARGET_PID
    run_sentinel(target)
