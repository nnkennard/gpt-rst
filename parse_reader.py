import glob
import json
import re

def multiple_replace(re_dict, text):
  for pattern, sub in re_dict.items():
    text = re.sub(pattern, sub, text)

  if '_!'  in text:
    actual_text = re.sub("[\s]+", " ", text.split("_!")[1].replace("(",
    "-LRB-").replace(")", "-RRB-")).strip()
    text = re.sub("\(text._!.*_!\)", "FAKE_TEXT", text)
    return actual_text, text.replace("FAKE_TEXT", actual_text)
  else:
    return "", text

re_dict = {
   "\(span[0-9\s]+\)\s?" : "",
   "Root " : "",
   "\(rel2par.[A-Za-z\-]+\)" : "",
   "\(leaf.[0-9]+\) " : "",
    "Nucleus " : "",
    "Satellite " : "",
}

def process_text(filename):
  actual_texts = []
  processed_lines = []
  with open(filename, 'r') as f:
    for line in f:
      actual_text, new_line = multiple_replace(re_dict, line)
      if actual_text:
        actual_texts.append(actual_text)
      processed_lines.append(new_line)

  return (" ".join(actual_texts),
    re.sub("[\s]+", " ", "".join(processed_lines)))



def main():

  examples = []
  for filename in glob.glob("data/RSTtrees-WSJ-main-1.0/TRAINING/wsj_*.out.dis"):
    original, parsed = process_text(filename)
    examples.append({
    "prompt": original,
    "completion": parsed})

  with open("gpt3_input.jsonl", 'w') as f:
    f.write("\n".join([json.dumps(e) for e in examples]))


if __name__ == "__main__":
  main()

