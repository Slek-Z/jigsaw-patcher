#!/bin/bash
# jigsaw-patcher shell script
# Copyright (C) 2018 Slek.

if [ "$#" -ne 2 ]; then
  echo "Usage: jigsaw-patcher SOURCE TARGET"
  exit 1
fi

tmpdir=$(mktemp -d)

source="$1"
source_filename="${source##*/}"

target="$2"
target_filename="${target##*/}"
target_stem="${target_filename%.*}"

echo "Creating patch"

xdelta3 -f -e -s "$1" "$2" "$tmpdir/$target_stem.xdelta"

echo "@echo off" > "$tmpdir/$target_stem.bat"
echo "echo $target_stem.bat created with Jigsaw-patcher. https://github.com/Slek-Z/jigsaw-patcher" >> "$tmpdir/$target_stem.bat"
echo "echo Patch to use in Microsoft Windows." >> "$tmpdir/$target_stem.bat"
echo "echo." >> "$tmpdir/$target_stem.bat"
echo "echo Old file: $source_filename." >> "$tmpdir/$target_stem.bat"
echo "echo New file: $target_filename." >> "$tmpdir/$target_stem.bat"
echo "echo Applying patch..." >> "$tmpdir/$target_stem.bat"
echo "xdelta3.0u.x86-32.exe -d -s \"$source_filename\" \"$target_stem.xdelta\" \"$target_filename\"" >> "$tmpdir/$target_stem.bat"
echo "echo Patch applied." >> "$tmpdir/$target_stem.bat"
echo "pause" >> "$tmpdir/$target_stem.bat"

echo "#!/bin/bash" > "$tmpdir/$target_stem.sh"
echo >> "$tmpdir/$target_stem.sh"
echo "echo \"$target_stem.sh created with Jigsaw-patcher. https://github.com/Slek-Z/jigsaw-patcher\"" >> "$tmpdir/$target_stem.sh"
echo "echo \"Patch to use in GNU/Linux.\"" >> "$tmpdir/$target_stem.sh"
echo "echo " >> "$tmpdir/$target_stem.sh"
echo "echo \"Old file $source_filename.\"" >> "$tmpdir/$target_stem.sh"
echo "echo \"New file: $target_filename.\"" >> "$tmpdir/$target_stem.sh"
echo "echo \"Applying patch...\"" >> "$tmpdir/$target_stem.sh"
echo "./xdelta3.0v.x86-32.bin -d -s \"$source_filename\" \"$target_stem.xdelta\" \"$target_filename\"" >> "$tmpdir/$target_stem.sh"
echo "echo \"Patch applied.\"" >> "$tmpdir/$target_stem.sh"
echo "read -p \"Press a key to exit...\"" >> "$tmpdir/$target_stem.sh"
echo "exit 0" >> "$tmpdir/$target_stem.sh"
echo "fi" >> "$tmpdir/$target_stem.sh"

chmod +x "$tmpdir/$target_stem.sh"

echo "readme.txt" > "$tmpdir/readme.txt"
echo "Patch created with Jigsaw-patcher, thanks to xdelta3." >> "$tmpdir/readme.txt"
echo >> "$tmpdir/readme.txt"
echo "To patch under Microsoft Windows run the file with the extension: .bat" >> "$tmpdir/readme.txt"
echo "To patch under GNU/Linux run the file with the extension: .sh" >> "$tmpdir/readme.txt"
echo >> "$tmpdir/readme.txt"
echo "It is necessary to put the original file in the same folder, with the patch files." >> "$tmpdir/readme.txt"
echo >> "$tmpdir/readme.txt"
echo "Visit the web project @ https://github.com/Slek-Z/jigsaw-patcher" >> "$tmpdir/readme.txt"

zip -j -T "$target_stem.zip" "$tmpdir/$target_stem.bat" "$tmpdir/$target_stem.sh" "$tmpdir/$target_stem.xdelta" "$tmpdir/readme.txt" ./data/xdelta3.0u.x86-32.exe ./data/xdelta3.0v.x86-32.bin

rm -R "$tmpdir"