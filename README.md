# textGPT
Fully customizable SMS interface to OpenAI deployed with Twilio and Flask.
- All models are hosted on OpenAI's API are supported
- All model settings including system_prompt are modifiable mid conversation
- Messages are stored in SQL db giving GPT memory of the conversation history
- Images can be created edited using the #image command
- Token limits, message rate limits, etc support soon


## [textGPT](textGPT.py) Commands
```
TextGPT Commands:
#help
- prints this help message

#get [<key>|'settings'] 
- get your current setting for <key> or all settings

#set <key> <value>
- set your current setting for <key> to <value>

Keys for #get and #set:
- model: the OpenAI model to use 
- system_prompt: the prompt to use to insruct the model of what to do
- stop_sequence: the sequence of tokens to use to stop the model from generating more tokens
- max_tokens: the maximum number of tokens to generate
- temperature: the sample temperature to use when generating tokens (higher = more random)
- top_p: the nucleus sampling probability to use when generating tokens (higher = more random)
- frequency_penalty: the frequency penalty to use when generating tokens (higher = more conservative)
- presence_penalty: the presence penalty to use when generating tokens (higher = more conservative)

#reset ['all'|'messages'|'settings']
- all: resets everything
- messages: resets all messages
- settings: resets all settings

#models
- prints all available models

#limits
- prints your current usage limits

#image <'create'|'edit'|'variation'> <prompt>
- create: creates an image from the prompt
- edit: edits an image from the prompt
- variation: creates a new variation of an image 
```

## [infinite-free-ngrok.sh](infinite-free-ngrok.sh) Usage

Shell script to run ngrok in a loop and update the webhook url in Twilio each time ngrok restarts after ~2 hours
- Usage:
```./infinite-free-ngrok.sh <flask port> <timeout>``` 
- Requires Twilio account SID, auth token, and phone number exported as environment variables `(TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`)
