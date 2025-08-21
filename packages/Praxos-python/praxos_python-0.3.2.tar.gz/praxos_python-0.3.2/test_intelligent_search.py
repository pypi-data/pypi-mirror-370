"""
Test script to verify intelligent search functionality in the installed SDK
"""

def test_intelligent_search_import():
    """Test that we can import and use the new search methods"""
    try:
        from praxos_python import SyncClient
        
        # Check if the new methods exist
        client = SyncClient(api_key="test_key", base_url="http://localhost")
        
        # Verify search method exists
        assert hasattr(client, 'search'), "search method not found"
        assert hasattr(client, 'intelligent_search'), "intelligent_search method not found"
        
        print("✅ Import successful - intelligent search methods available")
        
        # Check method signatures
        import inspect
        search_sig = inspect.signature(client.search)
        intel_sig = inspect.signature(client.intelligent_search)
        
        print(f"✅ search() method signature: {len(search_sig.parameters)} parameters")
        print(f"✅ intelligent_search() method signature: {len(intel_sig.parameters)} parameters")
        
        # Check that intelligent is default modality
        search_params = search_sig.parameters
        if 'search_modality' in search_params:
            default_modality = search_params['search_modality'].default
            print(f"✅ Default search modality: {default_modality}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_search_parameters():
    """Test that all expected search parameters are available"""
    try:
        from praxos_python import SyncClient
        import inspect
        
        client = SyncClient(api_key="test_key", base_url="http://localhost")
        search_sig = inspect.signature(client.search)
        
        expected_params = [
            'query', 'environment_id', 'search_modality', 'top_k',
            'node_type', 'node_label', 'node_kind', 'temporal_filter',
            'known_anchors', 'target_type', 'source_type'  # Legacy params
        ]
        
        available_params = list(search_sig.parameters.keys())
        
        missing_params = []
        for param in expected_params:
            if param not in available_params:
                missing_params.append(param)
        
        if missing_params:
            print(f"❌ Missing parameters: {missing_params}")
            return False
        else:
            print(f"✅ All expected parameters available: {len(available_params)} total")
            return True
            
    except Exception as e:
        print(f"❌ Parameter test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Praxos Python SDK v0.3.0 with Intelligent Search")
    print("=" * 60)
    
    success = True
    
    # Test imports
    success &= test_intelligent_search_import()
    print()
    
    # Test parameters
    success &= test_search_parameters()
    print()
    
    if success:
        print("🎉 All tests passed! SDK is ready to use.")
        print("\nExample usage:")
        print("""
from praxos_python import SyncClient

client = SyncClient(api_key="your_api_key")

# Intelligent search
results = client.intelligent_search(
    query="financial transactions in November 2023",
    environment_id="your_env_id"
)

# Advanced search  
results = client.search(
    query="withdrawal amounts from TD Bank",
    environment_id="your_env_id",
    search_modality="intelligent", 
    top_k=20,
    include_graph_context=True
)
        """)
    else:
        print("❌ Some tests failed. Check installation and try again.")