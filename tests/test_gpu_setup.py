import sys
import os
import pytest
from unittest.mock import MagicMock, patch

@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific DLL loading test")
def test_nvidia_dll_loading():
    """
    Verify that we correctly locate and add the 'bin' directories of nvidia packages
    to the DLL search path, even if they are namespace packages (no __file__).
    """
    # We need to force a reload of the CLI module to trigger the top-level code
    if "local_transcribe_cli.cli" in sys.modules:
        del sys.modules["local_transcribe_cli.cli"]

    # Mock os.add_dll_directory to verify calls, but let it execute so other libs (like PyAV) load correctly
    real_add_dll_directory = os.add_dll_directory
    with patch("os.add_dll_directory", side_effect=real_add_dll_directory) as mock_add_dll, \
         patch.dict(os.environ, {}, clear=False):
        
        import local_transcribe_cli.cli
        
        # We expect at least two calls (cublas and cudnn)
        import nvidia.cudnn
        import nvidia.cublas
        
        assert mock_add_dll.call_count >= 2, "os.add_dll_directory should be called for cublas and cudnn"
        
        # Verify the paths end in 'bin'
        calls = [args[0] for args, _ in mock_add_dll.call_args_list]
        assert any(p.endswith("bin") and "cudnn" in p for p in calls), "Did not add cudnn/bin path to DLL directory"
        assert any(p.endswith("bin") and "cublas" in p for p in calls), "Did not add cublas/bin path to DLL directory"

        # Verify PATH modification
        current_path = os.environ["PATH"]
        # Note: Windows paths are case-insensitive, but python string check is case-sensitive.
        # We check if the path string is present.
        assert any("cudnn" in p.lower() and "bin" in p.lower() for p in current_path.split(os.pathsep)), "Did not add cudnn/bin path to PATH"
        assert any("cublas" in p.lower() and "bin" in p.lower() for p in current_path.split(os.pathsep)), "Did not add cublas/bin path to PATH"
