# Quick Fix for deskMATE

## The Problem
The `_create_open_resource_intent` method is missing from `app/core/llm_client.py`.

## The Solution
Add this method to the file after line 272 (after `_create_shell_intent`):

```python
def _create_open_resource_intent(self, command: str) -> Intent:
    """Create open resource intent for URLs, apps, or file explorer"""
    command_lower = command.lower()
    
    # Check for URLs
    if any(x in command_lower for x in ['.com', '.org', '.net', 'http', 'www.', 'youtube', 'google']):
        url = command_lower.replace('open', '').replace('visit', '').replace('go to', '').strip()
        return Intent(
            intent="open_resource",
            target=url,
            steps=[{"action": "open_url", "params": {"url": url}}],
            confirmation_required=False,
            assumptions=["url is valid"]
        )
        
    # Check for file explorer
    elif 'explorer' in command_lower or 'folder' in command_lower or 'directory' in command_lower:
        path = "."
        return Intent(
            intent="open_resource",
            target="file explorer",
            steps=[{"action": "open_explorer", "params": {"path": path}}],
            confirmation_required=False,
            assumptions=["path exists"]
        )
        
    # Default to application
    else:
        app_name = command_lower.replace('open', '').replace('launch', '').replace('start', '').strip()
        return Intent(
            intent="open_resource",
            target=app_name,
            steps=[{"action": "open_app", "params": {"app_name": app_name}}],
            confirmation_required=False,
            assumptions=["application is installed"]
        )
```

## Steps to Fix:
1. Restore the file: `git checkout app/core/llm_client.py`
2. Open `app/core/llm_client.py` in your editor
3. Find line 272 (end of `_create_shell_intent` method)
4. Add the above method after it
5. Save the file
6. The server should auto-reload

Then your app will work!
