"""Download required NLTK data with retry logic."""
import nltk
import time
import ssl
import os

# Try to fix SSL issues on some Windows machines
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

resources = ['punkt_tab', 'stopwords', 'wordnet', 'averaged_perceptron_tagger_eng']

for resource in resources:
    for attempt in range(3):
        try:
            print(f"Downloading {resource} (attempt {attempt + 1})...")
            result = nltk.download(resource, quiet=False)
            if result:
                print(f"  OK - {resource} downloaded successfully")
                break
            else:
                print(f"  OK - {resource} already exists")
                break
        except Exception as e:
            print(f"  FAIL - Attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                time.sleep(3)
    else:
        print(f"  FAIL - Could not download {resource} after 3 attempts")

# Verify
print("")
print("Verification:")
for resource in resources:
    try:
        if "punkt" in resource:
            nltk.data.find(f"tokenizers/{resource}")
        elif resource in ["stopwords", "wordnet"]:
            nltk.data.find(f"corpora/{resource}")
        else:
            nltk.data.find(f"taggers/{resource}")
        print(f"  OK - {resource} found")
    except LookupError:
        print(f"  MISSING - {resource} NOT found")
