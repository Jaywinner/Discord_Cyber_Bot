# 🛡️ Discord Cyber Academy Bot

A comprehensive, interactive Discord bot designed to teach cybersecurity fundamentals through gamified learning experiences. Features professional multimedia content, session management, and hands-on challenges. Perfect for Discord communities, educational servers, and anyone looking to master cybersecurity skills.

## ✨ Features

### 🎓 Interactive Learning Platform
- **Structured Courses**: Multiple cybersecurity courses from beginner to advanced
- **Hands-on Lessons**: Practical exercises with real-world examples
- **Interactive Quizzes**: Test knowledge with immediate feedback and explanations
- **CTF Challenges**: Capture-the-flag style security challenges
- **Professional Multimedia**: Real cybersecurity images and visual content
- **Progress Tracking**: Monitor learning journey and achievements

### 🔄 Session Management System
- **⏸️ Stop & Resume**: Pause training anytime and resume exactly where you left off
- **Session Persistence**: Training progress survives bot restarts and Discord outages
- **Multi-Session Support**: Save multiple training sessions across different content types
- **Smart Recovery**: Automatic session restoration with detailed progress tracking

### 🎮 Gamification & Engagement
- **XP System**: Earn experience points for completing lessons and challenges
- **Level Progression**: Advance through levels as you learn
- **Achievement Badges**: Unlock special achievements for milestones
- **Leaderboards**: Compete with other learners in your server
- **Interactive UI**: Modern Discord embeds with responsive buttons

### 🔧 Advanced Features
- **Slash Commands**: Modern Discord slash command interface
- **Course Selection**: Choose your learning path from available courses
- **Smart Navigation**: Seamless progression between lessons and courses
- **Admin Dashboard**: Comprehensive management tools (admin only)
- **Database Persistence**: SQLite-based data storage with session management

## 📚 Learning Content

### 🎓 Structured Courses
#### Beginner Level
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

#### Intermediate Level
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

### 🚩 CTF Challenges
- **Beginner**: Basic security concepts and tools
- **Intermediate**: Network analysis and cryptography
- **Advanced**: Reverse engineering and exploitation
- **Expert**: Advanced persistent threats and forensics

### 🎥 Multimedia Learning
- **🎣 Phishing Examples**: Real-world phishing email screenshots
- **🔐 Password Demonstrations**: Visual password strength examples
- **🌐 Network Diagrams**: Security architecture visualizations
- **🦠 Malware Analysis**: Safe malware behavior examples
- **📚 Educational Videos**: Curated cybersecurity content
- **🎵 Audio Content**: Podcasts and security briefings

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
   - Select "bot" and "applications.commands" scopes
   - Select these permissions:
     - Send Messages
     - Use Slash Commands
     - Embed Links
     - Read Message History
     - Add Reactions
     - Attach Files
     - Use External Emojis

3. **Invite Bot to Server**
   - Use the generated URL to invite the bot to your server
   - Make sure the bot has the necessary permissions

4. **Sync Slash Commands**
   - After starting the bot, slash commands will automatically sync
   - Commands may take up to 1 hour to appear globally
   - For immediate testing, set `GUILD_ID` in your `.env` file

## 🎯 Commands

### 📚 Learning Commands
- `/start` - Begin your cybersecurity learning journey
- `/lesson [course] [module] [lesson]` - View lessons with **⏸️ Stop & Save** functionality
- `/courses` - Browse all available courses and select your path
- `/quiz [course] [module] [lesson]` - Take interactive quizzes with **⏸️ Stop & Save**
- `/ctf [difficulty]` - Access CTF challenges with **⏸️ Stop & Save**
- `/multimedia [type]` - View professional cybersecurity content with **⏸️ Stop & Save**

### 🔄 Session Management
- `/sessions` - **NEW!** View and manage all your saved training sessions
  - Resume any paused lesson, quiz, CTF, or multimedia session
  - Delete old sessions you no longer need
  - See detailed progress information

### 📊 Progress & Social
- `/progress [@user]` - Check learning progress and statistics
- `/achievements` - View earned badges and achievements
- `/leaderboard` - See top learners in the server
- `/help` - Get comprehensive help with all bot commands

### 🛠️ Admin Commands (Admin Only)
- `/admin_stats` - View detailed server statistics
- `/admin_reset_user <user>` - Reset a user's progress
- `/admin_add_xp <user> <amount>` - Add XP to a user
- `/admin_courses` - Manage course content and structure

### 🎮 Interactive Features
All training commands now include:
- **⏸️ Stop & Save buttons** - Pause anytime and resume later
- **Smart navigation** - Seamless progression through content
- **Progress indicators** - Visual feedback on your learning journey
- **Session persistence** - Never lose your progress

## 🗄️ Database

The bot uses SQLite for data storage with the following tables:
- **users**: User profiles, XP, levels, and current progress
- **course_progress**: Detailed lesson completion tracking
- **achievements**: User achievement records
- **quiz_attempts**: Quiz performance history
- **training_sessions**: **NEW!** Session management for stop/resume functionality
  - Stores paused lesson, quiz, CTF, and multimedia sessions
  - Enables seamless resume functionality across bot restarts
  - Tracks session metadata and progress details

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
├── bot.py                 # Main bot file with slash commands
├── database.py            # Database management with session support
├── courses.py             # Course content and structure
├── achievements.py        # Achievement system
├── quiz.py               # Interactive quiz functionality
├── ctf.py                # CTF challenge system
├── multimedia.py         # Professional multimedia content
├── training_session.py   # NEW! Session management system
├── admin.py              # Admin commands and management
├── requirements.txt      # Python dependencies
├── .env.example         # Environment template
├── .gitignore           # Git ignore rules
├── academy.db           # SQLite database (auto-created)
└── README.md            # This file
```

### Adding New Content

**Adding a New Course:**
1. Edit `courses.py`
2. Add course structure to `COURSES` dictionary
3. Include lessons, quizzes, and exercises
4. Test with `/courses` command

**Adding New Achievements:**
1. Edit `achievements.py`
2. Add achievement definition to `ACHIEVEMENTS`
3. Implement trigger conditions
4. Test achievement unlocking

**Adding Multimedia Content:**
1. Edit `multimedia.py`
2. Add content to appropriate category in `MULTIMEDIA_CONTENT`
3. Include title, description, URL, and metadata
4. Test with `/multimedia` command

**Adding CTF Challenges:**
1. Edit `ctf.py`
2. Add challenge to `CTF_CHALLENGES` dictionary
3. Include flag, hints, and difficulty rating
4. Test with `/ctf` command

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

*Start your cybersecurity journey today with `/start` and never lose your progress with our **⏸️ Stop & Resume** system!*

## 🆕 Latest Updates

### Version 2.0 - Comprehensive Learning Platform
- ✅ **Stop/Resume Training Sessions** - Pause and resume anytime
- ✅ **Professional Multimedia Content** - Real cybersecurity images and videos
- ✅ **Modern Slash Commands** - Updated Discord interface
- ✅ **CTF Challenge System** - Hands-on security challenges
- ✅ **Session Management Dashboard** - Track all your saved progress
- ✅ **Enhanced Database** - Persistent session storage