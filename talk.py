talk_model_name="dicta-il/dictalm-7b-instruct"
import torch
from transformers import AutoTokenizer,AutoModelForCausalLM

# Check if CUDA (GPU support) is available
if torch.cuda.is_available():
    # Check which GPU is currently selected (if multiple are available)
    device = torch.cuda.current_device()
    print(f"Current GPU Device: {torch.cuda.get_device_name(device)}")
else:
    print("No GPU available, using CPU for computation.")


model=AutoModelForCausalLM.from_pretrained(talk_model_name,trust_remote_code=True).to(device)
tokenizer=AutoTokenizer.from_pretrained(talk_model_name,trust_remote_code=True)


def generate_prompt(text, question):
    """
    Generates a prompt for the model to encourage direct quoting from the text in response to a question.

    Args:
    - text (str): The Hebrew text to be summarized.
    - question (str): The user's specific question.

    Returns:
    - str: The generated prompt for the model.
    """

    prompt = f"""
    טקסט: {text}
    שאלה: {question}
    הנחיות: נא לצטט באופן ישיר מהטקסט כחלק מהתשובה. התשובה צריכה להתייחס במדויק לפרטים המופיעים בטקסט.
    תשובה:
    """

    return prompt

@torch.no_grad
def generate_summary(text, question):
    """
    Generates a summary of a given Hebrew text from the Supreme Court decisions database,
    focusing on aspects relevant to the user's question.

    Args:
    - model (transformers.PreTrainedModel): The loaded Hugging Face model.
    - tokenizer (transformers.PreTrainedTokenizer): The loaded tokenizer.
    - text (str): The Hebrew text to summarize.
    - question (str): The user's specific question to focus the summary on.

    Returns:
    - str: The generated summary.
    """

    # Combine the text and the question to provide context to the model
    prompt = generate_prompt(text,question)#f"טקסט: {text}\nשאלה: {question}\nתקציר:"

    # Encode the combined prompt
    input_ids = tokenizer.encode(prompt, return_tensors='pt').to(model.device)

    # Generate the response
    output = model.generate(input_ids, max_new_tokens=150, num_return_sequences=1, no_repeat_ngram_size=2)

    # Decode the generated text
    summary = tokenizer.decode(output[0][input_ids.shape[-1]:].cpu(), skip_special_tokens=True)

    return summary
