# Fix markdown formatting issues
$files = @(
    'ARCHITECTURAL_REVIEW.md',
    'IMPLEMENTATION_SUMMARY.md',
    'RUNTIME_TOPICS_GUIDE.md',
    'IMPROVEMENTS_SUMMARY.md'
)

foreach ($file in $files) {
    Write-Host "Fixing $file..."
    $content = Get-Content $file -Raw -Encoding UTF8
    
    # Fix table separators - add spaces around pipes
    $content = $content -replace '\|(\-+)\|', { 
        $dashes = $Matches[1]
        "| $dashes |"
    }
    
    # Fix empty code blocks followed by text - add text language
    $content = $content -replace '(?m)^```\r?\n([A-Za-Z0-9\+\-\*\#\s])', '```text${1}'
    
    # Fix empty code blocks followed by directory structure
    $content = $content -replace '(?m)^```\r?\n(Application|User Input|TopicProvider)', '```text${1}'
    
    # Save back
    $content | Set-Content $file -Encoding UTF8 -NoNewline
    Write-Host "  Done with $file"
}

Write-Host ""
Write-Host "All markdown files fixed."
