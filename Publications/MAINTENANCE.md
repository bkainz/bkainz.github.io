# Website Maintenance Guide
*Internal documentation for bkainz.github.io*

Last updated: December 25, 2025

## Overview

This document provides comprehensive guidance for maintaining and updating the personal academic website. The site uses Jekyll/GitHub Pages and includes automated tools for publication management.

---

## 1. Publication List Management

### Quick Update Process

1. Export publications from Google Scholar to BibTeX format
2. Replace or update `Publications/publications2025.bib`
3. Run the parser: `cd Publications && python3 parse_bib.py`
4. Update the website: `head -321 index.html > new_index.html && cat publications_generated.html >> new_index.html && mv new_index.html index.html`
5. Commit and push changes

### Automated BibTeX Parser (`parse_bib.py`)

**Location:** `/Publications/parse_bib.py`

**Key Features:**
- **Automatic duplicate removal** - Deduplicates based on normalized titles (case-insensitive, removes braces)
- **Year correction** - Fixes Google Scholar export bug (1804 → 2018)
- **LaTeX character handling** - Converts umlauts and special characters:
  - `{\"u}` → ü, `{\"a}` → ä, `{\"o}` → ö
  - `{\'e}` → é, `{\`e}` → è, `{\^e}` → ê
  - `{\~n}` → ñ, `{\ss}` → ß, etc.
- **Nested brace support** - Properly parses fields with nested braces like `M{\"u}ller`
- **Reverse chronological numbering** - Publications numbered from total count down to 1
- **Smart badge assignment** - Top Journal/Top Conference badges with configurable exclusions

**Badge Logic:**

*Top Journal Badge (Green):*
- Applied to ALL journals EXCEPT:
  - arXiv preprints
  - CoRR
  - medRxiv

*Top Conference Badge (Blue):*
- Applied to ALL conferences EXCEPT:
  - Workshops (contains "workshop")
  - BVM/Bildverarbeitung für die Medizin
  - arXiv
  - RöFo (Fortschritte auf dem Gebiet der Röntgenstrahlen)

**Current Statistics:**
- Total publications: 407
- Duplicates removed per run: ~22
- File: `publications2025.bib` (3,486 lines)

### Modifying Badge Criteria

Edit the functions in `parse_bib.py`:

```python
def is_top_journal(journal_name):
    # Modify excluded list to add/remove journals
    excluded = ['arxiv', 'corr', 'medrxiv']
    
def is_top_conference(venue):
    # Modify excluded list to add/remove venues
    excluded = ['workshop', 'bvm', 'bildverarbeitung', 'rofo', 'fortschritte']
```

### HTML Integration

The parser generates `publications_generated.html` which is inserted into `index.html` after line 321 (the closing `</style>` tag). The integration includes:
- Custom CSS for publication styling
- Flexbox layout for numbering
- Badge styling (green for journals, blue for conferences)
- Hover effects for publication entries

**Critical:** Always ensure the CSS section is properly closed with `</style>` before the generated content begins, or the entire publication list will be invisible!

---

## 2. Team Page Management

### Adding New Team Members

**Location:** `/team/index.html`

**Process:**
1. Add team member photo to `/team/` directory
2. Edit `team/index.html` and add entry in appropriate row
3. Follow existing HTML structure:

```html
<div class="team-member">
  <div class="image">
    <img src="MemberName.jpg">
  </div>
  <div class="caption">
    <h3>Member Name</h3>
    <p>Position/Role</p>
    <p>Affiliation (if applicable)</p>
    <div class="social-links">
      <a href="mailto:email@example.com"><i class="fas fa-envelope"></i></a>
      <a href="URL"><i class="fab fa-linkedin"></i></a>
    </div>
  </div>
</div>
```

**Team Structure:**
- **Row 1:** Principal Investigator
- **Row 2:** Collaborators
- **Row 3-5:** Senior Researchers, Postdocs
- **Row 6-7:** PhD Students, Researchers
- **Row 8:** Team Support
- **Alumni Section:** Former team members

### Moving to Alumni

1. Copy entire team member `<div class="team-member">...</div>`
2. Paste in Alumni section at bottom of page
3. Remove from current position
4. Update photo if needed

---

## 3. Research Content Updates

### NeurIPS Highlights Section

**Location:** `Publications/index.html` lines ~110-130

Update annually with new conference papers. Includes:
- Paper titles and descriptions
- Links to arXiv, code repositories, weights
- Project-specific information

### Research Streams

**Location:** `Publications/index.html` lines ~20-100

Five main categories:
1. Real-Time Clinical Guidance & Human-AI Collaboration
2. Normative Learning & Population Health
3. Explainable AI & Causal Reasoning
4. Advanced Image Analysis & Reconstruction
5. Data Augmentation & Synthetic Data

Update project links and descriptions as needed.

### Acknowledgments

**Location:** `Publications/index.html` lines ~140-148

Currently includes:
- NHR@FAU (projects b143dc, b180dc)
- Isambard-AI AIRR
- ERC MIA-NORMAL 101083647
- DFG grants
- State of Bavaria (HTA)

---

## 4. File Structure

```
bkainz.github.io/
├── Publications/
│   ├── index.html              # Main publications page
│   ├── parse_bib.py           # BibTeX parser script
│   ├── publications2025.bib   # Source BibTeX database
│   ├── publications_generated.html  # Auto-generated HTML
│   └── MAINTENANCE.md         # This file
├── team/
│   ├── index.html             # Team page
│   └── [member photos]        # Individual team member images
├── _layouts/
│   ├── default.html           # Site template
│   └── post.html
├── css/
│   └── main.css               # Global styles
└── [other pages]
```

---

## 5. Common Tasks & Commands

### Update Publications from Fresh Google Scholar Export

```bash
# 1. Replace BibTeX file (via upload or copy)
# 2. Navigate to Publications directory
cd /Users/bernhardkainz/bkainz.github.io/Publications

# 3. Run parser
python3 parse_bib.py

# 4. Update index.html (line 321 is end of CSS)
head -321 index.html > new_index.html
cat publications_generated.html >> new_index.html
mv new_index.html index.html

# 5. Commit and push
cd ..
git add Publications/publications2025.bib Publications/index.html Publications/publications_generated.html
git commit -m "Update publication list from Google Scholar export"
git push
```

### Add Single Publication Manually

Edit `publications2025.bib` and add entry, then follow update process above.

### Fix Broken Publication Display

**Symptom:** Only see "Publications" heading, no list.

**Cause:** Missing `</style>` tag or malformed CSS.

**Fix:** Ensure line ~321 in `index.html` ends with proper CSS closure:

```html
.badge-conference {
    background-color: #2196f3;
    color: white;
}

</style>

<h3>2026</h3>
```

### Update Team Member Affiliation

```bash
# Edit team/index.html
# Find member's <div class="caption"> section
# Add/modify <p> tag with affiliation

git add team/index.html
git commit -m "Update team member affiliation"
git push
```

---

## 6. Parser Technical Details

### Entry Parsing Algorithm

1. **Regex pattern** matches `@type{key, fields}`
2. **Field extraction** handles nested braces by counting brace depth
3. **Title normalization** for duplicate detection (lowercase, remove braces)
4. **Author processing:**
   - LaTeX special character conversion
   - "and" → comma separation
   - Kainz name normalization (Bernhard → B.)
5. **HTML generation:**
   - Flexbox layout with number and content divs
   - Conditional badge insertion
   - Proper field formatting (volume, pages, etc.)

### Year Extraction with Auto-Fix

```python
def extract_year(entry):
    year = entry['fields'].get('year', '0000')
    year_int = int(year)
    # Fix Google Scholar bug
    if year_int == 1804:
        return 2018
    return year_int
```

### Numbering System

Publications are counted in reverse:
```python
total_pubs = sum(len(by_year[year]) for year in sorted_years if year != 0)
current_number = total_pubs  # Start at highest

# Decrement for each publication
for entry in by_year[year]:
    entry_html, _ = format_entry(entry, current_number)
    current_number -= 1
```

---

## 7. CSS Styling Reference

### Publication List Classes

- `.publication-list` - Container for publications
- `.pub-entry` - Flexbox container (number + content)
- `.pub-number` - Blue numbering on left (45px width)
- `.pub-content` - Main content flex container
- `.pub-title` - Publication title (1.05em)
- `.pub-authors` - Author list (0.95em, gray)
- `.pub-venue` - Journal/conference info (0.9em, lighter gray)
- `.badge` - Base badge styling
- `.badge-journal` - Green badge for journals
- `.badge-conference` - Blue badge for conferences

### Hover Effects

Publications have subtle hover animations:
- Border color changes to blue
- Box shadow appears
- Smooth transition (0.2s)

---

## 8. Git Workflow

### Standard Commit Pattern

```bash
git add [files]
git commit -m "Descriptive message"
git push
```

### Check Status Before Committing

```bash
git status
# Review modified files and unstaged changes
```

### Common Commit Messages

- "Update publication list from Google Scholar export"
- "Add new team member [Name]"
- "Move [Name] to alumni"
- "Update research highlights for [Conference/Year]"
- "Fix [specific issue]"

---

## 9. Troubleshooting

### Publication List Not Showing

1. Check for `</style>` closure in index.html around line 321
2. Verify badge CSS is present:
   ```css
   .badge-journal { background-color: #4caf50; color: white; }
   .badge-conference { background-color: #2196f3; color: white; }
   ```
3. Confirm publications_generated.html exists and has content
4. Check browser console for CSS/HTML errors

### Parser Errors

1. **"Removed X duplicate entries"** - Normal, indicates duplicates found
2. **LaTeX character issues** - Update format_authors() regex patterns
3. **Missing fields** - Parser handles gracefully with get() defaults
4. **Year parsing errors** - Check extract_year() function

### Badge Not Appearing

1. Check venue/journal name in BibTeX
2. Verify exclusion lists in is_top_journal()/is_top_conference()
3. Ensure badge HTML is generated in format_entry()

---

## 10. Future Enhancements

### Potential Improvements

- **DOI/PDF links** - Add URL field parsing from BibTeX
- **Citation metrics** - Integrate Google Scholar API
- **Search functionality** - JavaScript-based publication filtering
- **Export options** - Generate CV-ready publication lists
- **Author highlighting** - Re-add name bolding with multi-author support
- **Venue abbreviations** - Expand common conference acronyms

### Adding New Features

When modifying `parse_bib.py`:
1. Test on a copy of the BibTeX file first
2. Verify output in `publications_generated.html`
3. Check rendering in browser before committing
4. Update this maintenance guide

---

## 11. Contact & Support

**Primary Contact:** Bernhard Kainz

**Key Files to Back Up:**
- `Publications/publications2025.bib` - Source data
- `Publications/parse_bib.py` - Parser logic
- `team/index.html` - Team configuration
- `Publications/index.html` - Research content

**Repository:** https://github.com/bkainz/bkainz.github.io

---

## Version History

- **v1.0** (Dec 25, 2025) - Initial maintenance documentation
  - 407 publications with automated parsing
  - Reverse numbering system
  - Smart badge logic
  - Comprehensive LaTeX character support
  - Duplicate detection and removal

---

*End of Maintenance Guide*
