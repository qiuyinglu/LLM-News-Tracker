"""
Flask Web UI for LLM News Thread Viewer
Provides a web interface to view and filter paginated threads.
"""

import os
import math
from flask import Flask, render_template, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'news_threads'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD'),
    'port': os.getenv('DB_PORT', 5432)
}

def get_db_connection():
    """Create and return a database connection."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def get_threads_data(page=1, per_page=25, status_filter=None, sort_by='created_at', sort_order='desc'):
    """
    Fetch threads data with pagination, filtering, and sorting.
    
    Args:
        page (int): Page number (1-indexed)
        per_page (int): Number of threads per page
        status_filter (str): Filter by status (optional)
        sort_by (str): Column to sort by ('created_at' or 'updated_at')
        sort_order (str): Sort order ('asc' or 'desc')
    
    Returns:
        dict: Contains threads data, pagination info, and total count
    """
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Build the WHERE clause
            where_clause = ""
            params = []
            
            if status_filter:
                where_clause = "WHERE t.status = %s"
                params.append(status_filter)
            
            # Build the ORDER BY clause
            valid_sort_columns = ['created_at', 'updated_at']
            valid_sort_orders = ['asc', 'desc']
            
            if sort_by not in valid_sort_columns:
                sort_by = 'created_at'
            if sort_order not in valid_sort_orders:
                sort_order = 'desc'
            
            order_clause = f"ORDER BY t.{sort_by} {sort_order.upper()}"
            
            # Count total threads
            count_query = f"""
                SELECT COUNT(*) as total
                FROM Threads t
                {where_clause}
            """
            cur.execute(count_query, params)
            total_threads = cur.fetchone()['total']
            
            # Calculate pagination
            total_pages = math.ceil(total_threads / per_page)
            offset = (page - 1) * per_page
            
            # Fetch threads with associated news
            threads_query = f"""
                SELECT 
                    t.uuid,
                    t.category,
                    t.country,
                    t.language,
                    t.llm_title,
                    t.llm_summary,
                    t.status,
                    t.created_at,
                    t.updated_at
                FROM Threads t
                {where_clause}
                {order_clause}
                LIMIT %s OFFSET %s
            """
            
            params.extend([per_page, offset])
            cur.execute(threads_query, params)
            threads = cur.fetchall()
            
            # For each thread, fetch associated news
            for thread in threads:
                news_query = """
                    SELECT 
                        n.uuid,
                        n.title,
                        n.url,
                        tn.embedding_cos_similarity,
                        tn.llm_similarity_score
                    FROM ThreadsToNews tn
                    JOIN News n ON tn.news_uuid = n.uuid
                    WHERE tn.thread_uuid = %s
                    ORDER BY tn.llm_similarity_score DESC, tn.embedding_cos_similarity DESC
                """
                cur.execute(news_query, (thread['uuid'],))
                thread['news'] = cur.fetchall()
            
            return {
                'threads': threads,
                'pagination': {
                    'current_page': page,
                    'per_page': per_page,
                    'total_pages': total_pages,
                    'total_threads': total_threads,
                    'has_prev': page > 1,
                    'has_next': page < total_pages,
                    'prev_page': page - 1 if page > 1 else None,
                    'next_page': page + 1 if page < total_pages else None
                }
            }
    
    except Exception as e:
        print(f"Database query error: {e}")
        return None
    finally:
        conn.close()

def get_status_counts():
    """Get count of threads by status for filter dropdown."""
    conn = get_db_connection()
    if not conn:
        return {}
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT status, COUNT(*) as count
                FROM Threads
                GROUP BY status
                ORDER BY status
            """)
            results = cur.fetchall()
            return {row['status']: row['count'] for row in results}
    
    except Exception as e:
        print(f"Database query error: {e}")
        return {}
    finally:
        conn.close()

@app.route('/')
def index():
    """Main page displaying threads."""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', None)
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')
    
    # Get threads data
    data = get_threads_data(
        page=page,
        status_filter=status_filter,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    if not data:
        return "Database connection error", 500
    
    # Get status counts for filter dropdown
    status_counts = get_status_counts()
    
    return render_template(
        'index.html',
        threads=data['threads'],
        pagination=data['pagination'],
        status_counts=status_counts,
        current_status_filter=status_filter,
        current_sort_by=sort_by,
        current_sort_order=sort_order
    )

@app.route('/api/threads')
def api_threads():
    """API endpoint for threads data (for AJAX requests)."""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', None)
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')
    
    data = get_threads_data(
        page=page,
        status_filter=status_filter,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    if not data:
        return jsonify({'error': 'Database connection error'}), 500
    
    return jsonify(data)

@app.route('/health')
def health():
    """Health check endpoint."""
    conn = get_db_connection()
    if conn:
        conn.close()
        return jsonify({'status': 'healthy', 'database': 'connected'})
    else:
        return jsonify({'status': 'unhealthy', 'database': 'disconnected'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
