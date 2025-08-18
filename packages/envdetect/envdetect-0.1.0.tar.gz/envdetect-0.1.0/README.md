# EnvDetect

EnvDetect is a lightweight Python library for detecting detailed system environment information, including OS, CPU, memory, GPU, Python runtime, and installed packages.  

It can be used for debugging, reproducibility, environment validation, or as part of ML/AI pipelines where knowing the exact system setup is crucial.

---

## Features

- **OS Information**: Name, version, release, architecture, and more.  
- **CPU Information**: Count, frequency, brand, cores, cache sizes, etc.  
- **Memory Information**: Total, available, used, swap, and percentages.  
- **GPU Information**: Vendor, name, driver version, VRAM, and more (if available).  
- **Python Runtime**: Version, implementation, executable path, installed packages.  
- **Environment Summary**: Aggregates all details into one dictionary for easy export/logging.

---

## Installation

```bash
pip install envdetect
```

## Usage

```python
from envdetect import os_info, cpu_info, memory_info, gpu_info, python_info, environment_summary

print("=== OS Info ===")
print(os_info())

print("=== CPU Info ===")
print(cpu_info())

print("=== Memory Info ===")
print(memory_info())

print("=== GPU Info ===")
print(gpu_info())

print("=== Python Info ===")
print(python_info())

print("=== Full Environment Summary ===")
print(environment_summary())
```

## CLI

```bash
python -m envdetect
```

This will print a full environment summary in JSON format.

### Example Output

```json
{
  "os": {
    "system": "Linux",
    "release": "5.15.0-78-generic",
    "version": "#85-Ubuntu SMP Tue Jun 6 23:34:54 UTC 2023",
    "architecture": ["64bit", "ELF"],
    "machine": "x86_64",
    "processor": "Intel(R) Xeon(R) CPU"
  },
  "cpu": {
    "physical_cores": 4,
    "total_cores": 8,
    "cpu_freq_mhz_max": 4200.0,
    "cpu_freq_mhz_min": 800.0,
    "cpu_freq_mhz_current": 2300.0,
    "l1_cache_kb": 256,
    "l2_cache_kb": 1024,
    "l3_cache_kb": 8192,
    "brand": "Intel(R) Core(TM) i7-8750H CPU @ 2.20GHz"
  },
  "memory": {
    "total": 16,
    "available": 10.5,
    "used": 5.3,
    "percent": 34.5,
    "swap_total": 2,
    "swap_used": 0.1,
    "swap_free": 1.9
  },
  "gpu": [
    {
      "id": "GPU-0",
      "name": "NVIDIA GeForce RTX 3070",
      "driver_version": "535.54",
      "memory_total_MB": 8000,
      "memory_free_MB": 6500,
      "memory_used_MB": 1500
    }
  ],
  "python": {
    "version": "3.10.12",
    "implementation": "CPython",
    "executable": "/usr/bin/python3",
    "packages_count": 240
  }
}
```

## Running Tests

```bash
python -m unittest discover -s tests
```
