from fastmcp import FastMCP
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel
from typing import Optional

app = FastMCP("web-tool-mcp-server")

class WebPageResponse(BaseModel):
    """Response model for web page content"""
    title: str
    content: str
    url: str
    status: str

class SearchResponse(BaseModel):
    """Response model for search results"""
    search_term: str
    url: str
    matches: list[str]
    total_matches: int
    status: str

@app.tool()
def get_web_page(url: str) -> WebPageResponse:
    """
    Get the content of a web page
    
    Args:
        url: The URL of the web page to fetch
        
    Returns:
        WebPageResponse: Contains title, content, URL and status
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
        
        return WebPageResponse(
            title=title,
            content=text_content[:2000] + "..." if len(text_content) > 2000 else text_content,
            url=url,
            status="success"
        )
        
    except requests.RequestException as e:
        return WebPageResponse(
            title="Error",
            content=f"Error fetching {url}: {str(e)}",
            url=url,
            status="error"
        )
    except Exception as e:
        return WebPageResponse(
            title="Error",
            content=f"Unexpected error: {str(e)}",
            url=url,
            status="error"
        )

@app.tool()
def search_web_content(url: str, search_term: str) -> SearchResponse:
    """
    Search for specific content within a web page
    
    Args:
        url: The URL of the web page to search
        search_term: The term to search for
        
    Returns:
        SearchResponse: Contains search results with context
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
        
        return SearchResponse(
            search_term=search_term,
            url=url,
            matches=matching_lines[:10],  # Limit results
            total_matches=len(matching_lines),
            status="success"
        )
            
    except requests.RequestException as e:
        return SearchResponse(
            search_term=search_term,
            url=url,
            matches=[f"Error fetching {url}: {str(e)}"],
            total_matches=0,
            status="error"
        )
    except Exception as e:
        return SearchResponse(
            search_term=search_term,
            url=url,
            matches=[f"Unexpected error: {str(e)}"],
            total_matches=0,
            status="error"
        )

def main():
    """Main function for running the MCP server"""
    app.run()

if __name__ == "__main__":
    main()