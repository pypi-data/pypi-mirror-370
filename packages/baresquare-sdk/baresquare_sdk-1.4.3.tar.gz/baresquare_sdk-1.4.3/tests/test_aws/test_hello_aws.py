def test_import():
    """Test that we can import from our package."""
    from baresquare_sdk import aws

    assert aws.ssm is not None, "SSM module imported successfully"
