import argparse
import glob
import json
import re



parser = argparse.ArgumentParser(
    description="Convert RST parse file into GPT-3 input")
parser.add_argument("-i",
                    "--input_dir",
                    type=str,
                    help="path to input directory")
parser.add_argument("-o",
                    "--output_dir",
                    type=str,
                    help="path to output file")


def multiple_replace(re_dict, text):
  for pattern, sub in re_dict.items():
    text = re.sub(pattern, sub, text)

  if "_!" in text:
    actual_text = re.sub(
        "[\s]+",
        " ",
        text.split("_!")[1].replace("(", "-LRB-").replace(")", "-RRB-"),
    ).strip()
    text = re.sub("\(text._!.*_!\)", "FAKE_TEXT", text)
    return actual_text, text.replace("FAKE_TEXT", actual_text)
  else:
    return "", text


re_dict = {
    "\(span[0-9\s]+\)\s?": "",
    "\(rel2par.[A-Za-z\-]+\)": "",
    "\(leaf.[0-9]+\) ": "",
    "Root ": "",
    "Nucleus ": "",
    "Satellite ": "",
}


def process_text(filename):
  actual_texts = []
  processed_lines = []
  with open(filename, "r") as f:
    for line in f:
      actual_text, new_line = multiple_replace(re_dict, line)
      if actual_text:
        actual_texts.append(actual_text)
      processed_lines.append(new_line)

  return (" " + " ".join(actual_texts) + " ->", " "+re.sub("[\s]+", " ",
                                         "".join(processed_lines)).strip()+"\n")


def get_paths(directory):
  train_dev_files = glob.glob(f'{directory}/TRAINING/wsj_*.out.dis')
  train_files = train_dev_files[:300]
  dev_files = train_dev_files[300:]
  test_files = glob.glob(f'{directory}/TESTING/wsj_*.out.dis')
  return {"train": train_files,
          "dev": dev_files,
          "test": test_files}




def main():

  args = parser.parse_args()

  for subset, filenames in get_paths(args.input_dir).items():
    examples = []
    for filename in filenames:
      original, parsed = process_text(filename)
      examples.append({"prompt": original, "completion": parsed})
    with open(f"{args.output_dir}/{subset}.jsonl", "w") as f:
      f.write("\n".join([json.dumps(e) for e in examples]))


if __name__ == "__main__":
  main()
