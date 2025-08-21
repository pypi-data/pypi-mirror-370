def pytest_addoption(parser):
    parser.addoption(
        "--generate-references",
        action="store_true",
        help="Generate reference data instead of validating it"
    )
