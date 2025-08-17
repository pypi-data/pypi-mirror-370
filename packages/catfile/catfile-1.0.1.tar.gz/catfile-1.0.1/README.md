# catfile

A simple Python script that automatically organizes files in a directory into folders based on their file types.  
If a file type is not recognized, it will be placed in the `others` folder.

## Features
- Sorts files into categories such as `application`, `images`, `documents`, `spreadsheets`, `presentation`, `audio`, `video`, `archives`, `code`
- Automatically creates the target folders if they don't exist
- Puts unknown file types into an `others` folder
- Cross-platform support (Linux, macOS, Windows)

## Example
Before sorting:
![Alt text](reference/before.png?raw=true "Before")

After Sorting :
![Alt text](reference/after.png?raw=true "After") 

## How to Install

## How to Use
- Open terminal in the directory you want to sort
- Type `catfile `
- `directories` (optional) use to determined wich directories you want the script to run. If empty will default into the current directory
- `flags` (optional) use to determine wich directories you want to create. If empty will create all directories 
### Flags
flags determined wich directories will be created, you can combine multiple flags by typing `catfile -flags`. 
- `-a` create a directory for applications only
- `-i` create a directory for images only
- `-d` create a directory for documents only
- `-s` create a directory for spreadsheets only
- `-p` → create a directory for Presentations only
- `-au` → create a directory for Audio files only
- `-v` → create a directory for Videos only
- `-ar` → create a directory for Archives / compressed files only
- `-c` → create a directory for Code / source files only
### You can combine multiple arguments for example:
```bash
catfile Downloads/ -a -c -d
```
Will sort files in the Downloads directories that match the directories created wich is `applicaton`, `code`, and `documents` 

## Supported File Types
- Applications <br />
`.exe, .msi, .bat, .cmd, .app, .dmg, .pkg, .bin, .run, .sh, .deb, .rpm, .jar, .apk, .xpi`

- Images <br />
`.jpg, .jpeg, .png, .gif, .bmp, .tiff, .tif, .webp, .avif, .heif, .heic, .svg, .eps, .ai, .cr2, .cr3, .nef, .arw, .orf, .rw2, .dng`

- Documents<br />
`.txt, .rtf, .odt, .md, .doc, .docx, .dot, .dotx, .pdf, .epub, .mobi, .azw3`

- Spreadsheets<br />
`.xls, .xlsx, .xlsm, .xlsb, .xlt, .xltx, .xltm, .ods, .ots, .csv, .tsv, .numbers`

- Presentations<br />
`.ppt, .pptx, .pptm, .pot, .potx, .potm, .odp, .otp, .key`

- Audio<br />
`.mp3, .aac, .ogg, .wma, .m4a, .wav, .flac, .alac, .aiff, .aif, .opus, .amr, .mid, .midi`

- Video<br />
`.mp4, .m4v, .mov, .avi, .wmv, .flv, .mkv, .webm, .ogv, .3gp, .3g2, .mts, .m2ts, .ts, .vob`

- Archives<br />
`.zip, .rar, .7z, .tar, .gz, .bz2, .xz, .iso, .img, .dmg, .vhd, .vhdx, .tgz, .tbz2, .lz, .z`

- Code<br />
`.html, .htm, .css, .js, .mjs, .cjs, .ts, .tsx, .php, .phtml, .rb, .aspx, .cshtml, .py, .pyw, .ipynb, .java, .c, .h, .cpp, .cc, .cxx, .hpp, .hxx, .cs, .go, .rs, .kt, .kts, .swift, .m, .mm, .sh, .bash, .ps1, .pl, .pm, .lua, .r, .R, .m, .jl, .sas, .yml, .yaml, .json, .xml, .toml, .ini, .md`

