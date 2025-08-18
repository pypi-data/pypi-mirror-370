import subprocess
import sys

class TestCLIIntegration:
    def test_help_command(self):
        result = subprocess.run([
            sys.executable, "-m", "marsa", "--help"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert "MARSA" in result.stdout
        assert "analyze-text" in result.stdout
        assert "analyze-file" in result.stdout
    
    def test_no_command(self):
        result = subprocess.run([
            sys.executable, "-m", "marsa"
        ], capture_output=True, text=True)
        
        assert result.returncode == 1
        assert "MARSA" in result.stdout
    
    def test_command_aliases(self):
        result = subprocess.run([
            sys.executable, "-m", "marsa", "text", "--help"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert "analyze-text" in result.stdout or "text" in result.stdout