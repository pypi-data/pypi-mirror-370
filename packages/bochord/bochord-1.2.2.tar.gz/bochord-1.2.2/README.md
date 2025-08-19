# bochord

Backup books from macOS Books to usable ePubs

This works because macOS Books with iCloud turned on stores books as exploded
epub directories with their proper titles as the directory name. This program
zips them up into epub archives to a specified backup dir and copies other,
non-epub dir files, like PDFs, to that directory as well.

## Why

I like to manage my books with Apple Books instead of Calibre for convenience on
all my Apple devices, but Apple makes it a pain to export books
programmatically. Backing up books like this also defends against Apple making
all my books inaccessible someday for no reason.
