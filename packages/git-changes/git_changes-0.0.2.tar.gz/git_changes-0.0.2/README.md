# git-changes

I just want to manage my commit messages.

---

## Why?

i just want to keep track of the changes that I make. Instead of adding many changes at once and then writing a long commit message, I just want to add the each change with a message and then commit them.

---

## Installation

```console
pip3 install git-changes
```

---

## Usage

### Initializing

After installing run the below command in a **git repo**

```console
gitc --init
```

### Adding changes with messages

```console
$ git addm file -m 'adding a new file' --type=fix
[fix] adding a new file
```

The `--type` is optional. The currently supported choices for `--type` are

```console
$ git addm -help
usage: gitc-add [-h] -m MESSAGE [--type {feat,fix,docs,style,refactor,perf,test,build,ci,chore,revert}]

options:
  -h, --help            show this help message and exit
  -m MESSAGE, --message MESSAGE
                        Message to add
  --type {feat,fix,docs,style,refactor,perf,test,build,ci,chore,revert}
                        The type of the change
```


### Show Message

To list all the messages that will added to the next commit, run

```console
$ git show-messages
[fix] new hello file
[fix] adding a new file
[perf] fix some_function
[refactor] change var name
```

### Commit

In order to commit with all these message all you have to do is run.

```console
$ git commit
```
This will open up commit message editor with all the set message for the current commit.

![Terminal image](docs/image.png)

> NOTE: you cannot simply save and exit this file; since this is a template you have to make
> some changes to it. I suggest adding a title that summarizes all these changes.

After a successful commit all the messages will be automatically removed.

```console
$ git show-messages
No commit messages yet!.. To add new message run
git addm -m <message> [--type]

```

### Bye...
