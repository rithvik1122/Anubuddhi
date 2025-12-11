#!/usr/bin/env python3
"""
Script to inspect the actual HTML structure of the Streamlit app
"""

import requests
from bs4 import BeautifulSoup
import time

def inspect_streamlit_html():
    """Fetch and parse the Streamlit app HTML"""
    
    # Give Streamlit a moment to fully load
    print("Fetching HTML from http://localhost:8501...")
    
    try:
        # Fetch the page
        response = requests.get('http://localhost:8501', timeout=5)
        
        if response.status_code != 200:
            print(f"Error: Got status code {response.status_code}")
            return
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        print("\n" + "="*80)
        print("STREAMLIT APP STRUCTURE")
        print("="*80)
        
        # Find the main app container
        app = soup.find('div', class_='stApp')
        if app:
            print(f"\n✓ Found .stApp container")
            print(f"  Classes: {app.get('class')}")
            print(f"  Style: {app.get('style', 'none')}")
        
        # Find the block container
        block = soup.find('div', class_='block-container')
        if block:
            print(f"\n✓ Found .block-container")
            print(f"  Classes: {block.get('class')}")
        
        # Find columns
        columns = soup.find_all('div', attrs={'data-testid': 'column'})
        print(f"\n✓ Found {len(columns)} columns")
        
        for idx, col in enumerate(columns, 1):
            print(f"\n{'='*60}")
            print(f"COLUMN {idx}")
            print(f"{'='*60}")
            print(f"Classes: {col.get('class')}")
            print(f"Style: {col.get('style', 'none')}")
            
            # Get all direct children
            children = col.find_all(recursive=False)
            print(f"\nDirect children: {len(children)}")
            
            for child_idx, child in enumerate(children):
                print(f"\n  [{child_idx}] {child.name.upper()}")
                print(f"      Classes: {child.get('class', ['none'])}")
                print(f"      ID: {child.get('id', 'none')}")
                
                # Check for data-testid
                testid = child.get('data-testid')
                if testid:
                    print(f"      data-testid: {testid}")
                
                # Show inline styles if present
                style = child.get('style')
                if style:
                    print(f"      Inline style: {style[:100]}...")
                
                # Count nested children
                nested = len(child.find_all())
                print(f"      Nested elements: {nested}")
        
        # Find the chat input container
        print(f"\n{'='*60}")
        print("CHAT INPUT CONTAINER")
        print(f"{'='*60}")
        
        chat_input = soup.find('div', class_='chat-input-container')
        if chat_input:
            print("✓ Found .chat-input-container")
            print(f"  Classes: {chat_input.get('class')}")
            print(f"  Style: {chat_input.get('style', 'none')}")
        else:
            print("✗ .chat-input-container NOT FOUND!")
        
        # Check for any element with large heights in inline styles
        print(f"\n{'='*60}")
        print("ELEMENTS WITH INLINE HEIGHT/MARGIN STYLES")
        print(f"{'='*60}")
        
        elements_with_styles = soup.find_all(style=True)
        for elem in elements_with_styles[:20]:  # First 20
            style = elem.get('style', '')
            if 'height' in style.lower() or 'margin' in style.lower():
                print(f"\n{elem.name.upper()} - {elem.get('class', ['no-class'])}")
                print(f"  Style: {style}")
        
        # Save full HTML for inspection
        with open('/home/rithvik/nvme_data2/AgenticQuantum/Agentic/streamlit_page.html', 'w') as f:
            f.write(soup.prettify())
        
        print(f"\n{'='*80}")
        print("✓ Full HTML saved to: streamlit_page.html")
        print("="*80)
        
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to http://localhost:8501")
        print("Make sure Streamlit is running: streamlit run app.py")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    inspect_streamlit_html()
