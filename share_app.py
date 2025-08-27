import os
import sys
import time
import subprocess
from pyngrok import ngrok

def find_streamlit():
    # Try to find streamlit executable
    try:
        # Try direct import first
        import streamlit
        streamlit_path = os.path.join(os.path.dirname(sys.executable), 'Scripts', 'streamlit.exe')
        if os.path.exists(streamlit_path):
            return streamlit_path
        
        # Try python -m streamlit
        return f'"{sys.executable}" -m streamlit'
    except ImportError:
        return 'streamlit'

def main():
    process = None
    try:
        print("Starting Streamlit app...")
        
        # Get the current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Find streamlit command
        streamlit_cmd = find_streamlit()
        
        # Build the command
        cmd = f"{streamlit_cmd} run \"{os.path.join(current_dir, 'real_estate_dashboard.py')}\""
        
        print(f"Running command: {cmd}")
        
        # Start Streamlit using shell=True to handle paths with spaces
        process = subprocess.Popen(cmd, shell=True)
        
        # Give Streamlit a moment to start
        print("Waiting for Streamlit to start...")
        time.sleep(8)
        
        print("\nSetting up secure tunnel...")
        # Set up ngrok
        public_url = ngrok.connect(8501)
        
        print("\n" + "="*80)
        print(f"Your app is now available at: {public_url}")
        print("="*80)
        print("\nNote: This URL will be active as long as this script is running")
        print("Press Ctrl+C to stop the server and close the tunnel")
        
        # Keep the script running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down gracefully...")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nCleaning up...")
        if process:
            try:
                # For Windows
                if os.name == 'nt':
                    import ctypes
                    ctypes.windll.kernel32.GenerateConsoleCtrlEvent(1, process.pid)
                else:
                    process.terminate()
                process.wait(timeout=5)
            except Exception as e:
                print(f"Error stopping process: {e}")
        try:
            ngrok.kill()
        except Exception as e:
            print(f"Error stopping ngrok: {e}")
        print("Tunnel and app server have been stopped.")

if __name__ == "__main__":
    main()
