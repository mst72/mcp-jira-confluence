# Project Standards and Guidelines

This document outlines the standards and guidelines for the Jira-Confluence MCP Server project.

## 🌍 Language Policy

### **ENGLISH ONLY - NO EXCEPTIONS**

All aspects of this project MUST be in English:

| Category | Requirement | ✅ Correct | ❌ Wrong |
|----------|-------------|-----------|----------|
| **Code** | Variable names | `get_issue()` | `получить_задачу()` |
| **Code** | Class names | `JiraClient` | `ЖираКлиент` |
| **Comments** | Inline comments | `# Fetch data` | `# Получить данные` |
| **Docstrings** | Function docs | `"""Get issue."""` | `"""Получить задачу."""` |
| **Documentation** | README, guides | English text | Russian text |
| **Commits** | Commit messages | `fix: bug in API` | `исправил: баг в API` |
| **Issues** | Bug reports | English | Russian |
| **PRs** | Pull requests | English | Russian |

### Rationale

1. **International Collaboration**: Open-source projects need global contributors
2. **Industry Standard**: Professional software is developed in English
3. **Tool Integration**: Better support from IDEs, linters, and tools
4. **Community Access**: Wider audience can understand and contribute
5. **Career Development**: English code is a professional skill

## 📝 Code Style Standards

### Python (PEP 8 Compliant)

```python
# ✅ CORRECT
def search_jira_issues(jql: str, max_results: int = 50) -> Dict[str, Any]:
    """
    Search for Jira issues using JQL.

    Args:
        jql: JQL query string
        max_results: Maximum number of results (default: 50)

    Returns:
        Dictionary containing search results

    Raises:
        JiraConfluenceError: If API request fails
    """
    if not jql:
        raise ValueError("JQL query cannot be empty")

    return self._request('POST', '/rest/api/3/search/jql', json={
        'jql': jql,
        'maxResults': max_results
    })

# ❌ WRONG - Russian names and comments
def поиск_задач(запрос: str, макс: int = 50) -> Dict[str, Any]:
    """Поиск задач по JQL."""  # Russian docstring
    # Проверяем запрос
    if not запрос:
        raise ValueError("Пустой запрос")
    return self._request('POST', '/rest/api/3/search/jql')
```

### Formatting Rules

- **Indentation**: 4 spaces (no tabs)
- **Line Length**: Maximum 100 characters
- **Naming Conventions**:
  - Functions/variables: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`
- **Imports**: Group and sort (stdlib → third-party → local)
- **Type Hints**: Always use for function parameters and returns

### Documentation Standards

```python
# ✅ CORRECT - Comprehensive English docstring
class JiraConfluenceClient:
    """
    HTTP client for Atlassian Jira and Confluence REST APIs.

    This client handles authentication, request formatting, and error handling
    for both Jira Cloud REST API v3 and Confluence Cloud REST API v1.

    Attributes:
        base_url: Base URL of Atlassian instance
        email: User email for authentication
        session: Requests session with authentication headers

    Example:
        >>> client = JiraConfluenceClient(
        ...     "https://your-domain.atlassian.net",
        ...     "user@company.com",
        ...     "api-token"
        ... )
        >>> issues = client.search_jira_issues("project = TEST")
    """
    pass

# ❌ WRONG - Russian or no docstring
class ЖираКлиент:
    """Клиент для работы с Jira."""  # Russian
    pass
```

## 📁 File Organization

### Required Files

All projects must include:

- ✅ `README.md` - Project overview (English)
- ✅ `SPECIFICATION.md` - Technical specification (English)
- ✅ `CLAUDE.md` - Claude Code instructions (English)
- ✅ `TESTING.md` - Testing guide (English)
- ✅ `CONTRIBUTING.md` - Contribution guidelines (English)
- ✅ `.editorconfig` - Code style configuration
- ✅ `.gitignore` - Git ignore rules
- ✅ `.env.example` - Environment variable template

### Directory Structure

```
jira-confluence/
├── jira_confluence_mcp/     # Source code
│   ├── __init__.py
│   ├── server.py            # MCP server
│   ├── client.py            # HTTP client
│   ├── errors.py            # Error handling
│   └── formatters.py        # Data formatters
├── docs/                    # Additional documentation
├── tests/                   # Test files
│   ├── test_connection.py
│   ├── test_mcp_tools.py
│   └── test_my_tasks.py
├── README.md               # Main documentation
├── SPECIFICATION.md        # Technical spec
├── CLAUDE.md              # AI assistant instructions
├── TESTING.md             # Testing guide
├── CONTRIBUTING.md        # Contribution guide
├── PROJECT_STANDARDS.md   # This file
├── pyproject.toml         # Project configuration
├── .editorconfig          # Editor configuration
├── .gitignore            # Git ignore rules
└── .env.example          # Environment template
```

## 🧪 Testing Standards

### Required Tests

Before any commit or PR:

1. **Connection Test**
   ```bash
   uv run python test_connection.py
   ```
   - Must verify Jira connection
   - Must verify Confluence connection
   - Must handle authentication errors

2. **MCP Tools Test**
   ```bash
   uv run python test_mcp_tools.py
   ```
   - Must verify all 10 tools registered
   - Must test Jira search
   - Must test Confluence search

3. **MCP Inspector Test**
   ```bash
   npx @modelcontextprotocol/inspector uv run jira-confluence-mcp
   ```
   - Manual verification of tool functionality
   - Check error handling
   - Verify response formats

### Test File Standards

```python
# ✅ CORRECT - Clear English descriptions
def test_jira_search_with_valid_jql():
    """Test Jira search with valid JQL query."""
    client = JiraConfluenceClient(BASE_URL, EMAIL, TOKEN)
    result = client.search_jira_issues("project = TEST", max_results=5)

    assert 'issues' in result
    assert len(result['issues']) <= 5

# ❌ WRONG - Russian function name and docstring
def тест_поиска():
    """Тест поиска задач."""
    pass
```

## 📋 Git Commit Standards

### Commit Message Format

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

### Commit Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

### Examples

```bash
# ✅ CORRECT
git commit -m "feat(jira): add support for issue attachments"
git commit -m "fix(confluence): handle missing version field"
git commit -m "docs(readme): update installation instructions"

# ❌ WRONG - Russian
git commit -m "добавил поддержку вложений"
git commit -m "исправил баг с версией"
```

## 🔒 Security Standards

### API Credentials

**NEVER commit sensitive data:**

```bash
# ❌ WRONG - Hardcoded credentials
JIRA_BASE_URL = "https://your-domain.atlassian.net"
JIRA_API_TOKEN = "your-api-token-here"  # Secret token exposed!

# ✅ CORRECT - Environment variables
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
```

### .gitignore Requirements

Must include:
```
.env
*.pyc
__pycache__/
.venv/
venv/
*.log
.DS_Store
```

## 📊 Code Review Checklist

Before submitting PR, verify:

### Language Requirements
- [ ] All code in English
- [ ] All comments in English
- [ ] All docstrings in English
- [ ] All commit messages in English
- [ ] All documentation in English

### Code Quality
- [ ] Follows PEP 8 style guide
- [ ] Has type hints
- [ ] Has comprehensive docstrings
- [ ] No hardcoded credentials
- [ ] Error handling implemented
- [ ] Logging added where appropriate

### Testing
- [ ] Connection tests pass
- [ ] MCP tools tests pass
- [ ] Manual testing completed
- [ ] Edge cases covered

### Documentation
- [ ] README updated if needed
- [ ] SPECIFICATION updated if needed
- [ ] Examples added for new features
- [ ] TESTING guide updated if needed

## 🛠️ Development Tools

### Recommended Setup

1. **Editor Configuration**
   - Install EditorConfig plugin
   - Configure for 4-space indentation
   - Enable auto-formatting on save

2. **Python Tools**
   ```bash
   # Install development tools
   uv pip install black ruff mypy pytest

   # Format code
   black .

   # Lint code
   ruff check .

   # Type check
   mypy .
   ```

3. **Pre-commit Hooks** (optional)
   ```bash
   # Install pre-commit
   uv pip install pre-commit

   # Setup hooks
   pre-commit install
   ```

## 📖 Documentation Guidelines

### Markdown Standards

1. **Headings**: Use proper hierarchy
   ```markdown
   # Main Title
   ## Section
   ### Subsection
   #### Details
   ```

2. **Code Blocks**: Always specify language
   ```markdown
   ```python
   def example():
       pass
   ```
   ```

3. **Lists**: Use consistent formatting
   - Bullets for unordered
   1. Numbers for ordered
   - [ ] Checkboxes for tasks

4. **Links**: Use descriptive text
   ```markdown
   # ✅ CORRECT
   See [Jira API Documentation](https://developer.atlassian.com/...)

   # ❌ WRONG
   See documentation here: https://developer.atlassian.com/...
   ```

## 🎯 Quality Metrics

### Code Quality Goals

- **Test Coverage**: Aim for >80%
- **Docstring Coverage**: 100% for public APIs
- **Type Hint Coverage**: 100% for function signatures
- **Line Length**: Max 100 characters
- **Cyclomatic Complexity**: Max 10 per function

### Performance Goals

- API response time: <2 seconds
- Startup time: <3 seconds
- Memory usage: <100MB

## 📞 Getting Help

### Resources

1. **Documentation**
   - Read CLAUDE.md for development guide
   - Check SPECIFICATION.md for technical details
   - Review TESTING.md for test procedures

2. **Issues**
   - Search existing issues first
   - Create new issue with template
   - Provide clear reproduction steps

3. **Community**
   - Keep all communication in English
   - Be respectful and professional
   - Provide context with questions

## ⚡ Quick Reference

### Before Every Commit

```bash
# 1. Format code (if tools installed)
black .

# 2. Run tests
uv run python test_connection.py
uv run python test_mcp_tools.py

# 3. Check commit message is in English
git log -1

# 4. Verify no secrets
git diff --cached | grep -i "token\|password\|secret"
```

### Before Every PR

```bash
# 1. Update from main
git pull origin main

# 2. Run all tests
uv run python test_connection.py
uv run python test_mcp_tools.py

# 3. Test with MCP Inspector
npx @modelcontextprotocol/inspector uv run jira-confluence-mcp

# 4. Check documentation
# - README.md updated?
# - SPECIFICATION.md updated?
# - Examples added?
```

---

## 🎓 Summary

**The Golden Rule: EVERYTHING IN ENGLISH**

This is not optional. This is not a suggestion. This is a requirement.

If you see any code, comments, or documentation in a language other than English, it should be:
1. Fixed immediately
2. Reported as a bug
3. Never merged into main

Quality software is international software. International software is English software.

---

**Last Updated:** 2025-11-06
**Version:** 1.0
