# RB-Commons

RB-Commons is a lightweight async Python library that simplifies database operations through a clean manager interface built on top of SQLAlchemy's async capabilities. It provides a robust foundation for handling common database operations while maintaining full type safety through Python's typing system.

## Features

### Async-First Design
- Built on top of SQLAlchemy's async functionality
- Efficient handling of async database operations
- Proper transaction and session management
- Type-safe operations with Generic types

### Core Functionality
- **CRUD Operations**: Complete set of Create, Read, Update, and Delete operations
- **Flexible Filtering**: Support for dynamic query filtering
- **Instance Management**: Both instance-level and query-level updates
- **Error Handling**: Comprehensive error handling with custom exceptions
- **Transaction Safety**: Automatic rollbacks on failures

## Installation

```bash
pip install rb-commons
```

## Quick Start

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from rb_commons.orm import BaseManager

# Define your model
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)

# Create your manager
class UserManager(BaseManager[User]):
    model = User

# Usage in async context
async def main():
    # Setup database connection
    engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db")
    async with AsyncSession(engine) as session:
        # Initialize manager
        user_manager = UserManager(session)
        
        # Create user
        user = await user_manager.create(
            name="John Doe",
            email="john@example.com"
        )
        
        # Get user
        user = await user_manager.get(id=1)
        
        # Filter users
        users = await user_manager.filter(name="John Doe")
        
        # Update user by filters
        updated_user = await user_manager.update_by_filters(
            filters={"id": 1},
            name="Jane Doe"
        )
        
        # Delete user
        success = await user_manager.delete(id=1)
```

## Core Operations

### Get and Filter

```python
# Get single instance (returns Optional[ModelType])
user = await user_manager.get(id=1)

# Filter multiple instances (returns List[ModelType])
active_users = await user_manager.filter(is_active=True)

# Check existence
exists = await user_manager.is_exists(email="john@example.com")
```

### Create

```python
try:
    user = await user_manager.create(
        name="John Doe",
        email="john@example.com"
    )
except DatabaseException as e:
    print(f"Database error: {e}")
except InternalException as e:
    print(f"Internal error: {e}")
```

### Update

RB-Commons provides three different ways to update records:

```python
# 1. Update by filters - updates records matching filters and returns updated instance
updated_user = await user_manager.update_by_filters(
    filters={"id": 1},
    name="New Name"
)

# 2. Update instance with specific fields
user = await user_manager.get(id=1)
if user:
    updated_user = await user_manager.update(
        instance=user,
        name="New Name"
    )

# 3. Save modified instance
user = await user_manager.get(id=1)
if user:
    user.name = "New Name"
    saved_user = await user_manager.save(user)
```

### Delete

```python
# Delete by ID
success = await user_manager.delete(id=1)

# Delete by filters
success = await user_manager.delete(email="old@example.com")

# Bulk delete
deleted_count = await user_manager.bulk_delete(is_active=False)
```

## Error Handling

RB-Commons provides custom exceptions for better error handling:

- `DatabaseException`: For SQLAlchemy and database-related errors
- `InternalException`: For internal operation errors

```python
try:
    user = await user_manager.create(name="John")
except DatabaseException as e:
    # Handle database errors (e.g., constraint violations)
    print(f"Database error: {e}")
except InternalException as e:
    # Handle internal errors
    print(f"Internal error: {e}")
```

## Method Return Types

- `get()`: `Optional[ModelType]`
- `filter()`: `List[ModelType]`
- `create()`: `ModelType`
- `delete()`: `bool | None`
- `bulk_delete()`: `int`
- `update()`: `Optional[ModelType]`
- `update_by_filters()`: `Optional[ModelType]`
- `save()`: `Optional[ModelType]`
- `is_exists()`: `bool`

## Best Practices

1. **Choose the Right Update Method**: 
   - Use `update_by_filters()` for query-based updates
   - Use `update()` for updating specific fields of an instance
   - Use `save()` for saving modified instances
2. **Always Use Async Context**: The library is designed for async operations, ensure you're running within an async context
3. **Session Management**: Properly manage your database sessions using async context managers
4. **Error Handling**: Implement proper error handling using the provided exception classes
5. **Type Safety**: Utilize the generic typing system for better IDE support and type safety

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.