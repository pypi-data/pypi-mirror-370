# Changelog

All notable changes to the Tallyfy SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.8] - 2025-07-29

### Changed
- **BREAKING**: Refactored user management from monolithic to modular architecture
  - `user_management.py` → `user_management/` package with specialized modules
  - New `UserManager` class replaces `UserManagement` (backward compatible alias maintained)
  - Improved separation of concerns with dedicated retrieval and invitation modules

### Added
- **Enhanced User Management Features**:
  - `get_user_by_email()` - Find users by email address with exact matching
  - `get_guest_by_email()` - Find guests by email address with exact matching
  - `search_members_by_name()` - Fuzzy search for users and guests by name
  - `get_all_organization_members()` - Convenience method to get users and guests in one call
  - `invite_multiple_users()` - Batch invitation support with default role/message handling
  - `resend_invitation()` - Resend invitations with custom messaging
  - `get_invitation_template_message()` - Generate customized invitation messages
  - `validate_invitation_data()` - Validate invitation data before sending

- **Modular Architecture Improvements**:
  - `user_management/base.py` - Common validation and error handling
  - `user_management/retrieval.py` - User and guest retrieval operations
  - `user_management/invitation.py` - User invitation operations with enhanced features
  - Direct access to specialized modules via `sdk.users.retrieval` and `sdk.users.invitation`

### Improved
- **Enhanced Validation**: Comprehensive email validation with regex patterns
- **Better Error Handling**: Context-aware error messages with operation details
- **Query Parameter Handling**: Flexible parameter building with proper boolean conversion
- **Code Organization**: Clear separation between retrieval and invitation concerns
- **Type Safety**: Enhanced type hints and validation across all user operations

### Fixed
- **Python Keyword Conflicts**: Resolved issues with `with` keyword in query parameters
- **Import Compatibility**: Maintained full backward compatibility while enabling new functionality

### Deprecated
- `UserManagement` class name (use `UserManager` instead, though alias is maintained)

## [1.0.0] - 2025-06-25

### Added
- Initial release of Tallyfy SDK
- Complete user management functionality
- Task management with natural language processing
- Template management with automation support
- Form field management with AI-powered suggestions
- Comprehensive data models with type safety
- Error handling with automatic retry logic
- Session management and connection pooling
- Full API coverage for Tallyfy platform

### Features
- **User Management**: Organization members, guests, and invitations
- **Task Management**: Personal tasks, process tasks, and natural language creation
- **Template Management**: Template CRUD, automation rules, and health assessment
- **Form Fields**: Dynamic form field management with AI suggestions
- **Search**: Universal search across processes, templates, and tasks
- **Natural Language Processing**: Date extraction and task parsing
- **Error Handling**: Comprehensive error handling with detailed response data
- **Type Safety**: Full dataclass models with type hints

### Dependencies
- requests>=2.25.0
- typing-extensions>=4.0.0 (Python < 3.8)

### Development
- Python 3.7+ support
- Comprehensive test suite
- Type checking with mypy
- Code formatting with black
- Linting with flake8