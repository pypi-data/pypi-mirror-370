import os
import sys
import plotly.io as pio
from plotly.io._kaleido import KaleidoScope

def override_kaleido_executable():
    """Override Kaleido executable path to use conda environment"""
    
    # Get conda environment path
    conda_env_path = sys.prefix
    kaleido_executable = os.path.join(conda_env_path, "lib", "site-packages", "kaleido", "executable", "kaleido")
    
    # If not found in conda, try to find it elsewhere
    if not os.path.exists(kaleido_executable):
        # Try to find kaleido executable
        import kaleido
        kaleido_path = os.path.dirname(kaleido.__file__)
        kaleido_executable = os.path.join(kaleido_path, "executable", "kaleido")
        
        if not os.path.exists(kaleido_executable):
            # Look in system Python
            system_kaleido = r"C:\Users\sroni\AppData\Roaming\Python\Python36\site-packages\kaleido\executable\kaleido"
            if os.path.exists(system_kaleido):
                kaleido_executable = system_kaleido
            else:
                kaleido_executable = "kaleido"  # Use PATH
    
    print(f"Setting Kaleido executable to: {kaleido_executable}")
    
    # Override the KaleidoScope class
    class CustomKaleidoScope(KaleidoScope):
        def _build_proc_args(self):
            return [kaleido_executable, self.scope_name]
    
    # Replace the default scope
    pio.kaleido.scope = CustomKaleidoScope()
    
    # Test
    try:
        import plotly.graph_objects as go
        fig = go.Figure()
        img = fig.to_image(format="png")
        print("✅ Plotly/Kaleido working with custom path!")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    override_kaleido_executable() 