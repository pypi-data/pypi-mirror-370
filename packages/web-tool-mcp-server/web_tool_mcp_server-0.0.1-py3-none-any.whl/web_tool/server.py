from fastmcp import FastMCP
import requests
from bs4 import BeautifulSoup
import json
import sys

app = FastMCP("web-tool-mcp-server")

@app.tool()
def get_web_page(url: str) -> str:
    """
    Get the content of a web page
    
    Args:
        url: The URL of the web page to fetch
        
    Returns:
        The content of the web page
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract text content
        text_content = soup.get_text(separator='\n', strip=True)
        
        # Get title
        title = soup.title.string if soup.title else "No title"
        
        return f"Title: {title}\n\nContent:\n{text_content[:1000]}..."  # Limit content length
        
    except requests.RequestException as e:
        return f"Error fetching {url}: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

@app.tool()
def search_web_content(url: str, search_term: str) -> str:
    """
    Search for specific content within a web page
    
    Args:
        url: The URL of the web page to search
        search_term: The term to search for
        
    Returns:
        Search results with context
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        text_content = soup.get_text(separator='\n', strip=True)
        
        # Simple search implementation
        lines = text_content.split('\n')
        matching_lines = []
        
        for i, line in enumerate(lines):
            if search_term.lower() in line.lower():
                # Get context (previous and next lines)
                start = max(0, i - 2)
                end = min(len(lines), i + 3)
                context = '\n'.join(lines[start:end])
                matching_lines.append(f"Line {i+1}: {context}")
        
        if matching_lines:
            return f"Found {len(matching_lines)} matches for '{search_term}':\n\n" + '\n\n'.join(matching_lines[:5])  # Limit results
        else:
            return f"No matches found for '{search_term}' in {url}"
            
    except requests.RequestException as e:
        return f"Error fetching {url}: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

def main():
    """Main function for running the MCP server"""
    app.run()

if __name__ == "__main__":
    main()