# Shell Scripting Cheat Sheet

> Personal reference guide for everyday shell scripting tasks.

## Quick Reference Table

| Topic      | Key Syntax                     | Example                                           |
|------------|-------------------------------|---------------------------------------------------|
| Variable   | `VAR="value"`               | `NAME="DevOps"`                                 |
| Argument   | `$1`, `$2`                    | `./script.sh arg1 arg2`                           |
| If         | `if [ condition ]; then`      | `if [ -f file ]; then`                            |
| For loop   | `for i in list; do`           | `for i in 1 2 3; do`                              |
| Function   | `name() { ... }`              | `greet() { echo "Hi"; }`                        |
| Grep       | `grep pattern file`           | `grep -i "error" log.txt`                       |
| Awk        | `awk '{print $1}' file`       | `awk -F: '{print $1}' /etc/passwd`               |
| Sed        | `sed 's/old/new/g' file`      | `sed -i 's/foo/bar/g' config.txt`                 |

---

## 1. Basics

### Shebang
```bash
#!/bin/bash  # tells the kernel which interpreter to use
```

### Running a script
```bash
chmod +x script.sh        # make executable
./script.sh                # run via path
bash script.sh             # run with bash explicitly
```

### Comments
```bash
# full line comment
echo hi  # inline comment
```

### Variables
```bash
VAR=hello                  # no spaces around =
echo "$VAR"              # expands with quoting
echo '$VAR'                # literal $VAR
```

### Reading user input
```bash
read -p "Name? " name
echo "Hi, $name"
```

### Command-line arguments
```bash
echo "script: $0"
echo "first arg: $1"
echo "count: $#"
echo "all: $@"
command; echo "exit code:$?"
```

## 2. Operators and Conditionals

### String comparisons
```bash
if [ "$a" = "x" ]; then echo yes; fi
if [ -z "$a" ]; then echo empty; fi
```

### Integer comparisons
```bash
if [ $n -lt 10 ]; then echo small; fi
if [ $n -ge 100 ]; then echo big; fi
```

### File tests
```bash
[ -f file ] && echo regular
[ -d dir ] && echo directory
[ -x prog ] && echo executable
```

### if/elif/else
```bash
if [ cond ]; then
  ...
elif [ cond2 ]; then
  ...
else
  ...
fi
```

### Logical operators
```bash
[ -f a ] && echo exists
[ -f a ] || echo no
if ! [ -z "$var" ]; then ... fi
```

### Case statement
```bash
case $1 in
  start) echo starting ;;  
  stop)  echo stopping ;;  
  *)     echo usage ;;     
 esac
```

## 3. Loops

### for loop
```bash
for item in a b c; do echo $item; done
for ((i=0;i<5;i++)); do echo $i; done  # C-style
```

### while loop
```bash
count=0
while [ $count -lt 3 ]; do
  echo $count
  ((count++))
done
```

### until loop
```bash
i=5
until [ $i -le 0 ]; do
  echo $i
  ((i--))
done
```

### Control
```bash
for i in {1..5}; do
  [ $i -eq 3 ] && continue
  [ $i -eq 4 ] && break
  echo $i
done
```

### Loop over files
```bash
for file in *.log; do
  echo "processing $file"
done
```

### Loop over command output
```bash
ps aux | while read line; do
  echo "line: $line"
done
```

## 4. Functions

```bash
myfunc() {                # define
  echo "arg1=$1"
  return 5              # set exit code
}

myfunc foo             # call
rc=$?                  # return code
```

### Arguments & return
```bash
add() {
  local x=$1 y=$2
  echo $((x+y))         # use echo for output
}
sum=$(add 3 4)
```

### Local variables
```bash
func() {
  local tmp="hi"
  echo $tmp
}
```

## 5. Text Processing Commands

### grep
```bash
grep pattern file           # basic
grep -i "error" file       # ignore case
grep -r "foo" /path        # recursive
grep -c "match" file       # count
grep -n "match" file       # line numbers
grep -v "skip" file        # inverse
grep -E "a|b" file         # extended regex
```

### awk
```bash
awk '{print $1}' file               # first column
awk -F: '{print $1}' /etc/passwd    # custom FS
awk '/error/ {count++} END{print count}' file
```

### sed
```bash
sed 's/old/new/g' file               # substitute
sed '/^#/d' file                     # delete lines
sed -i 's/foo/bar/g' file            # in-place
```

### cut
```bash
cut -d, -f1 file                     # comma delimiter
```

### sort/uniq
```bash
sort file                          # alphabetical
sort -n file                       # numeric
sort -u file                       # unique
uniq file                          # remove dupes
uniq -c file                       # count
```

### tr
```bash
echo "aA" | tr '[:upper:]' '[:lower:]'
tr -d '\r' < file                  # delete
```

### wc
```bash
wc -l file   # lines
wc -w file   # words
wc -c file   # bytes
```

### head/tail
```bash
head -n 5 file           # first 5 lines
tail -n 5 file           # last 5 lines
tail -f file             # follow
```

## 6. Useful Patterns and One‑Liners

- **Find/delete old files**: `find /tmp -type f -mtime +30 -delete`
- **Count lines in logs**: `wc -l *.log`
- **Replace string in many files**: `grep -rl foo . | xargs sed -i 's/foo/bar/g'`
- **Check service**: `systemctl is-active --quiet ssh && echo running`
- **Disk alert**: `df -h | awk '$5>80{print $0}'`
- **Parse CSV**: `awk -F, '{print $2}' file.csv`
- **Tail+filter errors**: `tail -f app.log | grep --line-buffered ERROR`

## 7. Error Handling and Debugging

```bash
cmd
echo $?             # exit status
exit 0              # success
exit 1              # failure
```

```bash
set -e               # exit on error
set -u               # unset vars are errors
set -o pipefail      # fail if any pipe command fails
set -x               # trace execution
```

```bash
trap 'echo cleanup; rm /tmp/foo' EXIT  # run on exit
```

