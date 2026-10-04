import os
import sys
import importlib.metadata
import streamlit.version

if sys.version_info < (3, 10):
    import importlib_metadata
else:
    importlib_metadata = importlib.metadata

try:
    importlib_metadata.version("streamlit")
except importlib_metadata.PackageNotFoundError:
    class DummyDistribution(importlib_metadata.Distribution):
        def read_text(self, filename):
            if filename == "METADATA":
                return "Name: streamlit\nVersion: 1.32.0"
            return None
        def locate_file(self, path):
            return ""
    
    original_distribution = importlib_metadata.distribution
    def patched_distribution(distribution_name, *args, **kwargs):
        if distribution_name == "streamlit":
            return DummyDistribution()
        return original_distribution(distribution_name, *args, **kwargs)
    
    importlib_metadata.distribution = patched_distribution

from streamlit.web import cli as stcli

if __name__ == "__main__":
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
        
    app_path = os.path.join(base_path, "app.py")
    
    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--global.developmentMode=false",
    ]
    sys.exit(stcli.main())