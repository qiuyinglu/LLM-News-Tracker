import os
import time
import requests
import psycopg2
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dotenv import load_dotenv
from llm_clients import get_llm_client
from prompts import SUMMARIZE_NEWS, SIMILARITY_SCORE, UPDATE_THREAD_SUMMARY

# Load environment variables
load_dotenv()


def is_debug_mode() -> bool:
    """Check if debug mode is enabled from environment variable."""
    debug_env = os.getenv('DEBUG_MODE', 'false').lower()
    return debug_env in ['true', '1', 'yes', 'on']


def debug_print(message: str) -> None:
    """Print debug message only if debug mode is enabled."""
    if is_debug_mode():
        print(message)


def clean_json_response(response_text: str) -> str:
    """Clean up LLM JSON response to handle common formatting issues."""
    if not response_text:
        return response_text
    
    # Remove any leading/trailing whitespace
    cleaned = response_text.strip()
    
    # Try to extract JSON from markdown code blocks if present
    if cleaned.startswith('```json'):
        cleaned = cleaned[7:]
    elif cleaned.startswith('```'):
        cleaned = cleaned[3:]
    
    if cleaned.endswith('```'):
        cleaned = cleaned[:-3]
    
    cleaned = cleaned.strip()
    
    # Fix common JSON formatting issues
    try:
        # First try to parse as-is
        json.loads(cleaned)
        return cleaned
    except json.JSONDecodeError:
        # Try to fix common issues
        
        # Fix multi-line strings by replacing actual newlines with \n
        # This handles the case where LLM puts actual line breaks in JSON strings
        lines = cleaned.split('\n')
        in_string = False
        quote_char = None
        fixed_lines = []
        current_line = ""
        
        for line in lines:
            i = 0
            while i < len(line):
                char = line[i]
                
                if not in_string:
                    if char in ['"', "'"]:
                        in_string = True
                        quote_char = char
                    current_line += char
                else:
                    if char == quote_char and (i == 0 or line[i-1] != '\\'):
                        in_string = False
                        quote_char = None
                    current_line += char
                
                i += 1
            
            if not in_string:
                # We're not inside a string, so this line should end
                fixed_lines.append(current_line)
                current_line = ""
            else:
                # We're inside a string, so add escaped newline and continue
                current_line += "\\n"
        
        if current_line:
            fixed_lines.append(current_line)
        
        cleaned = '\n'.join(fixed_lines)
        
        # Try parsing again
        try:
            json.loads(cleaned)
            return cleaned
        except json.JSONDecodeError:
            # If still failing, try more aggressive fixes
            
            # Remove extra commas before closing braces/brackets
            cleaned = re.sub(r',(\s*[}\]])', r'\1', cleaned)
            
            # Try to fix unescaped quotes in strings (basic attempt)
            # This is a simple heuristic and may not work in all cases
            cleaned = re.sub(r'(?<!\\)"(?=[^,}\]]*[,}\]])', r'\\"', cleaned)
            
            return cleaned
    
    return cleaned


def parse_llm_json_response(response_text: str, required_fields: List[str]) -> Dict[str, Any]:
    """Parse LLM JSON response with error handling and validation."""
    cleaned_response = clean_json_response(response_text)
    
    try:
        result = json.loads(cleaned_response)
        
        # Validate required fields
        missing_fields = [field for field in required_fields if field not in result]
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")
        
        return result
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}. Cleaned response: '{cleaned_response[:200]}...'")


def fetch_news() -> List[Dict[str, Any]]:
    """
    Fetch news from GNews API based on configured categories.
    
    Returns:
        List[Dict[str, Any]]: List of news dictionaries with standardized properties
    """
    # Get configuration from environment variables
    api_key = os.getenv('GNEWS_API_KEY')
    categories = os.getenv('GNEWS_CATEGORIES', 'world,nation,business,technology,science').split(',')
    lang = os.getenv('GNEWS_LANG', 'en')
    country = os.getenv('GNEWS_COUNTRY', 'us')
    max_per_page = int(os.getenv('GNEWS_MAX_PER_PAGE', '25'))
    max_news_per_category = int(os.getenv('GNEWS_MAX_NEWS_PER_CATEGORY', '200'))
    
    if not api_key:
        raise ValueError("GNEWS_API_KEY is required but not set in environment variables")
    
    # Create HTTP client session for connection reuse
    session = requests.Session()
    
    # Initialize list to store all fetched news
    fetched_news = []
    
    # Track URLs to avoid duplicates
    seen_urls = set()
    
    # Process each category
    for category in categories:
        category = category.strip()  # Remove any whitespace
        print(f"Fetching news for category: {category}")
        
        category_news_count = 0
        page = 1
        
        while category_news_count < max_news_per_category:
            try:
                # Prepare API request parameters
                params = {
                    'category': category,
                    'apikey': api_key,
                    'lang': lang,
                    'country': country,
                    'max': max_per_page,
                    'page': page,
                    'expand': 'content'
                }
                
                # Make API request
                response = session.get('https://gnews.io/api/v4/top-headlines', params=params)
                response.raise_for_status()
                
                data = response.json()
                
                # Check if we have articles in the response
                if 'articles' not in data or not data['articles']:
                    print(f"No more articles found for category {category} on page {page}")
                    break
                
                articles = data['articles']
                new_articles_added = 0
                
                # Process each article
                for article in articles:
                    # Check for duplicates by URL
                    article_url = article.get('url', '')
                    if article_url in seen_urls or not article_url:
                        continue
                    
                    # Extract source information
                    source = article.get('source', {})
                    source_name = source.get('name', '') if source else ''
                    source_url = source.get('url', '') if source else ''
                    
                    # Create standardized news dictionary
                    news_item = {
                        'title': article.get('title', ''),
                        'description': article.get('description', ''),
                        'content': article.get('content', ''),
                        'url': article_url,
                        'image': article.get('image', ''),
                        'publishedAt': article.get('publishedAt', ''),
                        'source_name': source_name,
                        'source_url': source_url
                    }
                    
                    # Add to our collections
                    fetched_news.append(news_item)
                    seen_urls.add(article_url)
                    category_news_count += 1
                    new_articles_added += 1
                    
                    # Check if we've reached the limit for this category
                    if category_news_count >= max_news_per_category:
                        break
                
                print(f"Page {page}: Added {new_articles_added} new articles for {category} "
                      f"(total: {category_news_count}/{max_news_per_category})")
                
                # If no new articles were added, break the pagination loop
                if new_articles_added == 0:
                    print(f"No new articles found on page {page} for category {category}")
                    break
                
                # Move to next page
                page += 1
                
                # Sleep to avoid API rate limiting
                time.sleep(1)
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching news for category {category}, page {page}: {e}")
                break
            except ValueError as e:
                print(f"Error parsing response for category {category}, page {page}: {e}")
                break
    
    # Close the session
    session.close()
    
    print(f"Total news articles fetched: {len(fetched_news)}")
    return fetched_news


def get_db_connection():
    """Get a database connection using environment variables."""
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'news_threads'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', ''),
        port=os.getenv('DB_PORT', '5432')
    )


def get_llm_summary(title: str, description: str, content: str) -> Tuple[str, bool, str]:
    """Get LLM summary for news content."""
    client = get_llm_client()
    
    prompt = SUMMARIZE_NEWS.format(
        title=title,
        description=description,
        content=content
    )
    
    return client.get_chat_completion(prompt, temperature=0.3)


def get_embedding(text: str) -> Tuple[Optional[List[float]], bool, str]:
    """Get embedding for text using configured LLM provider."""
    client = get_llm_client()
    return client.get_embedding(text)


def get_similarity_score(news_item: Dict[str, Any], thread_item: Dict[str, Any]) -> Tuple[Dict[str, Any], bool, str]:
    """Get similarity score and justification from LLM."""
    client = get_llm_client()
    max_retries = int(os.getenv('LLM_MAX_RETRY_ATTEMPTS', '3'))
    
    prompt = SIMILARITY_SCORE.format(
        news_title=news_item.get('title', ''),
        news_description=news_item.get('description', ''),
        news_content=news_item.get('content', ''),
        thread_title=thread_item.get('llm_title', ''),
        thread_summary=thread_item.get('llm_summary', '')
    )
    
    for attempt in range(max_retries):
        try:
            response_text, is_blocked, block_reason = client.get_chat_completion(prompt, temperature=0.1)
            
            if is_blocked:
                print(f"LLM response blocked in get_similarity_score: {block_reason}")
                return {}, True, block_reason
            
            if not response_text.strip():
                raise ValueError("Empty response from LLM")
            
            # Use the robust JSON parser
            required_fields = ['llm_similarity_score', 'llm_similarity_justification']
            result = parse_llm_json_response(response_text, required_fields)
            
            return result, False, ""
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error in get_similarity_score attempt {attempt + 1}/{max_retries}: {e}")
            debug_print(f"Raw LLM response from get_similarity_score (attempt {attempt + 1}): '{response_text[:2000]}...'" if len(response_text) > 2000 else f"Raw LLM response from get_similarity_score (attempt {attempt + 1}): '{response_text}'")
            if attempt == max_retries - 1:  # Last attempt
                raise Exception(f"Failed to get valid JSON response after {max_retries} attempts: {e}. Last response: '{response_text}'" if 'response_text' in locals() else f"Failed to get valid JSON response after {max_retries} attempts: {e}")
            continue
    

def update_thread_summary(news_item: Dict[str, Any], thread_item: Dict[str, Any]) -> Tuple[Dict[str, Any], bool, str]:
    """Get updated thread summary from LLM."""
    client = get_llm_client()
    max_retries = int(os.getenv('LLM_MAX_RETRY_ATTEMPTS', '3'))
    
    prompt = UPDATE_THREAD_SUMMARY.format(
        news_title=news_item.get('title', ''),
        news_description=news_item.get('description', ''),
        news_content=news_item.get('content', ''),
        thread_title=thread_item.get('llm_title', ''),
        thread_summary=thread_item.get('llm_summary', '')
    )
    
    for attempt in range(max_retries):
        try:
            response_text, is_blocked, block_reason = client.get_chat_completion(prompt, temperature=0.3)
            
            if is_blocked:
                print(f"LLM response blocked in update_thread_summary: {block_reason}")
                return {}, True, block_reason
            
            if not response_text.strip():
                raise ValueError("Empty response from LLM")
            
            # Use the robust JSON parser
            required_fields = ['llm_title', 'llm_summary', 'status']
            result = parse_llm_json_response(response_text, required_fields)
            
            return result, False, ""
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error in update_thread_summary attempt {attempt + 1}/{max_retries}: {e}")
            debug_print(f"Raw LLM response from update_thread_summary (attempt {attempt + 1}): '{response_text[:2000]}...'" if len(response_text) > 2000 else f"Raw LLM response from update_thread_summary (attempt {attempt + 1}): '{response_text}'")
            if attempt == max_retries - 1:  # Last attempt
                raise Exception(f"Failed to get valid JSON response after {max_retries} attempts: {e}. Last response: '{response_text}'" if 'response_text' in locals() else f"Failed to get valid JSON response after {max_retries} attempts: {e}")
            continue


def process_and_save_news(news_item: Dict[str, Any], category: str, language: str, country: str) -> Optional[Dict[str, Any]]:
    """
    Process and save news. Returns None if news already exists, or returns the updated news_item object if it is new.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if news already exists
        cursor.execute("SELECT uuid FROM News WHERE url = %s", (news_item['url'],))
        if cursor.fetchone():
            return None
        
        # Get LLM summary
        llm_summary, summary_blocked, summary_block_reason = get_llm_summary(
            news_item.get('title', ''),
            news_item.get('description', ''),
            news_item.get('content', '')
        )
        
        # Get embedding - only if summary wasn't blocked
        llm_embedding = None
        embedding_blocked = False
        embedding_block_reason = ""
        
        if not summary_blocked and llm_summary:
            embedding_text = f"{news_item.get('title', '')} {news_item.get('description', '')} {news_item.get('content', '')}"
            llm_embedding, embedding_blocked, embedding_block_reason = get_embedding(embedding_text)
        
        # Handle the case where embedding is blocked or summary is blocked
        final_blocked = summary_blocked or embedding_blocked
        final_block_reason = summary_block_reason if summary_blocked else embedding_block_reason
        
        # If embedding is None due to blocking, we need to provide a default embedding for database storage
        if llm_embedding is None:
            # Create a zero vector for database storage when blocked
            llm_embedding = [0.0] * 3072
        
        # Update news_item with new properties
        news_item.update({
            'category': category,
            'language': language,
            'country': country,
            'llm_summary': llm_summary if not summary_blocked else "",
            'llm_embedding': llm_embedding,
            'llm_blocked': final_blocked,
            'llm_blocked_reason': final_block_reason
        })
        
        # Convert publishedAt to proper timestamp format
        published_at = news_item.get('publishedAt', datetime.now().isoformat())
        if isinstance(published_at, str):
            try:
                published_at = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            except:
                published_at = datetime.now()
        
        # Convert embedding to string format for pgvector
        embedding_str = str(llm_embedding).replace(' ', '')
        
        # Insert into database
        insert_query = """
        INSERT INTO News (category, country, language, title, description, content, url, image, 
                         published_at, source_name, source_url, llm_summary, llm_embedding,
                         llm_blocked, llm_blocked_reason)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING uuid
        """
        
        cursor.execute(insert_query, (
            category,
            country,
            language,
            news_item.get('title', ''),
            news_item.get('description', ''),
            news_item.get('content', ''),
            news_item['url'],
            news_item.get('image', ''),
            published_at,
            news_item.get('source_name', ''),
            news_item.get('source_url', ''),
            news_item.get('llm_summary', ''),
            embedding_str,
            final_blocked,
            final_block_reason
        ))
        
        # Get the generated UUID
        news_uuid = cursor.fetchone()[0]
        news_item['uuid'] = str(news_uuid)
        
        conn.commit()
        return news_item
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def find_relevant_thread_and_save(news_item: Optional[Dict[str, Any]], category: str, language: str, country: str) -> None:
    """
    Find relevant thread(s) for the news or create a new thread if none found.
    Save the thread(s) and news-to-thread mapping(s) to the database.
    """
    if news_item is None:
        return
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cos_similarity_threshold = float(os.getenv('COS_SIMILARITY_THRESHOLD', '0.7'))
        llm_similarity_threshold = int(os.getenv('LLM_SIMILARITY_THRESHOLD', '70'))
        
        # Convert embedding to string format for pgvector
        embedding_str = str(news_item['llm_embedding']).replace(' ', '')
        
        # Search for relevant threads using cosine similarity
        search_query = """
        SELECT uuid, category, country, language, llm_title, llm_summary, llm_embedding, status, created_at, updated_at,
               1 - (llm_embedding <=> %s) AS cosine_similarity
        FROM Threads
        WHERE category = %s AND country = %s AND language = %s
        AND 1 - (llm_embedding <=> %s) >= %s
        ORDER BY cosine_similarity DESC
        LIMIT 10
        """
        
        cursor.execute(search_query, (
            embedding_str,
            category,
            country,
            language,
            embedding_str,
            cos_similarity_threshold
        ))
        
        relevant_threads = cursor.fetchall()
        actual_relevant_threads = 0
        
        if relevant_threads:
            # Process each relevant thread
            for thread_row in relevant_threads:
                thread_item = {
                    'uuid': str(thread_row[0]),
                    'category': thread_row[1],
                    'country': thread_row[2],
                    'language': thread_row[3],
                    'llm_title': thread_row[4],
                    'llm_summary': thread_row[5],
                    'llm_embedding': thread_row[6],
                    'status': thread_row[7],
                    'created_at': thread_row[8],
                    'updated_at': thread_row[9]
                }
                cosine_similarity = float(thread_row[10])
                
                # Get LLM similarity score
                similarity_result, similarity_blocked, similarity_block_reason = get_similarity_score(news_item, thread_item)
                
                # If similarity check is blocked, skip this thread
                if similarity_blocked:
                    print(f"Similarity check blocked for thread {thread_item['uuid']}: {similarity_block_reason}")
                    continue
                
                llm_similarity_score = similarity_result['llm_similarity_score']
                llm_similarity_justification = similarity_result['llm_similarity_justification']
                
                # Check LLM similarity threshold
                if llm_similarity_score < llm_similarity_threshold:
                    debug_print(f"Skipping thread {thread_item['uuid']} due to low LLM similarity score: {llm_similarity_score} (threshold: {llm_similarity_threshold}). Cosine similarity: {cosine_similarity} (threshold: {cos_similarity_threshold})")
                    continue
                else:
                    debug_print(f"Thread {thread_item['uuid']} is **relevant** due to high LLM similarity score: {llm_similarity_score} (threshold: {llm_similarity_threshold}). Cosine similarity: {cosine_similarity} (threshold: {cos_similarity_threshold})")
                
                # Update thread with new information
                thread_update, thread_update_blocked, thread_update_block_reason = update_thread_summary(news_item, thread_item)
                
                # Handle blocked thread updates
                thread_blocked = thread_update_blocked
                thread_block_reason = thread_update_block_reason
                
                # Get new embedding for updated thread - only if not blocked
                updated_embedding = None
                embedding_blocked = False
                embedding_block_reason = ""
                
                if not thread_update_blocked and thread_update:
                    updated_embedding_text = f"{thread_update['llm_title']} {thread_update['llm_summary']}"
                    updated_embedding, embedding_blocked, embedding_block_reason = get_embedding(updated_embedding_text)
                    
                    # Update blocking status if embedding is blocked
                    if embedding_blocked:
                        thread_blocked = True
                        thread_block_reason = embedding_block_reason
                
                # If blocked, use original thread info
                if thread_blocked or not thread_update:
                    final_title = thread_item['llm_title']
                    final_summary = thread_item['llm_summary']
                    final_status = thread_item['status']
                    final_embedding = thread_item['llm_embedding']
                else:
                    final_title = thread_update['llm_title']
                    final_summary = thread_update['llm_summary']
                    final_status = thread_update['status']
                    final_embedding = updated_embedding if updated_embedding else thread_item['llm_embedding']
                
                # Convert embedding to string format for pgvector
                if isinstance(final_embedding, list):
                    updated_embedding_str = str(final_embedding).replace(' ', '')
                else:
                    updated_embedding_str = str(final_embedding)
                
                # Update thread in database
                update_thread_query = """
                UPDATE Threads 
                SET llm_title = %s, llm_summary = %s, llm_embedding = %s, status = %s, updated_at = %s,
                    llm_blocked = %s, llm_blocked_reason = %s
                WHERE uuid = %s
                """
                
                cursor.execute(update_thread_query, (
                    final_title,
                    final_summary,
                    updated_embedding_str,
                    final_status,
                    datetime.now(),
                    thread_blocked,
                    thread_block_reason,
                    thread_item['uuid']
                ))
                
                # Insert into ThreadsToNews
                insert_mapping_query = """
                INSERT INTO ThreadsToNews (thread_uuid, news_uuid, embedding_cos_similarity, 
                                         llm_similarity_score, llm_similarity_justification, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(insert_mapping_query, (
                    thread_item['uuid'],
                    news_item['uuid'],
                    cosine_similarity,
                    llm_similarity_score,
                    llm_similarity_justification,
                    datetime.now()
                ))

                actual_relevant_threads += 1
        
        if actual_relevant_threads == 0:
            # Create new thread
            debug_print(f"No relevant threads found for news item {news_item['uuid']}. Creating new thread.")
            published_at = news_item.get('publishedAt', datetime.now().isoformat())
            if isinstance(published_at, str):
                try:
                    published_at = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                except:
                    published_at = datetime.now()
            
            # Convert embedding to string format for pgvector
            embedding_str = str(news_item['llm_embedding']).replace(' ', '')
            
            insert_thread_query = """
            INSERT INTO Threads (category, country, language, llm_title, llm_summary, 
                               llm_embedding, status, created_at, updated_at, llm_blocked, llm_blocked_reason)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING uuid
            """
            
            cursor.execute(insert_thread_query, (
                category,
                country,
                language,
                news_item.get('title', ''),
                news_item.get('llm_summary', ''),
                embedding_str,
                'started',
                published_at,
                published_at,
                news_item.get('llm_blocked', False),
                news_item.get('llm_blocked_reason', '')
            ))
            
            thread_uuid = cursor.fetchone()[0]
            
            # Insert into ThreadsToNews for new thread
            insert_mapping_query = """
            INSERT INTO ThreadsToNews (thread_uuid, news_uuid, embedding_cos_similarity, 
                                     llm_similarity_score, llm_similarity_justification, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(insert_mapping_query, (
                str(thread_uuid),
                news_item['uuid'],
                1.0,  # Perfect similarity for new thread
                101,  # Special score for new thread
                '',   # Empty justification for new thread
                published_at
            ))
        
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def main():
    """
    Main function to fetch news, process through LLM, and save to database.
    """
    try:
        # Print debug mode status
        debug_status = "ENABLED" if is_debug_mode() else "DISABLED"
        print(f"Starting news processing (Debug mode: {debug_status})")
        
        # Get configuration from environment variables
        categories = os.getenv('GNEWS_CATEGORIES', 'world,nation,business,technology,science').split(',')
        lang = os.getenv('GNEWS_LANG', 'en')
        country = os.getenv('GNEWS_COUNTRY', 'us')
        
        # Fetch news articles
        news_articles = fetch_news()
        
        if news_articles:
            print(f"\nSuccessfully fetched {len(news_articles)} news articles")
            
            processed_count = 0
            skipped_count = 0
            
            # Process each article
            for i, article in enumerate(news_articles):
                try:
                    # Determine the category for this article (you might want to implement category detection)
                    # For now, we'll cycle through categories based on article index
                    category = categories[i % len(categories)].strip()
                    
                    print(f"\nProcessing article {i+1}/{len(news_articles)}: {article['title'][:100]}...")
                    
                    # Process and save the news
                    processed_news = process_and_save_news(article, category, lang, country)
                    
                    if processed_news is None:
                        print(f"  Skipped (already exists): {article['url']}")
                        skipped_count += 1
                        continue
                    
                    # Find relevant thread and save
                    find_relevant_thread_and_save(processed_news, category, lang, country)
                    
                    processed_count += 1
                    print(f"  Processed successfully")
                    
                    # Add delay to avoid overwhelming the LLM API
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"  Error processing article: {e}")
                    continue
            
            print(f"\nProcessing complete:")
            print(f"  Processed: {processed_count} articles")
            print(f"  Skipped: {skipped_count} articles")
            
        else:
            print("No news articles were fetched")
            
    except Exception as e:
        print(f"Error in main execution: {e}")


if __name__ == "__main__":
    main()
