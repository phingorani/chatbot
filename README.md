# 💬 AI chat bot Auto build

A simple Streamlit app that shows how to build a chatbot using Google's [Gemini Models](https://ai.google.dev/gemini-api/docs/models).

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://chatbot-template.streamlit.app/)

### Requirements
1. A GitHub account
2. A [Gemini API key](https://ai.google.dev/gemini-api/docs/quickstart)
3. A [Google Cloud Platform](https://cloud.google.com/) account
4. A [Streamlit Cloud](https://streamlit.io/cloud) account
5. Python 3.8 or higher

### How to run it on your own machine

1. Install the requirements

   ```
   $ pip install -r requirements.txt
   ```

2. Create an .env file with the following fields for your local environment. (Dont forget to add this to your .gitignore file as you dont want your API key to be public)

   ```
   GEMINI_API_KEY=*** //enter your API key here
   SYSTEM_PROMPT="***" //enter what the prupose of your bot is
   GEMINI_MODEL="***" //enter the model you chose from the list above
   BOT_NAME="***" //enter the bot's name here
   ```

3. Run the app

   ```
   $ streamlit run streamlit_app.py
   ```
Note:
You can also run the app using the command `streamlit run streamlit_app.py --server.port 8501` to use a different port.

Once you run the app, you can start chatting with the bot!

The option to deploy the app on the web is not available yet.
If you want to deploy it on the web, you can use streamlit cloud once you've linked it to your GitHub account.