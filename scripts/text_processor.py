#!/usr/bin/env python3
"""
Text Processing Utilities for Hindu Scriptures
Helps convert and process scripture files for better Q&A performance.
"""

import os
import re
from pathlib import Path
from typing import List, Dict

def clean_text(text: str) -> str:
    """Clean and normalize text content."""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep Sanskrit diacritics
    text = re.sub(r'[^\w\s\u0900-\u097F\u0100-\u017F\u1E00-\u1EFF.,;:!?()-]', '', text)
    
    # Normalize line breaks
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    return text.strip()

def extract_verses(text: str) -> List[Dict[str, str]]:
    """Extract individual verses from scripture text."""
    verses = []
    
    # Pattern for verse numbers (e.g., "2.47:", "Verse 2.47:", etc.)
    verse_pattern = r'(?:Verse\s+)?(\d+\.?\d*):?\s*'
    
    # Split text by verse patterns
    parts = re.split(verse_pattern, text)
    
    for i in range(1, len(parts), 2):
        if i + 1 < len(parts):
            verse_num = parts[i].strip()
            verse_text = parts[i + 1].strip()
            
            if verse_text and len(verse_text) > 20:  # Filter out very short segments
                verses.append({
                    'number': verse_num,
                    'text': clean_text(verse_text)
                })
    
    return verses

def extract_chapters(text: str) -> List[Dict[str, str]]:
    """Extract chapters from scripture text."""
    chapters = []
    
    # Pattern for chapter headings
    chapter_pattern = r'(?:Chapter\s+)?(\d+):?\s*([^\n]+)'
    
    # Find all chapter matches
    matches = re.finditer(chapter_pattern, text, re.IGNORECASE)
    
    for match in matches:
        chapter_num = match.group(1)
        chapter_title = match.group(2).strip()
        
        chapters.append({
            'number': chapter_num,
            'title': chapter_title
        })
    
    return chapters

def process_text_file(file_path: Path) -> Dict:
    """Process a single text file and extract structured information."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Clean the content
        cleaned_content = clean_text(content)
        
        # Extract verses and chapters
        verses = extract_verses(content)
        chapters = extract_chapters(content)
        
        # Split into paragraphs for better search
        paragraphs = [p.strip() for p in cleaned_content.split('\n\n') if len(p.strip()) > 50]
        
        return {
            'filename': file_path.name,
            'content': cleaned_content,
            'verses': verses,
            'chapters': chapters,
            'paragraphs': paragraphs,
            'word_count': len(cleaned_content.split()),
            'verse_count': len(verses),
            'chapter_count': len(chapters)
        }
    
    except Exception as e:
        print(f"❌ Error processing {file_path.name}: {e}")
        return None

def process_all_texts(texts_dir: Path = Path("hindu_texts")) -> List[Dict]:
    """Process all text files in the hindu_texts directory."""
    if not texts_dir.exists():
        print(f"❌ Directory {texts_dir} not found!")
        return []
    
    txt_files = list(texts_dir.glob("*.txt"))
    
    if not txt_files:
        print("⚠️ No .txt files found in hindu_texts directory")
        return []
    
    processed_texts = []
    
    print(f"📚 Processing {len(txt_files)} text files...")
    
    for file_path in txt_files:
        print(f"Processing: {file_path.name}")
        result = process_text_file(file_path)
        
        if result:
            processed_texts.append(result)
            print(f"✅ {file_path.name}: {result['word_count']} words, {result['verse_count']} verses, {result['chapter_count']} chapters")
        else:
            print(f"❌ Failed to process {file_path.name}")
    
    return processed_texts

def create_summary_report(processed_texts: List[Dict]) -> str:
    """Create a summary report of all processed texts."""
    if not processed_texts:
        return "No texts processed."
    
    total_words = sum(text['word_count'] for text in processed_texts)
    total_verses = sum(text['verse_count'] for text in processed_texts)
    total_chapters = sum(text['chapter_count'] for text in processed_texts)
    
    report = f"""
🕉️ Hindu Scriptures Collection Summary
{'=' * 50}

📊 Statistics:
• Total Files: {len(processed_texts)}
• Total Words: {total_words:,}
• Total Verses: {total_verses}
• Total Chapters: {total_chapters}

📚 Files Processed:
"""
    
    for text in processed_texts:
        report += f"• {text['filename']}: {text['word_count']:,} words, {text['verse_count']} verses\n"
    
    return report

def main():
    """Main function for text processing."""
    print("🕉️ Hindu Scriptures Text Processor")
    print("=" * 50)
    
    # Process all texts
    processed_texts = process_all_texts()
    
    if processed_texts:
        # Create summary report
        report = create_summary_report(processed_texts)
        print(report)
        
        # Save report to file
        with open("docs/text_processing_report.md", "w", encoding="utf-8") as f:
            f.write(report)
        
        print(f"\n✅ Processing complete! Report saved to docs/text_processing_report.md")
    else:
        print("❌ No texts were successfully processed.")

if __name__ == "__main__":
    main() 