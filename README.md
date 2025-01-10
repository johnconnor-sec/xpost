# xp - X Post Scheduler

A command-line tool for posting and scheduling tweets/posts to X (formerly Twitter).

## Features

- Post single tweets or threads immediately
- Schedule tweets/threads for future posting
- List and manage scheduled posts
- Support for reading tweets from files or stdin
- Natural language datetime parsing for scheduling
- Secure credential storage

## Installation

1. Clone the repository:
```bash
git clone https://github.com/johnconnor-sec/xp.git
cd xp
```

2. Build and install using the build script:
```bash
poetry install
poetry run build
```

The executable will be installed in the `dist` directory.
Consider moving the executable to `/usr/local/bin` (root) or `~/.local/bin` (user).

## Usage

### Post immediately

Post a single tweet:
```bash
xp post "Hello, X!"
```

Post a thread:
```bash
xp post "First tweet" "Second tweet" "Third tweet"
```

Post from a file (one tweet per line):
```bash
xp post --file tweets.txt
```

### Schedule posts

Schedule a single tweet:
```bash
xp schedule "My scheduled tweet" --time "tomorrow at 3pm"
```

Schedule a thread:
```bash
xp schedule "First tweet" "Second tweet" --time "next Friday at noon"
```

Natural language time formats supported:
- "tomorrow at 3pm"
- "next Friday at noon"
- "in 2 hours"
- "2023-12-25 15:30:00"

### Manage scheduled posts

List all scheduled posts:
```bash
xp list
```

List with filters:
```bash
xp list --status pending
xp list --status posted
xp list --verbose
```

### Run the scheduler

Start the scheduler daemon to post pending tweets:
```bash
xp run
```

## First-time Setup

On first run, the tool will prompt for your X API credentials:
- Consumer Key
- Consumer Secret
- Access Token
- Access Token Secret

These are stored securely in `~/.tweet/credentials.txt`.

## Requirements

- Python 3.8+
- tweepy
- schedule
- dateparser

## License

MIT License

