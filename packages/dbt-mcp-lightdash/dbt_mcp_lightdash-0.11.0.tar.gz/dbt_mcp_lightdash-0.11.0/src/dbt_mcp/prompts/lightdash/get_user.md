# Tool Name: lightdash_get_user

## Description
Get current Lightdash user information including organization details and permissions.

## When to Use
- Checking authentication status
- Getting organization context
- Debugging permission issues
- Understanding user access levels
- Internal operations requiring user context

## Parameters
None - this tool takes no parameters

## JSON Examples

### Example 1: Get current user info
```json
{}
```

### Example 2: Check authentication
```json
{}
```

### Example 3: Get organization details
```json
{}
```

## Common Mistakes to Avoid
- ❌ Passing any parameters - this tool takes none
- ❌ Using for user management (read-only)
- ✅ Use for debugging access issues
- ✅ Note organization UUID for RLS

## Related Tools
- `lightdash_list_spaces` - See spaces user can access
- `lightdash_get_embed_url` - Uses org context for RLS

## Response Structure
Returns user object with:
- User UUID
- Email
- First/Last name
- Organization UUID
- Organization name
- Role
- Created date

## Notes
- Organization UUID used for row-level security
- API key permissions affect what's returned
- Mainly used internally by other tools