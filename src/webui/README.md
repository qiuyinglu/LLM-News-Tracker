# LLM News Thread Web UI

A web interface for viewing and filtering paginated news threads analyzed by LLM models.

## Features

- **Paginated Thread Listing**: View threads with 25 items per page by default
- **Status Filtering**: Filter threads by their current status (started, evolving, stale, likely resolved)
- **Sorting Options**: Sort by creation date or update date in ascending/descending order
- **Thread Details**: Each thread shows:
  - LLM-generated title and summary
  - Related news articles with numbered links and hover tooltips
  - Thread metadata (category, country, language, status)
  - Creation and update timestamps
- **Responsive Design**: Works on desktop and mobile devices
- **AJAX Navigation**: Smooth page transitions without full page reloads

## Prerequisites

1. **Python Dependencies**: Install required packages:
   ```bash
   pip install -r ../../requirements.txt
   ```

2. **Database Setup**: Ensure PostgreSQL is running with the required schema
3. **Environment Variables**: Create a `.env` file in the project root with database configuration:
   ```env
   DB_HOST=localhost
   DB_NAME=news_threads
   DB_USER=postgres
   DB_PASSWORD=your-password
   DB_PORT=5432
   ```

## Running the Web UI

### Option 1: Direct Python execution
```bash
python run.py
```

### Option 2: Using the Flask app directly
```bash
python app.py
```

The web interface will be available at: http://localhost:5000

## API Endpoints

The web UI also provides API endpoints for programmatic access:

- `GET /` - Main web interface
- `GET /api/threads` - JSON API for thread data with query parameters:
  - `page`: Page number (default: 1)
  - `status`: Filter by status (optional)
  - `sort_by`: Sort column - 'created_at' or 'updated_at' (default: 'created_at')
  - `sort_order`: Sort direction - 'asc' or 'desc' (default: 'desc')
- `GET /health` - Health check endpoint

## File Structure

```
webui/
├── app.py              # Flask application
├── run.py              # Startup script
├── templates/
│   └── index.html      # Main HTML template
└── static/
    ├── style.css       # CSS styles
    └── script.js       # JavaScript functionality
```

## Database Schema

The web UI expects the following PostgreSQL tables:

- `Threads`: Main thread information
- `News`: News article details
- `ThreadsToNews`: Many-to-many relationship between threads and news

## Configuration

The web UI uses environment variables for database connection. See the main project's `.env-example` file for all available configuration options.

## Development

For development with auto-reload:
```bash
export FLASK_ENV=development
python app.py
```

## Troubleshooting

1. **Database Connection Issues**: 
   - Verify PostgreSQL is running
   - Check database credentials in `.env` file
   - Ensure database and tables exist

2. **Missing Dependencies**:
   - Run `pip install -r ../../requirements.txt`
   - Check that Flask is installed: `pip show flask`

3. **Port Already in Use**:
   - Change the port in `app.py` or `run.py`
   - Or kill the process using port 5000

## Browser Compatibility

The web UI supports modern browsers with:
- CSS Grid and Flexbox support
- ES6 JavaScript features
- Fetch API for AJAX requests

For older browsers, consider adding polyfills.
