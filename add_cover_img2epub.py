import argparse
import sys
from pathlib import Path
from core.epub import EpubGenerator

def main():
    parser = argparse.ArgumentParser(description="Generate EPUB from Markdown and Cover Image")
    parser.add_argument("markdown_file", help="Path to the bilingual Markdown file")
    parser.add_argument("--cover", help="Path to the cover image (default: {markdown_stem}_cover.png)")
    parser.add_argument("--output", help="Path to the output EPUB file (default: {markdown_stem}.epub)")
    parser.add_argument("--title", help="Title of the book (default: derived from filename)")

    args = parser.parse_args()

    md_path = Path(args.markdown_file)
    if not md_path.exists():
        print(f"❌ Error: Markdown file not found: {md_path}")
        sys.exit(1)

    # Determine cover image path
    if args.cover:
        cover_path = Path(args.cover)
    else:
        # Try to find cover image with common naming patterns
        possible_covers = [
            md_path.parent / f"{md_path.stem}_cover.png",
            md_path.parent / f"{md_path.stem.replace('_bilingual', '')}_bilingual_cover.png",
            md_path.parent / "cover.png"
        ]
        cover_path = None
        for p in possible_covers:
            if p.exists():
                cover_path = p
                break
        
        if not cover_path:
            print(f"⚠️ Warning: No cover image found. Tried: {[str(p) for p in possible_covers]}")

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = md_path.with_suffix(".epub")

    # Determine title
    title = args.title or md_path.stem.replace("_bilingual", "").replace("_", " ")

    print(f"🚀 Generating EPUB...")
    print(f"📝 Markdown: {md_path}")
    print(f"🎨 Cover: {cover_path if cover_path else 'None'}")
    print(f"📚 Output: {output_path}")
    print(f"📖 Title: {title}")

    generator = EpubGenerator()
    try:
        generator.generate(
            str(md_path),
            str(output_path),
            str(cover_path) if cover_path else None,
            title=title
        )
        print(f"✅ EPUB generated successfully: {output_path}")
    except Exception as e:
        print(f"❌ Failed to generate EPUB: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

# usage: add_cover_img2epub.py [-h] markdown_file
#                            [--cover cover] [--output output] [--title title]
# example: python add_cover_img2epub.py "path/to/bilingual.md" --cover "path/to/cover.png" --output "book.epub"
# python add_cover_img2epub.py "output/Deep-Sky Companions Southern Gems Southern Gems (Stephen James OMeara) (2013)/auto/Deep-Sky Companions Southern Gems Southern Gems (Stephen James OMeara) (2013)_bilingual.md" --cover "output/Deep-Sky Companions Southern Gems Southern Gems (Stephen James OMeara) (2013)/auto/Deep-Sky Companions Southern Gems Southern Gems (Stephen James OMeara) (2013)_bilingual_cover.png" --output "output/Deep-Sky Companions Southern Gems Southern Gems (Stephen James OMeara) (2013)/auto/Deep-Sky Companions Southern Gems Southern Gems (Stephen James OMeara) (2013)_bilingual.epub"
# python add_cover_img2epub.py "output/Deep-Sky Companions Hidden Treasures (Stephen James OMeara) (2007)/auto/Deep-Sky Companions Hidden Treasures (Stephen James OMeara) (2007)_bilingual.md" --cover "output/Deep-Sky Companions Hidden Treasures (Stephen James OMeara) (2007)/auto/Deep-Sky Companions Hidden Treasures (Stephen James OMeara) (2007)_bilingual_cover.png" --output "output/Deep-Sky Companions Hidden Treasures (Stephen James OMeara) (2007)/auto/Deep-Sky Companions Hidden Treasures (Stephen James OMeara) (2007)_bilingual.epub"
# python add_cover_img2epub.py "output/Deep Sky Companions The Messier Objects (Deep-Sky Companions) (Stephen James OMeara) (1998)/auto/Deep Sky Companions The Messier Objects (1998)_bilingual.md" --cover "output/Deep Sky Companions The Messier Objects (Deep-Sky Companions) (Stephen James OMeara) (1998)/auto/Deep Sky Companions The Messier Objects (1998)_bilingual_cover.png" --output "output/Deep Sky Companions The Messier Objects (Deep-Sky Companions) (Stephen James OMeara) (1998)/auto/Deep Sky Companions The Messier Objects (1998)_bilingual.epub"    