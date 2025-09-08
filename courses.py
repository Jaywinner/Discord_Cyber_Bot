"""
Cybersecurity Course Content - From Beginner to Intermediate
Interactive, practical lessons with hands-on exercises
"""

COURSES = {
    1: {
        "title": "🛡️ Cybersecurity Fundamentals",
        "description": "Learn the basics of cybersecurity and develop a security mindset",
        "level": "Beginner",
        "modules": {
            1: {
                "title": "Introduction to Cybersecurity",
                "lessons": {
                    1: {
                        "title": "What is Cybersecurity?",
                        "content": """
🔐 **Welcome to Cybersecurity!**

Cybersecurity is like being a digital bodyguard - protecting information, systems, and networks from digital attacks.

**Think of it this way:**
• Your phone = Your house
• Your apps = Rooms in your house  
• Cybersecurity = Locks, alarms, and security cameras

**Real-world example:** 
When you use online banking, cybersecurity protects your money from digital thieves trying to steal it through the internet.

**Why does it matter?**
• 🏦 Protects your money and identity
• 📱 Keeps your personal photos and messages safe
• 💼 Secures business data and operations
• 🌐 Maintains trust in digital services

**Your mission:** Complete this lesson to earn your first 100 XP!
                        """,
                        "xp_reward": 100,
                        "practical_exercise": {
                            "title": "Security Mindset Challenge",
                            "description": "Look around your digital life and identify 3 things you want to protect",
                            "example_answers": ["Bank account", "Social media", "Email", "Photos", "Work files"]
                        },
                        "quiz": {
                            "question": "What is the main purpose of cybersecurity?",
                            "options": ["To make computers faster", "To protect information, systems, and networks from digital attacks", "To create new software", "To design websites"],
                            "correct": 1,
                            "explanation": "Cybersecurity is like being a digital bodyguard - its main purpose is to protect information, systems, and networks from digital attacks and threats."
                        }
                    },
                    2: {
                        "title": "Common Cyber Threats",
                        "content": """
⚠️ **Know Your Digital Enemies**

Just like in the real world, the digital world has different types of threats:

**1. 🎣 Phishing (Digital Fishing)**
• Fake emails/websites trying to steal your info
• Example: "Your bank account is locked! Click here to unlock"
• Reality: It's a trap to steal your login details

**2. 🦠 Malware (Digital Viruses)**
• Harmful software that damages your device
• Types: Viruses, ransomware, spyware
• Like getting your computer "sick"

**3. 👤 Social Engineering (Digital Manipulation)**
• Tricking people into giving away secrets
• Example: Fake tech support calls
• Uses psychology, not just technology

**4. 🔓 Data Breaches (Digital Break-ins)**
• When hackers break into company databases
• Your personal info gets stolen in bulk
• Like someone breaking into a filing cabinet

**Real Example:** In 2017, Equifax was breached and 147 million people's personal data was stolen - including Social Security numbers!

**Remember:** Knowing these threats is your first line of defense!
                        """,
                        "xp_reward": 150,
                        "quiz": {
                            "question": "Which threat involves tricking people psychologically rather than using technical methods?",
                            "options": ["Malware", "Social Engineering", "Data Breach", "Phishing"],
                            "correct": 1,
                            "explanation": "Social Engineering uses psychological manipulation to trick people into revealing information or performing actions."
                        }
                    },
                    3: {
                        "title": "Building a Security Mindset",
                        "content": """
🧠 **Think Like a Security Expert**

A security mindset means always thinking "What could go wrong?" and "How can I protect myself?"

**The Security Mindset Principles:**

**1. 🤔 Question Everything**
• Is this email really from my bank?
• Why is this app asking for my location?
• Should I really click this link?

**2. 🔒 Assume Breach**
• What if someone gets my password?
• How would I recover if my phone was stolen?
• What's my backup plan?

**3. 🎯 Think Like an Attacker**
• How would someone try to trick me?
• What information am I sharing publicly?
• Where are my weak points?

**Practical Exercise:**
Look at your social media profiles. What could a cybercriminal learn about you?
• Your birthday (for password guessing)
• Your location (for targeted attacks)
• Your friends/family (for social engineering)

**Real-world Application:**
Before posting "Going on vacation to Hawaii!" think: "Am I telling criminals my house will be empty?"

**Your Challenge:** Practice the security mindset for one day. Question 3 things you normally wouldn't think twice about!
                        """,
                        "xp_reward": 200,
                        "practical_exercise": {
                            "title": "Security Mindset Practice",
                            "description": "For the next 24 hours, question 3 digital activities you normally do without thinking",
                            "examples": ["Why does this app need camera access?", "Is this WiFi network safe?", "Should I share this location?"]
                        },
                        "quiz": {
                            "question": "What is the first principle of a security mindset?",
                            "options": ["Trust everything by default", "Question everything", "Share information freely", "Ignore security warnings"],
                            "correct": 1,
                            "explanation": "The security mindset starts with questioning everything - asking 'What could go wrong?' and 'How can I protect myself?' before taking any action."
                        }
                    }
                }
            }
        }
    },
    2: {
        "title": "🔐 Password Security Mastery",
        "description": "Master the art of creating and managing secure passwords",
        "level": "Beginner",
        "modules": {
            1: {
                "title": "Password Fundamentals",
                "lessons": {
                    1: {
                        "title": "Password Strength Secrets",
                        "content": """
💪 **What Makes a Password Strong?**

Think of passwords like the locks on your house. A weak password is like a flimsy lock - easy to break!

**The Password Strength Formula:**

**Length > Complexity**
• "ILovePizza123!" = Weak (predictable pattern)
• "Coffee-Morning-Sunshine-2024" = Strong (long + unpredictable)

**What Makes Passwords Weak:**
• 🚫 Personal info (birthday, pet names)
• 🚫 Dictionary words
• 🚫 Common patterns (123456, qwerty)
• 🚫 Short length (under 12 characters)

**What Makes Passwords Strong:**
• ✅ 12+ characters long
• ✅ Mix of words, numbers, symbols
• ✅ Unpredictable combinations
• ✅ Unique for each account

**The Passphrase Method:**
Instead of "P@ssw0rd1" try "Purple-Elephant-Dancing-42"
• Easier to remember
• Harder to crack
• More fun to create!

**Real Example:**
Bad: "Sarah1995!" (name + birth year)
Good: "Midnight-Coffee-Tastes-Purple-77"

**Your Mission:** Create a strong password using the passphrase method!
                        """,
                        "xp_reward": 150,
                        "quiz": {
                            "question": "Which password is stronger?",
                            "options": ["P@ssw0rd123!", "Banana-Helicopter-Music-2024", "JohnSmith1990", "abc123"],
                            "correct": 1,
                            "explanation": "Long passphrases with random words are much stronger than short complex passwords with predictable patterns."
                        }
                    },
                    2: {
                        "title": "Password Managers: Your Digital Vault",
                        "content": """
🗝️ **Never Remember Another Password!**

Password managers are like having a super-secure digital vault that remembers all your passwords for you.

**How Password Managers Work:**
1. You create ONE master password
2. The manager generates unique, strong passwords for every site
3. It automatically fills them in when you need them
4. Everything is encrypted and secure

**Popular Password Managers:**
• **Bitwarden** (Free & Open Source)
• **1Password** (Premium features)
• **LastPass** (Freemium)
• **Dashlane** (User-friendly)

**Real-world Benefits:**
• 🎯 Unique password for every account
• 🚀 Faster login (auto-fill)
• 🛡️ Protection against data breaches
• 📱 Works across all your devices

**The "Breach-Proof" Strategy:**
When LinkedIn gets hacked and your password is stolen, it doesn't matter because:
1. That password is unique to LinkedIn
2. Your other accounts are still safe
3. You can easily change just that one password

**Practical Exercise:**
Set up a password manager today and migrate your top 5 most important accounts (email, banking, social media).

**Pro Tip:** Your master password should be a long, memorable passphrase that you'll never forget - like "My-Favorite-Coffee-Shop-Has-Purple-Chairs-2024"
                        """,
                        "xp_reward": 200,
                        "practical_exercise": {
                            "title": "Password Manager Setup",
                            "description": "Install a password manager and secure your top 3 accounts with unique, strong passwords",
                            "steps": ["Choose a password manager", "Create a strong master password", "Add your most important accounts"]
                        },
                        "quiz": {
                            "question": "What is the main advantage of using a password manager?",
                            "options": ["It makes passwords shorter", "It allows you to use unique, strong passwords for every account", "It eliminates the need for passwords", "It makes websites load faster"],
                            "correct": 1,
                            "explanation": "Password managers allow you to use unique, strong passwords for every account without having to remember them all. This means if one site gets breached, your other accounts remain safe."
                        }
                    },
                    3: {
                        "title": "Two-Factor Authentication (2FA)",
                        "content": """
🔐 **Double Your Security Power!**

2FA is like having two locks on your door instead of one. Even if someone steals your password, they still can't get in!

**How 2FA Works:**
1. **Something you know** (your password)
2. **Something you have** (your phone/app)
3. Both are required to log in

**Types of 2FA:**

**📱 Authenticator Apps (BEST)**
• Google Authenticator, Authy, Microsoft Authenticator
• Generates time-based codes
• Works without internet

**📧 Email Codes (OKAY)**
• Code sent to your email
• Better than nothing
• Vulnerable if email is compromised

**📞 SMS Codes (RISKY)**
• Code sent via text message
• Can be intercepted
• Still better than no 2FA

**🔑 Hardware Keys (ULTIMATE)**
• Physical USB/NFC devices
• Highest security level
• Used by security professionals

**Real-world Impact:**
Google found that 2FA blocks 99.9% of automated attacks!

**Where to Enable 2FA First:**
1. 📧 Email accounts (Gmail, Outlook)
2. 🏦 Banking and financial accounts
3. 📱 Social media accounts
4. 💼 Work accounts
5. 🛒 Shopping accounts with saved payment info

**Your Challenge:** Enable 2FA on your email account right now - it takes 2 minutes and dramatically improves your security!
                        """,
                        "xp_reward": 250,
                        "quiz": {
                            "question": "What percentage of automated attacks does 2FA block according to Google?",
                            "options": ["50%", "75%", "90%", "99.9%"],
                            "correct": 3,
                            "explanation": "Google's research shows that 2FA blocks 99.9% of automated attacks, making it incredibly effective."
                        }
                    }
                }
            }
        }
    },
    3: {
        "title": "🎣 Phishing Defense Academy",
        "description": "Learn to spot and avoid phishing attacks like a pro",
        "level": "Beginner",
        "modules": {
            1: {
                "title": "Phishing Detection Mastery",
                "lessons": {
                    1: {
                        "title": "Anatomy of a Phishing Email",
                        "content": """
🕵️ **Become a Phishing Detective!**

Phishing emails are like digital disguises - they pretend to be someone trustworthy to steal your information.

**🚨 Red Flags to Watch For:**

**1. Urgent Language**
• "Your account will be closed in 24 hours!"
• "Immediate action required!"
• "Verify now or lose access!"

**2. Generic Greetings**
• "Dear Customer" instead of your actual name
• "Dear Sir/Madam"
• No personalization

**3. Suspicious Sender**
• amazon-security@gmail.com (not @amazon.com)
• Misspelled company names
• Random email addresses

**4. Suspicious Links**
• Hover over links to see the real destination
• bit.ly/suspicious-link instead of official URLs
• Misspelled domains (amazom.com instead of amazon.com)

**5. Grammar and Spelling Errors**
• Professional companies proofread their emails
• Multiple typos = major red flag
• Awkward phrasing

**Real Phishing Example:**
"Dear Valued Customer, Your PayPal account has been limited due to suspicious activity. Click here to verify: http://paypal-security.fake-site.com"

**Red Flags Found:**
• Generic greeting ❌
• Urgent language ❌
• Suspicious URL ❌
• Creates fear ❌

**Your Mission:** Practice identifying these red flags in every email you receive!
                        """,
                        "xp_reward": 175,
                        "practical_exercise": {
                            "title": "Phishing Email Analysis",
                            "description": "Look at your recent emails and identify any that have phishing red flags",
                            "red_flags": ["Urgent language", "Generic greetings", "Suspicious links", "Grammar errors", "Requests for personal info"]
                        },
                        "quiz": {
                            "question": "Which of these is the BIGGEST red flag in a phishing email?",
                            "options": ["The email is long", "Generic greeting like 'Dear Customer'", "The email has images", "It's sent on a weekend"],
                            "correct": 1,
                            "explanation": "Generic greetings like 'Dear Customer' are a major red flag because legitimate companies usually address you by name. This indicates the sender doesn't actually know you or have your real information."
                        }
                    },
                    2: {
                        "title": "Social Engineering Tactics",
                        "content": """
🎭 **The Psychology of Deception**

Social engineering is like being a con artist - attackers use psychology to manipulate you into giving them what they want.

**Common Social Engineering Tactics:**

**1. 😨 Fear and Urgency**
• "Your computer is infected! Call now!"
• "Suspicious login detected!"
• Creates panic to bypass logical thinking

**2. 🎁 Too Good to Be True**
• "You've won $1,000,000!"
• "Free iPhone - just pay shipping!"
• Exploits greed and excitement

**3. 👔 Authority Impersonation**
• "This is IT support, we need your password"
• "IRS calling about unpaid taxes"
• People naturally obey authority figures

**4. 🤝 Trust and Familiarity**
• "Hi, I'm calling from your bank..."
• Using information from social media
• Building fake relationships

**5. 💔 Emotional Manipulation**
• Fake charity appeals
• Romance scams
• Exploiting empathy and kindness

**Real-world Example:**
Scammer calls pretending to be your grandchild: "Grandma, I'm in jail and need bail money. Please don't tell my parents!"

**Defense Strategy - The STOP Method:**
• **S**top and think
• **T**ake a breath
• **O**bserve red flags
• **P**roceed with caution (or not at all)

**Your Challenge:** Next time someone asks for personal information (even if they seem legitimate), use the STOP method!
                        """,
                        "xp_reward": 200,
                        "quiz": {
                            "question": "What should you do when someone creates urgency to get you to act quickly?",
                            "options": ["Act immediately to avoid problems", "Use the STOP method", "Give them what they want", "Ignore them completely"],
                            "correct": 1,
                            "explanation": "The STOP method helps you pause and think rationally when someone is trying to create urgency to manipulate you."
                        }
                    },
                    3: {
                        "title": "Safe Browsing Practices",
                        "content": """
🌐 **Navigate the Web Like a Security Pro**

The internet is like a big city - there are safe neighborhoods and dangerous ones. Learn to stay in the safe areas!

**🛡️ Safe Browsing Rules:**

**1. Check the Lock (HTTPS)**
• Look for 🔒 in the address bar
• URL starts with "https://" not "http://"
• Especially important for login pages and shopping

**2. Verify Website URLs**
• amazon.com ✅ vs amazom.com ❌
• paypal.com ✅ vs paypaI.com ❌ (that's an "i" not "l")
• When in doubt, type the URL manually

**3. Be Suspicious of Pop-ups**
• "Your computer is infected!" = Fake
• "You've won a prize!" = Scam
• Close pop-ups with the X button, never click inside them

**4. Download Safely**
• Only download from official websites
• Avoid "free" versions of paid software
• Scan downloads with antivirus

**5. Use Reputable Browsers**
• Chrome, Firefox, Safari, Edge
• Keep them updated
• Use ad blockers to reduce malicious ads

**Browser Security Features:**
• **Safe Browsing** - Warns about dangerous sites
• **Pop-up Blocker** - Stops annoying/malicious pop-ups
• **Password Manager** - Built-in password storage
• **Private/Incognito Mode** - Doesn't save browsing history

**Red Flag Websites:**
• Excessive pop-ups and ads
• Poor design and grammar
• Requests for unnecessary personal information
• No contact information or privacy policy
• Too-good-to-be-true offers

**Your Mission:** Check your browser's security settings and enable safe browsing features!
                        """,
                        "xp_reward": 225,
                        "practical_exercise": {
                            "title": "Browser Security Audit",
                            "description": "Check and enable security features in your web browser",
                            "checklist": ["Enable safe browsing", "Turn on pop-up blocker", "Update browser", "Install ad blocker", "Check privacy settings"]
                        },
                        "quiz": {
                            "question": "What should you look for to verify a website is secure for entering personal information?",
                            "options": ["The website has lots of colors", "The URL starts with 'https://' and shows a lock icon", "The website loads quickly", "The website has many advertisements"],
                            "correct": 1,
                            "explanation": "A secure website will have 'https://' in the URL and show a lock icon in the address bar. This indicates the connection is encrypted and safer for entering personal information."
                        }
                    }
                }
            }
        }
    },
    4: {
        "title": "🌐 Network Security Basics",
        "description": "Understand networks and protect your connections",
        "level": "Intermediate",
        "modules": {
            1: {
                "title": "Understanding Networks",
                "lessons": {
                    1: {
                        "title": "How Networks Work",
                        "content": """
🔗 **The Digital Highway System**

Networks are like roads that connect different places. Understanding how they work helps you travel safely!

**Network Basics:**

**What is a Network?**
• A system that connects devices together
• Allows sharing of information and resources
• Like a postal system for digital messages

**Types of Networks:**

**🏠 Home Network (LAN - Local Area Network)**
• Your WiFi router connects all your devices
• Printer, laptop, phone, smart TV all connected
• Private and controlled by you

**🌍 Internet (WAN - Wide Area Network)**
• Global network connecting millions of devices
• Public and shared by everyone
• Requires security measures

**☁️ Cloud Networks**
• Remote servers you access over the internet
• Google Drive, Netflix, email services
• Your data stored on someone else's computers

**How Data Travels:**
1. Your device sends a request
2. Router forwards it to your ISP
3. ISP routes it across the internet
4. Destination server receives and responds
5. Response travels back the same way

**Network Security Concerns:**
• **Eavesdropping** - Someone listening to your traffic
• **Man-in-the-Middle** - Someone intercepting your communications
• **Unauthorized Access** - Strangers using your network

**Real-world Analogy:**
Sending data is like mailing a postcard - anyone handling it can read it unless you put it in an envelope (encryption)!
                        """,
                        "xp_reward": 200,
                        "quiz": {
                            "question": "What does LAN stand for?",
                            "options": ["Large Area Network", "Local Area Network", "Limited Access Network", "Long Access Network"],
                            "correct": 1,
                            "explanation": "LAN stands for Local Area Network - a network that connects devices in a small area like your home or office."
                        }
                    },
                    2: {
                        "title": "WiFi Security Essentials",
                        "content": """
📶 **Secure Your Wireless World**

WiFi is like having an invisible cable connecting your devices. But if not secured properly, anyone can tap into that cable!

**WiFi Security Standards:**

**🔐 WPA3 (Best)**
• Latest and strongest encryption
• Protects against most attacks
• Use this if available

**🔒 WPA2 (Good)**
• Still secure for most users
• Widely supported
• Minimum acceptable standard

**⚠️ WEP (Dangerous)**
• Old and easily cracked
• Never use this
• Can be broken in minutes

**🚫 Open/No Security (Never!)**
• No encryption at all
• Anyone can see your traffic
• Only use for guest access

**Securing Your Home WiFi:**

**1. Change Default Passwords**
• Router admin password
• WiFi network password
• Use strong, unique passwords

**2. Update Router Firmware**
• Fixes security vulnerabilities
• Check manufacturer's website
• Enable automatic updates if available

**3. Use Strong Network Names**
• Avoid personal information
• "Smith_Family_WiFi" reveals too much
• "Network_2024" is better

**4. Enable Guest Networks**
• Separate network for visitors
• Protects your main devices
• Can be turned off when not needed

**5. Disable WPS**
• WiFi Protected Setup has vulnerabilities
• Turn it off in router settings
• Use manual password entry instead

**Public WiFi Safety:**
• Never access sensitive accounts
• Use your phone's hotspot instead
• If you must use public WiFi, use a VPN

**Your Mission:** Check your home WiFi security settings and upgrade to WPA3 if possible!
                        """,
                        "xp_reward": 250,
                        "practical_exercise": {
                            "title": "WiFi Security Audit",
                            "description": "Check and improve your home WiFi security settings",
                            "steps": ["Check WiFi encryption type", "Change default passwords", "Update router firmware", "Set up guest network", "Disable WPS"]
                        },
                        "quiz": {
                            "question": "Which WiFi security standard is the strongest and most secure?",
                            "options": ["WEP", "WPA", "WPA2", "WPA3"],
                            "correct": 3,
                            "explanation": "WPA3 is the latest and strongest WiFi security standard, providing the best protection against attacks. It should be used whenever available."
                        }
                    }
                }
            }
        }
    }
}

def get_course(course_id: int):
    """Get course by ID"""
    return COURSES.get(course_id)

def get_module(course_id: int, module_id: int):
    """Get module by course and module ID"""
    course = COURSES.get(course_id)
    if course:
        return course.get("modules", {}).get(module_id)
    return None

def get_lesson(course_id: int, module_id: int, lesson_id: int):
    """Get lesson by course, module, and lesson ID"""
    module = get_module(course_id, module_id)
    if module:
        return module.get("lessons", {}).get(lesson_id)
    return None

def get_all_courses():
    """Get all available courses"""
    return COURSES

def get_course_list():
    """Get simplified course list for display"""
    course_list = []
    for course_id, course in COURSES.items():
        course_list.append({
            "id": course_id,
            "title": course["title"],
            "description": course["description"],
            "level": course["level"]
        })
    return course_list

def get_next_lesson(course_id: int, module_id: int, lesson_id: int):
    """Get the next lesson in sequence"""
    course = get_course(course_id)
    if not course:
        return None
    
    # Try next lesson in current module
    next_lesson = get_lesson(course_id, module_id, lesson_id + 1)
    if next_lesson:
        return (course_id, module_id, lesson_id + 1)
    
    # Try first lesson of next module
    next_module = get_module(course_id, module_id + 1)
    if next_module:
        return (course_id, module_id + 1, 1)
    
    # Try first lesson of next course
    next_course = get_course(course_id + 1)
    if next_course:
        return (course_id + 1, 1, 1)
    
    return None  # No more lessons
