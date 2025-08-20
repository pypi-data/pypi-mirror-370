"""Tests for Batch builder class.

Testing:
1. Builder pattern and method chaining
2. Default parameter handling and validation
3. Job addition and batch execution
"""

import pytest
from unittest.mock import patch, MagicMock

from batchata import Batch
from batchata.exceptions import ValidationError
from tests.mocks.mock_provider import MockProvider


class TestBatch:
    """Test Batch builder functionality."""
    
    def test_builder_pattern_method_chaining(self, temp_dir):
        """Test that all builder methods return self for chaining."""
        results_dir = str(temp_dir / "results")
        
        # Patch get_provider to return mock
        with patch('batchata.core.batch.get_provider') as mock_get:
            mock_provider = MockProvider()
            mock_get.return_value = mock_provider
            
            batch = Batch(results_dir)
            
            # Test method chaining
            result = (batch
                     .set_state(file=str(temp_dir / "state.json"))
                     .set_default_params(model="mock-model-basic", temperature=0.5)
                     .add_cost_limit(usd=10.0)
                     .add_job(messages=[{"role": "user", "content": "test"}]))
            
            assert result is batch
            assert batch.config.default_params["model"] == "mock-model-basic"
            assert batch.config.default_params["temperature"] == 0.5
            assert batch.config.cost_limit_usd == 10.0
            assert len(batch.jobs) == 1
    
    def test_default_parameters_and_job_creation(self, temp_dir):
        """Test default parameters are applied to jobs and validation works."""
        results_dir = str(temp_dir / "results")
        
        # Patch get_provider to return mock
        with patch('batchata.core.batch.get_provider') as mock_get:
            mock_provider = MockProvider()
            mock_get.return_value = mock_provider
            
            batch = (Batch(results_dir)
                    .set_state(file=str(temp_dir / "state.json"))
                    .set_default_params(model="mock-model-basic", temperature=0.8, max_tokens=500))
            
            # Add job without specifying all params
            batch.add_job(messages=[{"role": "user", "content": "Hello"}])
            
            assert len(batch.jobs) == 1
            job = batch.jobs[0]
            
            # Check defaults were applied
            assert job.model == "mock-model-basic"
            assert job.temperature == 0.8
            assert job.max_tokens == 500
            
            # Add job with override
            batch.add_job(
                messages=[{"role": "user", "content": "Hi"}],
                temperature=0.2
            )
            
            assert len(batch.jobs) == 2
            assert batch.jobs[1].temperature == 0.2
            assert batch.jobs[1].model == "mock-model-basic"
    
    @pytest.mark.parametrize("raw_files,results_dir,expected", [
        (None, "/tmp/results", True),    # Auto-determined from results_dir
        (None, "", False),                # Empty results_dir
        (True, "/tmp/results", True),    # Explicitly set
        (False, "/tmp/results", False),   # Explicitly disabled
    ])
    def test_raw_files_configuration(self, temp_dir, raw_files, results_dir, expected):
        """Test raw_files is correctly configured based on inputs."""
        if results_dir:
            results_dir = str(temp_dir / "results")
        
        batch = Batch(
            results_dir=results_dir,
            raw_files=raw_files
        )
        
        assert batch.config.raw_files == expected