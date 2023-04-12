import bip39
import sr25519
import os

msg = b"register"

def generate_seed():
    # Generate Seed Phrase
    entropy = os.urandom(16)
    mnemonic = bip39.encode_bytes(entropy)
    print(f"seed_phrase is: {mnemonic}")
    return bip39.phrase_to_seed(mnemonic)[32:]

def generate_pair(seed):
    # Get pub/prv key given seed
    (public, private) = sr25519.pair_from_seed(seed)
    print(f"public is: {public}")
    print(f"private is: {private}")
    return (public, private)

# add signing function

# add verifying

def main():
    (public, private) = generate_pair(generate_seed())

if __name__ == '__main__':
    main()