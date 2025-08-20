def test_imports():
    import mcpstack_mimic.tools.mimic as m

    assert hasattr(m, "MIMIC")
