"""
Tests for the NTATool enum.
"""
from mcp_server_nta.server import NTATool


class TestNTAToolEnum:
    """Test class for NTATool enum."""

    def test_enum_values(self):
        """Test that the enum has the expected values."""
        assert NTATool.GET_TRIP_UPDATES.value == "get_trip_updates"
        assert NTATool.GET_VEHICLES.value == "get_vehicles"
        assert NTATool.GTFSR.value == "get_gtfs_realtime"

    def test_enum_members(self):
        """Test that the enum has the expected members."""
        assert len(NTATool) == 3
        assert "GET_TRIP_UPDATES" in NTATool.__members__
        assert "GET_VEHICLES" in NTATool.__members__
        assert "GTFSR" in NTATool.__members__

    def test_enum_case_sensitivity(self):
        """Test that the enum values are case-sensitive."""
        assert NTATool.GET_TRIP_UPDATES.value != "GET_TRIP_UPDATES"
        assert NTATool.GET_VEHICLES.value != "GET_VEHICLES"
        assert NTATool.GTFSR.value != "GTFSR"
