import json

# Read files
with open('Linacre-LLM-Benchmarks/src/style.css', 'r') as f:
    css = f.read()

with open('Linacre-LLM-Benchmarks/src/script.js', 'r') as f:
    js = f.read()

with open('Linacre-LLM-Benchmarks/src/data/models.json', 'r') as f:
    models_data = f.read()

with open('Linacre-LLM-Benchmarks/src/index.html', 'r') as f:
    html = f.read()

# Make CSS cooler (CSS4 vibe)
css = css.replace('--bg-dark: #0a0a12;', '--bg-dark: color-mix(in oklch, #0a0a12, #1a1a2e 20%);')
css = css.replace('.glass-panel {', '.glass-panel {\n    backdrop-filter: blur(25px) saturate(120%);\n    -webkit-backdrop-filter: blur(25px) saturate(120%);\n    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);\n    background: linear-gradient(135deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.01));\n    border-top: 1px solid rgba(255, 255, 255, 0.1);\n    border-left: 1px solid rgba(255, 255, 255, 0.1);\n')

# Replace link with style block
html = html.replace('<link rel="stylesheet" href="style.css">', f'<style>\n{css}\n</style>')

# Replace script fetch with inline data
js = js.replace("const response = await fetch('data/models.json');\n        categoriesData = await response.json();", f"categoriesData = {models_data};")

# Replace script tag with inline script
html = html.replace('<script src="script.js"></script>', f'<script>\n{js}\n</script>')

# Write to preview.html and overwrite index.html
with open('Linacre-LLM-Benchmarks/src/index.html', 'w') as f:
    f.write(html)

print("Bundled into index.html successfully.")
