import customtkinter
import tkinter.filedialog
import os
# import devbot
# import devbot_assistant
from . import devbot_assistant
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("green")

class App(customtkinter.CTk):

    def __init__(self):
        super().__init__()

        # configure window
        self.title("DevBot")
        self.geometry(f"{800}x{580}")
        customtkinter.set_widget_scaling(1.2)

        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # widgets for sidebar
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="DevBot", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, command=self.home_button_event, text="Home")
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)
        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame, command=self.sign_in_event, text="Login")
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=(10,0))

        self.models_label = customtkinter.CTkLabel(self.sidebar_frame, text="Models:", anchor="w")
        self.models_label.grid(row=3, column=0, padx=20, pady=(10, 0))

        self.models_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame,
                                                 values=["gpt-4o", "gpt-4o-mini", "o3", "o1",
                                                         "meta-llama/llama-4-maverick-17b-128e-instruct",
                                                         "gemini-2.0-flash", "gemini-1.5-pro", 
                                                         "llama-3.3-70b-versatile", "llama-3.1-8b-instant",
                                                         "llama-guard-3-8b", "llama3-70b-8192",
                                                         "llama3-8b-8192", "gemma2-9b-it"])
        self.models_optionemenu.grid(row=4, column=0, padx=20, pady=(10, 5))

        self.docs_label = customtkinter.CTkLabel(self.sidebar_frame, text="Prompt:", anchor="w")
        self.docs_label.grid(row=5, column=0, padx=20, pady=(10, 0))

        self.docs_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame,
                                                 values=["Zero-Shot", "In-Context", "Chain-of-Thought", "SDD", "Details"])
        self.docs_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 5))

        self.continue_chat_label = customtkinter.CTkLabel(self.sidebar_frame, text="Continue Chat:", anchor="w")
        self.continue_chat_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.continue_chat_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Yes", "No"]) #command=self.change_appearance_mode_event
        self.continue_chat_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 5))
       
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=9, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=10, column=0, padx=20, pady=(10, 5))

        self.description_label = customtkinter.CTkLabel(self, text="Enter System Desciption:", anchor="w")
        self.description_label.grid(row=2, column=1, padx=(0,0), pady=(0, 0), sticky="w")
        # Entry to enter system description
        self.description_entry = customtkinter.CTkTextbox(self, width=400, height=100)  # system description stored here
        self.description_entry.grid(row=3, column=1, padx=(0, 0), pady=(0, 10))

        # button to start api call
        self.main_button_1 = customtkinter.CTkButton(master=self, text="Generate", fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), command=self.send_request)
        self.main_button_1.grid(row=3, column=3, padx=(20, 20), pady=(20, 20))

        self.textbox = customtkinter.CTkTextbox(self, width=340)
        self.textbox.grid(row=0, column=1, columnspan=3, padx=(0, 0), pady=(0, 0), sticky="nsew")

        # set default values
        self.continue_chat_optionemenu.set("No")
        self.scaling_optionemenu.set("120%")
        self.textbox.insert("0.0", "Devbot to generate Software Architecture powered by ChatGPT, Llama, and more.\n\n")
        self.textbox.insert("end", "Enter API keys for OPENAI, GoogleAI and Groq before Continuing.\n\n")
    def home_button_event(self):
        print("Home button pressed")

    def sign_in_event(self):
        print("Sign in press")
        self.window = customtkinter.CTkToplevel(self)
        self.window.title("Sign In")
        self.window.geometry("340x145")

        self.usertoken_label = customtkinter.CTkLabel(self.window, text="Access Token:", anchor="w")
        self.usertoken_label.grid(row=0, column=0, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.usertoken_entry = customtkinter.CTkEntry(self.window) # contains the access token of user
        self.usertoken_entry.grid(row=0, column=1, padx=(20, 20), pady=(20, 0), sticky="nsew")
        self.save_button = customtkinter.CTkButton(self.window, text="Save", command=self.save_login_button_event)
        self.save_button.grid(row=5, column=0, columnspan=2, padx=(20, 20), pady=(20, 20), sticky="nsew")

    def save_login_button_event(self):
        self.store_api_key_to_file(self.usertoken_entry.get())
        self.textbox.insert("end", "API Key saved.\n")
        self.window.destroy()

    def store_api_key_to_file(self, api_key):
        """
        Writes the API key to a file.
        """
        # get directory where script is downloaded to create output file
        script_dir = os.path.dirname(os.path.realpath(__file__))
        name= ''
        if self.models_optionemenu.get() in ["gpt-4o", "gpt-4o-mini", "o3", "o1"]:
            name = 'openai_api_key'
        elif self.models_optionemenu.get() in ["gemini-2.0-flash", "gemini-1.5-pro"]:
            name = 'google_api_key'
        else:
            name = 'groq_api_key'

        api_file = os.path.join(script_dir, name)
        with open(api_file, "w") as f:
            f.write(api_key)

    def send_request(self):
        description = self.description_entry.get("1.0", "end").strip()
        model = self.models_optionemenu.get()
        docType = self.docs_optionemenu.get()
        continueChat = True if self.continue_chat_optionemenu.get() == "Yes" else False
        #devbot.query_llm(description, model, docType)
        try:
            devbot_assistant.query_llm(description, model, docType, continueChat)
            self.textbox.insert("end", "✅ System design document created for the given system.\n\n")
        except FileNotFoundError as e:
            self.textbox.insert("end", f"❌ Error: {str(e)}\n\n")
        except RuntimeError as e:
            self.textbox.insert("end", f"❌ Runtime error: {str(e)}\n\n")
        except Exception as e:
            self.textbox.insert("end", f"❌ Unexpected error: {str(e)}\n\n")

    def change_continue_chat_event(self, new_appearance_mode):
        pass
    #     customtkinter.set_appearance_mode(new_appearance_mode)


    def change_scaling_event(self, new_scaling):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()