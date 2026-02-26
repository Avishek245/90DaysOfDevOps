# Day 22 Notes - Git Workflow Questions

1. **Difference between `git add` and `git commit`**

   `git add` stages changes by putting modified files into the index (staging area). It tells Git which updates you want to include in the next snapshot. `git commit` takes whatever is currently staged and records a new commit in the repository history with a message.

2. **What does the staging area do? Why doesn't Git just commit directly?**

   The staging area (index) lets you assemble a precise set of changes before committing. You might only want to commit some of your modifications or reorganize edits into multiple logical commits. Without this intermediate step, every change in the working directory would be forced into the next commit, reducing flexibility and clarity.

3. **What information does `git log` show you?**

   `git log` displays the commit history for the current branch. It shows commit hashes, author, date, and commit messages. With options (like `--oneline`, `--graph`) it can also summarize the history or show merges.

4. **What is the `.git/` folder and what happens if you delete it?**

   The `.git/` directory contains all of Git's internal metadata for the repository: object database, configuration, refs, stage, logs, hooks, etc. If you delete it, the folder stops being a Git repository; you lose all version data and history. The working files remain but you cannot run Git commands until you reinitialize.

5. **Difference between working directory, staging area, and repository**

   - **Working directory**: the files and directories you see and edit on disk.
   - **Staging area**: the index where you place selected changes with `git add` before committing.
   - **Repository**: the `.git/` database of committed snapshots and metadata. Commits live here and form the project history.
