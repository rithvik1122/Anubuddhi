#!/usr/bin/env python3
"""
Use Selenium to inspect the fully rendered Streamlit app
"""

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    import time
    
    print("Setting up headless browser...")
    
    # Setup Chrome in headless mode
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    print("Loading Streamlit app...")
    driver.get('http://localhost:8501')
    
    # Wait for Streamlit to fully load
    time.sleep(3)
    
    print("\n" + "="*80)
    print("ANALYZING RENDERED DOM")
    print("="*80)
    
    # Find columns
    columns = driver.find_elements(By.CSS_SELECTOR, '[data-testid="column"]')
    print(f"\n✓ Found {len(columns)} columns")
    
    for idx, col in enumerate(columns, 1):
        print(f"\n{'='*70}")
        print(f"COLUMN {idx}")
        print(f"{'='*70}")
        
        # Get computed styles
        size = col.size
        location = col.location
        
        print(f"Position: x={location['x']}, y={location['y']}")
        print(f"Size: width={size['width']}, height={size['height']}")
        
        # Get all direct children
        children = col.find_elements(By.XPATH, './*')
        print(f"\nDirect children: {len(children)}")
        
        for child_idx, child in enumerate(children):
            tag = child.tag_name
            classes = child.get_attribute('class') or 'none'
            test_id = child.get_attribute('data-testid') or ''
            
            # Get computed style
            height = driver.execute_script("return window.getComputedStyle(arguments[0]).height", child)
            margin_top = driver.execute_script("return window.getComputedStyle(arguments[0]).marginTop", child)
            margin_bottom = driver.execute_script("return window.getComputedStyle(arguments[0]).marginBottom", child)
            padding_top = driver.execute_script("return window.getComputedStyle(arguments[0]).paddingTop", child)
            display = driver.execute_script("return window.getComputedStyle(arguments[0]).display", child)
            
            print(f"\n  [{child_idx}] {tag.upper()}")
            if test_id:
                print(f"      data-testid: {test_id}")
            print(f"      Classes: {classes[:60]}")
            print(f"      HEIGHT: {height}")
            print(f"      MARGIN-TOP: {margin_top} ⚠️" if margin_top != '0px' else f"      MARGIN-TOP: {margin_top}")
            print(f"      MARGIN-BOTTOM: {margin_bottom}")
            print(f"      PADDING-TOP: {padding_top}")
            print(f"      DISPLAY: {display}")
    
    # Check chat input
    print(f"\n{'='*70}")
    print("CHAT INPUT CONTAINER")
    print(f"{'='*70}")
    
    try:
        chat_input = driver.find_element(By.CLASS_NAME, 'chat-input-container')
        rect = driver.execute_script("""
            const elem = arguments[0];
            const rect = elem.getBoundingClientRect();
            return {
                top: rect.top,
                bottom: rect.bottom,
                left: rect.left,
                right: rect.right,
                width: rect.width,
                height: rect.height
            };
        """, chat_input)
        
        viewport_height = driver.execute_script("return window.innerHeight")
        
        print(f"✓ Found chat input")
        print(f"  Position: top={rect['top']:.0f}px, bottom={rect['bottom']:.0f}px")
        print(f"  Size: {rect['width']:.0f}px × {rect['height']:.0f}px")
        print(f"  Viewport height: {viewport_height}px")
        
        if rect['top'] >= viewport_height:
            print(f"  ⚠️  INPUT IS BELOW VIEWPORT! Need to scroll {rect['top'] - viewport_height:.0f}px down")
        else:
            print(f"  ✓ Input is visible (starts {viewport_height - rect['top']:.0f}px from bottom)")
            
    except Exception as e:
        print(f"✗ Chat input not found: {e}")
    
    # Save page source
    with open('/home/rithvik/nvme_data2/AgenticQuantum/Agentic/streamlit_rendered.html', 'w') as f:
        f.write(driver.page_source)
    
    print(f"\n{'='*80}")
    print("✓ Full rendered HTML saved to: streamlit_rendered.html")
    print("="*80)
    
    driver.quit()
    
except ImportError:
    print("ERROR: Selenium not installed")
    print("Install with: pip install selenium")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
