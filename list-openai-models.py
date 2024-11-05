import openai

# Set your OpenAI API key only if you do not have the OPENAI_API_KEY environment variable set
#openai.api_key = '<OPENAI_API_KEY>'

print("Listing your available models to use programmatically\n")
models = openai.models.list()
for model in models:#['data']:
    print(model.id)
