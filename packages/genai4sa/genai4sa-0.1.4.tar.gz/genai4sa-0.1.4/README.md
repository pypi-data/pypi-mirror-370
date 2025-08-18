# GenAI-for-SA
 A tool to generate software design document using LLM models and different prompting techniques.

![alt text](<Screenshot 2025-08-17 183501.png>)

# How to use the tool:
        1. Enter the API Key for OpenAI, GoogleAI or GroqAI depending on the model you want to use.
        2. Select the Model to use.
        3. Select the Prompting technique to use.
        4. Input the textual description of the system. 
        5. Press Generate and wait for the PDF to open. The PDF will be saved in the current working directory from where you ran the tool.
        6. If you want to continue the conversation and iterate over the LLM respond, set Continue Conversation to Yes, and enter the prompt in Textbox and Press Generate.
# Steps to run locally the first time

        1. Clone the repository
        2. Open terminal and go to where repo was cloned.

                cd <repo name>

        3. Run this command there

                pip install -e .

        4. Then enter this command to run the program

                devbot_sa