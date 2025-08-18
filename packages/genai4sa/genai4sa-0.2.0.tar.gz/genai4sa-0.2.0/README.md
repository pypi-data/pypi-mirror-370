# GenAI-for-SA
 A tool to generate software design document using LLM models and different prompting techniques.

[![PyPi](https://img.shields.io/pypi/v/GenAI4SA.svg)](https://pypi.org/project/genai4sa/)
[![Downloads](https://static.pepy.tech/badge/GenAI4SA)](https://pypi.org/project/genai4sa/)
![alt text](<Screenshot 2025-08-17 183501.png>)

# How to use the tool:
        1. Enter the API Key for OpenAI, GoogleAI or GroqAI depending on the model you want to use.
        2. Select the Model to use.
        3. Select the Prompting technique to use.
        4. Input the textual description of the system. 
        5. Press Generate and wait for the PDF to open. The PDF will be saved in the current working directory 
        from where you ran the tool.
        6. If you want to continue the conversation and iterate over the LLM respond, set Continue Conversation 
        to Yes, and enter the prompt in Textbox and Press Generate.

# How to download the library and run the tool:
        1. Install with this command (enter in command prompt/terminal):
            pip install genai4sa
        2. Run with this command:
            genai4sa
            
# How to Contribute:
        1. Fork the repository at https://github.com/yorku-ease/devbot_SA
        2. Create a feature branch: `git checkout -b feature/my-feature`
        3. Make your changes and test.
        4. Commit and push.
        5. Open a Pull Request (PR)

# How to run locally
        1. Open terminal and go to where repo was cloned.
                cd <repo name>
        2. Run this command there
                pip install -e .
        3. Then enter this command to run the program
                genai4sa
