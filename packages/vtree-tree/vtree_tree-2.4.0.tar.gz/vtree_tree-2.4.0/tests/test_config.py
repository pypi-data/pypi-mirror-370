"""Tests for configuration handling"""
import pytest
from pathlib import Path
import tempfile
import configparser
from unittest.mock import Mock, patch
from vtree.main import VTreeApp


class TestConfigurationHandling:
    """Test configuration loading and saving"""
    
    def test_default_settings(self):
        """Test default settings structure"""
        with tempfile.TemporaryDirectory() as tmpdir:
            app = VTreeApp(tmpdir)
            settings = app._settings
            
            # Check all default settings exist
            assert "file_notify_timer" in settings
            assert settings["file_notify_timer"] == 120
            assert settings["show_hidden"] is False
            assert settings["show_file_panel"] is False
            assert settings["theme"] == "dark"
            assert settings["hidden_file_color"] == "#4a4a4a"
            assert settings["changed_file_bg"] == "dark_red"
            assert settings["changed_file_fg"] == "white"
    
    def test_create_default_config(self):
        """Test creating default config file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            config_file = tmppath / ".vtree.conf"
            
            app = VTreeApp(tmpdir)
            
            # Config file should be created
            assert config_file.exists()
            
            # Read and verify content
            config = configparser.ConfigParser()
            config.read(config_file)
            
            assert "settings" in config
            assert config["settings"]["file_notify_timer"] == "120"
            assert config["settings"]["show_hidden"] == "false"
            assert config["settings"]["show_file_panel"] == "false"
    
    def test_load_existing_config(self):
        """Test loading existing config file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            config_file = tmppath / ".vtree.conf"
            
            # Create custom config
            config = configparser.ConfigParser()
            config["settings"] = {
                "file_notify_timer": "60",
                "show_hidden": "true",
                "show_file_panel": "true",
                "theme": "light",
                "hidden_file_color": "#666666",
            }
            
            with open(config_file, 'w') as f:
                config.write(f)
            
            # Load app
            app = VTreeApp(tmpdir)
            
            # Check loaded settings
            assert app._settings["file_notify_timer"] == 60
            assert app._settings["show_hidden"] is True
            assert app._settings["show_file_panel"] is True
            assert app._settings["theme"] == "light"
            assert app._settings["hidden_file_color"] == "#666666"
    
    def test_save_settings_preserves_manual_edits(self):
        """Test that _save_settings preserves manual edits"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            config_file = tmppath / ".vtree.conf"
            
            # Create initial config
            app = VTreeApp(tmpdir)
            app.show_hidden = False
            app.show_file_panel = False
            app._save_settings()
            
            # Manually edit the config file
            config = configparser.ConfigParser()
            config.read(config_file)
            config["settings"]["file_notify_timer"] = "10"
            config["settings"]["custom_setting"] = "custom_value"
            with open(config_file, 'w') as f:
                config.write(f)
            
            # Change a programmatic setting and save
            app.show_hidden = True
            app._save_settings()
            
            # Read config again
            config = configparser.ConfigParser()
            config.read(config_file)
            
            # Manual edits should be preserved
            assert config["settings"]["file_notify_timer"] == "10"
            assert config["settings"]["custom_setting"] == "custom_value"
            # Programmatic changes should be applied
            assert config["settings"]["show_hidden"] == "true"
    
    def test_config_with_invalid_values(self):
        """Test handling invalid config values"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            config_file = tmppath / ".vtree.conf"
            
            # Create config with invalid values
            config = configparser.ConfigParser()
            config["settings"] = {
                "file_notify_timer": "not_a_number",
                "show_hidden": "not_a_bool",
            }
            
            with open(config_file, 'w') as f:
                config.write(f)
            
            # App should fall back to defaults on error
            app = VTreeApp(tmpdir)
            assert app._settings["file_notify_timer"] == 120  # Default
            assert app._settings["show_hidden"] is False  # Default