
import os
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()

# Access the environment variables
telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
openai_key = os.getenv('OPENAI_API_KEY')



import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from transformers import pipeline # type: ignore


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

logger = logging.getLogger(__name__)

# Initialize the GPT-2 pipeline
generator = pipeline('text-generation', model='gpt2')

# Defining Conversation States
ASK_SYMPTOMS, ASK_CONSENT, ASK_CONTACTS = range(3)

# Start Command Handler
def start(update: Update, context) -> int:
    update.message.reply_text("Bot has started!")
    update.message.reply_text(
        "Hello! I'm here to help you reflect on how you're feeling. "
        "You can share anything that's on your mind."
    )
    return ASK_SYMPTOMS

# Handling User Messages
def ask_symptoms(update: Update, context) -> int:
    user_message = update.message.text
    user_id = update.message.from_user.id

    # Assess risk level using GPT-2 (replace OpenAI with GPT-2)
    risk_level = assess_risk_level(user_message)
    logging.info(f"User ID: {user_id}, Risk Level: {risk_level}")

    # Save risk level in context
    context.user_data['risk_level'] = risk_level

    # Provide feedback based on risk level
    if 'High' in risk_level:
        update.message.reply_text(
            "I'm sorry to hear that you're feeling this way. "
            "Would you like me to notify a trusted contact?"
        )
        return ASK_CONSENT
    elif 'Medium' in risk_level:
        return handle_medium_risk(update, context)
    elif 'Low' in risk_level:
        return handle_low_risk(update, context)
    else:
        update.message.reply_text(
            "Thank you for sharing. Remember, I'm here to listen anytime."
        )
        return ConversationHandler.END
# Function for Low Risk
def handle_low_risk(update: Update, context:CallbackContext): # type: ignore
    # Send a supportive message for low-risk users
    update.message.reply_text(
        "It seems like you're doing well overall. Keep taking care of yourself! "
        "Remember, it's always good to talk about how you're feeling. I'm here if you need me."
    )
    return ConversationHandler.END


# Function for Medium Risk
def handle_medium_risk(update: Update, context: CallbackContext): # type: ignore
    # Send a message for medium-risk users, encouraging self-care or reaching out for support
    update.message.reply_text(
        "It seems like you're going through something challenging. Please remember that it's okay to ask for help. "
        "Consider reaching out to a friend, family member, or mental health professional. I'm here if you need to talk."
    )
    return ConversationHandler.END
from textblob import TextBlob # type: ignore



# Assessing Risk Levels
def assess_risk_level(user_message):

  low_risk_keywords = [
    # Existing words
    "stressed", "a bit stressed", "managing", "handling", "coping", "positive", "okay", "fine", "breaks", "relax", 
    "calm", "taking care", "self-care", "not too bad", "getting better", "balanced", "improving", "manageable", 
    "dealing with it", "stay positive", "coping well", "manageable stress", "working through",
    
    # New words and phrases
    "feeling good", "feeling okay", "hopeful", "content", "calm and relaxed", "taking it easy", 
    "in control", "feeling rested", "taking time for myself", "feeling energized", "well-rested", 
    "positive outlook", "good mood", "happy", "feeling balanced", "mental clarity", "feeling great", 
    "feeling refreshed", "steady progress", "feeling better", "finding peace", "inner peace", 
    "peaceful", "mentally strong", "feeling light", "keeping things together", "feeling optimistic", 
    "maintaining balance", "keeping calm", "taking a break", "good vibes", "feeling centered", 
    "taking it one step at a time", "feeling motivated", "feeling encouraged", "mentally clear", 
    "calm mind", "peaceful thoughts", "emotionally stable", "taking care of myself", "no stress", 
    "mentally refreshed", "regaining control", "back to normal", "calm and collected", "good day", 
    "positive energy", "mental well-being", "feeling accomplished", "doing well", "everything’s fine", 
    "working it out", "feeling lucky", "doing great", "everything is okay", "smooth sailing", 
    "lighthearted", "everything is under control", "mentally sound", "in a good place", 
    "feeling joyful", "staying calm", "everything is working out", "relaxing day", "enjoying life", 
    "coping effectively", "moving forward", "feeling fulfilled", "feeling grateful", "feeling confident", 
    "keeping it positive", "emotionally balanced", "feeling upbeat", "good state of mind", "feeling secure", 
    "calm and serene", "calm state of mind", "peace of mind", "feeling reassured", "emotionally calm", 
    "steady progress", "feeling stable", "emotionally resilient", "staying focused", "feeling strong", 
    "handling things well", "not overwhelmed", "emotionally composed", "feeling healthy", "all is well", 
    "coping just fine", "dealing with things", "managing just fine", "clear mind", "all good", 
    "good mindset", "feeling safe", "not stressed", "calm energy", "keeping it together", 
    "feeling at ease", "mentally balanced", "moving in the right direction", "taking things in stride", 
    "coping without trouble", "emotionally sound", "mentally sharp", "clear thinking", 
    "mentally capable", "feeling at peace", "emotionally stable", "relaxed and focused", 
    "keeping a positive attitude", "focusing on the good", "mentally fresh", "finding joy", 
    "relaxing and taking care", "feeling calm", "good place mentally", "mentally prepared", 
    "feeling calm and stable", "everything is on track", "no worries", "feeling relieved", 
    "staying strong", "emotionally centered", "clear focus", "mentally resilient", "feeling encouraged", 
    "feeling bright", "emotionally composed", "in good spirits", "maintaining composure", "feeling fine", 
    "feeling serene", "in control of emotions", "feeling calm and clear", "staying level-headed", 
    "in control of stress", "feeling good emotionally", "mentally content", "keeping perspective", 
    "good perspective", "feeling peaceful", "emotionally secure", "emotionally intact", 
    "holding it together", "not feeling rushed", "mentally on track", "feeling happy and calm", 
    "not feeling stressed", "mentally and emotionally stable", "feeling good about life", 
    "managing emotions well", "coping without stress", "keeping things in balance", 
    "handling emotions with care", "not feeling burdened", "emotionally grounded", "emotionally stable", 
    "feeling positive about the future", "staying optimistic", "good emotional well-being", 
    "handling everything just fine", "mentally unworried", "dealing with stress well", 
    "feeling good mentally and emotionally", "emotionally clear", "in a positive headspace", 
    "keeping stress in check", "feeling calm and optimistic", "all in good order", 
    "maintaining emotional balance", "dealing with things positively", "not burdened by stress", 
    "feeling good about myself", "no mental blocks", "mentally at peace", "emotionally content", 
    "mentally satisfied", "staying in control", "emotionally positive", "feeling well-balanced", 
    "feeling emotionally grounded", "handling things calmly", "not feeling pressed", 
    "keeping things under control", "no emotional overwhelm", "in a good mood", "calmly managing things", 
    "feeling optimistic and positive", "no major worries", "feeling mentally fit", "emotionally safe", 
    "keeping everything under control", "feeling strong emotionally", "not feeling anxious", 
    "handling emotions calmly", "everything is going fine", "coping easily", "emotionally steady", 
    "feeling upbeat and relaxed", "calm and positive", "in a calm state of mind", "not emotionally stressed", 
    "emotionally capable", "clear mind and focused", "feeling emotionally confident", 
    "emotionally prepared", "in control of my emotions", "emotionally calm and stable", 
    "feeling good and relaxed", "feeling no pressure", "mentally and emotionally sharp", 
    "no stress at all", "staying balanced emotionally", "feeling clear and calm", "no tension", 
    "mentally feeling good", "in control of everything", "emotionally positive and calm", 
    "handling stress calmly", "feeling no tension", "calm and focused", "feeling strong and confident", 
    "mentally calm", "emotionally capable and strong", "keeping a clear head", "feeling peaceful and calm", 
    "managing things well", "in a peaceful state", "feeling peaceful and in control", "staying grounded", 
    "emotionally aware", "calm and mentally fit", "mentally clear and capable", "emotionally calm and composed", 
    "feeling free of stress", "emotionally composed and stable", "staying mentally and emotionally balanced", 
    "emotionally and mentally sound", "keeping stress at bay", "clear emotions", "feeling steady and calm", 
    "mentally and emotionally at ease", "keeping stress levels low", "feeling calm and positive", 
    "emotionally balanced and composed", "staying in control emotionally", "feeling mentally and emotionally in control"
]
  high_risk_keywords = [
    # Suicidal ideation
    "want to die", "better off dead", "suicide", "end it all", "can't go on", 
    "give up", "no way out", "life is meaningless", "no point in living", 
    "want to disappear", "hurt myself", "self-harm", "cut myself", 
    "overdose", "end my life", "kill myself", "dying inside", 
    "no reason to live", "suffocating", "can't breathe", 
    "feeling trapped", "feeling hopeless", "can't take it anymore", 
    "nothing matters", "I don’t matter", "I can't cope", "I'm done", 
    "no escape", "I don't care anymore", "I can't handle it", 
    "I just want to sleep forever", "it's too much", 
    "feeling dead inside", "worthless", "nobody cares", 
    "nobody would miss me", "nothing will ever change", "there’s no hope", 
    "can’t find a reason to keep going", "life isn't worth it", 
    "I don’t want to live", "ready to give up", "no one understands", 
    "alone forever", "I’m a burden", "better off without me", "it’s too late", 
    
    # Extreme emotional distress
    "breaking down", "crying constantly", "can't stop crying", 
    "completely overwhelmed", "can't control my emotions", "losing it", 
    "falling apart", "shaking uncontrollably", "feeling numb", 
    "can't feel anything", "emotionally broken", "feel like I'm drowning", 
    "everything is crashing down", "nothing left", "it hurts too much", 
    "I’m in so much pain", "emotionally exhausted", "I can't feel anything", 
    "I feel empty", "everything is pointless", "I have no control", 
    "I can't go on", "I want it to end", "I’m suffocating", 
    "everything is falling apart", "I feel trapped", "I can’t handle the pain", 
    
    # Self-harm
    "cutting myself", "I want to hurt myself", "I deserve the pain", 
    "cutting", "burn myself", "burning", "punish myself", 
    "I deserve to suffer", "no one cares if I hurt", "hurting myself", 
    "self-inflicted pain", "pain makes it better", "I want to bleed", 
    "I want to cut", "I need to hurt", "hurting feels good", 
    
    # Hopelessness
    "there's no hope", "I can’t see a future", "life has no meaning", 
    "I’m lost", "there’s nothing left", "it’s all over", 
    "nothing will get better", "no light at the end of the tunnel", 
    "there’s no way out", "there’s no reason to go on", 
    "life is too hard", "I feel so stuck", "life is unbearable", 
    "everything is pointless", "I don’t belong", "no one needs me", 
    "the pain never stops", "nothing ever changes", "I feel like giving up", 
    "I’m hopeless", "I feel helpless", "there's nothing to live for", 
    
    # Isolation and abandonment
    "no one cares", "I'm completely alone", "I have no one", 
    "I don't belong", "no one would miss me", "everyone has left me", 
    "I’m a burden", "I’m not wanted", "I feel invisible", 
    "no one understands me", "I don’t fit in", "I’m abandoned", 
    "I have nobody", "everyone is better off without me", 
    "I’m always alone", "I’ll always be alone", "I don’t deserve love", 
    
    # Severe anxiety or panic
    "I can’t breathe", "I’m suffocating", "I’m panicking", 
    "everything is closing in", "I can’t calm down", "I’m losing control", 
    "I’m having a breakdown", "I feel like I'm dying", "I’m terrified", 
    "I feel like I’m going crazy", "I’m trapped", "everything is too much", 
    "I’m completely overwhelmed", "I’m out of control", "I can’t stop it", 
    "I’m drowning", "I’m choking", "I can’t handle this anymore", 
    "I can’t do this", "I’m freaking out", 
    
    # Loss of self-worth
    "I'm worthless", "I don't matter", "I'm a failure", 
    "I'm not good enough", "I hate myself", "I'm disgusting", 
    "I'm pathetic", "no one would care if I was gone", "I'm useless", 
    "I hate my life", "I ruin everything", "I'm nothing", "I'm trash", 
    "I don't deserve to live", "I'm such a disappointment", 
    "I let everyone down", "I deserve to be alone", "I can’t do anything right", 
    
    # Desperation
    "I’m desperate", "I need help", "I can’t do this alone", 
    "I have no options", "I need someone", "I don’t know what to do", 
    "I can’t find a way out", "I need to escape", "I can’t go on like this", 
    "I don’t know how to stop", "I’m crying for help", 
    "I don’t know how much longer I can hold on", 
    "I need someone to save me", "I’m reaching out", "I’m begging for help"




  
    # Original keywords
    "paranoid", "threatening", "persecution", "mind control", "dangerous thoughts", 
    "fearful", "disturbing", "unreal", "trapped", "surveillance", "poisoned", 
    "disconnected", "bizarre", "shadowy figures", "out to get me", "conspiracy", 
    "being watched", "manipulated", "implanted thoughts", "doom", "exploding thoughts", 
    "intruders", "losing control", "end of the world", "monitored", "fearing death", 
    "hopeless", "in danger", "blackout", "irrational", "mental collapse", "psychotic", 
    "voices in head", "schizophrenic", "paranoia", "split mind", "lost grip", 
    "unreal reality", "vision", "pursued", "frightened", "euphoria", "false beliefs", 
    "triggered", "unsafe", "fragile", "confused", "disoriented", "menacing", 
    "deranged", "powerless", "powerful", "angry", "aggressive", "helpless", 
    "crisis", "breakdown", "obsession", "terror", "out of body", "watched", 
    "spied on", "harassed", "overwhelmed", "out of touch", "captive", 
    "dissociated", "fragmented", "chaos", "unhinged", "malfunction", 
    "tormented", "haunted", "besieged", "possessed", "explosive", "incoherent", 
    "imploding", "entrapment", "fatal thoughts", "worsening", "critical", 
    "catastrophic", "anxiety", "fear of others", "psychopath", "schizo", 
    "nightmares", "violent", "assault", "shadow", "attack", "self-harm", 
    "trouble", "break", "shattered", "losing sanity", "dark thoughts", 
    "uncontrolled", "destruction", "spiraling", "lost time", "delusional", 
    "hallucination", "scary", "risk zone", "danger", "voices", "suicidal",
    
    # Appended keywords based on speech patterns in episodes of high-risk mental illness
    "everyone is against me", "I don't belong here", "they are after me", "I see things", 
    "they're watching", "something is wrong with me", "nothing makes sense", "I can’t trust anyone", 
    "it’s all falling apart", "my head is exploding", "I can’t stop the voices", "I want to disappear", 
    "I’m not real", "someone is controlling me", "my thoughts aren’t mine", "I’m losing my mind", 
    "they’ve poisoned me", "everything is collapsing", "I hear whispers", "they are spying on me", 
    "I feel trapped", "I don’t want to live anymore", "I’m seeing things that aren't there", 
    "I feel disconnected from reality", "I need to escape", "the world is ending", "I can't take it anymore", 
    "I’m a danger to myself", "I feel dead inside", "I can’t breathe", "I feel haunted", 
    "they are manipulating me", "I’m being punished", "nothing matters", "I want to hurt myself", 
    "my mind is breaking", "I'm terrified of everything", "I’m falling apart", "I’m in a dream", 
    "I’m being followed", "there are cameras everywhere", "I can’t control it", "I’m out of control", 
    "everything is a lie", "my brain is on fire", "I’m seeing demons", "I am being possessed", 
    "there’s no escape", "I feel like a ghost", "I hear screams", "they’re reading my mind", 
    "there’s something evil inside me", "they’ve implanted something in me", "I feel so broken", 
    "I’m fading away", "I’m invisible", "it’s not real", "everything is distorted", 
    "I'm losing time", "I’m falling into a black hole", "I feel like I’m being watched", 
    "I’m going to die", "they’re planning to kill me", "I’m a monster", "there’s something wrong with me", 
    "I’m afraid of what I might do", "the walls are closing in", "I feel like I’m drowning", 
    "I’m shattered", "I hear things that aren’t there", "I’m going crazy", "it’s all my fault", 
    "I deserve this", "I can’t escape my mind", "the world is dangerous", "I feel like I’m falling apart", 
    "I feel like I’m being attacked", "I can’t trust my own mind", "I don’t know who I am", 
    "I’m lost in my own thoughts", "I’m afraid of myself", "everything feels so heavy", 
    "I can’t connect to anything", "my life is falling apart", "nothing is real anymore", 
    "my mind is turning against me", "I feel like I’m sinking", "I’m terrified of my own thoughts", 
    "everything is too loud", "I feel like I’m being hunted", "I’m a prisoner in my own head"
]

  medium_risk_keywords = [
    # Commonly used words and phrases indicating moderate stress
    "anxious", "overwhelmed", "tired", "worried", "burnt out", "frustrated", "drained", "exhausted", 
    "mentally exhausted", "emotionally drained", "stressed out", "trouble focusing", "feeling low", 
    "feeling off", "feeling stuck", "can't relax", "on edge", "unmotivated", "feeling down", 
    "can't concentrate", "feeling out of it", "emotionally tired", "struggling", "stressed", 
    "feeling heavy", "can't sleep", "feeling scattered", "uncertain", "foggy mind", "lost focus", 
    "mentally tired", "trouble sleeping", "disconnected", "apathetic", "distracted", 
    "mentally foggy", "insecure", "worried about the future", "nervous", "irritable", 
    "feeling numb", "isolated", "unfocused", "overloaded", "pressured", "nervous energy", 
    "feeling rushed", "can’t think straight", "feeling empty", "moody", "feeling worn out", 
    "feeling tense", "clouded judgment", "emotionally unstable", "feeling flat", 
    "can't keep up", "having doubts", "mentally scattered", "off balance", 
    "feeling disconnected", "emotionally distant", "feeling unsatisfied", "feeling hopeless", 
    "mentally distant", "can't switch off", "running on empty", "feeling shaky", 
    "feeling fragile", "can’t focus", "fearing the worst", "trouble handling things", 
    "emotionally unstable", "mentally checked out", "on autopilot", "mentally overwhelmed", 
    "scattered thoughts", "unsure of myself", "unsure of the future", "emotionally overloaded", 
    "mentally stuck", "emotionally drained", "constantly worried", "feeling vulnerable", 
    "questioning everything", "in a slump", "emotionally vulnerable", "mentally unsteady", 
    "out of sync", "fearful", "doubtful", "unable to think clearly", "barely managing", 
    "feeling unsure", "feeling weak", "mentally slow", "emotionally scattered", 
    "overworking", "worried a lot", "mentally fogged", "mentally blocked", 
    "emotionally out of balance", "feeling disheartened", "can't seem to focus", 
    "feeling out of control", "having difficulty", "feeling weighed down", 
    "unsure how to proceed", "mentally worn", "running on low", "out of energy", 
    "feeling strained", "mentally drained", "on the edge", "losing control", 
    "second-guessing myself", "can't seem to focus", "worried all the time", 
    "burned out", "emotionally strained", "mentally fatigued", "feeling in limbo", 
    "mentally bogged down", "feeling disorganized", "feeling distant", "mentally unstable", 
    "emotionally off-balance", "constantly stressed", "feeling weighed down", 
    "emotionally fragile", "can't switch off my mind", "stressed but hanging on", 
    "mentally checked out", "emotionally stuck", "feeling restless", "emotionally fogged", 
    "feeling off-kilter", "mentally worn down", "feeling pressured", "feeling behind", 
    "mentally unclear", "under pressure", "emotionally shaken", "feeling fatigued", 
    "feeling unfocused", "feeling behind schedule", "mentally lost", 
    "emotionally uncertain", "feeling uneasy", "barely holding on", 
    "feeling spaced out", "nervous thoughts", "mentally overloaded", "feeling unsure of myself", 
    "facing challenges", "feeling stuck in a rut", "feeling unsure of things", 
    "unsure of what to do", "feeling emotionally heavy", "mentally fragile", 
    "struggling with decisions", "emotionally trapped", "trouble making decisions", 
    "can’t shake this feeling", "feeling emotionally lost", "mentally unsure", 
    "feeling pressured by time", "mentally behind", "under a lot of pressure", 
    "emotionally drained by work", "emotionally unfocused", "mentally unbalanced", 
    "struggling to find balance", "mentally strained", "feeling mentally scattered", 
    "constantly feeling rushed", "feeling overwhelmed at work", "mentally stretched thin", 
    "mentally strained from responsibilities", "struggling to keep up", 
    "unsure about future decisions", "emotionally unsure", "feeling mentally stuck", 
    "mentally confused", "emotionally drained by responsibilities", 
    "feeling overwhelmed and unsure", "emotionally overwhelmed", 
    "mentally overloaded with thoughts", "mentally unprepared", "feeling emotionally pressured", 
    "worried about work", "mentally off balance", "feeling like I’m falling behind", 
    "feeling disoriented", "struggling to manage everything", "mentally ungrounded", 
    "feeling out of control emotionally", "emotionally uncertain about decisions", 
    "constantly overthinking", "worried about how things are going", "constantly on edge", 
    "feeling emotionally blocked", "feeling unsettled", "worried about everything", 
    "feeling tense all the time", "mentally strained by expectations", 
    "overwhelmed by responsibilities", "unsure if I’m doing enough", "emotionally stuck in a loop", 
    "emotionally behind schedule", "mentally falling behind", "emotionally out of sync", 
    "emotionally unstable with decisions", "mentally strained by stress", 
    "constantly anxious", "feeling mentally fragile", "emotionally distant from myself", 
    "emotionally burdened by expectations", "emotionally unclear", "feeling weighed down emotionally", 
    "unsure how to handle things", "mentally struggling with time management", 
    "feeling mentally blocked", "unsure how to manage stress", 
    "constantly emotionally tired", "mentally exhausted from work", 
    "emotionally out of balance due to stress", "feeling stuck in my head", 
    "constantly questioning my decisions", "mentally unsure of what to do next", 
    "emotionally overwhelmed by decisions", "constantly feeling emotionally unsteady", 
    "unsure of how to cope", "mentally blocked by indecision", 
    "feeling weighed down by mental fatigue", "emotionally confused by decisions", 
    "emotionally unbalanced by stress", "constantly feeling out of sync", 
    "worried about not keeping up", "feeling mentally trapped", 
    "mentally fatigued by responsibilities", "emotionally unsettled by stress", 
    "emotionally drained by decisions", "mentally lost in overthinking", 
    "emotionally out of touch with myself", "mentally bogged down by thoughts", 
    "emotionally stretched thin by work", "feeling emotionally vulnerable at work", 
    "emotionally confused about life decisions", "emotionally strained by expectations", 
    "mentally weighed down by stress", "feeling emotionally strained by time", 
    "constantly questioning my abilities", "emotionally confused about how to proceed", 
    "emotionally drained by mental blocks", "feeling mentally off-balance by responsibilities", 
    "emotionally unprepared for what’s ahead", "feeling emotionally strained by decisions"
]





  for word in low_risk_keywords:
    if word in user_message.lower():
      return "Low risk"
    
  for word in medium_risk_keywords:
    if word in user_message.lower():
      return "Medium risk"
    
    
    

  for word in high_risk_keywords:
    if word in user_message.lower():
      return "High risk"
    
    # Use the GPT-2 model for further evaluation
    try:
        result = generator(
            f"As a mental health assistant, assess the following message understanding mental health risks .Answer in just two words, Classify the risk as 'Low risk', 'Medium risk', or 'High risk': {user_message}\nRisk Level:",
            max_length=1000,
            truncation=True
        )
        risk_level = result[0]['generated_text'].strip()
        return risk_level
    except Exception as e:
        print(f"GPT-2 error: {e}")
        return None


# Handling Consent for Notifications
def ask_consent(update: Update, context) -> int:
    user_response = update.message.text.lower()
    if 'yes' in user_response:
        update.message.reply_text(
            "Please provide the contact information (Telegram username) of your trusted person."
        )
        return ASK_CONTACTS
    else:
        update.message.reply_text(
            "Alright, I respect your decision. Please consider reaching out to a mental health professional."
        )
        return ConversationHandler.END

# Collecting Trusted Contact Information
def ask_contacts(update: Update, context) -> int:
    trusted_contact = update.message.text
    user_id = update.message.from_user.id

    # Save trusted contact
    context.user_data['trusted_contact'] = trusted_contact

    # Notify trusted contact
    notify_trusted_contact(trusted_contact, user_id, context)

    update.message.reply_text(
        "Thank you. I've notified your trusted contact."
    )
    return ConversationHandler.END

# Notifying Trusted Contacts
def notify_trusted_contact(trusted_contact, user_id, context):
    message = (
        f"Hello, I'm reaching out because your friend (User ID: {user_id}) indicated that they trust you "
        "and may need support. Please consider checking in with them."
    )

    try:
        context.bot.send_message(chat_id='@' + trusted_contact, text=message)
    except Exception as e:
        logger.error(f"Failed to notify trusted contact: {e}")

# Cancel Handler
def cancel(update: Update, context) -> int:
    update.message.reply_text(
        "Conversation cancelled. Feel free to reach out anytime."
    )
    return ConversationHandler.END

# Main Function to Run the Bot
def main():
    # Use Updater instead of Application (for synchronous code)
    updater = Updater(token=telegram_token, use_context=True)

    # Add handlers
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ASK_SYMPTOMS: [MessageHandler(Filters.text & ~Filters.command, ask_symptoms)],
            ASK_CONSENT: [MessageHandler(Filters.text & ~Filters.command, ask_consent)],
            ASK_CONTACTS: [MessageHandler(Filters.text & ~Filters.command, ask_contacts)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Add the conversation handler to the dispatcher
    updater.dispatcher.add_handler(conv_handler)

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
       

