
#!/usr/bin/env python3
import os
import glob
from http.server import HTTPServer, SimpleHTTPRequestHandler
import webbrowser

def list_zip_files():
    """List all ZIP files in the current directory"""
    zip_files = glob.glob("*.zip")
    if not zip_files:
        print("No ZIP files found in the current directory.")
        return []
    
    print("Available ZIP files:")
    for i, file in enumerate(zip_files, 1):
        size = os.path.getsize(file) / (1024 * 1024)  # Size in MB
        print(f"{i}. {file} ({size:.2f} MB)")
    
    return zip_files

def serve_files():
    """Start a simple HTTP server to serve files"""
    port = 8000
    
    class CustomHandler(SimpleHTTPRequestHandler):
        def end_headers(self):
            self.send_header('Access-Control-Allow-Origin', '*')
            super().end_headers()
    
    try:
        with HTTPServer(("0.0.0.0", port), CustomHandler) as httpd:
            print(f"\nServing files at http://0.0.0.0:{port}")
            print("You can now download your ZIP files by clicking the links above.")
            print("Press Ctrl+C to stop the server.")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")

if __name__ == "__main__":
    zip_files = list_zip_files()
    if zip_files:
        print(f"\nStarting file server...")
        serve_files()
