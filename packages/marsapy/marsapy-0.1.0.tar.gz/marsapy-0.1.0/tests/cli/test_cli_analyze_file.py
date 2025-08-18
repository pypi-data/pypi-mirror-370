import subprocess
import sys
import json
import tempfile
from pathlib import Path

class TestCLIAnalyzeText:
    def test_analyze_text_console_output(self):
        result = subprocess.run([
            sys.executable, "-m", "marsa", "analyze-text",
            "Great camera but poor battery",
            "-c", "tests/fixtures/test_cli_config.yaml"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert "Text:" in result.stdout
        assert "Aspects found:" in result.stdout
    
    def test_analyze_text_file_output(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            result = subprocess.run([
                sys.executable, "-m", "marsa", "analyze-text",
                "Amazing screen quality",
                "-c", "tests/fixtures/test_cli_config.yaml",
                "-o", tmp.name
            ], capture_output=True, text=True)
            
            assert result.returncode == 0
            assert "Results saved to" in result.stdout
            
            output_path = Path(tmp.name)
            assert output_path.exists()
            
            with open(output_path) as f:
                data = json.load(f)
                assert len(data) == 1
                assert data[0]['original_text'] == "Amazing screen quality"
    
    def test_analyze_text_missing_config(self):
        result = subprocess.run([
            sys.executable, "-m", "marsa", "analyze-text",
            "Some text",
            "-c", "nonexistent.yaml"
        ], capture_output=True, text=True)
        
        assert result.returncode == 1
        assert "Config file" in result.stdout
        assert "does not exist" in result.stdout
    
    def test_analyze_text_empty_string(self):
        result = subprocess.run([
            sys.executable, "-m", "marsa", "analyze-text",
            "",
            "-c", "tests/fixtures/test_cli_config.yaml"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0