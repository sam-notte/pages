#!/usr/bin/env python3
"""
Gemini-Powered GEO Analyzer
Analyzes websites for Generative Engine Optimization using Google Gemini
"""

import sys
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from datetime import datetime
import json

def fetch_page_content(url):
    """Fetch and extract content from a webpage"""
    print(f"📥 Fetching content from {url}...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract key elements
    title = soup.find('title').text if soup.find('title') else 'No title'
    
    meta_desc = ''
    meta_tag = soup.find('meta', {'name': 'description'})
    if meta_tag:
        meta_desc = meta_tag.get('content', '')
    
    # Get all text content
    for script in soup(["script", "style"]):
        script.decompose()
    
    text_content = soup.get_text()
    lines = (line.strip() for line in text_content.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = ' '.join(chunk for chunk in chunks if chunk)
    
    # Get headings
    headings = {
        'h1': [h.text.strip() for h in soup.find_all('h1')],
        'h2': [h.text.strip() for h in soup.find_all('h2')],
        'h3': [h.text.strip() for h in soup.find_all('h3')],
    }
    
    return {
        'url': url,
        'title': title,
        'meta_description': meta_desc,
        'headings': headings,
        'content': text[:10000],  # Limit to first 10k chars
        'word_count': len(text.split())
    }

def analyze_with_gemini(page_data, api_key):
    """Analyze content for GEO using Gemini"""
    print("🤖 Analyzing with Gemini AI for GEO optimization...")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    prompt = f"""You are an expert in Generative Engine Optimization (GEO) - optimizing content to be cited by AI search engines like Google AI Overviews, Perplexity, ChatGPT, and SearchGPT.

Analyze this webpage for GEO optimization:

**URL:** {page_data['url']}
**Title:** {page_data['title']}
**Meta Description:** {page_data['meta_description']}
**Word Count:** {page_data['word_count']}

**H1 Headings:** {', '.join(page_data['headings']['h1'])}
**H2 Headings:** {', '.join(page_data['headings']['h2'][:5])}

**Content Preview:**
{page_data['content'][:3000]}

---

Provide a comprehensive GEO analysis with:

## 1. GEO Score (1-10)
Rate the current GEO-readiness with explanation.

## 2. Expertise Signals Analysis
- What expertise signals are present/missing?
- How can the page demonstrate more authority?
- What credentials, data, or research should be added?

## 3. AI Citation Potential
- Would AI engines likely cite this page? Why/why not?
- What makes content citation-worthy for AI?
- Specific gaps preventing AI citations

## 4. Content Depth & Structure
- Is content comprehensive enough for AI?
- Content structure issues for AI parsing
- Missing topics or angles

## 5. Conversational Engagement
- How conversational is the tone?
- Does it answer questions AI users might ask?
- FAQ-style improvements needed

## 6. Specific Action Items
Provide 5-10 concrete, actionable recommendations prioritized by impact.

Be specific, technical, and actionable. Focus on what will make AI engines trust and cite this source."""

    response = model.generate_content(prompt)
    return response.text

def format_analysis(analysis):
    """Convert markdown-style formatting to proper HTML structure"""
    import re
    
    lines = analysis.split('\n')
    formatted_lines = []
    in_list = False
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            formatted_lines.append('')
            continue
        
        # Headers
        if line.startswith('## '):
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            header_text = line[3:].strip()
            formatted_lines.append(f'<h3>{header_text}</h3>')
            
        elif line.startswith('### '):
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            header_text = line[4:].strip()
            formatted_lines.append(f'<h4>{header_text}</h4>')
            
        # Bullet points
        elif line.startswith('- ') or line.startswith('* '):
            if not in_list:
                formatted_lines.append('<ul>')
                in_list = True
            item_text = line[2:].strip()
            # Process inline formatting
            item_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', item_text)
            item_text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', item_text)
            formatted_lines.append(f'<li>{item_text}</li>')
            
        # Regular paragraphs
        else:
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            
            # Process inline formatting
            line = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)
            line = re.sub(r'\*(.*?)\*', r'<em>\1</em>', line)
            
            # Only wrap in <p> if it's not already HTML
            if not line.startswith('<'):
                formatted_lines.append(f'<p>{line}</p>')
            else:
                formatted_lines.append(line)
    
    # Close any remaining list
    if in_list:
        formatted_lines.append('</ul>')
    
    return '\n'.join(formatted_lines)

def generate_html_report(page_data, analysis):
    """Generate HTML report"""
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GEO Analysis Report - {page_data['url']}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header .url {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .metadata {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .metadata h2 {{
            color: #667eea;
            margin-bottom: 15px;
        }}
        
        .meta-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        
        .meta-item {{
            padding: 15px;
            background: #f8f9fa;
            border-radius: 5px;
            border-left: 4px solid #667eea;
        }}
        
        .meta-item strong {{
            display: block;
            color: #667eea;
            margin-bottom: 5px;
        }}
        
        .analysis {{
            background: white;
            padding: 35px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        
        .analysis h2 {{
            color: #667eea;
            margin-top: 30px;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #f0f0f0;
        }}
        
        .analysis h2:first-child {{
            margin-top: 0;
        }}
        
        .analysis h3 {{
            color: #764ba2;
            margin-top: 20px;
            margin-bottom: 10px;
        }}
        
        .analysis ul {{
            margin-left: 25px;
            margin-top: 10px;
        }}
        
        .analysis li {{
            margin-bottom: 8px;
        }}
        
        .analysis p {{
            margin-bottom: 15px;
        }}
        
        .analysis strong {{
            color: #667eea;
        }}
        
        .analysis code {{
            background: #f8f9fa;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        
        .analysis h4 {{
            color: #555;
            margin-top: 15px;
            margin-bottom: 8px;
            font-size: 1.1em;
        }}
        
        .analysis ul {{
            margin: 15px 0;
            padding-left: 25px;
        }}
        
        .analysis li {{
            margin-bottom: 8px;
            line-height: 1.6;
        }}
        
        .analysis strong {{
            color: #667eea;
            font-weight: 600;
        }}
        
        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            margin-top: 40px;
        }}
        
        .timestamp {{
            background: white;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 10px;
            }}
            
            .header {{
                padding: 20px;
            }}
            
            .header h1 {{
                font-size: 1.8em;
            }}
            
            .meta-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 GEO Analysis Report</h1>
            <div class="url">{page_data['url']}</div>
        </div>
        
        <div class="timestamp">
            <strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
        
        <div class="metadata">
            <h2>📊 Page Metadata</h2>
            <div class="meta-grid">
                <div class="meta-item">
                    <strong>Title</strong>
                    {page_data['title']}
                </div>
                <div class="meta-item">
                    <strong>Word Count</strong>
                    {page_data['word_count']} words
                </div>
                <div class="meta-item">
                    <strong>H1 Headings</strong>
                    {len(page_data['headings']['h1'])} found
                </div>
                <div class="meta-item">
                    <strong>H2 Headings</strong>
                    {len(page_data['headings']['h2'])} found
                </div>
            </div>
            
            <div style="margin-top: 20px;">
                <strong style="color: #667eea;">Meta Description:</strong>
                <p style="margin-top: 5px;">{page_data['meta_description'] or 'No meta description found'}</p>
            </div>
        </div>
        
        <div class="analysis">
            <h2>🤖 Gemini AI GEO Analysis</h2>
            <div style="line-height: 1.8;">{format_analysis(analysis)}</div>
        </div>
        
    </div>
</body>
</html>"""
    
    return html

def main():
    if len(sys.argv) < 2:
        print("Usage: python gemini_geo_analyzer.py <url> [gemini_api_key]")
        print("\nExample:")
        print("  python gemini_geo_analyzer.py https://example.com")
        print("  python gemini_geo_analyzer.py https://example.com YOUR_API_KEY")
        sys.exit(1)
    
    url = sys.argv[1]
    api_key = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Try to get API key from environment if not provided
    if not api_key:
        import os
        api_key = os.environ.get('GEMINI_API_KEY')
    
    if not api_key:
        print("❌ Error: No Gemini API key provided!")
        print("Provide it as argument or set GEMINI_API_KEY environment variable")
        sys.exit(1)
    
    try:
        # Fetch page content
        page_data = fetch_page_content(url)
        
        print(f"✅ Fetched {page_data['word_count']} words from {url}")
        print(f"   Title: {page_data['title']}")
        print(f"   H1s: {len(page_data['headings']['h1'])}, H2s: {len(page_data['headings']['h2'])}")
        
        # Analyze with Gemini
        analysis = analyze_with_gemini(page_data, api_key)
        
        print("✅ GEO analysis complete!")
        
        # Generate report
        html_report = generate_html_report(page_data, analysis)
        
        # Save report
        filename = f"geo-report-{url.replace('https://', '').replace('http://', '').replace('/', '-')}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_report)
        
        print(f"\n🎉 Report saved: {filename}")
        print(f"\n📊 Quick Summary:")
        print(analysis[:500] + "...\n")
        
        # Try to open the report
        import os
        if sys.platform == 'darwin':  # macOS
            os.system(f'open "{filename}"')
        elif sys.platform == 'win32':  # Windows
            os.system(f'start "{filename}"')
        else:  # Linux
            os.system(f'xdg-open "{filename}"')
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

