import os
import shutil
import argparse

#if Dir does not exist
def mkdir(base_dir, directories):
    for dir in directories:
        path = os.path.join(base_dir, dir)
        if not os.path.exists(path):
            os.makedirs(path)

def sort_files(base_dir, allowed_categories, all_file_types):
    for file in os.listdir(base_dir):
        path = os.path.join(base_dir, file)

        # Skip directories and hidden files
        if os.path.isdir(path) or file.startswith('.'):
            continue

        file_ext = os.path.splitext(file)[1].lower()

        for category, extensions in all_file_types.items():
            if category in allowed_categories and file_ext in extensions:
                target_dir = os.path.join(base_dir, category)
                shutil.move(path, target_dir)
                break   

def main():
    file_types = {
        'Application' : [
                        # Windows executables and installers
                        ".exe", ".msi", ".bat", ".cmd",

                        # macOS applications and packages
                        ".app", ".dmg", ".pkg",

                        # Linux / Unix executables and installers
                        ".bin", ".run", ".sh", ".deb", ".rpm",

                        # Cross-platform / other executable formats
                        ".jar", ".apk", ".xpi"],
        'Images': [# Common Raster Formats
                   ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif",

                   # Web & Modern Formats
                   ".webp", ".avif", ".heif", ".heic",

                   # Vector Formats
                   ".svg", ".eps", ".ai",

                   # RAW Camera Formats (common ones)
                   ".cr2", ".cr3", ".nef", ".arw", ".orf", ".rw2", ".dng"],
        'Documents': [# Text Documents
                      ".txt", ".rtf", ".odt", ".md",

                      # Microsoft Word & Similar
                      ".doc", ".docx", ".dot", ".dotx",

                      # PDFs & Other Read-Only Docs
                      ".pdf",

                      # eBooks
                      ".epub", ".mobi", ".azw3"],
        "Spreadsheets": [# Microsoft Excel
                        ".xls", ".xlsx", ".xlsm", ".xlsb", ".xlt", ".xltx", ".xltm",

                        # OpenDocument & LibreOffice
                        ".ods", ".ots",

                        # Comma/Tab Delimited
                        ".csv", ".tsv",

                        # Other spreadsheet formats
                        ".numbers"],
        'Presentations': [# Microsoft PowerPoint
                          ".ppt", ".pptx", ".pptm", ".pot", ".potx", ".potm",

                          # OpenDocument & LibreOffice
                          ".odp", ".otp",

                          # Other presentation formats
                          ".key"],
        'Audio': [# Common Compressed Formats
                  ".mp3", ".aac", ".ogg", ".wma", ".m4a",

                  # Uncompressed / Lossless Formats
                  ".wav", ".flac", ".alac", ".aiff", ".aif",

                  # Other / Less Common
                  ".opus", ".amr", ".mid", ".midi"],
        'Video': [# Common Formats
                  ".mp4", ".m4v", ".mov", ".avi", ".wmv", ".flv", ".mkv",

                  # Web & Streaming Formats
                  ".webm", ".ogv",

                  # Other / Less Common
                  ".3gp", ".3g2", ".mts", ".m2ts", ".ts", ".vob"],
        'Archives': [# Common Archive Formats
                     ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz",

                     # Disk Image Formats
                     ".iso", ".img", ".dmg", ".vhd", ".vhdx",

                     # Other / Less Common
                     ".tgz", ".tbz2", ".lz", ".z"],
        'Code': [# Web Development
                ".html", ".htm",
                ".css",
                ".js", ".mjs", ".cjs",
                ".ts", ".tsx",
                ".php", ".phtml",
                ".rb",
                ".aspx", ".cshtml",

                # General-Purpose Programming
                ".py", ".pyw", ".ipynb",
                ".java",
                ".c", ".h",
                ".cpp", ".cc", ".cxx", ".hpp", ".hxx",
                ".cs",
                ".go",
                ".rs",
                ".kt", ".kts",
                ".swift",
                ".m", ".mm",

                # Scripting Languages
                ".sh",
                ".bash",
                ".ps1",
                ".pl", ".pm",
                ".lua",

                # Data Science / Analytics
                ".r", ".R",
                ".m",  # MATLAB
                ".jl",
                ".sas",

                # Markup & Configuration
                ".yml", ".yaml",
                ".json",
                ".xml",
                ".toml",
                ".ini",
                ".md"],
        'Others': []}
    
    #Map CLI flags to category names
    flag_map = {
    "a": "Application",
    "i": "Images",
    "d": "Documents",
    "s": "Spreadsheets",
    "p": "Presentations",
    "au": "Audio",
    "v": "Video",
    "ar": "Archives",
    "c": "Code"
    }

    #Parse Command 
    parser = argparse.ArgumentParser(description="Sort files into selected categories.")
    parser.add_argument("directory", nargs="?", default=".", help="Directory to sort")
    for flag, name in flag_map.items():
        parser.add_argument(f"-{flag}", action="store_true", help=f"Include {name} files")
    args = parser.parse_args()

    base_dir = os.path.abspath(args.directory)

    selected_categories = [category for flag, category in flag_map.items() if getattr(args, flag)]

    if not selected_categories:
        #No flags → process all categories
        selected_categories = list(file_types.keys())
        mkdir(base_dir, selected_categories)
        sort_files(base_dir, selected_categories, file_types)
    else:
        mkdir(base_dir, selected_categories)
        sort_files(base_dir, selected_categories, file_types)

if __name__ == "__main__":
    main()
