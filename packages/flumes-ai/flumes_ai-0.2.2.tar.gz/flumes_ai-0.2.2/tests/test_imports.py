def test_public_imports():
    import importlib

    sdk = importlib.import_module("flumes")
    assert hasattr(sdk, "Agent")
    assert hasattr(sdk, "MemoryClient")
    assert hasattr(sdk, "AsyncAgent")
    assert hasattr(sdk, "AsyncMemoryClient")
