import os
import glob
import subprocess
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.request import HTTPXRequest
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = ''

def get_main_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("📊 All queue Status", callback_data='status'),
            InlineKeyboardButton("📈 Check Job Logs", callback_data='log_list'),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("🔙 Back to Main Menu", callback_data='main')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# ==========================================
# 3. Handler Functions
# ==========================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Please select a menu:', reply_markup=get_main_keyboard())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    # 1. Back to main menu
    if query.data == 'main':
        await query.edit_message_text(
            text='Please select a menu:',
            reply_markup=get_main_keyboard()
        )
    # 2. Check overall qstat status
    elif query.data == 'status':
        try:
            result = subprocess.check_output(['qstat'], text=True, stderr=subprocess.STDOUT)
            
            if not result.strip():
                msg = "There are no jobs waiting in the queue or currently running."
            else:
                msg = f"<b>[Overall Status Summary]</b>\n<pre>{result}</pre>"
        except Exception as e:
            msg = f"Error executing qstat:\n{e}"
        
        await query.edit_message_text(
            text=msg,
            parse_mode='HTML',
            reply_markup=get_back_keyboard()
        )
        
    # 3. Display user's job list as buttons
    elif query.data == 'log_list':
        try:
            user_name = os.getenv("USER")
            qstat_cmd = ['qstat', '-u', user_name] if user_name else ['qstat']
            qstat_out = subprocess.check_output(qstat_cmd, text=True, stderr=subprocess.STDOUT)
            
            lines = [line.strip() for line in qstat_out.strip().splitlines() if line.strip()]
            
            if len(lines) <= 2:
                await query.edit_message_text(
                    text="You have no running or queued jobs.",
                    reply_markup=get_back_keyboard()
                )
                return

            keyboard = []
            for line in lines[2:]:
                cols = line.split()
                if len(cols) >= 5:
                    job_id = cols[0]
                    job_name = cols[2]
                    job_state = cols[4]
                    
                    btn_text = f"🔹 ID: {job_id} | {job_name} ({job_state})"
                    keyboard.append([InlineKeyboardButton(btn_text, callback_data=f'log_job:{job_id}')])

            keyboard.append([InlineKeyboardButton("🔙 Back to Main Menu", callback_data='main')])

            await query.edit_message_text(
                text="<b>Please select a job to check its logs:</b>",
                parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        except Exception as e:
            await query.edit_message_text(
                text=f"Error occurred while fetching job list:\n{e}",
                reply_markup=get_back_keyboard()
            )
    
    # 4. Track exact log of a specific Job ID
    elif query.data.startswith('log_job:'):
        job_id = query.data.split(':')[1]

        job_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔄 Refresh", callback_data=f'log_job:{job_id}'),
                InlineKeyboardButton("📋 Back to Job List", callback_data='log_list')
            ],
            [
                InlineKeyboardButton("🔙 Back to Main Menu", callback_data='main')
            ]
        ])

        try:
            # Run qstat -j <job_id> to track working directory
            job_info = subprocess.check_output(['qstat', '-j', job_id], text=True, stderr=subprocess.STDOUT)
            
            workdir = None
            for line in job_info.splitlines():
                if 'sge_o_workdir:' in line:
                    workdir = line.split('sge_o_workdir:')[1].strip()
                    break

            if not workdir or not os.path.exists(workdir):
                await query.edit_message_text(
                    text=f"Working directory not found.\nJob ID: {job_id}\nPath: {workdir}",
                    reply_markup=job_keyboard
                )
                return

            search_pattern = os.path.join(workdir, f"*.o{job_id}*")
            list_of_files = glob.glob(search_pattern)

            if not list_of_files:
                await query.edit_message_text(
                    text=(
                        f"Log file for the selected job (<code>*.o{job_id}</code>) has not been created yet.\n"
                        f"The job might be pending (qw) or just started.\n\n"
                        f"📂 Path: <code>{workdir}</code>"
                    ),
                    parse_mode='HTML',
                    reply_markup=job_keyboard
                )
                return

            latest_file = max(list_of_files, key=os.path.getctime)
            file_name = os.path.basename(latest_file)

            result = subprocess.check_output(['tail', '-n', '15', latest_file], text=True)
            
            if not result.strip():
                msg = f"<b>[Job ID: {job_id} | {file_name}]</b>\nLog file is still empty."
            else:
                msg = (
                    f"<b>[Job ID: {job_id} | {file_name}]</b>\n"
                    f"📂 <code>{workdir}</code>\n\n"
                    f"<pre>{result}</pre>"
                )

            await query.edit_message_text(
                text=msg,
                parse_mode='HTML',
                reply_markup=job_keyboard
            )

        except Exception as e:
            await query.edit_message_text(text=f"Cannot load info for Job ID {job_id}.\n(The job might have finished or been canceled)\n\nError:\n{e}",
            reply_markup=job_keyboard
            )

# ==========================================
# 4. Main
# ==========================================
def main():
    request_kwargs = HTTPXRequest(
        connect_timeout=30.0,
        read_timeout=30.0,
        write_timeout=30.0,
        pool_timeout=30.0
    )

    app = (
        Application.builder()
        .token(TOKEN)
        .request(request_kwargs)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Cluster monitoring bot has started.")
    app.run_polling()

if __name__ == '__main__':
    main()
