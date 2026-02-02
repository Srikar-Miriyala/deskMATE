# FINAL FIX - Copy and Paste This Exactly

## Problem
The file `app/core/llm_client.py` is missing the `_create_open_resource_intent` method.

## Solution
1. Open `app/core/llm_client.py`
2. Go to line 272 (the line with just `        )` after `_create_shell_intent`)
3. Press Enter to create a new line
4. Paste this EXACT code (make sure indentation is correct - 4 spaces):

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

5. Save the file
6. Wait for uvicorn to reload (you'll see "Application startup complete" in the terminal)
7. Try your app!

## Important
- The method starts with 4 spaces (class-level indentation)
- The code inside has 8 spaces
- Don't add extra blank lines
- Make sure it's after `_create_shell_intent` and before `_extract_filename`
