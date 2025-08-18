"""
Tests for ModelSensor
"""

import pytest
import json
from modelsensor import ModelSensor, JSONFormatter, MarkdownFormatter


class TestModelSensor:
    """Test cases for ModelSensor class"""

    def setup_method(self):
        """Setup for each test method"""
        self.sensor = ModelSensor()

    def test_sensor_initialization(self):
        """Test sensor can be initialized"""
        assert self.sensor is not None
        assert self.sensor.data == {}

    def test_get_time_info(self):
        """Test time information collection"""
        time_info = self.sensor.get_time_info()
        
        required_keys = [
            "current_time", "utc_time", "timestamp", 
            "timezone", "weekday", "formatted_time"
        ]
        
        for key in required_keys:
            assert key in time_info
        
        assert isinstance(time_info["timestamp"], int)
        assert isinstance(time_info["weekday"], str)

    def test_get_system_info(self):
        """Test system information collection"""
        system_info = self.sensor.get_system_info()
        
        required_keys = [
            "system", "node_name", "release", "version",
            "machine", "processor", "platform", "python_version",
            "hostname", "user"
        ]
        
        for key in required_keys:
            assert key in system_info
        
        assert isinstance(system_info["system"], str)
        assert isinstance(system_info["hostname"], str)

    def test_get_resource_info(self):
        """Test resource information collection"""
        resource_info = self.sensor.get_resource_info()
        
        assert "cpu" in resource_info
        assert "memory" in resource_info
        assert "disk" in resource_info
        assert "network" in resource_info
        
        # Check CPU info
        cpu = resource_info["cpu"]
        assert "usage_percent" in cpu
        assert "count" in cpu
        assert isinstance(cpu["usage_percent"], (int, float))
        assert isinstance(cpu["count"], int)
        
        # Check memory info
        memory = resource_info["memory"]
        assert "total" in memory
        assert "used" in memory
        assert "percentage" in memory
        assert isinstance(memory["total"], int)
        assert isinstance(memory["percentage"], (int, float))

    def test_get_environment_info(self):
        """Test environment information collection"""
        env_info = self.sensor.get_environment_info()
        
        required_keys = [
            "working_directory", "home_directory", "temp_directory",
            "path_separator", "line_separator", "shell", "runtime_context"
        ]
        
        for key in required_keys:
            assert key in env_info
        
        assert isinstance(env_info["runtime_context"], dict)

    def test_get_network_info(self):
        """Test network information collection"""
        network_info = self.sensor.get_network_info()
        
        assert "interfaces" in network_info
        assert isinstance(network_info["interfaces"], list)

    def test_collect_all_data(self):
        """Test collecting all data"""
        data = self.sensor.collect_all_data()
        
        required_sections = [
            "sensor_info", "time", "system", 
            "resources", "environment", "network"
        ]
        
        for section in required_sections:
            assert section in data
        
        # Test with location
        data_with_location = self.sensor.collect_all_data(include_location=True)
        assert "location" in data_with_location

    def test_to_json(self):
        """Test JSON output"""
        json_output = self.sensor.to_json()
        
        # Should be valid JSON
        parsed = json.loads(json_output)
        assert isinstance(parsed, dict)
        
        # Should contain main sections
        assert "sensor_info" in parsed
        assert "time" in parsed

    def test_to_dict(self):
        """Test dictionary output"""
        dict_output = self.sensor.to_dict()
        
        assert isinstance(dict_output, dict)
        assert "sensor_info" in dict_output


class TestFormatters:
    """Test cases for formatters"""

    def setup_method(self):
        """Setup for each test method"""
        self.sensor = ModelSensor()
        self.data = self.sensor.collect_all_data()

    def test_json_formatter(self):
        """Test JSON formatter"""
        json_output = JSONFormatter.format(self.data)
        
        # Should be valid JSON
        parsed = json.loads(json_output)
        assert isinstance(parsed, dict)
        
        # Test compact format
        compact_output = JSONFormatter.format_compact(self.data)
        assert len(compact_output) <= len(json_output)

    def test_markdown_formatter(self):
        """Test Markdown formatter"""
        markdown_output = MarkdownFormatter.format(self.data)
        
        # Should contain markdown elements
        assert "# System Information Report" in markdown_output
        assert "## 🕒 Time Information" in markdown_output
        assert "## 💻 System Information" in markdown_output
        
        # Test summary format
        summary = MarkdownFormatter.format_summary(self.data)
        assert "**Time**:" in summary
        assert "**System**:" in summary


if __name__ == "__main__":
    pytest.main([__file__]) 