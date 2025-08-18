"""
Tests for the TranslinkTool enum.
"""
from mcp_server_translink.server import TranslinkTool


class TestTranslinkToolEnum:
    """Test class for TranslinkTool enum."""

    def test_enum_values(self):
        """Test that the enum has the expected values."""
        assert TranslinkTool.GET_TRIP_UPDATES.value == "get_trip_updates"
        assert TranslinkTool.GET_POSITION_UPDATES.value == "get_position_updates"
        assert TranslinkTool.GET_SERVICE_ALERTS.value == "get_service_alerts"

    def test_enum_members(self):
        """Test that the enum has the expected members."""
        assert len(TranslinkTool) == 3
        assert "GET_TRIP_UPDATES" in TranslinkTool.__members__
        assert "GET_POSITION_UPDATES" in TranslinkTool.__members__
        assert "GET_SERVICE_ALERTS" in TranslinkTool.__members__

    def test_enum_case_sensitivity(self):
        """Test that the enum values are case-sensitive."""
        assert TranslinkTool.GET_TRIP_UPDATES.value != "GET_TRIP_UPDATES"
        assert TranslinkTool.GET_POSITION_UPDATES.value != "GET_POSITION_UPDATES"
        assert TranslinkTool.GET_SERVICE_ALERTS.value != "GET_SERVICE_ALERTS"
