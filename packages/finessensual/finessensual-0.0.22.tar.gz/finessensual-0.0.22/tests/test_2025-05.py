from finessensual.analyze import analyze

def test_finessensual_cli():
    """Test the finessensual CLI script."""

    result = analyze( datadir = 'tests/2025-05',
                      output  = 'tests/2025-05/output.xlsx' )
    assert result == True

