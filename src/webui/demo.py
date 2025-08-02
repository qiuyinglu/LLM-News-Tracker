"""
Demo script to show the Web UI functionality

This script demonstrates the key features of the LLM News Thread Web UI.
It can be used for testing and showcasing the application.
"""

import os
import sys
import webbrowser
import time
from threading import Thread

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from webui.app import app

def demo_browser_launch():
    """Launch browser after a short delay to allow server to start."""
    time.sleep(2)  # Wait for server to start
    print("Opening web browser...")
    webbrowser.open('http://localhost:5000')

def print_demo_info():
    """Print information about the demo."""
    print("=" * 60)
    print("LLM News Thread Web UI Demo")
    print("=" * 60)
    print()
    print("Features demonstrated:")
    print("✓ Paginated thread listing (25 threads per page)")
    print("✓ Status filtering (started, evolving, stale, likely resolved)")
    print("✓ Sorting by creation date or update date")
    print("✓ Thread details with LLM-generated titles and summaries")
    print("✓ Related news articles with hover tooltips")
    print("✓ Responsive design for desktop and mobile")
    print("✓ AJAX navigation for smooth page transitions")
    print()
    print("Navigation tips:")
    print("• Use the filter dropdowns to filter by status and sort options")
    print("• Click numbered news links to view original articles")
    print("• Hover over news numbers to see article titles and similarity scores")
    print("• Use pagination controls or keyboard arrows to navigate pages")
    print("• The interface automatically adapts to your screen size")
    print()
    print("API Endpoints available:")
    print("• GET /              - Main web interface")
    print("• GET /api/threads   - JSON API for thread data")
    print("• GET /health        - Application health check")
    print()
    print("Database requirements:")
    print("• PostgreSQL with threads, news, and threadstonews tables")
    print("• Configure database connection in .env file")
    print()
    print("=" * 60)
    print("Starting Flask development server...")
    print("Access the demo at: http://localhost:5000")
    print("Press Ctrl+C to stop the demo")
    print("=" * 60)
    print()

def run_demo():
    """Run the demo with automatic browser launch."""
    print_demo_info()
    
    # Start browser in a separate thread
    browser_thread = Thread(target=demo_browser_launch)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start the Flask app
    try:
        app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
    except KeyboardInterrupt:
        print("\n\nDemo stopped by user")
        print("Thank you for trying the LLM News Thread Web UI!")
    except Exception as e:
        print(f"\nError running demo: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure PostgreSQL is running and accessible")
        print("2. Check that .env file has correct database configuration")
        print("3. Verify all required Python packages are installed")
        print("4. Make sure port 5000 is not in use by another application")

if __name__ == '__main__':
    run_demo()
