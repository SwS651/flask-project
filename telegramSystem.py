import html
import os
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime
from app.extensions import db
 
user_state = ""
 
print("Bot Start...")
API_KEY: Final = '7038381879:AAFW53rnahyEubeiBuB_t63-xYcKivWcIoI'
BOT_USERNAME: Final = '@UOW_S_Mart_bot'
 
 
# /info
async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎉 Welcome to S-Mart's Telegram Bot! 🎉\n\n"
        "Hello and thank you for choosing S-Mart, your reliable shopping partner. Our bot is designed to make your shopping experience as seamless and informative as possible. 🛍️✨\n\n"
        "Here's what you can do with our bot:\n"
        "1. 📢 Check Announcements: Stay updated with the latest news and updates from S-Mart.\n"
        "2. 💹 Latest Stock Prices: Get real-time updates on the stock availability of your favorite products.\n"
        "3. 🎊 Promotions: Don't miss out on our exciting promotions and discounts.\n"
        "4. ❓ FAQ: Have questions? Access our Frequently Asked Questions to find quick answers.\n\n"
        "\n\n To get started, you can use the following commands: \n"
        "/announce - View the latest announcements from S-Mart.\n"
        "/pricetdy - Check the latest stock prices.\n"
        "/promo - Explore current promotions.\n"
        "/faq - Browse through the frequently asked questions for quick help.\n"
        "\n\nThank you for using S-Mart. Happy shopping!"
       
    )
 
 
# /announce
async def announce_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # content = read_announcement_md('announcement.md')
    
    content = str(read_md('announcement.md'))
    await update.message.reply_text(text = content)
 
 
# /pricetdy
async def pricetdy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    content = str(read_md('price_today.md'))
    await update.message.reply_text(text = content)
 
 
# /promo
async def promo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    content = str(read_md('promo.md'))
    await update.message.reply_text(text = content)
 
 
# /FAQ
async def faq_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓Frequently Asked Questions (FAQs):❓\n\n"
        "❓Q1: How do I check for product availability?\n"
        "\t 🔍A: To check if a product is in stock, use the /pricetdy command followed by the product name.\n\n"
        "❓Q2: How can I learn about current promotions?\n"
        "\t 🔍A: Simply type /promo to see a list of all current promotions available at S-Mart.\n\n"
        "❓Q3: Where can I find the latest S-Mart announcements?\n"
        "\t 🔍A: Stay up-to-date with S-Mart news by using the /announce command.\n\n"
        "❓Q4: What are the store hours for S-Mart?\n"
        "\t 🔍A: Monday to Friday, 1:30pm to 3:30pm. S-Mart will be closed during semester break and public holiday.\n\n"
        "❓Q5: Can I reserve a product through the bot?\n"
        "\t 🔍A: Currently, product reservation is not available through our Telegram bot.\n\n"
    )

import markdown
from bs4 import BeautifulSoup
def read_md(filename):
    basedir = os.path.abspath(os.path.dirname(__file__))
    file_path = os.path.join(basedir,filename)
    with open(file_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
        html_content = markdown.markdown(md_content)
        content = BeautifulSoup(html_content, 'html.parser')
        return content.get_text()


# def handle_response(user:str, text: str) -> str:
#     global user_state
#     processed: str = text.lower()
#     user_id: str = user
#     url = "https://api.telegram.org/bot6675579546%3AAAF7wXkfZpboqwaZg1XaygvljNWc_Mw52xs/sendDocument"
 
#     parameters = {
#         "chat_id": f"{user_id}",
#         "caption": "csv file"
#     }
 
#     if user_state == "request_data":
#         # For this example, let's assume a simplistic month check.
#         # In a real-world application, you might want to verify the month more thoroughly.
 
#         if processed.lower() in ("jan", "feb", "mar", "apr", "may", "jun",
#                          "jul", "aug", "sep", "oct", "nov", "dec"):
#             user_state = ""  # Reset the user state
 
#             my_file = open(
#                 f"C:\\Users\\Alfred\\PycharmProjects\\PythonProject\\FinalYearProject\\dataset\\apims\\{processed.capitalize()}.csv")
#             files = {
#                 "document": my_file
#             }
#             response = requests.get(url, data=parameters, files=files)
#             print(response.text)
#             return "Here's the CSV for the month of " + processed.capitalize() + "."
 
#         if is_valid_date_format(processed):
#             user_state = ""  # Reset the user state
#             my_file = open(
#                 f"C:\\Users\\Alfred\\PycharmProjects\\PythonProject\\FinalYearProject\\dataset\\apims\\2023\\apims_{processed}.csv")
#             files = {
#                 "document": my_file
#             }
#             response = requests.get(url, data=parameters, files=files)
#             return "Here's the CSV for the date " + processed + "."
 
#         else:
#             user_state = ""  # Reset the user state
#             return "Invalid format. Please Try Again. Type 'download' to begin."
 
#     if processed.lower() == "download":
#         user_state = "request_data"
#         return f"Which month would you like the data for? \n(e.g., 'Jan', 'Feb', etc.)\n\nWhich date would you like data for? \n(e.g., '2023-10-31',2023-09-28',etc.) "
#     else:
#         return "I'm not sure how to respond to that. Type 'download' to begin."
 
 
async def error(update: Update, context:ContextTypes.DEFAULT_TYPE):
    print(f'Update{update} caused error {context.error}')
 
if __name__ == "__main__":
 
    print("Bot Run")
    app = Application.builder().token(API_KEY).build()
 
    # Commands
    app.add_handler(CommandHandler('info',info_command))
    app.add_handler(CommandHandler('announce',announce_command))
    app.add_handler(CommandHandler('pricetdy',pricetdy_command))
    app.add_handler(CommandHandler('promo',promo_command))
    app.add_handler(CommandHandler('faq',faq_command))
 
    # Message
    app.add_error_handler(error)
    # print("Bot Polling...")
    app.run_polling(poll_interval=0.5)