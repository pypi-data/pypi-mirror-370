#!/usr/bin/env python3
"""
Automated Test Suite for the Local AI Chat project.

This script verifies that all core components are functioning correctly,
including model downloading, loading, and basic inference.
It is designed to be run in a CI/CD environment or as a pre-flight check.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Ensure the project root is in the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# --- Local Imports ---
# We are testing these modules
try:
    from llmocal.models.manager import download_model_if_needed, get_model_path, DEFAULT_REPO_ID, DEFAULT_FILENAME
    from llmocal.core.engine import LLMEngine
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Python path: {sys.path}")
    print(f"Project root: {project_root}")
    raise

# --- Test Suite ---

class TestLocalAISetup(unittest.TestCase):
    """Test suite for verifying the setup and core functions."""

    def setUp(self): 
        """Set up common resources for tests."""
        self.console_mock = MagicMock()
        # Use a temporary directory for model downloads to avoid side effects
        self.temp_models_dir = Path("./temp_test_models")
        self.temp_models_dir.mkdir(exist_ok=True)

    def tearDown(self):
        """Clean up after tests."""
        # This cleanup is basic. For a real-world scenario,
        # you might want to recursively delete the temp directory.
        pass

    @patch('llmocal.models.manager.hf_hub_download')
    @patch('llmocal.models.manager.MODELS_DIR', new=Path("./temp_test_models"))
    def test_01_model_download(self, mock_hf_download):
        """Test Case 1: Model download logic."""
        print("\n🧪 Running Test: Model Download Logic")
        
        # Create the expected model path structure
        test_repo_name = DEFAULT_REPO_ID.replace("/", "_")
        model_dir = self.temp_models_dir / test_repo_name
        model_dir.mkdir(parents=True, exist_ok=True)
        model_path = model_dir / DEFAULT_FILENAME
        
        # Mock successful download
        mock_hf_download.return_value = str(model_path)
        
        # Create a dummy file to simulate successful download
        model_path.touch()
        model_path.write_text("dummy model data")

        # Call the function to test
        result_path = download_model_if_needed()

        # Assertions
        self.assertIsNotNone(result_path, "Download function should return a path.")
        self.assertTrue(result_path.exists(), "Model file should exist after download.")
        print("✅ Test Passed")

    @patch('llmocal.core.engine.Llama')
    def test_02_model_loading(self, mock_llama):
        """Test Case 2: AI Engine model loading."""
        print("\n🧪 Running Test: AI Engine Model Loading")
        # Create a dummy model file for the test
        dummy_model_path = self.temp_models_dir / "dummy_model.gguf"
        dummy_model_path.touch()

        # Mock the Llama class to avoid actual model loading
        mock_llama.return_value = MagicMock() # Simulate a successful load

        # Initialize and load the model
        engine = LLMEngine(dummy_model_path, console=self.console_mock)
        engine.load_model()

        # Assertions
        self.assertIsNotNone(engine.llm, "LLM object should be instantiated after loading.")
        self.assertTrue(mock_llama.called, "Llama constructor should have been called.")
        print("✅ Test Passed")

    @patch('llmocal.core.engine.Llama')
    def test_03_inference(self, mock_llama):
        """Test Case 3: AI Engine response generation."""
        print("\n🧪 Running Test: Basic Inference")
        dummy_model_path = self.temp_models_dir / "dummy_model.gguf"
        dummy_model_path.touch()

        # Mock the response stream from the Llama model
        mock_response = iter([{
            'choices': [{
                'text': 'This is a test response.'
            }]
        }])
        mock_llm_instance = MagicMock()
        mock_llm_instance.return_value = mock_response
        mock_llama.return_value = mock_llm_instance

        # Setup engine and generate response
        engine = LLMEngine(dummy_model_path, console=self.console_mock)
        engine.load_model() # This now uses the mocked Llama
        response_generator = engine.generate_response("[INST] Hello [/INST]")
        full_response = "".join(list(response_generator))

        # Assertions
        self.assertEqual(full_response, "This is a test response.")
        print("✅ Test Passed")


def run_tests():
    """Runs the test suite."""
    print("--- Running Local AI Test Suite ---")
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestLocalAISetup)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    print("--- Test Suite Finished ---")
    return len(result.failures) == 0 and len(result.errors) == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
