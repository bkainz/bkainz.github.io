#!/usr/bin/env python3
import re
from collections import defaultdict

def parse_bibtex(filename):
    """Parse BibTeX file and return list of entries (deduplicated by title)"""
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    entries = []
    seen_titles = set()
    duplicates_count = 0
    
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
        
        # Check for duplicate title
        title = fields.get('title', '').strip().lower().replace('{', '').replace('}', '')
        if title and title in seen_titles:
            duplicates_count += 1
            continue  # Skip duplicate
        
        if title:
            seen_titles.add(title)
        
        entries.append({
            'type': entry_type,
            'key': entry_key,
            'fields': fields
        })
    
    if duplicates_count > 0:
        print(f"Removed {duplicates_count} duplicate entries")
    
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
    """Check if conference is top-tier - all conferences except workshops, BVM, arXiv"""
    if not venue:
        return False
    venue_lower = venue.lower()
    # Exclude workshops, BVM (Bildverarbeitung fuer die Medizin), and arXiv only (not medrxiv journals)
    excluded = ['workshop', 'bvm', 'bildverarbeitung']
    # Special case: exclude if it's arxiv but NOT if it's a journal containing arxiv (like medrxiv)
    if 'arxiv' in venue_lower and 'medrxiv' not in venue_lower:
        return False
    return not any(exc in venue_lower for exc in excluded)

def format_authors(authors):
    """Format author list and handle LaTeX special characters"""
    if not authors:
        return ""
    
    # Handle LaTeX umlauts: \"a or {\"a} -> ä
    authors = re.sub(r'\{?\\"([aouAOU])\}?', lambda m: {'a': 'ä', 'o': 'ö', 'u': 'ü', 'A': 'Ä', 'O': 'Ö', 'U': 'Ü'}[m.group(1)], authors)
    
    # Handle other common LaTeX accents
    authors = re.sub(r"\{?\\'([eaiouEAIOU])\}?", lambda m: {'e': 'é', 'a': 'á', 'i': 'í', 'o': 'ó', 'u': 'ú', 'E': 'É', 'A': 'Á', 'I': 'Í', 'O': 'Ó', 'U': 'Ú'}[m.group(1)], authors)
    authors = re.sub(r'\{?\\`([eaiouEAIOU])\}?', lambda m: {'e': 'è', 'a': 'à', 'i': 'ì', 'o': 'ò', 'u': 'ù', 'E': 'È', 'A': 'À', 'I': 'Ì', 'O': 'Ò', 'U': 'Ù'}[m.group(1)], authors)
    authors = re.sub(r'\{?\\\^([eaiouEAIOU])\}?', lambda m: {'e': 'ê', 'a': 'â', 'i': 'î', 'o': 'ô', 'u': 'û', 'E': 'Ê', 'A': 'Â', 'I': 'Î', 'O': 'Ô', 'U': 'Û'}[m.group(1)], authors)
    authors = re.sub(r'\{?\\~([nNoO])\}?', lambda m: {'n': 'ñ', 'N': 'Ñ', 'o': 'õ', 'O': 'Õ'}[m.group(1)], authors)
    authors = re.sub(r'\{?\\c c\}?', 'ç', authors)
    authors = re.sub(r'\{?\\c C\}?', 'Ç', authors)
    authors = re.sub(r'\{?\\ss\}?', 'ß', authors)
    
    # Remove remaining curly braces
    authors = authors.replace('{', '').replace('}', '')
    
    # Replace 'and' with comma
    authors = authors.replace(' and ', ', ')
    
    # Bold Kainz - handle both "Kainz, Bernhard" and "Kainz, B." formats
    # Do Bernhard first, which converts to B., then do B. only if not already tagged
    authors = re.sub(r'Kainz, Bernhard\b', 'Kainz, B.', authors)
    authors = re.sub(r'(?<!<strong>)Kainz, B\.(?!</strong>)', '<strong>Kainz, B.</strong>', authors)
    
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
    
    # Just render complete list by year with highlights
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
