from pathlib import Path
from PIL import Image


def setup_output_dirs(output_base: Path) -> tuple[Path, Path]:
    """
    Create and return paths for image and markdown output directories.

    Args:
        output_base (Path): The base directory for output.
    """
    image_dir = output_base / "images"
    markdown_dir = output_base / "markdown"

    image_dir.mkdir(parents=True, exist_ok=True)
    markdown_dir.mkdir(parents=True, exist_ok=True)

    return image_dir, markdown_dir


def resize_image(image_path: str, output_path: str, width: int) -> None:
    """
    Resize an image to the specified width while maintaining aspect ratio.

    Args:
        image_path (str): Path to the input image file
        output_path (str): Path where the resized image will be saved
        width (int): Desired width of the image
    """
    if width == 0:
        return
    else:
        img = Image.open(image_path)
        w_percent = width / float(img.size[0])
        h_size = int((float(img.size[1]) * float(w_percent)))
        img = img.resize((width, h_size), Image.Resampling.LANCZOS)
        img.save(output_path)


def merge_markdown_files(markdown_dir: Path, pdf_filename: str = None) -> Path:
    """
    Merge all individual markdown files into a single merged file.

    Args:
        markdown_dir (Path): Directory containing individual markdown files.
        pdf_filename (str): Optional original PDF filename to use for merged file.

    Returns:
        Path: Path to the created merged file.
    """
    markdown_files = sorted(markdown_dir.glob("page_*.md"))
    
    # Determine the merged filename
    if pdf_filename:
        # Remove .pdf extension if present and add .md
        base_name = Path(pdf_filename).stem
        merged_filename = f"{base_name}.md"
    else:
        merged_filename = "merged.md"
    
    merged_file = markdown_dir / merged_filename

    if markdown_files:
        with open(merged_file, "w", encoding="utf-8") as merged_f:
            merged_f.write("# Merged Document\n\n")
            merged_f.write(f"*Generated from {len(markdown_files)} pages*\n\n")
            merged_f.write("---\n\n")
            
            for i, md_file in enumerate(markdown_files, 1):
                with open(md_file, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read().strip()
                    if content:  # Only add non-empty content
                        merged_f.write(content)
                        merged_f.write("\n\n")
                        if i < len(markdown_files):  # Add separator between pages
                            merged_f.write("---\n\n")

    return merged_file
