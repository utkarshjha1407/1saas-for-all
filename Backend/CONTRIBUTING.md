# Contributing to CareOps Backend

## Development Setup

1. Fork the repository
2. Clone your fork
3. Create a feature branch
4. Make your changes
5. Run tests
6. Submit a pull request

## Code Standards

### Python Style
- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use meaningful variable names

### Code Organization
- Keep functions small and focused
- One class per file (exceptions allowed)
- Group related functionality
- Use dependency injection

### Documentation
- Docstrings for all public functions
- Type hints for all parameters
- Comments for complex logic
- Update README for new features

## Testing

### Writing Tests
```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_booking():
    """Test booking creation"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/bookings", json={...})
        assert response.status_code == 200
```

### Running Tests
```bash
# All tests
pytest

# Specific file
pytest tests/test_bookings.py

# With coverage
pytest --cov=app --cov-report=html

# Verbose
pytest -v
```

## Git Workflow

### Branch Naming
- `feature/description` - New features
- `fix/description` - Bug fixes
- `refactor/description` - Code refactoring
- `docs/description` - Documentation updates

### Commit Messages
```
type(scope): subject

body (optional)

footer (optional)
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

Example:
```
feat(bookings): add recurring booking support

- Add RecurringBooking model
- Implement recurrence rules
- Add API endpoints

Closes #123
```

## Pull Request Process

1. Update documentation
2. Add tests for new features
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Request review from maintainers

### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests added/updated
- [ ] All tests passing
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings
```

## Code Review Guidelines

### For Authors
- Keep PRs small and focused
- Provide context in description
- Respond to feedback promptly
- Update based on comments

### For Reviewers
- Be constructive and respectful
- Focus on code quality
- Check for security issues
- Verify tests are adequate

## Adding New Features

### 1. Create Schema
```python
# app/schemas/new_feature.py
from pydantic import BaseModel

class NewFeatureCreate(BaseModel):
    name: str
    description: str
```

### 2. Create Service
```python
# app/services/new_feature_service.py
from app.services.base_service import BaseService

class NewFeatureService(BaseService):
    def __init__(self, supabase):
        super().__init__(supabase, "new_features")
```

### 3. Create Endpoint
```python
# app/api/v1/endpoints/new_feature.py
from fastapi import APIRouter

router = APIRouter()

@router.post("")
async def create_new_feature(data: NewFeatureCreate):
    # Implementation
    pass
```

### 4. Register Router
```python
# app/api/v1/router.py
from app.api.v1.endpoints import new_feature

api_router.include_router(
    new_feature.router,
    prefix="/new-feature",
    tags=["New Feature"]
)
```

### 5. Add Tests
```python
# tests/test_new_feature.py
import pytest

@pytest.mark.asyncio
async def test_create_new_feature():
    # Test implementation
    pass
```

### 6. Update Documentation
- Add to API_DOCUMENTATION.md
- Update README.md if needed
- Add migration if database changes

## Database Changes

### Creating Migrations
```sql
-- migrations/001_add_new_table.sql
CREATE TABLE new_table (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Running Migrations
1. Add SQL to `supabase_schema.sql`
2. Run in Supabase SQL Editor
3. Update models and schemas
4. Test thoroughly

## Performance Guidelines

### Database Queries
- Use indexes for frequently queried columns
- Avoid N+1 queries
- Use pagination for large datasets
- Profile slow queries

### API Endpoints
- Keep response times < 200ms
- Use async/await properly
- Implement caching where appropriate
- Monitor with logging

### Background Tasks
- Keep tasks idempotent
- Add retry logic
- Log task execution
- Monitor queue length

## Security Checklist

- [ ] Input validation
- [ ] Authentication required
- [ ] Authorization checked
- [ ] SQL injection prevented
- [ ] XSS prevented
- [ ] CSRF protection
- [ ] Rate limiting considered
- [ ] Sensitive data encrypted
- [ ] Logs don't contain secrets
- [ ] Dependencies up to date

## Documentation

### Code Documentation
```python
def create_booking(data: BookingCreate) -> Booking:
    """
    Create a new booking.
    
    Args:
        data: Booking creation data
        
    Returns:
        Created booking object
        
    Raises:
        ValidationException: If data is invalid
        ConflictException: If time slot unavailable
    """
    pass
```

### API Documentation
- Use FastAPI's automatic docs
- Add examples to schemas
- Document error responses
- Include authentication requirements

## Troubleshooting

### Common Issues

**Import errors**
```bash
pip install --upgrade -r requirements.txt
```

**Database connection failed**
```bash
# Check .env configuration
# Verify Supabase project is active
```

**Tests failing**
```bash
# Clear pytest cache
pytest --cache-clear
```

## Getting Help

- Check existing documentation
- Search closed issues
- Ask in team chat
- Contact maintainers

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

Thank you for contributing to CareOps! 🎉
