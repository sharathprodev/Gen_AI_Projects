# Slack app : https://api.slack.com/apps/A05TA7REDCZ/general?
# Python code to talk to Slack APIs and respond back using OpenAI's APIs
# A Custom Slack Emoji :slackifyai: is added in this app
# Path of the Image new Emoji :slackifyai: ========== \Downloads\einstein.png

# A Custom Slack app 'SlackifyAI' using OpenAI's ChatGPT APIs. Solution is build on top of that.
# App Built with Pride by : "DXCSlackesters" Team, lead by Sombir Sheoran<sombir.sheoran2@dxc.com>

                    ############################################################
# +++++++++++++++++++ MAIN Supported Methods in this App are as follows: START ++++++++++++++++++++++++++
                    ###########################################################

# 1. @app.event("message")                              : Listens to DirectMessages sent to the Slack app bot
# 2. @app.event("app_mention")                          : Listens to @mention events for the Slack app bot. Bot replies in a Thread.
# 3. @app.event("app_home_opened")                      : Listens to events @app_home_opened when the Home page of the Slack app is opened
# 4. Slash Commands / supported are as below:
#    4.a. @app.command('/askmeanythingai')              : Whenever someone runs the "/askmeanythingai [Input Text]" Slash command - ASK ANYTHING USING AI
#    4.b  @app.command('/texttranslationai')            : Whenever someone runs the "/texttranslationai [Input Text]" Slash command  - TEXT IS TRANSLATED TO OTHER LANGUAGES USING AI
#    4.c  @app.command('/summarizeachannel')            : Whenever someone runs the "/summarizeachannel [Input Text]" Slash command  - READS ALL MESSGAES IN A CHANNEL AND SHOWS A SUMMARY USING AI
# 5. Message/Global Shortcuts for App are as below:
#    5.a  @app.shortcut("summarize_msg_sc")             : A Message Level Shortcut - Summarizes a LONG Message to a SHORT, CRISP Summarized Messages for easy reading and evaluation
#    5.b  @app.shortcut("sentiment_analysis_msg_sc")    : A Message Level Shortcut - For SENTIMENT ANALYSIS of the Long Text, to identify if the Sentiments are Positive, Negative or Neurtal.
#    5.c  @app.shortcut("translate_text_ai_msg_sc")     : A Message Level Shortcut  - For Translating the Input Text into a Target Language of {drop-down} your own choice
#    5.d  @app.shortcut("summarize_global_sc")          : A Global Level Shortcut  - A GLOBAL Shortcut for the Slackify app that can help Summarize the Long text
# 6. Interactions using the EMOJI Reactions for the main event : @app.event("reaction_added")
#    6.a  :sentiments_ai: Emoji for Sentiment Analysis  : An :sentiments_ai: Emoji reaction is used for the sentiments analysis for the given Text, similar to Message Shortcuts, using OpenAI
#    6.b  :translation_ai: Emoji for Translation        : A :translation_ai: Emoji reaction is used For Translating the Input Text into a Target Language of {drop-down} your own choice
# +++++++++++++++++++ MAIN Supported Methods in this App are as follows: END ++++++++++++++++++++++++++

import os
import openai
import requests
import json
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_bolt import App
from slack_sdk.models.blocks import SectionBlock, DividerBlock, ActionsBlock, ButtonElement
from datetime import date, datetime, timedelta

#Read the JSON Configuration file
with open('env.json') as SlackConfig:
    slack_config_data = json.load(SlackConfig)

# ++++++++++++++++++++++++++++++++++   MAIN APP GLOBAL VARIABLES ++++++++++++++++++++++++++++++++++

SLACK_BOT_TOKEN = slack_config_data['SLACK_BOT_TOKEN']  #Slack App bot token
SLACK_APP_TOKEN = slack_config_data['SLACK_APP_TOKEN']  #Slack app token
OPENAI_API_KEY = slack_config_data['OPENAI_API_KEY']    #Open AI API Key from the OpenAI Account, get from https://platform.openai.com/account/api-keys


# ++++++++++++++++++++++++++++++++++   GENERAL BLOCKKIT UI BLOCKS ++++++++++++++++++++++++++++++++++

buttons_added = False
# Define the UI component blocks with buttons and with a  message
blocksWithButtons = [
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Relevant :thumbsup:"
                    },
                    "style": "primary",
                    "action_id": "button_clicked_relevant"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Irrelevant :thumbsdown:"
                    },
                    "style": "danger",
                    "action_id": "button_clicked_irrelevant"
                }
        ]
        }
]

blocksWithLanguageTranslationOptions = [
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Translate Text :translation_ai:"
                        },
                        "style": "primary",
                        "action_id": "button_clicked_translate"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Select Language for Transalation: "
                },
                "accessory": {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select a language",
                        "emoji": True
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "French",
                                "emoji": True
                            },
                            "value": "french"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "German",
                                "emoji": True
                            },
                            "value": "german"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Hindi",
                                "emoji": True
                            },
                            "value": "hindi"
                        }
                    ],
                    "action_id": "static_language_select_action"
            },
		}
]

# Initialize Slack API clients
bot_client = WebClient(token=SLACK_BOT_TOKEN)
app_client = WebClient(token=SLACK_APP_TOKEN)

# Event API & Web API
app = App(token=SLACK_BOT_TOKEN)

# ++++++++++++++++++++++++++++++++++   @app.event("message") - START +++++++++++++++++++++++++++++++

# Define a listener function for message events - DirectMessages sent to Slack bot
@app.event("message")
def handle_direct_message_to_bot(event, logger, say):
    if event["channel"].startswith("D"):
        respond_bot_direct_message(event, logger, say)

# Function to respond to direct messages
def respond_bot_direct_message(event, logger, say):
    prompt = event["text"]
    display_to_user = f"User asked: {prompt}"
    print(display_to_user)
    logger.info(display_to_user)
    
    say(f"Bot :slackifyai: received your input. Request is under Process :man-running:")

    try:
        # Call the ChatGPT API to generate a response
        openai.api_key = OPENAI_API_KEY
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=512,
            n=1,
            stop=None,
            temperature=0.5,
        )
        response_text_from_bot = response.choices[0].text.strip()
        
        reply_text = f"*What you asked for*: {prompt} \n\n*Below is the response to your input* :thread:\n\n{response_text_from_bot}"
        # Send the response back to the user who sent the message
        bot_client.chat_postMessage(
            channel=event["channel"],
            text=reply_text,
        )
        print(reply_text)
        logger.info(reply_text)

    except SlackApiError as e:
        print("Error sending message: {}".format(e))
        
# ++++++++++++++++++++++++++++++++++   @app.event("message") - END +++++++++++++++++++++++++++++++

# +++++++++++++++++++++++++++++++ @app.event("app_mention")- START +++++++++++++++++++++++++++++++

# This gets activated when the bot is tagged in a channel
@app.event("app_mention")
def handle_message_events(body, say, logger):
    # Log message
    prompt = str(body["event"]["text"]).split(">")[1]
    global buttons_added
    
    # Let the user know that we are busy with the request
    bot_client.chat_postMessage(
        channel=body["event"]["channel"],
        thread_ts=body["event"]["event_ts"],
        text="Hello, I am your SlackifyAI Bot :slackifyai:\nThanks for your input to @app:mention, it's being processed :mag_right:."
    )
    
    # Check ChatGPT
    openai.api_key = OPENAI_API_KEY
    completion = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=512,
        n=1,
        stop=None,
        temperature=0.5
    )
    response_text = completion.choices[0].text

    # Reply to thread
    bot_client.chat_postMessage(
        channel=body["event"]["channel"],
        thread_ts=body["event"]["event_ts"],
        text=f"*What you asked for :sentiments_ai:*: {prompt} \n\n*Below is the respond to your input* :thread:\n{response_text}"
    )
    
    # Update the Slack app's Home tab with the welcome message and app information
    if not buttons_added:
        say(
            blocks=blocksWithButtons,
            thread=body["event"]["event_ts"]
        )
        buttons_added = True
    
# +++++++++++++++++++++++++++++++ @app.event("app_mention")- END +++++++++++++++++++++++++++++++

# +++++++++++++++++++++++++++++++ @app.event("app_home_opened")- START +++++++++++++++++++++++++++++++

# Define a listener function for ("app_home_opened") events

# Define the 'Home' tab view
def home_tab_view(user_id):
    printText = f"Hello, <@{user_id}>! Welcome to the Home tab of *Slackify* app :slackifyai:.\n"
    f"Slackify is a game-changing application that revolutionizes the interaction within Slack using AI. Harnessing the power of Generative AI, it responds to customer queries with unmatched precision and speed, just like GPT.\n"
    f"Just say goodbye to mundane, time-consuming tasks, and hello to a seamless, efficient support experience.\n"
    f"Check 'About' Tab for more details..."
    return {
        "type": "home",
        "blocks": [
            {
                "type": "section",
                "block_id": "home_greeting",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Hello, <@{user_id}>! Welcome to the Home tab :slackifyai:."
                }
            },
            {
                "type": "section",
                "block_id": "home_buttons",
                "text": {
                    "type": "mrkdwn",
                    "text": "What would you like to do? Slackify is a game-changing application that revolutionizes the interaction within Slack using AI. Harnessing the power of Generative AI, it responds to customer queries with unmatched precision and speed, just like GPT."
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "style" : "danger",
                        "text": "Connect to Salesforce"
                    },
                    "action_id": "connect_to_salesforce_button",
                    "url": "https://login.salesforce.com"  # Redirect URL for Salesforce OAuth
                }
            }
        ]
    }

@app.event("app_home_opened")
def handle_app_home_opened(event, say, client):
    global buttons_added
    # Example: Send a message to the user
    user_id = event["user"]
    # Use the user_id parameter to construct the 'Home' tab view
    view = home_tab_view(user_id)
    # Publish the view to the user's 'Home' tab
    client.views_publish(
        user_id=user_id,
        view=view
    )
    
    welcome_message = f"Dear user *<@{user_id}>!*, Welcome to the *'Slackify'* :slackifyai: app's Home page!"

    # Define the UI component blocks with buttons and with a  message
    blocks = [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": welcome_message},
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Relevant :thumbsup:"
                        },
                        "style": "primary",
                        "action_id": "button_clicked_relevant"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Irrelevant :thumbsdown:"
                        },
                        "style": "danger",
                        "action_id": "button_clicked_irrelevant"
                    }
            ]
            }
    ]
    
    # Update the Slack app's Home tab with the welcome message and app information
    if not buttons_added:
        say(blocks=blocks)
        buttons_added = True
        

# Action handler for 'button_clicked_relevant' and  'button_clicked_irrelevant' actions
# Action handler for 'button_clicked_relevant' action
@app.action("button_clicked_relevant")
def handle_button_clicked_relevant(ack, body, respond):
        ack()
        respond("Relevant :thumbsup: button clicked!.\nYour valuable feedback is really appreciated :clap:!")

# Action handler for 'button_clicked_irrelevant' action
@app.action("button_clicked_irrelevant")
def handle_button_clicked_irrelevant(ack, body, respond):
        ack()
        respond("Irrelevant :thumbsdown: button clicked!\nYour valuable feedback is really appreciated :clap:!")
        
# +++++++++++++++++++++++++++++++ @app.event("app_home_opened")- END +++++++++++++++++++++++++++++++

                                #########################################
                                # SLASH COMMANDS SECTION /command [text]
                                #########################################

# +++++++++++++++++++++++++++++++ @app.command('/askmeanythingai') - START +++++++++++++++++++++++++

# This gets activated when the bot receives a '/askmeanythingai' slash command
@app.command('/askmeanythingai')
def handle_slash_command_askmeanythingai(ack, body, logger, say):
    ack()
    logger.info(body)
    # Log command
    command = body["command"]
    text = body["text"]

    # Let the user know that we are processing the command
    bot_client.chat_postMessage(
        channel=body["channel_id"],
        text=f"\nBot :slackifyai: is processing your command *{command}* :hourglass_flowing_sand:"
    )

    # Process the command using ChatGPT
    openai.api_key = OPENAI_API_KEY
    completion = openai.Completion.create(
        model="text-davinci-003",
        prompt=text,
        temperature=0.3,
        max_tokens=512,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    response_text = completion.choices[0].text
        
    say(f"\n:ab: *Original Text: *= {text}\n")
    # Check if response_text is in tabular format
    is_tabular = False
    if '|' in response_text:
        is_tabular = True

    # Reply to the slash command
    if is_tabular:
        # Display as a table block
        table_block = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"```\n{response_text}\n```"
            }
        }
        say(
            blocks=[table_block],
            channel=body["channel_id"]
        )
    else:
        # Display as plain text
        say(
            text=response_text,
            channel=body["channel_id"]
        )
    
    logger.info('response_text=\n' + response_text)

# +++++++++++++++++++++++++++++++ @app.command('/askmeanythingai') - END +++++++++++++++++++++++++

# +++++++++++++++++++++++++++++++ @app.command('/texttranslationai') - START +++++++++++++++++++++

# This gets activated when the bot receives a '/texttranslationai' slash command
@app.command('/texttranslationai')
def handle_slash_command_texttranslationai(ack, body, logger,say):
    ack()
    logger.info(body)
    # Log command
    command = body["command"]
    text_to_translate = body["text"]

    # Let the user know that we are processing the command
    bot_client.chat_postMessage(
        channel=body["channel_id"],
        text=f"Bot :slackifyai: is translating your text using command *{command}* :hourglass_flowing_sand:"
    )

    openai.api_key = OPENAI_API_KEY
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"Translate below text into 1. French, 2. Japanese, 3. Hindi: Put respective translations in format with Numbered bullets with header mentioning language: Translation\n\n {text_to_translate}\n\n",
        temperature=0.3,
        max_tokens=512,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    
    translated_text = response.choices[0].text
    
    say(
        blocks=blocksWithLanguageTranslationOptions
    )
    
    # Call the OpenAI API for translation
    #translated_text = translate_text_function(text_to_translate)
    
    # Send the translation back to Slack
    #say(f"Translation for '{text_to_translate} is below :white_check_mark:':\n \n{translated_text}")
    
    # Reply to the slash command
    bot_client.chat_postMessage(
        channel=body["channel_id"],
        text=f"\n:translation_ai: *Original Text for Translation:*\n{text_to_translate}\n*Translated Text is as below*: :writing_hand:\n {translated_text}"
    )
    
    logger.info('translated_text=\n' + translated_text)

# +++++++++++++++++++++++++++++++ @app.command('/texttranslationai') - END +++++++++++++++++++++

@app.command('/summarizeachannel')
def handle_slash_command_summarizeachannel(ack, body, logger,say):
    ack()
    logger.info(body)
    
    # Log command
    command = body["command"]
    channel_id = body["channel_id"]
    
    # Fetch channel information to get the channel name
    channel_info = app.client.conversations_info(channel=channel_id)
    channel_name = channel_info["channel"]["name"]
    
    # Get today's date and the date for the previous day
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    
    # Calculate timestamps for oldest and latest
    oldest_ts = int((yesterday - timedelta(days=1)).timestamp())
    latest_ts = int(yesterday.timestamp())
    
    # Fetch channel history for yesterday
    response = app.client.conversations_history(
        channel=channel_id,
        oldest=oldest_ts,
        latest=latest_ts,
        inclusive=True
    )
    all_channel_messages = response["messages"]

    # Extract message texts, excluding bot messages
    all_channel_messages_texts = [message["text"] for message in all_channel_messages if "text" in message and message.get("subtype") != "bot_message"]
    
    say(f"Slack Command *{command}* received. Bot :slackifyai: is processing all the messages for summarization...")

    # Split the messages into chunks of 4096 tokens each
    chunks = []
    chunk = ""
    for text in all_channel_messages_texts:
        if len(chunk) + len(text) > 4096:
            chunks.append(chunk)
            chunk = text
        else:
            chunk += "\n" + text
    if chunk:
        chunks.append(chunk)

    final_summaries = []
    
    # Process each chunk separately
    for chunk in chunks:
        prompt2OpenAI = (
            f"Please provide a concise yet comprehensive summary of the content given at the end, that includes the following points:\n"
            f"1. Key discussions and Learnings\n"
            f"2. Important decisions made\n"
            f"3. Any points of actions\n"
            f"4. Significant information shared in the channel\n"
            f"Avoid unnecessory and duplicate contents. Give proper line spaces between the main headings (put in  Bold letters) and the bulleted notes\n"
            f"The final text to summarize has been given below. Please process this using the given instructions and prepare in bullet points with proper headings.\n\n"
            f"{chunk}\n"
        )
        
        # Call the ChatGPT API to generate the summary
        openai.api_key = OPENAI_API_KEY
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt2OpenAI,
            max_tokens=512,  # Adjust as needed for a longer summary
            temperature=0.5,  # You can experiment with the temperature for different levels of creativity
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop=None  # Allows the model to generate a more natural ending
        )

        # Extract the generated summary from the response and add it to final_summaries list
        final_summaries.append(response.choices[0].text.strip())

    # Join all summaries into a single string separated with a line break
    final_summarised_text_channel = "\n".join(final_summaries)
    
    # Reply to the slash command with formatted text
    say(
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f":book: *Here is the summary of messages in the channel *{channel_name}*:\n{final_summarised_text_channel}"
                }
            }
        ],
        channel=body["channel_id"]
    )
    
    logger.info('final_summarised_text_channel=\n' + final_summarised_text_channel)


# +++++++++++++++++++++++++++++++ @app.command('/summarizeachannel') - START +++++++++++++++++++++


# +++++++++++++++++++++++++++++++ @app.command('/summarizeachannel') - END +++++++++++++++++++++

                                ###########################################
                                # MESSAGE SHORTCUT SECTION: Global/Message
                                ###########################################

# ++++++++++++++++++++ @app.shortcut("handle_message_shortcut_summarize_msg_sc") - START ++++++++++

# This gets activated when the bot receives a message shortcut for LONG MESSAGE SUMMARIZATION
@app.shortcut("summarize_msg_sc")
def handle_message_shortcut_summarize_msg_sc(ack, body, logger, say):
    # Acknowledge the shortcut request
    ack()
    logger.info(body)
    # Log command
    #command = body["command"]
    text_to_summarise = body["message"]["text"]
    user_id = body["message"]["user"]
    message_ts = body["message"]["ts"]
  
    # Send the message back to Slack
    say(f"Bot :slackifyai: is summarising your text :hourglass_flowing_sand:")
    
    openai.api_key = OPENAI_API_KEY
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"Summarise below text in minimum possible words as bullet points: \n\n {text_to_summarise}\n\n",
        temperature=0.5,
        max_tokens=512,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    
    # Add your trademarked message
    trademarked_message = "\n\n_Copyright © 2023 DXC Technology. All rights reserved. Content processed using OpenAI's APIs._"
      
    summarised_text = response.choices[0].text.strip() + f"*{trademarked_message}*"
    
    # Send the message back to Slack
    say(f"\n:ab: *Original Text for Summarisation*= {text_to_summarise}\n\n*:arrow_forward: Summarised Text is as below*= :writing_hand:\n {summarised_text}")
    
    logger.info('summarised_text=\n' + summarised_text)

# ++++++++++++++++++++ @app.shortcut("handle_message_shortcut_summarize_msg_sc") - START ++++++++++

# ++++++++++++++++++++ @app.shortcut("handle_message_shortcut_sentiment_analysis_msg_sc") - START ++++++++++
# This gets activated when the bot receives a message shortcut for SENTIMENTS ANALYSIS
@app.shortcut("sentiment_analysis_msg_sc")
def handle_message_shortcut_sentiment_analysis_msg_sc(ack, body, logger, say):
    # Acknowledge the shortcut request
    ack()
    logger.info(body)
    # Log command
    #command = body["command"]
    text_for_sentiment_analysis = body["message"]["text"]
    user_id = body["message"]["user"]
    message_ts = body["message"]["ts"]
   
    # Send the message back to Slack
    say(f"Bot :slackifyai: is analysing sentiments for your text :hourglass_flowing_sand:")

    openai.api_key = OPENAI_API_KEY
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"You are an AI language model trained to analyze and detect the sentiment of product reviews or some text messages."
        f"Analyze the following product review or text message and determine if the sentiment is: positive, negative or neutral."
        f"Return only a single word, either POSITIVE :thumbsup: , NEGATIVE :thumbsdown: or NEUTRAL:heavy_equals_sign: : \n\n {text_for_sentiment_analysis}\n\n."
        f"Also, briefly summarize your reason and explanation for your choice",
        temperature=0.3,
        max_tokens=512,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    
    # Add your trademarked message
    trademarked_message = "\n\n_Copyright © 2023 DXC Technology. All rights reserved. Content processed using OpenAI's APIs._"
        
    analysis_output_text = response.choices[0].text.strip() + f"*{trademarked_message}*"

    # Send the message back to Slack
    say(f"\n:ab: *Original Text for Sentiment Analysis*= {text_for_sentiment_analysis}\n\n*:arrow_forward: Sentiments from the given message are*:= :writing_hand:\n {analysis_output_text}")
    logger.info('analysis_output_text=\n' + analysis_output_text)

# ++++++++++++++++++++ @app.shortcut("handle_message_shortcut_sentiment_analysis_msg_sc") - END ++++++++++

# +++++++++++++++++++++++++++++++++++++ @app.shortcut("translate_text_ai_msg_sc") - START ++++++++++++++++

class App:
    def __init__(self):
        self.body_text = None
     
    @staticmethod    
    @app.shortcut("translate_text_ai_msg_sc")
    def handle_message_shortcut_translate_text_ai_msg_sc(ack, body, say, logger):
        # Acknowledge the shortcut request
        ack()
        App.body_text = body["message"]["text"]
        # Define the language options for the drop-down menu
        language_translation_options = [
            {"text": "French", "value": "french"},
            {"text": "German", "value": "german"},
            {"text": "Hindi", "value": "hindi"}, 
            {"text": "Portuguese", "value": "portuguese"},
            {"text": "Spanish", "value": "spanish"}
        ]
        
        # Create a message with the drop-down menu
        popUpMessageForLangSelection = {
            "text": "Select a language for translation from the drop-down: :sentiments_ai:",
            "attachments": [
                {
                    "text": "Choose a language:",
                    "fallback": "You are unable to choose a language",
                    "callback_id": "translate_text_to_selected_language",
                    "color": "#3AA3E3",
                    "attachment_type": "default",
                    "actions": [
                        {
                            "name": "language_list",
                            "text": "Select a Language",
                            "type": "select",
                            "options": language_translation_options
                        }
                    ]
                }
            ]
        }

        # Send the message to Slack for Language Selection pop-up
        say(popUpMessageForLangSelection)

    @staticmethod
    @app.action("translate_text_to_selected_language")
    def handle_translate_text_to_selected_language(ack, body, client, say, logger):
        # Acknowledge the language selection
        ack()
        logger.info(body) 
        
        # Get the selected language from the user
        selected_language = body["actions"][0]["selected_options"][0]["value"]
        #say(f"*DEBUG: selected_language:*= {selected_language}")

        # Get the user's input text from the `body_text` variable in the `@app.shortcut("translate_text_ai_msg_sc")` function
        user_input_text = App.body_text
        #say(f"*DEBUG: user_input_text:*= {user_input_text}")
        
        say(f":slackifyai: is delighted to assist you with the translation into {selected_language}!\n")
    
        promptForTranslation=(
        f"Assume that you're a google Translator. Translate the following text into {selected_language} language with best possible accuracy:\n"
        f"{user_input_text}\n"
        )
        
        # Do the actual Text Tranlation call using the {selected_language} and the {user_input_text}
        openai.api_key = OPENAI_API_KEY
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=promptForTranslation,
            max_tokens=512,  # Adjust as needed, Max has been set here for you
            temperature=0.5  # Adjust for desired creativity
        )

        # Add your trademarked message
        trademarked_message = "\n\n_Copyright © 2023 DXC Technology. All rights reserved. Content processed using OpenAI's APIs._"
        
        translated_text = response.choices[0].text.strip() + f"*{trademarked_message}*"

        # Send the translated text back to Slack
        client.chat_postMessage(
            channel=body["channel"]["id"],
            text=f"Translated Text in ({selected_language}) language by :slackifyai: : {translated_text}"
        )
    
app_instance = App()
    
@app.shortcut("translate_text_ai_msg_sc")
def handle_message_shortcut_translate_text_ai_msg_sc(ack, body, say, logger): app_instance.handle_message_shortcut_translate_text_ai_msg_sc(ack, body, say, logger)

@app.action("translate_text_to_selected_language")
def handle_translate_text_to_selected_language(ack, body, client, say, logger): app_instance.handle_translate_text_to_selected_language(ack, body, client, say, logger)

# +++++++++++++++++++++++++++++++++++++ @app.shortcut("translate_text_ai_msg_sc") - END ++++++++++++++++

# ++++++++++++++++++++++++++++++++++++++++ @app.shortcut("summarize_global_sc") - START ++++++++++++++++++++
# This gets activated when the bot receives a GLOBAL SHORTCUT
@app.shortcut("summarize_global_sc")
def handle_global_shortcut(ack, body):
    # Acknowledge the shortcut request
    ack()

    # Extract the selected text
    text = body["message"]["text"]

    # Process the text using ChatGPT
    openai.api_key = OPENAI_API_KEY
    completion = openai.Completion.create(
        engine="text-davinci-003",
        prompt=text,
        max_tokens=512,
        n=1,
        stop=None,
        temperature=0.5
    )
    summary = completion.choices[0].text

    # Send the summarized response to the user
    bot_client.chat_postMessage(
        channel=body["user"]["id"],
        text=f"Summary: {summary}"
    )

# ++++++++++++++++++++++++++++++++++++++++ @app.shortcut("summarize_global_sc") - END ++++++++++++++++++++


# ++++++++++++++++ @app.event("reaction_added") : Sentiments Analysis using :sentiments_ai: Emoji- START         ++++++++++++++++++++
# ++++++++++++++++ @app.event("reaction_added") : Language Translations using :translation_ai: Emoji- START ++++++++++

class AppInstance:
    def __init__(self):
        self.body_text = None

app_instance_emoji = AppInstance()

@app.event("reaction_added")
def handle_reaction(event, say):
    emoji = event["reaction"]
    message_ts = event["item"]["ts"]
    channel = event["item"]["channel"]
    
    if emoji == "sentiments_ai":
        text_for_sentiment_analysis = get_message_text(channel, message_ts)
        #say(f"DEBUG Text= {text_for_sentiment_analysis}")
        if text_for_sentiment_analysis:
            say(f"Bot :slackifyai: is analyzing sentiments for the selected message using Emoji :sentiments_ai: ")
            app_instance_emoji.body_text = text_for_sentiment_analysis
            analyze_sentiments(say)

    elif emoji == "translation_ai":
        text_for_translation = get_message_text(channel, message_ts)
        #say(f"DEBUG :translation_ai: Text:= {text_for_translation}")
        if text_for_translation:
            say(f"Bot :slackifyai: is translating the selected message using Emoji :translation_ai:") 
            app_instance_emoji.body_text = text_for_translation
            send_language_selection_message(say)

def get_message_text(channel, message_ts):
    try:
        # Process the text using ChatGPT
        openai.api_key = OPENAI_API_KEY
        #result = app.client.conversations_history(channel=channel, latest=message_ts, limit=1)
        result = app.client.conversations_replies(channel=channel, ts=message_ts)
        
        message = result["messages"][0]
        if "text" in message:
            return message["text"]
    except Exception as e:
        print(f"Error retrieving message text: {str(e)}")
    return None

def analyze_sentiments(say):
    text_for_sentiment_analysis = app_instance_emoji.body_text
    #say(f"Bot :slackifyai: is analyzing sentiments for the selected Message :hourglass_flowing_sand:")

    # Process the text using ChatGPT
    openai.api_key = OPENAI_API_KEY
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"You are an AI language model trained to analyze and detect the sentiment of product reviews or some text messages."
        f"Analyze the following product review or text message and determine if the sentiment is: positive, negative, or neutral."
        f"Return only a single word, either POSITIVE :thumbsup:, NEGATIVE :thumbsdown:, or NEUTRAL:heavy_equals_sign: : \n\n {text_for_sentiment_analysis}\n\n."
        f"Also, briefly summarize your reason and explanation for your choice",
        temperature=0.3,
        max_tokens=512,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )

    # Add your trademarked message
    trademarked_message = "\n\n_Copyright © 2023 DXC Technology. All rights reserved. Content processed using OpenAI's APIs._"

    analysis_output_text = response.choices[0].text.strip() + f"*{trademarked_message}*"

    say(f"\n:ab: *Original Text for Sentiment Analysis*= {text_for_sentiment_analysis}\n\n*"
        f":arrow_forward: Sentiments from the given message are*:= :writing_hand:\n {analysis_output_text}")

def send_language_selection_message(say):
    language_translation_options = [
        {"text": "French", "value": "french"},
        {"text": "German", "value": "german"},
        {"text": "Hindi", "value": "hindi"},
        {"text": "Portuguese", "value": "portuguese"},
        {"text": "Spanish", "value": "spanish"}
    ]

    message = {
        "text": "Select a language for translation from the drop-down: :eyes:",
        "attachments": [
            {
                "text": "Choose a language:",
                "fallback": "You are unable to choose a language",
                "callback_id": "translate_text_to_selected_language_emoji",
                "color": "#3AA3E3",
                "attachment_type": "default",
                "actions": [
                    {
                        "name": "language_list",
                        "text": "Select a Language",
                        "type": "select",
                        "options": language_translation_options
                    }
                ]
            }
        ]
    }

    say(message)

@app.action("translate_text_to_selected_language_emoji")
def handle_translate_text_to_selected_language_emoji(ack, body, client, say, logger):
    ack()
    selected_language = body["actions"][0]["selected_options"][0]["value"]
    user_input_text = app_instance_emoji.body_text
    say(f":slackifyai: is translating text into {selected_language}!\n")

    prompt_for_translation = (
        f"Assume that you're a Google Translator. Translate the following text into {selected_language} language with the best possible accuracy and add the target language country Flag in the beginning of the Translated text output for country of language origin:\n"
        f"{user_input_text}\n"
    )

    # Process the text using ChatGPT
    openai.api_key = OPENAI_API_KEY
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt_for_translation,
        max_tokens=512,
        temperature=0.5
    )

    # Add your trademarked message
    trademarked_message = "\n\n_Copyright © 2023 DXC Technology. All rights reserved. Content processed using OpenAI's APIs._"

    translated_text = response.choices[0].text.strip() + f"*{trademarked_message}*"
    
    client.chat_postMessage(
        channel=body["channel"]["id"],
        text=f"Translated Text in ({selected_language}) language by :slackifyai: \n {translated_text}"
    )

# ++++++++++++++++ @app.event("reaction_added") : Sentiments Analysis using :sentiments_ai: Emoji- END ++++++++++
# ++++++++ @app.event("reaction_added") : Language Translations using :translation_ai: Emoji- END ++++++++++++

# =============== Start the Python Slack app =========================

if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()
    
# =============== Start the Python Slack app =========================