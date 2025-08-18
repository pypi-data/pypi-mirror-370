import subprocess
import sys
import json
import tempfile

class TestCLIAnalyzeFile:
    def test_analyze_file_success(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as input_file:
            input_file.write("Great camera quality\n")
            input_file.write("Poor battery life\n")
            input_file.write("Amazing screen\n")
            input_path = input_file.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as output_file:
            output_path = output_file.name
        
        result = subprocess.run([
            sys.executable, "-m", "marsa", "analyze-file", 
            input_path,
            "-c", "tests/fixtures/test_cli_config.yaml",
            "-o", output_path
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert "Analysis complete!" in result.stdout
        assert "Processed: 3 comments" in result.stdout
        
        with open(output_path) as f:
            data = json.load(f)
            assert len(data) == 3
            assert all('original_text' in item for item in data)
    
    def test_analyze_file_missing_input(self):
        result = subprocess.run([
            sys.executable, "-m", "marsa", "analyze-file",
            "nonexistent.txt", 
            "-c", "tests/fixtures/test_cli_config.yaml"
        ], capture_output=True, text=True)
        
        assert result.returncode == 1
        assert "Input file" in result.stdout
        assert "does not exist" in result.stdout
    
    def test_analyze_file_empty_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as input_file:
            input_path = input_file.name # empty file
        
        result = subprocess.run([
            sys.executable, "-m", "marsa", "analyze-file",
            input_path,
            "-c", "tests/fixtures/test_cli_config.yaml"  
        ], capture_output=True, text=True)
        
        assert result.returncode == 1
        assert "No comments found" in result.stdout