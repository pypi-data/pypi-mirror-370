#!/usr/bin/env python3
"""Launch script for GOD Mode Web Dashboard."""
import os
import sys
import subprocess
import time
import webbrowser
import socket
import random
import json
from pathlib import Path
from datetime import datetime
import signal

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    print("\n\nShutting down dashboard...")
    sys.exit(0)

def find_free_port(start=8000, end=9000):
    """Find a free port in the given range."""
    # Try random ports first for better distribution
    for _ in range(10):
        port = random.randint(start, end)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('', port))
                return port
            except:
                continue
    
    # Fallback to sequential search
    for port in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('', port))
                return port
            except:
                continue
    
    raise RuntimeError(f"No free port found in range {start}-{end}")

def check_dependencies():
    """Check if required dependencies are installed."""
    required = ['fastapi', 'uvicorn', 'psutil']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"Missing dependencies: {', '.join(missing)}")
        print("Installing...")
        subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing)

def start_backend(port=None):
    """Start the backend API server."""
    api_path = Path(__file__).parent / 'api' / 'server.py'
    
    if port is None:
        port = find_free_port(8000, 9000)
    
    print(f"🚀 Starting backend API server on port {port}...")
    
    # Set environment variable for port
    env = os.environ.copy()
    env['PORT'] = str(port)
    
    backend_process = subprocess.Popen(
        [sys.executable, str(api_path), '--port', str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env
    )
    
    # Wait for backend to start
    time.sleep(3)
    
    return backend_process, port

def start_frontend(backend_port=8000):
    """Start the frontend development server."""
    frontend_path = Path(__file__).parent / 'frontend'
    frontend_port = find_free_port(3000, 4000)
    
    # Check if node_modules exists
    if not (frontend_path / 'node_modules').exists():
        print("📦 Installing frontend dependencies...")
        subprocess.run(['npm', 'install'], cwd=frontend_path, check=True)
    
    print(f"🎨 Starting frontend development server on port {frontend_port}...")
    
    # Set environment variables for frontend
    env = os.environ.copy()
    env['PORT'] = str(frontend_port)
    env['VITE_API_URL'] = f'http://localhost:{backend_port}'
    
    frontend_process = subprocess.Popen(
        ['npm', 'run', 'dev', '--', '--port', str(frontend_port)],
        cwd=frontend_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env
    )
    
    return frontend_process, frontend_port

def main(auto_open=True, backend_port=None, frontend_port=None):
    """Main entry point.
    
    Args:
        auto_open: Whether to automatically open browser
        backend_port: Specific backend port (None for random)
        frontend_port: Specific frontend port (None for random)
    """
    signal.signal(signal.SIGINT, signal_handler)
    
    print("=" * 60)
    print("🚀 GOD Mode Web Dashboard Launcher")
    print("=" * 60)
    
    # Check dependencies
    check_dependencies()
    
    try:
        # Start backend with random or specified port
        backend, actual_backend_port = start_backend(backend_port)
        
        # Start frontend with random or specified port
        frontend, actual_frontend_port = start_frontend(actual_backend_port)
        
        # Wait a bit for servers to start
        time.sleep(5)
        
        dashboard_url = f"http://localhost:{actual_frontend_port}"
        api_url = f"http://localhost:{actual_backend_port}"
        
        print("\n" + "=" * 60)
        print("✅ Dashboard is running!")
        print("=" * 60)
        print(f"\n📊 Dashboard URL: {dashboard_url}")
        print(f"🔌 API Server URL: {api_url}")
        print(f"📝 API Docs: {api_url}/docs")
        print("\nPress Ctrl+C to stop the dashboard\n")
        
        # Save URLs to file for other processes to read
        urls_file = Path.home() / '.god-mode' / 'dashboard_urls.json'
        urls_file.parent.mkdir(exist_ok=True)
        with open(urls_file, 'w') as f:
            json.dump({
                'dashboard_url': dashboard_url,
                'api_url': api_url,
                'backend_port': actual_backend_port,
                'frontend_port': actual_frontend_port,
                'started_at': datetime.now().isoformat()
            }, f)
        
        # Open browser automatically if requested
        if auto_open:
            print(f"🌐 Opening browser to {dashboard_url}...")
            webbrowser.open(dashboard_url)
        
        # Keep running
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if backend.poll() is not None:
                print("⚠️  Backend server stopped unexpectedly")
                break
            if frontend.poll() is not None:
                print("⚠️  Frontend server stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up
        if 'backend' in locals():
            backend.terminate()
        if 'frontend' in locals():
            frontend.terminate()
        
        # Remove URLs file
        urls_file = Path.home() / '.god-mode' / 'dashboard_urls.json'
        if urls_file.exists():
            urls_file.unlink()
        
        print("Dashboard stopped.")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='GOD Mode Dashboard Launcher')
    parser.add_argument('--backend-port', type=int, default=None, 
                       help='Backend API port (default: random)')
    parser.add_argument('--frontend-port', type=int, default=None,
                       help='Frontend port (default: random)')
    parser.add_argument('--no-browser', action='store_true',
                       help="Don't open browser automatically")
    
    args = parser.parse_args()
    
    main(
        auto_open=not args.no_browser,
        backend_port=args.backend_port,
        frontend_port=args.frontend_port
    )