"""
Test the complete LLM designer with web search
"""

import sys
sys.path.append('/home/rithvik/nvme_data2/AgenticQuantum/Agentic')

from simple_llm import SimpleLLM
from llm_designer import LLMDesigner

# Import web search from app
from app import web_search_wrapper

def test_designer_with_search():
    """Test the designer with web search enabled."""
    
    print("="*70)
    print("Testing LLM Designer with Web Search")
    print("="*70)
    
    # Initialize LLM and designer
    llm = SimpleLLM(model="anthropic/claude-3.5-sonnet")
    designer = LLMDesigner(llm_client=llm, web_search_tool=web_search_wrapper)
    
    # Test with a query that should trigger web search
    query = "Design a Hong-Ou-Mandel interference experiment with typical parameters used in recent research"
    
    print(f"\n📝 Query: {query}\n")
    
    try:
        result = designer.design_experiment(query)
        
        print("\n" + "="*70)
        print("RESULTS:")
        print("="*70)
        print(f"✅ Title: {result.title}")
        print(f"✅ Description: {result.description}")
        print(f"✅ Components: {len(result.components)}")
        print(f"✅ Web Search Used: {result.web_search_used}")
        
        if result.web_search_used:
            print(f"\n🔍 Web Search Context:")
            print("-" * 70)
            print(result.web_search_context[:500] + "...")
        
        print(f"\n📋 Component List:")
        for i, comp in enumerate(result.components, 1):
            print(f"  {i}. {comp.get('name', 'N/A')} ({comp.get('type', 'N/A')})")
        
        if result.component_justifications:
            print(f"\n💡 Component Justifications:")
            for name, reason in result.component_justifications.items():
                print(f"  • {name}: {reason[:100]}...")
        
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_designer_with_search()
