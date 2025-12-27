import re
import sys
from pathlib import Path

def fix_markdown(file_path):
    path = Path(file_path)
    if not path.exists():
        print(f"File not found: {path}")
        return

    content = path.read_text(encoding='utf-8')
    
    # Replacements for malformed equals signs in HTML attributes
    # These seem to be LaTeX math artifacts from OCR/Translation
    
    # Replace $=, $\varepsilon$, $\equiv$, $\cdot^{=}$, $\cong$ with =
    # We need to be careful not to break actual math, but these are inside HTML tags usually
    # or look like attributes.
    
    # Regex for attributes: key $...$ "value"
    # But the patterns are inconsistent.
    
    # Simple string replacements for common patterns observed
    replacements = [
        (r'\$=', '='),
        (r'\$\\varepsilon\$', '='),
        (r'\$\\equiv\$', '='),
        (r'\$\\cdot\^\{=\}\$', '='),
        (r'\$\\cong\$', '='),
        (r'\$\\textless/\$\\textbar\{\\textmd h\}3\>', '</h3>'), # specific broken tag seen in line 5459
        (r'\$<\$', '<'),
        (r'\$>\$', '>'),
        (r'\$="', '="'),
        (r'\%\\\$ "', '%"'), # width $="100\%$ " -> width="100%"
        (r'\$ "', '"'),
    ]
    
    new_content = content
    
    # 1. Fix specific observed patterns
    new_content = new_content.replace('$=', '=')
    new_content = new_content.replace('$\\varepsilon$', '=')
    new_content = new_content.replace('$\\equiv$', '=')
    new_content = new_content.replace('$\\cdot^{=}$', '=')
    new_content = new_content.replace('$\\cong$', '=')
    
    # 2. Fix width="100\%$ " -> width="100%"
    new_content = new_content.replace('width $="100\\%$ "', 'width="100%"')
    new_content = new_content.replace('width $="20\\%$ "', 'width="20%"')
    
    # 3. Fix other weird artifacts
    # <corepatterns:department attribute $=$ "id"/ $>$ -> ... />
    new_content = new_content.replace('/ $>$', '/>')
    new_content = new_content.replace('$>$', '>')
    new_content = new_content.replace('$<$', '<')
    
    # 4. Fix JSP include directive artifacts
    # $<\frac{\circ}{\circ}\textcircled{<}$ include $\%>.$ -> <%@ include %>
    # This is very specific.
    new_content = new_content.replace('$<\\frac{\\circ}{\\circ}\\textcircled{<}$', '<%@')
    new_content = new_content.replace('$\\%>.$', '%>')
    
    # 5. Fix <jsp:include ... flush $\varepsilon$ "true"/>
    # Already handled by step 1
    
    # 6. Fix <table border $^{*=}$ "1"
    new_content = new_content.replace('$^{*=}$', '=')
    
    # 7. Fix duplicate table rows/content if possible? 
    # The duplication seems to be: English block, then English block again?
    # No, looking at the file:
    # 5809: <table ...
    # 5811: <table ... (Duplicate?)
    # It seems the translation model outputted the source text again or something.
    # But fixing syntax is safer than deleting content blindly.
    
    if content != new_content:
        path.write_text(new_content, encoding='utf-8')
        print(f"Fixed {file_path}")
    else:
        print(f"No changes made to {file_path}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        fix_markdown(sys.argv[1])
    else:
        print("Usage: python fix_markdown.py <file_path>")
