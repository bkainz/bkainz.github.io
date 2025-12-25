#!/usr/bin/env python3
import re
from collections import defaultdict

def parse_bibtex(filename):
    """Parse BibTeX file and return list of entries"""
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    entries = []
    # Match @type{key, ... }
    pattern = r'@(\w+)\{([^,]+),\s*(.*?)\n\}'
    
    for match in re.finditer(pattern, content, re.DOTALL):
        entry_type = match.group(1)
        entry_key = match.group(2)
        entry_content = match.group(3)
        
        # Parse fields
        fields = {}
        field_pattern = r'(\w+)\s*=\s*\{([^}]*)\}|(\w+)\s*=\s*"([^"]*)"'
        for field_match in re.finditer(field_pattern, entry_content):
            if field_match.group(1):
                field_name = field_match.group(1)
                field_value = field_match.group(2)
            else:
                field_name = field_match.group(3)
                field_value = field_match.group(4)
            fields[field_name] = field_value
        
        entries.append({
            'type': entry_type,
            'key': entry_key,
            'fields': fields
        })
    
    return entries

def extract_year(entry):
    """Extract year from entry"""
    year = entry['fields'].get('year', '0000')
    try:
        return int(year)
    except:
        return 0

def is_top_journal(journal_name):
    """Check if journal is a top-tier journal - all journals get badge"""
    if not journal_name:
        return False
    # All journals are top journals (inverted logic)
    return True

def is_top_conference(venue):
    """Check if conference is top-tier - all conferences except workshops, BVM, arXiv, medRxiv"""
    if not venue:
        return False
    venue_lower = venue.lower()
    # Exclude workshops, BVM, arXiv, medRxiv
    excluded = ['workshop', 'bvm', 'arxiv', 'medrxiv']
    return not any(exc in venue_lower for exc in excluded)

def format_authors(authors):
    """Format author list"""
    if not authors:
        return ""
    # Replace 'and' with comma
    authors = authors.replace(' and ', ', ')
    # Bold Kainz, B or Kainz, Bernhard
    authors = re.sub(r'Kainz, Bernhard', '<strong>Kainz, B.</strong>', authors)
    authors = re.sub(r'Kainz, B\.', '<strong>Kainz, B.</strong>', authors)
    return authors

def format_entry(entry):
    """Format a single entry as HTML"""
    fields = entry['fields']
    entry_type = entry['type']
    
    title = fields.get('title', 'No title')
    authors = format_authors(fields.get('author', ''))
    year = fields.get('year', '')
    
    # Clean title
    title = title.replace('{', '').replace('}', '')
    
    html = f'<li>\n'
    html += f'  <div class="pub-entry">\n'
    
    # Check if top-tier
    is_top = False
    badge = ''
    
    if entry_type == 'article':
        journal = fields.get('journal', '')
        volume = fields.get('volume', '')
        number = fields.get('number', '')
        pages = fields.get('pages', '')
        
        if is_top_journal(journal):
            is_top = True
            badge = '<span class="badge badge-journal">Top Journal</span>'
        
        html += f'    <div class="pub-title">{title} {badge}</div>\n'
        html += f'    <div class="pub-authors">{authors}</div>\n'
        html += f'    <div class="pub-venue"><em>{journal}</em>'
        
        if volume:
            html += f', {volume}'
        if number:
            html += f'({number})'
        if pages:
            html += f':{pages}'
        html += f', {year}</div>\n'
        
    elif entry_type == 'inproceedings':
        booktitle = fields.get('booktitle', '')
        pages = fields.get('pages', '')
        organization = fields.get('organization', '')
        
        if is_top_conference(booktitle):
            is_top = True
            badge = '<span class="badge badge-conference">Top Conference</span>'
        
        html += f'    <div class="pub-title">{title} {badge}</div>\n'
        html += f'    <div class="pub-authors">{authors}</div>\n'
        html += f'    <div class="pub-venue">In <em>{booktitle}</em>'
        
        if pages:
            html += f', pp. {pages}'
        html += f', {year}</div>\n'
    
    else:
        # Other types
        html += f'    <div class="pub-title">{title}</div>\n'
        html += f'    <div class="pub-authors">{authors}</div>\n'
        html += f'    <div class="pub-venue">{year}</div>\n'
    
    html += f'  </div>\n'
    html += f'</li>\n'
    
    return html, is_top

def generate_publication_list(entries):
    """Generate HTML publication list"""
    # Group by year
    by_year = defaultdict(list)
    for entry in entries:
        year = extract_year(entry)
        by_year[year].append(entry)
    
    # Sort years descending
    sorted_years = sorted(by_year.keys(), reverse=True)
    
    html = ''
    
    # First, featured publications (top-tier from recent years)
    html += '<h2>Selected Publications (Top-Tier Venues)</h2>\n'
    html += '<ul class="publication-list featured">\n'
    
    featured_count = 0
    for year in sorted_years:
        if year < 2018:  # Only recent ones for featured
            continue
        for entry in by_year[year]:
            entry_html, is_top = format_entry(entry)
            if is_top:
                html += entry_html
                featured_count += 1
    
    html += '</ul>\n'
    
    # Full list by year
    html += '<h2>Complete Publication List</h2>\n'
    
    for year in sorted_years:
        if year == 0:
            continue
        html += f'<h3>{year}</h3>\n'
        html += '<ul class="publication-list">\n'
        
        for entry in by_year[year]:
            entry_html, _ = format_entry(entry)
            html += entry_html
        
        html += '</ul>\n'
    
    return html

# Parse and generate
entries = parse_bibtex('publications2025.bib')
pub_html = generate_publication_list(entries)

# Save to file
with open('publications_generated.html', 'w', encoding='utf-8') as f:
    f.write(pub_html)

print(f"Generated HTML with {len(entries)} publications")
