## ✨ Features

### 👥 Team Management
| Command | Description |
|---|---|
| `/team-setup` | Creates a full team (category, channels, role) |
| `/team-supp` | Deletes an entire team |
| `/team-add` | Adds a member to a team |
| `/team-remove` | Removes a member from a team |
| `/team-list` | Lists all active teams |
| `/team-info` | Displays all members of a team |
| `/team-fix` | Manually links a role to a team |

### 🛠️ Utilities
| Command | Description |
|---|---|
| `/ping` | Shows bot latency |
| `/userinfo` | Displays member information |
| `/serverinfo` | Shows server stats |
| `/avatar` | Displays a member's avatar in full size |
| `/poll` | Creates a poll |
| `/say` | Bot repeats a message (admin only) |
| `/mp` | Sends an anonymous DM to a member |

### 🎮 Fun
| Command | Description |
|---|---|
| `/8ball` | Ask the bot a question |
| `/pfc` | Rock Paper Scissors |
| `/de` | Roll a dice |
| `/coinflip` | Heads or tails |
| `/random-membre` | Picks a random member |
| `/calcul` | Simple calculator |
| `/blague` | Random joke |
| `/ship` | Compatibility between 2 members |
| `/compliment` | Random compliment |
| `/insulte` | Funny (non-offensive) insult |
| `/citation` | Inspirational quote |
| `/deviner` | Guess a number between 1 and 100 |
| `/verite-ou-defi` | Truth or dare |
| `/top-membres` | Leaderboard of members with most roles |

### ❓ Help
| Command | Description |
|---|---|
| `/help` | Interactive help menu with dropdown |
| `invite` | Sends the server invite link (no prefix needed) |

---

## 🚀 Getting Started

### Requirements
- Python 3.11+
- A Discord bot created on the [Developer Portal](https://discord.com/developers/applications)

### 1. Clone the repository
```bash
git clone https://github.com/mineloulou/urabot.git
cd urabot
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up your token
Create a `TOKEN` environment variable with your Discord bot token:
```bash
export TOKEN=your_token_here
```

### 4. Run the bot
```bash
python bot.py
```

---

## ☁️ Hosting

This bot is hosted on **Replit** (free tier).

1. Create an account at [replit.com](https://replit.com)
2. Upload `bot.py` and `requirements.txt`
3. Add `TOKEN` in the **Secrets** tab
4. Hit Run ▶️

---

## ⚙️ Configuration

Edit these variables in `bot.py` to match your server:

```python
ROLE_MEMBRE_ID = 1476761476508155974  # Member role ID
GUILD_ID = 1476624785524920332        # Your server ID
```

---

## 🔒 Required Permissions

The bot requires the following permissions:
- ✅ Administrator (recommended)
- ✅ Manage Channels
- ✅ Manage Roles
- ✅ Send Messages
- ✅ Read Message History

---

## 📦 Dependencies

```
discord.py==2.3.2
```

---

## 🌐 Join the Server

[![Discord](https://img.shields.io/badge/Join_UraCraft-7289DA?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/V3S5QfQdkD)

---

## 📄 License

This project is licensed under the **MIT License** — free to use and modify.