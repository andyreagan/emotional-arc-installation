diskutil rename "NO NAME" BOOK
sleep .5
cp metadata/$1.json /Volumes/BOOK/metadata.json
sleep .5
diskutil unmountDisk BOOK
