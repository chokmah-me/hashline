## Base Hashline Instructions

Your patch language uses stable line anchors from the last read.

[PATH#TAG]

Operations:
- SWAP N.=M:   replace original lines N to M (inclusive) with the following + lines
- DEL N        delete line N
- INS.POST N:  insert the following + lines after line N
- INS.PRE N:   insert before line N
- INS.HEAD:    insert at start of file
- INS.TAIL:    insert at end of file

Body lines start with + (use bare + for blank line).

Critical rules:
1. Always re-read after applying a patch (new TAG is issued).
2. Only touch lines that actually change.
3. Never echo old content in the + body.
4. Use exact numbers from the latest read output.