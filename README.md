# PDFParser
Parses PDF text and annotations with regex, spits out a CSV of matches.

I wrote this very quickly because I got really annoyed with how unintuitive Adobe Readers COM bindings for VBA Were. I figured if I was going to introduce a dependency (Specific version of Adobe Reader), I may as well make it my own dependency.

There are a few dirty hacks that I used because I found windows was being weird when the path ended in \ due to it being an escape character.


# Usage
written as a command line program

-input: Select input file (if --directory or --recursive flags are used it will parse the directory instead)

-output: file to write.

-regex: regex command to use

## optional flags:

--notext: Supress text search (Used for searching for annotations only)

--annotation: Enables annotation searching

--directory: will search the directory rather than the file 

--recursive: will search the directory and all of its subfolders recursivly. 
