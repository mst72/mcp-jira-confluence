# Contributing to Jira-Confluence MCP Server

Thank you for your interest in contributing! This document provides guidelines and standards for contributing to this project.

## 🌍 Language Requirements

**CRITICAL: All code, comments, documentation, and communication MUST be in English ONLY.**

This is a non-negotiable requirement:

- ✅ **Code**: Variable names, function names, class names - English only
- ✅ **Comments**: Inline comments, docstrings - English only
- ✅ **Documentation**: All `.md` files, README, guides - English only
- ✅ **Commit Messages**: All git commits - English only
- ✅ **Pull Requests**: Titles, descriptions, discussions - English only
- ✅ **Issues**: Bug reports, feature requests - English only
- ❌ **NO Russian, Chinese, or any other language**

**Why English-only?**
- International collaboration
- Industry standard practice
- Better tool integration
- Wider community access
- Professional software development norms

## 📋 Code Style Guidelines

### Python Code Standards

1. **Follow PEP 8**
   - Use 4 spaces for indentation (no tabs)
   - Maximum line length: 100 characters
   - Use snake_case for functions and variables
   - Use PascalCase for classes

2. **Type Hints**
   ```python
   def get_issue(issue_key: str) -> Dict[str, Any]:
       """Get issue details."""
       pass
   ```

3. **Docstrings**
   - Use Google-style docstrings
   - Include Args, Returns, Raises sections
   - Example:
   ```python
   def search_issues(jql: str, max_results: int = 50) -> Dict[str, Any]:
       """
       Search for Jira issues using JQL.

       Args:
           jql: JQL query string
           max_results: Maximum number of results (default: 50)

       Returns:
           Dictionary containing search results with issues and metadata

       Raises:
           JiraConfluenceError: If API request fails
       """
       pass
   ```

4. **Error Handling**
   - Use custom exceptions from `errors.py`
   - Always provide meaningful error messages
   - Log errors appropriately

5. **Imports**
   - Group imports: stdlib, third-party, local
   - Sort alphabetically within groups
   - Use absolute imports

### Documentation Standards

1. **Markdown Files**
   - Use proper heading hierarchy (# > ## > ###)
   - Include code examples in fenced blocks with language tags
   - Add table of contents for long documents
   - Use lists for step-by-step instructions

2. **Code Examples**
   ```python
   # Good: Clear, commented example
   client = JiraConfluenceClient(base_url, email, token)
   result = client.search_jira_issues("project = TEST", max_results=10)
   ```

3. **README Updates**
   - Keep installation instructions current
   - Update feature list when adding functionality
   - Maintain examples section

## 🔧 Development Workflow

### Setting Up Development Environment

1. **Clone repository**
   ```bash
   git clone <repo-url>
   cd jira-confluence
   ```

2. **Install dependencies**
   ```bash
   uv pip install -e ".[dev]"
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. **Run tests**
   ```bash
   uv run python test_connection.py
   uv run python test_mcp_tools.py
   ```

### Making Changes

1. **Create feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code following style guidelines
   - Add tests for new functionality
   - Update documentation

3. **Test your changes**
   ```bash
   # Run connection tests
   uv run python test_connection.py

   # Run MCP tools tests
   uv run python test_mcp_tools.py

   # Test with MCP Inspector
   npx @modelcontextprotocol/inspector uv run jira-confluence-mcp
   ```

4. **Commit your changes**
   ```bash
   # Good commit message (English only!)
   git commit -m "Add support for Jira issue attachments"

   # Bad commit message (Russian)
   git commit -m "Добавил поддержку вложений"  # ❌ WRONG!
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Guidelines

Follow conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
feat(jira): add support for issue attachments
fix(confluence): handle pages without version number
docs(readme): update installation instructions
test(client): add tests for error handling
```

## 🧪 Testing Requirements

### Before Submitting PR

All PRs must pass these checks:

1. **Connection tests pass**
   ```bash
   uv run python test_connection.py
   ```

2. **MCP tools tests pass**
   ```bash
   uv run python test_mcp_tools.py
   ```

3. **Manual testing with MCP Inspector**
   - Launch inspector
   - Test affected tools
   - Verify error handling

4. **Code style checks** (if available)
   ```bash
   black --check .
   ruff check .
   mypy .
   ```

### Writing Tests

When adding new features:

1. Add unit tests for new functions
2. Add integration tests for API calls
3. Update test documentation in `TESTING.md`

## 📝 Documentation Requirements

### Required Documentation Updates

When making changes, update:

1. **CLAUDE.md** - If changing development workflow
2. **README.md** - If adding features or changing setup
3. **SPECIFICATION.md** - If modifying API or tools
4. **TESTING.md** - If adding new tests
5. **Docstrings** - For all new functions/classes

### Documentation Checklist

- [ ] All new functions have docstrings
- [ ] All docstrings are in English
- [ ] README updated if needed
- [ ] Examples added for new features
- [ ] CHANGELOG updated (if exists)

## 🐛 Reporting Bugs

### Bug Report Template

```markdown
## Description
Clear description of the bug

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- Python version:
- uv version:
- Operating System:
- Jira/Confluence version:

## Error Messages
```
Paste error messages here
```

## Additional Context
Any other relevant information
```

## 💡 Feature Requests

### Feature Request Template

```markdown
## Feature Description
Clear description of the proposed feature

## Use Case
Why is this feature needed? What problem does it solve?

## Proposed Implementation
How should this work? (optional)

## Alternatives Considered
What other solutions were considered? (optional)

## Additional Context
Any other relevant information
```

## 🔍 Code Review Process

### PR Review Checklist

Reviewers will check:

- [ ] Code is in English (names, comments, docs)
- [ ] Follows Python style guidelines
- [ ] Includes appropriate tests
- [ ] Documentation is updated
- [ ] Commit messages follow conventions
- [ ] No sensitive data (tokens, passwords) in code
- [ ] Error handling is appropriate
- [ ] Performance considerations addressed

### Getting Your PR Merged

1. **Address review comments** promptly
2. **Keep PR focused** - one feature/fix per PR
3. **Update PR description** if scope changes
4. **Resolve merge conflicts** quickly
5. **Be responsive** to feedback

## 🚀 Release Process

(For maintainers)

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create git tag
4. Build and publish (if applicable)

## 📞 Getting Help

If you have questions:

1. Check existing documentation
2. Search existing issues
3. Create new issue with question
4. Be specific and provide context

## ✅ Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Connection tests pass
- [ ] MCP tools tests pass
- [ ] Tested with MCP Inspector
- [ ] Manual testing performed

## Documentation
- [ ] Updated relevant documentation
- [ ] Added docstrings for new code
- [ ] Updated examples if needed

## Checklist
- [ ] Code follows style guidelines
- [ ] All code/comments in English
- [ ] Self-reviewed my code
- [ ] Added tests for changes
- [ ] All tests passing
- [ ] No sensitive data in code
```

## 📄 License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

**Thank you for contributing! 🎉**

Remember: **English only** - this is not just a guideline, it's a requirement.
