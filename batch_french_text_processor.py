import os
import re
import glob
import argparse
from openai import OpenAI

# Replace with your actual API key
client = OpenAI()
def parse_sentences_from_file(file_path):
    """
    Reads a text file and parses it into complete sentences.
    Splits on punctuation, handling periods, exclamation points, and question marks.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()

    # Split text into sentences using regex to account for punctuation.
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    # Return only non-empty sentences.
    return [sentence for sentence in sentences if sentence]

def send_request(sentences):
    """
    Sends a structured request to OpenAI's API for French learning tasks.
    """
    # Prepare the text of the sentences
    sentences_text = "\n".join(f"{i+1}. {sentence}" for i, sentence in enumerate(sentences))

    # Build messages for chat completion
    messages = [
        {
            "role": "system",
            "content": (
                "You are a French learning assistant. "
                "First, translate the entire sentence to English. "
                "Then translate every word to English, giving the genre of nouns and tense of verbs. "
                "Finally, explain the grammar in the sentence."
            )
        },
        {"role": "user", "content": sentences_text}
    ]

    # Note: Replace "gpt-4o-mini" with the actual model you want to use
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    return response.choices[0].message.content

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Process all .txt files in a given directory, sending sentences to the OpenAI API."
    )
    parser.add_argument(
        "input_dir",
        help="Path to the directory containing .txt files to process."
    )
    args = parser.parse_args()

    # Read input directory from command line
    input_dir = args.input_dir
    # The output directory will be <dir_name>-learning
    output_dir = input_dir + "-grammar-notes"

    # Check if input directory exists
    if not os.path.isdir(input_dir):
        print(f"Error: The directory '{input_dir}' does not exist.")
        return

    # Create the output directory if it does not exist
    os.makedirs(output_dir, exist_ok=True)

    # Get all .txt files in the input directory
    text_files = glob.glob(os.path.join(input_dir, "*.txt"))

    # Set how many sentences to process per chunk
    chunk_size = 3

    # Process each text file in the input directory
    for text_file in text_files:
        # Extract just the file name without the directory
        base_name = os.path.basename(text_file)
        # Remove original extension, add .md
        output_file_name = os.path.splitext(base_name)[0] + ".md"
        output_file_path = os.path.join(output_dir, output_file_name)

        # Parse sentences
        sentences = parse_sentences_from_file(text_file)

        # Clear or create the output file
        with open(output_file_path, "w", encoding="utf-8") as out_file:
            # Go through sentences in chunks of 'chunk_size'
            for i in range(0, len(sentences), chunk_size):
                chunk = sentences[i:i + chunk_size]  # e.g., 3 sentences at a time
                
                # Optional print to console
                print(f"Processing file: {base_name}, sentences {i+1}–{i + len(chunk)}")

                # Send chunk to the OpenAI API
                response = send_request(chunk)
                # Write the response to the output file
                out_file.write(response + "\n\n")

        print(f"Finished processing: {base_name} -> {output_file_path}")

if __name__ == "__main__":
    main()
