import re

files = [
    'ARCHITECTURAL_REVIEW.md',
    'IMPLEMENTATION_SUMMARY.md',
    'RUNTIME_TOPICS_GUIDE.md',
    'IMPROVEMENTS_SUMMARY.md'
]

for filepath in files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and fix empty code blocks
    # Pattern: triple backticks followed by newline and non-backtick content
    fixed = re.sub(r'```\n([A-Za-z0-9\+\-\*\|\#\[\]\{\}\(\) ])', r'```text\n\1', content)
    
    # Also fix cases where code blocks start with specific patterns
    fixed = re.sub(r'```\n(Application|User Input|TopicProvider|main\.py|--)', r'```text\n\1', fixed)
    fixed = re.sub(r'```\n(├|└|│|Before:|After:)', r'```text\n\1', fixed)
    fixed = re.sub(r'```\n(\d+\.)', r'```text\n\1', fixed)  # numbered lists
    fixed = re.sub(r'```\n(####|###)', r'```markdown\n\1', fixed)  # markdown headers
    fixed = re.sub(r'```\n(self\.|class |def )', r'```python\n\1', fixed)  # Python code
    fixed = re.sub(r'```\n(\$|PS )', r'```powershell\n\1', fixed)  # Shell commands
    
    with open(filepath, 'w', encoding='utf-8', newline='\n') as f:
        f.write(fixed)
    
    print(f'✓ Fixed {filepath}')

print('\nAll markdown files fixed!')
