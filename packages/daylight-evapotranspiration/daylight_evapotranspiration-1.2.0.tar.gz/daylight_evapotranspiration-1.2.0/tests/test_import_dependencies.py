import pytest

# List of dependencies
dependencies = [
    "dateutil",             # python-dateutil is imported as dateutil
    "numpy",
    "pandas",
    "rasters",
    "solar_apparent_time",  # solar-apparent-time is imported as solar_apparent_time
    "sun_angles",           # sun-angles is imported as sun_angles
    "verma_net_radiation"   # verma-net-radiation is imported as verma_net_radiation
]

# Generate individual test functions for each dependency
@pytest.mark.parametrize("dependency", dependencies)
def test_dependency_import(dependency):
    __import__(dependency)
