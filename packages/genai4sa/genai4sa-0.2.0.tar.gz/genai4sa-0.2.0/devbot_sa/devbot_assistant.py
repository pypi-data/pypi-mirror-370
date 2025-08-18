"""devbot_functions.py
A functional (non‑class) rewrite of the Devbot architecture‑assistant helper.

Prerequisites (defined/imported elsewhere):
• SYSTEM_PROMPT               – a short constant string
• HUMAN_DETAILS, HUMAN_SDD,
  HUMAN_ZERO, HUMAN_IN_CONTEXT,
  HUMAN_COT                    – PromptTemplate instances
• pdfGenerator.generate_pdf()  – function to create a PDF from a text file
• load_api_key_from_file()     – helper that reads keys from disk
• ChatOpenAI, ChatGoogleGenerativeAI, ChatGroq – LangChain chat wrappers

All heavy PromptTemplate objects and third‑party helpers are **assumed to be
available in the caller’s scope**; this file focuses purely on orchestration.
"""
from __future__ import annotations

import os, platform, subprocess
from pathlib import Path
from typing import Optional, Dict
from . import pdfGenerator
from .prompts import SYSTEM_PROMPT
from .prompts import software_architecture_assistant_prompt_1, software_architecture_assistant_prompt_2
from .prompts import software_architecture_zero_shot_prompt, software_architecture_in_context_prompt, software_architecture_chain_of_thought_prompt
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# ---------- Constants ----------------------------------------------------

# Output text file that stores the assistant’s last reply, enabling
# conversation continuation in a later call.
_SCRIPT_DIR: Path = Path(__file__).resolve().parent
_OUTPUT_FILE: Path = _SCRIPT_DIR / "output"

# Map docType → (human PromptTemplate, default PDF filename)
_DOC_CONFIG: Dict[str, tuple[PromptTemplate, str]] = {
    "Details":      (software_architecture_assistant_prompt_1,      "Software Architecture Details.pdf"),
    "SDD":          (software_architecture_assistant_prompt_2,          "Software Design Document.pdf"),
    "Zero-Shot":    (software_architecture_zero_shot_prompt,        "Software Architecture Zero Shot.pdf"),
    "In-Context":   (software_architecture_in_context_prompt,  "Software Architecture In Context.pdf"),
    "Chain-of-Thought": (software_architecture_chain_of_thought_prompt,     "Software Architecture Chain of Thought.pdf"),
}
# --- Load API KEY ---- 
def load_api_key_from_file(filename):
    
    #Reads the API key from a file and returns it.
    
    script_dir = os.path.dirname(os.path.realpath(__file__))
    api_file = os.path.join(script_dir, filename)
    if not os.path.exists(api_file):
        raise FileNotFoundError(f"API key file '{filename}' not found. Enter you API key")
    with open(api_file, "r") as f:
        api_key = f.read().strip()
    return api_key
# ---------- LLM selection ------------------------------------------------
def select_llm(model: str):
    """Return the correct LangChain chat‑model instance for *model*."""
    if model in {"gpt-4o", "gpt-4o-mini", "o3", "o1"}:
        api_key = load_api_key_from_file("openai_api_key")
        return ChatOpenAI(api_key=api_key, model=model, temperature=1)

    if model in {"gemini-2.0-flash", "gemini-1.5-pro"}:
        api_key = load_api_key_from_file("google_api_key")
        return ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key,
            temperature=1,
            top_p=0.8,
        )

    # Fallback: Groq Llama / Mixtral / etc.

    api_key = load_api_key_from_file("groq_api_key")
    return ChatGroq(api_key=api_key, model_name=model, temperature=1, top_p=0.8)

# ---------- Message construction ----------------------------------------

def build_messages(doc_type: str, previous_ai_reply: Optional[str] = None,
    refinement: Optional[str] = None):

    #Return a list[BaseMessage] for the current LLM call.
    if doc_type not in _DOC_CONFIG:
        raise ValueError(f"Unknown docType '{doc_type}'. Expected one of: {list(_DOC_CONFIG)}")

    human_prompt_template, _ = _DOC_CONFIG[doc_type]

    messages = [SystemMessage(content=SYSTEM_PROMPT)]

    # If we’re continuing a chat, give the assistant its own last reply.
    if previous_ai_reply:
        messages.append(AIMessage(content=previous_ai_reply))

    # Determine the current human message.
    if refinement is not None:
        messages.append(HumanMessage(content=refinement))
    else:
        if description is None:
            raise ValueError("'description' must be provided for the first turn")
        human_content = human_prompt_template.format(description=description)
        messages.append(HumanMessage(content=human_content))

    return messages

# ---------- File helpers -------------------------------------------------

def write_output(text: str) -> None:
    #Persist *text* to the shared output file for future chat turns.
    _OUTPUT_FILE.write_text(text, encoding="utf-8")


def read_previous_output() -> Optional[str]:
    """Return the last assistant reply if the file exists."""
    if _OUTPUT_FILE.exists():
        return _OUTPUT_FILE.read_text(encoding="utf-8").strip()
    return None


# ---------- PDF helpers --------------------------------------------------

def _generate_and_open_pdf(pdf_name: str) -> None:
    #Generate a PDF from `_OUTPUT_FILE` and open it with the OS viewer.

    pdfGenerator.generate_pdf(str(_OUTPUT_FILE), str(_SCRIPT_DIR), pdf_name)

    original_cwd = os.getcwd()
    #os.chdir(_SCRIPT_DIR)
    try:
        if platform.system() == "Windows":
            os.startfile(pdf_name)  # type: ignore[attr-defined]
        else:
            subprocess.run(["open", pdf_name], check=False)
    finally:
        os.chdir(original_cwd)

# ---------- Public API ---------------------------------------------------

def query_llm(
    description: str,
    model: str,
    doc_type: str,
    continue_chat: bool = False,
    refinement: Optional[str] = None
) -> str:
    """High‑level helper that performs a single LLM interaction and returns the reply.

    Parameters
    ----------
    description : str
        Full system description (required on the *first* turn).
    model : str
        Backend model name (e.g. "gpt-4o", "gemini-1.5-pro").
    doc_type : str
        One of the keys of `_DOC_CONFIG` ("SDD", "Details", …).
    continue_chat : bool, default False
        If True, includes the assistant’s previous reply (from the `output` file)
        in the context. If the file is absent, no previous reply is added.
    refinement : str | None
        If provided, this text becomes the current user instruction instead of
        the long description template.

    Returns
    -------
    str
        The raw text reply from the model (also written to `output`).
    """
    if continue_chat and not _OUTPUT_FILE.exists():
        # graceful degradation: no previous answer means fall back to first turn
        continue_chat = False
    # 1. Select provider
    llm = select_llm(model)

    if not continue_chat:
        # ----------------------------------------
        # FIRST TURN – use LLMChain & PromptTemplate
        # ----------------------------------------
        prompt_tpl, _ = _DOC_CONFIG[doc_type]
        if prompt_tpl is None:
            raise RuntimeError(f"PromptTemplate for '{doc_type}' not found in globals().")

        chain = LLMChain(llm=llm, prompt=prompt_tpl)
        reply_text: str = chain.invoke({"description": description})["text"]

    else:
        # ----------------------------------------
        # CONTINUATION – refine previous answer
        # ----------------------------------------
        previous_text = _OUTPUT_FILE.read_text(encoding="utf-8")
        # if not refinement:
        #     raise ValueError("'refinement' message required when continue_chat=True")

        messages = build_messages(doc_type, previous_text, description)
        reply_text = llm.invoke(messages).content  # type: ignore[attr-defined]    


    # 4. Persist + generate PDF + open
    write_output(reply_text)

    _, pdf_name = _DOC_CONFIG[doc_type]
    _generate_and_open_pdf(pdf_name)

    return reply_text

# ------------------------------------------------------------------------
# Convenience alias for older codebases
run_devbot = query_llm
