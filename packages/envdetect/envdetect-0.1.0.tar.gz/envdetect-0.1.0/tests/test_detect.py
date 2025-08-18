"""
Testing environment detection functions.
"""


import unittest
import envdetect


class TestEnvDetect(unittest.TestCase):
    """Unit tests for environment detection functions."""
    def test_python_info(self):
        """Test Python environment detection."""
        info = envdetect.python_info()
        self.assertIn("version", info)
        self.assertIn("implementation", info)
        self.assertIn("executable", info)

    def test_os_info(self):
        """Test OS environment detection."""
        info = envdetect.os_info()
        self.assertIn("system", info)
        self.assertIn("node", info)
        self.assertIn("release", info)
        self.assertIn("version", info)
        self.assertIn("machine", info)
        self.assertIn("processor", info)
        self.assertIn("architecture", info)

    def test_cpu_info(self):
        """Test CPU environment detection."""
        info = envdetect.cpu_info()
        self.assertIn("physical_cores", info)
        self.assertIn("total_cores", info)
        self.assertIn("cpu_freq_mhz_max", info)
        self.assertIn("cpu_freq_mhz_min", info)
        self.assertIn("cpu_freq_mhz_current", info)
        self.assertIn("cpu_percent_total", info)
        self.assertIn("load_avg", info)
        self.assertIn("brand_raw", info)

    def test_memory_info(self):
        """Test memory environment detection."""
        info = envdetect.memory_info()
        self.assertIn("total", info)
        self.assertIn("available", info)
        self.assertIn("used", info)
        self.assertIn("percent", info)
        self.assertIn("swap_total", info)
        self.assertIn("swap_used", info)
        self.assertIn("swap_free", info)
        self.assertIn("swap_percent", info)

    def test_gpu_info(self):
        """Test GPU environment detection."""
        info = envdetect.gpu_info()
        # GPU info may be empty on systems without GPUs
        self.assertIsInstance(info, list)
        if info[0]["status"] == "No GPU detected":
            return
        for gpu in info:
            self.assertIn("uuid", gpu)
            self.assertIn("name", gpu)
            self.assertIn("load_percent", gpu)
            self.assertIn("memory_total_gb", gpu)
            self.assertIn("memory_used_gb", gpu)
            self.assertIn("memory_free_gb", gpu)
            self.assertIn("driver", gpu)
            self.assertIn("temperature_celsius", gpu)
            self.assertIn("uuid", gpu)

    def test_environment_summary(self):
        """Test overall environment summary."""
        summary = envdetect.environment_summary()
        self.assertIn("python", summary)
        self.assertIn("os", summary)
        self.assertIn("cpu", summary)
        self.assertIn("memory", summary)
        self.assertIn("gpu", summary)


if __name__ == "__main__":
    unittest.main()
