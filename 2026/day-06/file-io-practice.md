# File I/O Practice Notes

## Goal
Create a small text file and practice basic read/write operations using shell commands.

## Commands (run on your machine)
1. `touch notes.txt`  # create empty file
2. `echo "Line 1" > notes.txt`  # write first line
3. `echo "Line 2" >> notes.txt`  # append second line
4. `echo "Line 3" | tee -a notes.txt`  # append and display
5. `cat notes.txt`  # read full file
6. `head -n 2 notes.txt`  # read first 2 lines
7. `tail -n 2 notes.txt`  # read last 2 lines

## Expected `notes.txt` content (example)
Line 1
Line 2
Line 3

## Quick observations to record
- Command run and exact output (paste outputs in this file)
- Any errors or unexpected behavior
- One sentence learning note (eg: "`tee` is handy to both write and view output")

---

Save this file as `2026/day-06/file-io-practice.md` and commit it to your fork.
