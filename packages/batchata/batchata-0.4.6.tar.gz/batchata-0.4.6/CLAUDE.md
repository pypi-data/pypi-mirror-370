# CLAUDE.md

## Process
1. Check SPEC.md for current feature specification
2. Write tests for the main functionality
3. Implement the feature to make tests pass
4. Update SPEC.md with progress
5. When complete, move SPEC.md to specs/ for archival with numbered prefix (e.g., 003-feature-name.md).

## General rules
- Less output is better, try to be succinct
- Less code is better
- Simple readable code is better
- No comments unless absolutely necessary
- Ask user before proceeding if multiple approaches exist
- Prefer early exists, instead of indented code mayhem.
- Don't create functions for code that can be understandable inline (like one simple conditional)
- Always update README.md, DEVELOPMENT.md and llms.txt after changes to the library that affect end users.
- Usually classes should be in separate classes.
- I almost never want backwards compatability, unless I ask for it specifically.

## Spec rules
- When creating a new SPEC.md or modifying it, ask the user before making changes to the SPEC.md
- SPEC.md should be pretty succinct, don't write full source code there, unless it is a helpful snippet to understand the spec.
- Add learnings into the spec when you have some.

## Testing
- Test main functionality, not every detail
- Tests must be real and verify actual behavior
- Focus on core behavior

## Project structure
(Update when it changes)
```
bachata/
├── CLAUDE.md          # This file
├── SPEC.md            # Current feature specification
├── pyproject.toml     # Project configuration
├── debug/             # Debug and test scripts
│   ├── debug_new_api.py
│   └── debug_nested_validation.py
├── examples/          # Example usage scripts
│   ├── citation_example.py
│   ├── citation_with_pydantic.py
│   ├── pdf_extraction.py
│   ├── raw_text_example.py
│   └── spam_detection.py
├── specs/             # Archived feature specifications (numbered by completion order)
├── src/               # Source code
│   ├── __init__.py
│   ├── batch_job.py
│   ├── citations.py
│   ├── core.py
│   ├── file_processing.py
│   └── providers/
│       ├── __init__.py
│       ├── anthropic.py
│       └── base.py
└── tests/             # Test files
    ├── __init__.py
    ├── test_bachata.py
    ├── test_batch_validation.py
    ├── test_citation_modes.py
    ├── test_pdf_processing.py
    ├── utils/
    │   ├── __init__.py
    │   └── pdf_utils.py
    └── e2e/
        └── test_batch_integration.py
```

## Commands
- `uv add <package>` - Add dependency
- `uv run pytest -v -n auto ` - Run tests
- `uv run python -m examples.spam_detection` - Run example
- `bachata-example` - Run spam detection example
- `bachata-pdf-example` - Run PDF extraction example


## Documentation
- Generate docs on each version
```bash
uv run pdoc -o docs/ batchata
```

## Version and releaseing
- Add good commit messages
- Add good version description, remember to bump pyproject.toml
```bash
# One-liner to update version, commit, push, and release
VERSION=0.0.2 && \
sed -i '' "s/version = \".*\"/version = \"$VERSION\"/" pyproject.toml && \
uv run pdoc -o docs/ batchata && \
git add pyproject.toml docs/ && \
git commit -m "Bump version to $VERSION" && \
git push && \
gh release create v$VERSION --title "v$VERSION" --generate-notes
```

Always add release notes that add value, and only call release with vx.x.x no description in the relese name.

Release notes should be:
- Concise, no marketing fluff
- List actual changes made
- Include "No breaking changes" if applicable

## Code Style
- **Typing**: Strict type annotations, use `BaseModel` for structured outputs
- **Imports**: Standard lib → third-party → local
- **Formatting**: Ruff with Black conventions
- **Error handling**: Custom exceptions from `exceptions.py`, Pydantic validation
- **Naming**: `snake_case` functions/variables, `PascalCase` classes
- **No mocking**: Tests use real API calls
