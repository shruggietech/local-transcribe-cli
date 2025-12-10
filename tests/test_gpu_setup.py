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

    # Mock os.add_dll_directory to verify calls
    with patch("os.add_dll_directory") as mock_add_dll:
        import local_transcribe_cli.cli
        
        # We expect at least two calls (cublas and cudnn)
        # We can't know the exact path on this machine easily without querying the real packages,
        # but we can check if it found *something*.
        
        # If the logic is broken (like before where it checked __file__ which was None),
        # mock_add_dll will not be called or called with wrong args.
        
        # Let's verify that we actually have the packages installed in this env
        import nvidia.cudnn
        import nvidia.cublas
        
        # If we have the packages, we expect calls.
        assert mock_add_dll.call_count >= 2, "os.add_dll_directory should be called for cublas and cudnn"
        
        # Verify the paths end in 'bin'
        calls = [args[0] for args, _ in mock_add_dll.call_args_list]
        assert any(p.endswith("bin") and "cudnn" in p for p in calls), "Did not add cudnn/bin path"
        assert any(p.endswith("bin") and "cublas" in p for p in calls), "Did not add cublas/bin path"
