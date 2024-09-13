
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler
import openai
import config
import asyncio

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

logger = logging.getLogger(__name__)

# OpenAI API Key
openai.api_key = config.OPENAI_API_KEY

# Defining Conversation States
ASK_SYMPTOMS, ASK_CONSENT, ASK_CONTACTS = range(3)

# Start Command Handler
async def start(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Bot has started!")
    await update.message.reply_text(
        "Hello! I'm here to help you reflect on how you're feeling. "
        "You can share anything that's on your mind."
    )
    return ASK_SYMPTOMS

# Handling User Messages
async def ask_symptoms(update: Update, context: CallbackContext) -> int:
    user_message = update.message.text
    user_id = update.message.from_user.id

    # Assess risk level
    risk_level = await assess_risk_level(user_message)
    logging.info(f"User ID: {user_id}, Risk Level: {risk_level}")

    # Save risk level in context
    context.user_data['risk_level'] = risk_level

    # Provide feedback based on risk level
    if risk_level == 'High risk':
        await update.message.reply_text(
            "I'm sorry to hear that you're feeling this way. "
            "Would you like me to notify a trusted contact?"
        )
        return ASK_CONSENT
    else:
        await update.message.reply_text(
            "Thank you for sharing. Remember, I'm here to listen anytime."
        )
        return ConversationHandler.END

# Assessing Risk Levels
async def assess_risk_level(user_message):
    try:
        prompt = (
            "You are a mental health assistant. Assess the following message for signs of early psychosis "
            "and classify the mental health risk as 'Low risk', 'Medium risk', or 'High risk'. "
            "Only provide the risk level in your response.\n\n"
            f"Message: {user_message}\n\nRisk Level:"
        )
        response = await openai.ChatCompletion.acreate(
            model='gpt-4',
            messages=[
                {"role": "system", "content": "You are a mental health assistant."},
                {"role": "user", "content": user_message}
            ]
        )
        risk_level = response.choices[0].message['content'].strip()
        logging.info(f"OpenAI GPT-4 response: {risk_level}")
        return risk_level
    except Exception as e:
        logging.error(f"OpenAI GPT-4 API error: {e}")
        return None

# Handling Consent for Notifications
async def ask_consent(update: Update, context: CallbackContext) -> int:
    user_response = update.message.text.lower()
    if 'yes' in user_response:
        await update.message.reply_text(
            "Please provide the contact information (Telegram username) of your trusted person."
        )
        return ASK_CONTACTS
    else:
        await update.message.reply_text(
            "Alright, I respect your decision. Please consider reaching out to a mental health professional."
        )
        return ConversationHandler.END

# Collecting Trusted Contact Information
async def ask_contacts(update: Update, context: CallbackContext) -> int:
    trusted_contact = update.message.text
    user_id = update.message.from_user.id

    # Save trusted contact
    context.user_data['trusted_contact'] = trusted_contact

    # Notify trusted contact
    await notify_trusted_contact(trusted_contact, user_id, context)

    await update.message.reply_text(
        "Thank you. I've notified your trusted contact."
    )
    return ConversationHandler.END

# Notifying Trusted Contacts
async def notify_trusted_contact(trusted_contact, user_id, context):
    message = (
        f"Hello, I'm reaching out because your friend (User ID: {user_id}) indicated that they trust you "
        "and may need support. Please consider checking in with them."
    )

    try:
        await context.bot.send_message(chat_id='@' + trusted_contact, text=message)
    except Exception as e:
        logger.error(f"Failed to notify trusted contact: {e}")

# Cancel Handler
async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(
        "Conversation cancelled. Feel free to reach out anytime."
    )
    return ConversationHandler.END

# Main Function to Run the Bot
async def main():
    # Use Application.builder() instead of Updater
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    # Clear any existing webhook to avoid conflict
    await application.bot.delete_webhook(drop_pending_updates=True)
    await application.initialize()

    # Add handlers
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ASK_SYMPTOMS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_symptoms)],
            ASK_CONSENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_consent)],
            ASK_CONTACTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_contacts)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Add the conversation handler to the application
    application.add_handler(conv_handler)

    # Start the bot
    await application.start()

    # Start polling
    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
    
       

