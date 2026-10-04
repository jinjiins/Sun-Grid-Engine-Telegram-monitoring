📊 SGE Telegram Monitoring Bot

SGE Telegram Monitoring Bot is a simple Telegram bot designed to monitor Sun Grid Engine (SGE) clusters. It allows users to check the overall queue status, list their active jobs, and read the latest output logs (tail) of specific jobs directly from the Telegram app.

✨ Features

Overall Queue Status: Run qstat to view a summary of all queued and running jobs in the cluster.

User Job List: Filter jobs by the current user (qstat -u $USER) and display them as interactive Telegram buttons.

Real-time Log Tracking (Tail): Select a specific Job ID to track its working directory (qstat -j <job_id>) and fetch the last 15 lines of its output log file (*.o<job_id>*).

Quick Refresh: Instantly refresh the log output using the '🔄 Refresh' button on the log view screen.

🛠 Requirements & Compatibility

1. Sun Grid Engine (SGE)

Compatible with most SGE environments (Sun Grid Engine 6.2+, Open Grid Scheduler, Son of Grid Engine, Univa Grid Engine, etc.).

Requires qstat and standard Linux commands like tail to be available in the system's PATH.

2. Python

Python 3.8+ (Required for python-telegram-bot v20+ async features).

3. Dependencies

python-telegram-bot (v20.x or higher recommended)

httpx

🚀 Installation & Setup

1. Install Dependencies

Install the required Python packages using pip:

pip install python-telegram-bot httpx


2. Configure Telegram Bot Token

Search for BotFather in Telegram and start a chat.

Send the /newbot command to create a new bot and get your HTTP API Token.

Open telegram_sungrid.py and paste your token into the TOKEN variable:

TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN_HERE'


3. Run the Bot

Run the script on the master node or submit node where SGE commands are accessible:

python telegram_sungrid.py


If you see the message "Cluster monitoring bot has started." in your terminal, the bot is running successfully.

📱 Usage

Open a chat with your newly created bot in Telegram.

Send the /start command.

Use the inline keyboard buttons to monitor the cluster:

[📊 All qstat Status]: Check the overall cluster job status.

[📈 Check Job Logs]: View your list of active jobs and click on a specific job to read its real-time output log.

📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
