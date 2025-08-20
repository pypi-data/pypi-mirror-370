# Testing Guide

Obsidian-AI maintains a comprehensive test suite with 102+ tests achieving high code coverage. This guide covers our testing philosophy, practices, and tools.

## Testing Philosophy

### Bacterial Testing Approach

Following our bacterial coding principles:

- **Small, focused tests** - Each test has one clear purpose
- **Synthetic test data** - Reproducible, controlled test environments
- **Copy-pasteable fixtures** - Reusable test components
- **Fast execution** - Tests run quickly for rapid feedback

### Test Pyramid

```
           ┌─────────────┐
           │ E2E Tests   │ (Few, slow, realistic)
           └─────────────┘
         ┌─────────────────┐
         │ Integration     │ (Some, medium, component interactions)
         │ Tests           │
         └─────────────────┘
       ┌─────────────────────┐
       │ Unit Tests          │ (Many, fast, isolated)
       └─────────────────────┘
```

## Test Structure

### Current Test Coverage

- **102 tests** passing
- **49% overall coverage**
- **100% coverage** for core components:
  - WikiLink parser
  - Configuration system
  - File system operations
- **93% coverage** for search engine
- **95%+ coverage** for prompt management

### Test Organization

```
tests/
├── conftest.py              # Shared fixtures
├── test_core.py             # Core business logic tests
├── test_infrastructure.py   # Config and file system tests
├── test_services.py         # External service tests
├── test_interfaces.py       # CLI and API tests
├── test_prompts.py          # Prompt management tests
├── test_search_engine.py    # Search functionality tests
└── test_wikilink_parser.py  # WikiLink parsing tests
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_core.py

# Run specific test
uv run pytest tests/test_core.py::TestWikilinkParser::test_extract_wikilinks_simple
```

### Coverage Analysis

```bash
# Run with coverage
uv run pytest --cov=src/obsidian_ai --cov-report=term-missing

# Generate HTML coverage report
uv run pytest --cov=src/obsidian_ai --cov-report=html

# Coverage for specific module
uv run pytest --cov=src/obsidian_ai.core --cov-report=term-missing tests/test_core.py
```

### Test Selection

```bash
# Run only fast tests
uv run pytest -m "not slow"

# Run only integration tests
uv run pytest -k "integration"

# Run failed tests from last run
uv run pytest --lf
```

## Writing Tests

### Test Structure Pattern

```python
class TestComponent:
    def test_specific_behavior(self):
        # Arrange
        input_data = create_test_data()
        
        # Act
        result = component.method(input_data)
        
        # Assert
        assert result == expected_output
```

### Fixtures and Test Data

#### Synthetic Knowledge Base

The `temp_brain` fixture creates a comprehensive synthetic knowledge base:

```python
@pytest.fixture
def temp_brain():
    """Create temporary brain directory with synthetic test data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        brain_dir = Path(tmpdir) / "brain"
        brain_dir.mkdir()
        create_synthetic_notes(brain_dir)
        yield brain_dir
```

#### Mock Services

```python
@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    with patch("obsidian_ai.services.openai_client.OpenAI") as mock_openai:
        mock_client = mock_openai.return_value
        mock_client.chat.completions.create.return_value.choices = [
            type("Choice", (), {"message": type("Message", (), {"content": "Test response"})()})()
        ]
        yield mock_client
```

### Testing Strategies

#### Unit Testing

Test individual functions in isolation:

```python
def test_extract_wikilinks_simple():
    text = "This mentions [[John Smith]] and [[Machine Learning]]."
    
    links = WikiLinkParser.extract_wikilinks(text)
    
    assert len(links) == 2
    assert links[0].target == "John Smith"
    assert links[1].target == "Machine Learning"
```

#### Integration Testing

Test component interactions:

```python
def test_search_integration(temp_brain):
    """Test search engine with actual file system."""
    from obsidian_ai.infrastructure.config import Config
    
    test_config = Config(
        brain_dir=temp_brain,
        model="gpt-4o",
        max_tool_calls=5,
        cache_dir=temp_brain / ".cache",
        ignore_patterns=[".git", "__pycache__"]
    )
    
    with patch("obsidian_ai.core.search_engine.config", test_config):
        search = ExactPhraseSearch()
        results = search.search("Tara", max_results=10)
    
    assert len(results) >= 1
    assert any("Tara" in result.text for result in results)
```

#### Mocking External Dependencies

```python
@patch("obsidian_ai.services.openai_client.OpenAI")
def test_openai_error_handling(mock_openai):
    mock_openai.return_value.chat.completions.create.side_effect = Exception("API Error")
    
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        client = OpenAIClient()
        result = client.simple_completion("test prompt")
    
    assert "Error:" in result
```

## Test Data Management

### Synthetic Knowledge Base Structure

Our test data simulates a realistic knowledge base:

```
brain/
├── daily/
│   ├── 2024-01-15.md     # Daily notes with tasks and meetings
│   └── 2024-01-16.md
├── people/
│   ├── john-smith.md     # Person profiles with connections
│   └── sarah-wilson.md
├── projects/
│   ├── machine-learning.md  # Project documentation
│   └── data-pipeline.md
├── concepts/
│   ├── deep-learning.md     # Concept explanations
│   └── neural-networks.md
└── research/
    └── paper-ideas.md       # Research notes
```

### Test Data Characteristics

- **Rich interconnections** with WikiLinks
- **Realistic content** mimicking actual knowledge bases
- **Edge cases** like special characters, Unicode, large files
- **Hierarchical structure** with subdirectories

## Debugging Tests

### Common Issues

#### Test Isolation
```python
# Good: Use fixtures for clean state
def test_with_fixture(temp_brain):
    # Test uses isolated temporary directory
    pass

# Bad: Tests depend on global state
def test_without_fixture():
    # Test modifies shared resources
    pass
```

#### Mock Configuration
```python
# Good: Patch at the right level
with patch("module.where.used.config", test_config):
    result = function_under_test()

# Bad: Patch at import level
with patch("module.where.defined.config", test_config):
    # Won't work if already imported
    pass
```

### Debugging Techniques

#### Print Debugging
```python
def test_with_debug():
    result = function_under_test()
    print(f"Debug: result = {result}")  # Use pytest -s to see output
    assert result == expected
```

#### Pytest Debugging
```bash
# Drop into debugger on failure
uv run pytest --pdb

# Drop into debugger immediately
uv run pytest --pdb-trace

# Show local variables in traceback
uv run pytest -l
```

## Performance Testing

### Timing Tests
```python
import time

def test_performance():
    start = time.time()
    result = expensive_operation()
    duration = time.time() - start
    
    assert duration < 1.0  # Should complete within 1 second
    assert result is not None
```

### Memory Testing
```python
import psutil
import os

def test_memory_usage():
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    result = memory_intensive_operation()
    
    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory
    
    assert memory_increase < 100 * 1024 * 1024  # Less than 100MB increase
```

## Continuous Integration

### GitHub Actions Integration

Our CI pipeline runs:
1. **Linting** with ruff
2. **Type checking** with mypy
3. **Test execution** with pytest
4. **Coverage reporting**
5. **Documentation building**

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

## Best Practices

### Do's
- ✅ Write tests before fixing bugs
- ✅ Use descriptive test names
- ✅ Keep tests independent
- ✅ Mock external dependencies
- ✅ Test edge cases and error conditions

### Don'ts
- ❌ Test implementation details
- ❌ Write overly complex tests
- ❌ Ignore flaky tests
- ❌ Skip testing error paths
- ❌ Use production data in tests

## Troubleshooting

### Common Test Failures

#### Import Errors
```bash
# Fix: Ensure package is properly installed
uv sync

# Or run tests with PYTHONPATH
PYTHONPATH=src uv run pytest
```

#### Mock Issues
```python
# Fix: Patch where the object is used, not where it's defined
# Wrong: patch("requests.get")
# Right: patch("mymodule.requests.get")
```

#### File System Tests
```python
# Fix: Use proper temporary directories
def test_file_operations(tmp_path):
    test_file = tmp_path / "test.md"
    test_file.write_text("content")
    # Test uses isolated filesystem
```

For more debugging help, see our [contribution guide](contributing.md) or check the [architecture documentation](architecture.md).