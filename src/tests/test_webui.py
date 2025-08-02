"""
Test script for the Web UI
Tests basic functionality of the Flask application
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from webui.app import app, get_db_connection, get_threads_data, get_status_counts

class TestWebUI(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Clean up after tests."""
        self.app_context.pop()
    
    def test_app_exists(self):
        """Test that the Flask app exists."""
        self.assertIsNotNone(app)
    
    def test_app_is_testing(self):
        """Test that the app is in testing mode."""
        self.assertTrue(app.config['TESTING'])
    
    @patch('webui.app.get_db_connection')
    def test_health_endpoint_healthy(self, mock_get_db):
        """Test health endpoint when database is available."""
        # Mock successful database connection
        mock_conn = MagicMock()
        mock_get_db.return_value = mock_conn
        
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['database'], 'connected')
        
        # Verify connection was closed
        mock_conn.close.assert_called_once()
    
    @patch('webui.app.get_db_connection')
    def test_health_endpoint_unhealthy(self, mock_get_db):
        """Test health endpoint when database is unavailable."""
        # Mock failed database connection
        mock_get_db.return_value = None
        
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 500)
        
        data = response.get_json()
        self.assertEqual(data['status'], 'unhealthy')
        self.assertEqual(data['database'], 'disconnected')
    
    @patch('webui.app.get_threads_data')
    @patch('webui.app.get_status_counts')
    def test_index_route(self, mock_status_counts, mock_threads_data):
        """Test the main index route."""
        # Mock return data
        mock_threads_data.return_value = {
            'threads': [],
            'pagination': {
                'current_page': 1,
                'per_page': 25,
                'total_pages': 1,
                'total_threads': 0,
                'has_prev': False,
                'has_next': False,
                'prev_page': None,
                'next_page': None
            }
        }
        mock_status_counts.return_value = {'started': 5, 'evolving': 3}
        
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        # Check that functions were called
        mock_threads_data.assert_called_once()
        mock_status_counts.assert_called_once()
    
    @patch('webui.app.get_threads_data')
    def test_api_threads_route(self, mock_threads_data):
        """Test the API threads route."""
        # Mock return data
        mock_threads_data.return_value = {
            'threads': [],
            'pagination': {'current_page': 1, 'total_pages': 1}
        }
        
        response = self.client.get('/api/threads')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIn('threads', data)
        self.assertIn('pagination', data)
    
    @patch('webui.app.get_threads_data')
    def test_api_threads_with_parameters(self, mock_threads_data):
        """Test the API threads route with query parameters."""
        mock_threads_data.return_value = {
            'threads': [],
            'pagination': {'current_page': 2, 'total_pages': 5}
        }
        
        response = self.client.get('/api/threads?page=2&status=started&sort_by=updated_at&sort_order=asc')
        self.assertEqual(response.status_code, 200)
        
        # Check that the function was called with correct parameters
        mock_threads_data.assert_called_once_with(
            page=2,
            status_filter='started',
            sort_by='updated_at',
            sort_order='asc'
        )
    
    @patch('webui.app.get_threads_data')
    def test_api_threads_database_error(self, mock_threads_data):
        """Test API threads route when database error occurs."""
        mock_threads_data.return_value = None
        
        response = self.client.get('/api/threads')
        self.assertEqual(response.status_code, 500)
        
        data = response.get_json()
        self.assertIn('error', data)

if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
