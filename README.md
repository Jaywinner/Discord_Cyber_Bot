# 🛡️ Discord Cyber Academy Bot

An interactive Discord bot designed to teach cybersecurity fundamentals through gamified learning experiences. Perfect for Discord communities, educational servers, and anyone looking to learn cybersecurity in an engaging way.

## ✨ Features

### 🎓 Interactive Learning
- **Structured Courses**: Multiple cybersecurity courses from beginner to intermediate
- **Hands-on Lessons**: Practical exercises and real-world examples
- **Interactive Quizzes**: Test knowledge with immediate feedback
- **Progress Tracking**: Monitor learning journey and achievements

### 🎮 Gamification
- **XP System**: Earn experience points for completing lessons
- **Level Progression**: Advance through levels as you learn
- **Achievement Badges**: Unlock special achievements for milestones
- **Leaderboards**: Compete with other learners in your server

### 🔧 Advanced Features
- **Course Selection**: Choose your learning path from available courses
- **Smart Navigation**: Seamless progression between lessons and courses
- **Admin Commands**: Manage content and users (admin only)
- **Modern UI**: Beautiful Discord embeds with interactive buttons

## 📚 Course Structure

### Beginner Level
1. **🛡️ Cybersecurity Fundamentals**
   - What is Cybersecurity?
   - Common Cyber Threats
   - Basic Security Mindset

2. **🔐 Password Security**
   - Password Strength
   - Password Managers
   - Two-Factor Authentication

3. **🎣 Phishing Awareness**
   - Identifying Phishing Emails
   - Social Engineering Tactics
   - Safe Browsing Practices

### Intermediate Level
4. **🌐 Network Security Basics**
   - Understanding Networks
   - Firewalls and VPNs
   - Secure Wi-Fi Practices

5. **🦠 Malware and Protection**
   - Types of Malware
   - Antivirus Solutions
   - Safe Software Practices

6. **🔒 Digital Privacy**
   - Data Protection
   - Privacy Settings
   - Anonymous Browsing

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- A Discord bot token
- Discord server with appropriate permissions

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Jaywinner/Discord_Cyber_Bot.git
   cd Discord_Cyber_Bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your Discord bot token
   ```

4. **Run the bot**
   ```bash
   python bot.py
   ```

### Discord Bot Setup

1. **Create a Discord Application**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Click "New Application" and give it a name
   - Go to the "Bot" section and create a bot
   - Copy the bot token

2. **Set Bot Permissions**
   - In the "OAuth2" > "URL Generator" section
   - Select "bot" scope
   - Select these permissions:
     - Send Messages
     - Use Slash Commands
     - Embed Links
     - Read Message History
     - Add Reactions

3. **Invite Bot to Server**
   - Use the generated URL to invite the bot to your server
   - Make sure the bot has the necessary permissions

## 🎯 Commands

### User Commands
- `!start` - Begin your cybersecurity learning journey
- `!lesson [course] [module] [lesson]` - View a specific lesson or your current lesson
- `!courses` - Browse all available courses
- `!quiz [course] [module] [lesson]` - Take a quiz for a lesson
- `!progress [@user]` - Check learning progress
- `!achievements` - View earned badges and achievements
- `!leaderboard` - See top learners in the server
- `!help_cyber` - Get help with bot commands

### Admin Commands (Admin Only)
- `!admin_stats` - View server statistics
- `!admin_reset_user <user>` - Reset a user's progress
- `!admin_add_xp <user> <amount>` - Add XP to a user
- `!admin_courses` - Manage course content

## 🗄️ Database

The bot uses SQLite for data storage with the following tables:
- **users**: User profiles, XP, levels, and current progress
- **course_progress**: Detailed lesson completion tracking
- **achievements**: User achievement records
- **quiz_attempts**: Quiz performance history

## 🔧 Configuration

### Environment Variables (.env)
```env
# Required
DISCORD_TOKEN=your_bot_token_here

# Optional
GUILD_ID=your_guild_id_here
DATABASE_PATH=academy.db
BOT_PREFIX=!
LOG_LEVEL=INFO
```

### Customization
- **Add New Courses**: Edit `courses.py` to add new learning content
- **Modify Achievements**: Update `achievements.py` for new badges
- **Adjust XP Values**: Customize XP rewards in lesson definitions
- **Change Bot Prefix**: Modify `PREFIX` in `bot.py`

## 📊 Bot Statistics

The bot tracks various metrics:
- Total users and their progress
- Lesson completion rates
- Quiz performance
- Achievement distribution
- Server engagement levels

## 🛠️ Development

### Project Structure
```
Discord_Cyber_Bot/
├── bot.py              # Main bot file
├── database.py         # Database management
├── courses.py          # Course content and structure
├── achievements.py     # Achievement system
├── quiz.py            # Quiz functionality
├── admin.py           # Admin commands
├── requirements.txt   # Python dependencies
├── .env.example      # Environment template
├── .gitignore        # Git ignore rules
└── README.md         # This file
```

### Adding New Content

**Adding a New Course:**
1. Edit `courses.py`
2. Add course structure to `COURSES` dictionary
3. Include lessons, quizzes, and exercises
4. Test with `!courses` command

**Adding New Achievements:**
1. Edit `achievements.py`
2. Add achievement definition to `ACHIEVEMENTS`
3. Implement trigger conditions
4. Test achievement unlocking

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 🐛 Troubleshooting

### Common Issues

**Bot doesn't respond:**
- Check bot token in `.env` file
- Verify bot has necessary permissions
- Check bot is online in Discord

**Database errors:**
- Ensure write permissions in bot directory
- Check SQLite installation
- Verify database file isn't corrupted

**Import errors:**
- Run `pip install -r requirements.txt`
- Check Python version (3.8+ required)
- Verify all files are present

### Getting Help
- Check the [Issues](https://github.com/Jaywinner/Discord_Cyber_Bot/issues) page
- Join our Discord server for support
- Review the troubleshooting section

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📞 Support

If you need help or have questions:
- Open an issue on GitHub
- Check the documentation
- Join our community Discord server

## 🎉 Acknowledgments

- Discord.py community for the excellent library
- Cybersecurity educators who inspired the content
- Beta testers who helped improve the bot

---

**Made with ❤️ for cybersecurity education**

*Start your cybersecurity journey today with `!start`*