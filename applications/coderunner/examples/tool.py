# Do not delete this, this is part of a demo and is preloaded into the blob storage.
import argparse
import sys

def get_joke(age):
    if age < 0:
        raise ValueError("Age cannot be negative. Please provide a valid age.")
    
    if age < 5:
        # Pre-schoolers (0-4)
        return "Why did the banana go to the doctor? Because it wasn't peeling well!"
    elif age < 11:
        # Elementary school (5-10)
        return "What do you call a fake noodle? A Impasta!"
    elif age < 14:
        # Middle schoolers (11-13)
        return "Why do programmers prefer dark mode? Because light attracts bugs."
    elif age < 18:
        # High schoolers (14-17) - Edgy/Sarcastic
        return "My life is like a broken pencil. Pointless."
    elif age < 30:
        # Young Adults (18-29) - Work/Life balance
        return "I told my boss I needed a raise because three other companies were after me. He asked, 'Who?' I said, 'The electric company, the water company, and the phone company.'"
    elif age < 65:
        # Adults (30-64) - Aging/Tech
        return "I'm at that age where my back goes out more than I do."
    else:
        # Seniors (65+)
        return "I don't have gray hair; I have wisdom highlights!"

def main():
    parser = argparse.ArgumentParser(description="A tool that tells jokes suitable for specific age ranges.")
    parser.add_argument("--age", type=int, required=True, help="Age of the audience (must be a non-negative integer)")
    args = parser.parse_args()
    joke = get_joke(args.age)
    print(joke)

if __name__ == "__main__":
    main()
