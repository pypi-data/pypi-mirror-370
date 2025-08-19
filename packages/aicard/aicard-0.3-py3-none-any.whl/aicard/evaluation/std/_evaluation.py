import os
import requests
import zipfile
from tqdm import tqdm
import json
import csv
import sys
import gdown
import sklearn
import numpy as np
from PIL import Image
import pandas as pd
from aicard.card import ModelCard
import kagglehub
import shutil
from typing import List, Any
import subprocess

try:
    import torch
    from torch.utils.data import Dataset
except ImportError:
    pass
try:
    import torchvision
except ImportError:
    pass
try:
    import torchtext

    try:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
    except ImportError:
        pass
except ImportError:
    pass


def check_and_download_data():
    try:  # try 7z
        process = subprocess.Popen(
            ["7z", "--help"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    except FileNotFoundError:  # No 7z case
        print(
            "Please install 7-Zip. Make sure you can run the 7z command in your terminal."
        )
        return False

    # Get the home directory and construct the path to the data
    home_dir = os.path.expanduser("~")
    data_dir = os.path.join(home_dir, ".transparency_service", "data", "std")

    # Check if the directory exists
    if not os.path.exists(data_dir):
        print(f"Directory {data_dir} does not exist. Downloading data...")
        # Call the download function (to be implemented later)
        os.makedirs(data_dir)

        # https://github.com/several27/FakeNewsCorpus/releases/tag/v1.0
        # https://github.com/several27/FakeNewsCorpus
        # https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/ULHLCB
        # https://ojs.aaai.org/index.php/ICWSM/article/view/3261/3129
        os.makedirs(f"{data_dir}/FakeNewsCorpus")
        root = "https://github.com/several27/FakeNewsCorpus/releases/download/v1.0/"
        files = [
            "news.csv.z01",
            "news.csv.z02",
            "news.csv.z03",
            "news.csv.z04",
            "news.csv.z05",
            "news.csv.z06",
            "news.csv.z07",
            "news.csv.z08",
            "news.csv.z09",
            "news.csv.zip",
        ]
        for f in files:
            downloaddata(f"{root}{f}", f"{data_dir}/FakeNewsCorpus/{f}")
            downloaddata(
                "https://github.com/several27/FakeNewsCorpus/archive/refs/tags/v1.0.zip",
                f"{data_dir}/FakeNewsCorpus/FakeNewsCorpus-1.0.zip",
            )
            downloaddata(
                "https://github.com/several27/FakeNewsCorpus/archive/refs/tags/v1.0.tar.gz",
                f"{data_dir}/FakeNewsCorpus/FakeNewsCorpus-1.0.tar.gz",
            )

        # https://d1wqtxts1xzle7.cloudfront.net/59076176/95-IJSES-V3N220190429-35946-1opr19p-libre.pdf?1556550748=&response-content-disposition=inline%3B+filename%3DFake_News_Prediction_A_Survey.pdf&Expires=1734957546&Signature=TuUKstHIQ1DAMQNA047SrarFZB03JCFpJ42br06cMi6USdOYrsWV7XINOBVIXZZpzGD4fwAJlXkosIddn08-t2y4pb6EZNy5XKVLnoORta6YhnjQn7QQwn8UoIHSAOqLUs18epa~xiLxmaXIcJnFCIbUpBNLgC-gFfDfLMMfN-3b6mxxQuSAvFIY~FLbGUC-UOIHhoDD5mV9q33I392u7PD67uLRF01u0W9e2bpdzPLpDNsAs3jeilpD1HIy7beJdqFOiU-v0ZjARnG70RpL~gfTeCqsT-HQnWrQSLWP5SYELUXiR73SKrcnfcRmEKuB-U4Mcr1AEVAH47tucgnYVw__&Key-Pair-Id=APKAJLOHF5GGSLRBV4ZA
        # https://www.kaggle.com/datasets/vimlendusharma/fake-or-real-news
        # https://www.kaggle.com/datasets/uppalaputarunkumar/fake-or-real-news
        # https://www.kaggle.com/datasets/raymonddelacroixyibo/fake-or-real-news
        os.makedirs(f"{data_dir}/fake-or-real-news")
        # Download
        path = kagglehub.dataset_download("uppalaputarunkumar/fake-or-real-news")
        # TODO: error handling
        # move
        source_path = f"{path}/fake_or_real_news.csv"
        destination_path = f"{data_dir}/fake-or-real-news/fake_or_real_news.csv"
        shutil.move(source_path, destination_path)
        os.rmdir(path)

        # https: // arxiv.org / abs / 1703.09398
        os.makedirs(f"{data_dir}/Horne2017")
        downloaddata(
            "https://github.com/rpitrust/fakenewsdata1/raw/refs/heads/master/Horne2017_FakeNewsData.zip",
            f"{data_dir}/Horne2017/Horne2017_FakeNewsData.zip",
        )
        # Extract
        zip_file_path = f"{data_dir}/Horne2017/Horne2017_FakeNewsData.zip"
        extract_to_path = f"{data_dir}/Horne2017"
        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            zip_ref.extractall(extract_to_path)
        print(f"Extracted to {extract_to_path}")

        # https://huggingface.co/datasets/ErfanMoosaviMonazzah/fake-news-detection-dataset-English/tree/main
        os.makedirs(f"{data_dir}/fake-news-detection-dataset-english")
        downloaddata(
            "https://huggingface.co/datasets/ErfanMoosaviMonazzah/fake-news-detection-dataset-English/resolve/main/test.tsv",
            f"{data_dir}/fake-news-detection-dataset-english/test.tsv",
        )
        downloaddata(
            "https://huggingface.co/datasets/ErfanMoosaviMonazzah/fake-news-detection-dataset-English/resolve/main/train.tsv",
            f"{data_dir}/fake-news-detection-dataset-english/train.tsv",
        )
        downloaddata(
            "https://huggingface.co/datasets/ErfanMoosaviMonazzah/fake-news-detection-dataset-English/resolve/main/validation.tsv",
            f"{data_dir}/fake-news-detection-dataset-english/validation.tsv",
        )
        downloaddata(
            "https://huggingface.co/datasets/ErfanMoosaviMonazzah/fake-news-detection-dataset-English/resolve/main/README.md",
            f"{data_dir}/fake-news-detection-dataset-english/README.md",
        )

        # https://github.com/tfs4/liar_dataset
        # https://arxiv.org/pdf/1705.00648
        os.makedirs(f"{data_dir}/liar")
        # downloaddata("https://www.cs.ucsb.edu/~william/data/liar_dataset.zip","liar_dataset.zip")
        downloaddata(
            "https://raw.githubusercontent.com/thiagorainmaker77/liar_dataset/master/test.tsv",
            f"{data_dir}/liar/test.tsv",
        )

        # https://github.com/rowanz/grover
        os.makedirs(f"{data_dir}/grover")
        datasplits = [
            "new_ctrl.csv",
            "new_gpt.csv",
            "new_gpt2.csv",
            "new_grover.csv",
            "new_xlm.csv",
            "new_xlnet.csv",
            "new_pplm.csv",
            "new_human.csv",
            "new_fair.csv",
        ]
        for ds in datasplits:
            downloaddata(
                f"https://raw.githubusercontent.com/AdaUchendu/Authorship-Attribution-for-Neural-Text-Generation/refs/heads/master/data/{ds}",
                f"{data_dir}/grover/{ds}",
            )

        # https://arxiv.org/abs/2008.00036
        os.makedirs(f"{data_dir}/tweepfake")
        downloaddata(
            "https://raw.githubusercontent.com/tizfa/tweepfake_deepfake_text_detection/refs/heads/master/data/splits/test.csv",
            f"{data_dir}/tweepfake/test.csv",
        )
        downloaddata(
            "https://raw.githubusercontent.com/tizfa/tweepfake_deepfake_text_detection/refs/heads/master/data/splits/train.csv",
            f"{data_dir}/tweepfake/train.csv",
        )
        downloaddata(
            "https://raw.githubusercontent.com/tizfa/tweepfake_deepfake_text_detection/refs/heads/master/data/splits/validation.csv",
            f"{data_dir}/tweepfake/validation.csv",
        )

        # https://github.com/openai/gpt-2-output-dataset/
        os.makedirs(f"{data_dir}/gpt-2-output-dataset")
        for ds in [
            "webtext",
            "small-117M",
            "small-117M-k40",
            "medium-345M",
            "medium-345M-k40",
            "large-762M",
            "large-762M-k40",
            "xl-1542M",
            "xl-1542M-k40",
        ]:
            for split in ["valid", "test"]:  # 'train',
                filename = ds + "." + split + ".jsonl"
                downloaddata(
                    f"https://openaipublic.azureedge.net/gpt-2/output-dataset/v1/{filename}",
                    f"{data_dir}/gpt-2-output-dataset/{filename}",
                )
        print("Now preparing data...")
        prepare_data()
        print("Cleaning up...")
        clean_up()
        print("All data ready")
    else:
        print(f"Directory {data_dir} already exists. No need to download.")


def downloaddata(url, output_path):
    response = requests.get(url, stream=True)

    # Check if ok
    if response.status_code == 200:
        # Get the total file size
        total_size = int(response.headers.get("Content-Length", 0))

        # progress bar
        with open(output_path, "wb") as file:
            if total_size > 0:
                progress_bar = tqdm(
                    total=total_size, unit="B", unit_scale=True, desc=output_path
                )
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
                    progress_bar.update(len(chunk))
                progress_bar.close()
            else:
                # without a progress bar
                file.write(response.content)
        print(f"File downloaded successfully {output_path}")
    else:
        print(f"Failed to download the file. Status code: {response.status_code}")


def prepare_data():
    home_dir = os.path.expanduser("~")
    data_root = os.path.join(home_dir, ".transparency_service", "data", "std")
    splits = [
        "FakeNewsCorpus",
        "Horne2017",
        "fake-news-detection-dataset-english",
        "fake-or-real-news",
        "gpt-2-output-dataset",
        "grover",
        "liar",
        "tweepfake",
    ]

    # FakeNewsCorpus
    dir = os.path.join(data_root, splits[0])
    # Unzip

    try:  # try 7z
        process = subprocess.Popen(
            ["7z", "x", os.path.join(dir, "news.csv.zip"), f"-o{dir}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        # Read and print the output from 7z
        for line in process.stdout:
            print(line.strip())
        # Wait for the process to finish
        process.wait()
        if process.returncode != 0:
            # If there was an error, print the stderr
            error_message = process.stderr.read()
            print(f"Extraction failed. Error: {error_message}")
        # split the data into fake and reliable
        csv.field_size_limit(sys.maxsize)
        input_file = os.path.expanduser(f"{dir}/news_cleaned_2018_02_13.csv")
        reliable_file = os.path.expanduser(
            f"{dir}/news_cleaned_2018_02_13.reliable.csv"
        )
        fake_file = os.path.expanduser(f"{dir}/news_cleaned_2018_02_13.fake.csv")
        with open(input_file, mode="r", encoding="utf-8") as infile, open(
            reliable_file, mode="w", encoding="utf-8", newline=""
        ) as reliable_out, open(
            fake_file, mode="w", encoding="utf-8", newline=""
        ) as fake_out:
            reader = csv.DictReader(infile)
            reliable_writer = csv.DictWriter(reliable_out, fieldnames=reader.fieldnames)
            fake_writer = csv.DictWriter(fake_out, fieldnames=reader.fieldnames)
            # Write headers to the output files
            reliable_writer.writeheader()
            fake_writer.writeheader()
            for row in reader:
                if not row or "type" not in row or row["type"] is None:
                    continue  # Skip invalid rows
                # Normalize the type field
                row_type = row["type"].strip().lower()
                if row_type == "reliable":
                    reliable_writer.writerow(row)
                elif row_type == "fake":
                    fake_writer.writerow(row)
    except FileNotFoundError:  # No 7z case
        print(f"Error extracting {os.path.join(dir, 'news.csv.zip')}")
        print("Error: 7-Zip is not installed or not found. Please install it.")

    # Horne2017
    dir = os.path.join(data_root, splits[1])
    # Extract
    with zipfile.ZipFile(
        os.path.join(dir, "Horne2017_FakeNewsData.zip"), "r"
    ) as zip_ref:
        zip_ref.extractall(dir)
    # Read data and conver to csv
    rootfolder = f"{dir}/Public Data"
    folders = {
        "Fake": [
            f"{rootfolder}/Buzzfeed Political News Dataset/Fake",
            f"{rootfolder}/Random Poltical News Dataset/Fake",
        ],
        "Fake_titles": [
            f"{rootfolder}/Buzzfeed Political News Dataset/Fake_titles",
            f"{rootfolder}/Random Poltical News Dataset/Fake_titles",
        ],
        "Real": [
            f"{rootfolder}/Buzzfeed Political News Dataset/Real",
            f"{rootfolder}/Random Poltical News Dataset/Real",
        ],
        "Real_titles": [
            f"{rootfolder}/Buzzfeed Political News Dataset/Real_titles",
            f"{rootfolder}/Random Poltical News Dataset/Real_titles",
        ],
        "Satire": [f"{rootfolder}/Random Poltical News Dataset/Satire"],
        "Satire_titles": [f"{rootfolder}/Random Poltical News Dataset/Satire_titles"],
    }
    # Initialize an empty list to store data
    data = []

    # Function to read files and populate data
    def read_files(text_folders, title_folders, label):
        for text_folder, title_folder in zip(text_folders, title_folders):
            if not os.path.exists(text_folder) or not os.path.exists(title_folder):
                print(f"Skipping missing folder: {text_folder} or {title_folder}")
                continue

            text_files = sorted(os.listdir(text_folder))
            title_files = sorted(os.listdir(title_folder))

            for text_file, title_file in zip(text_files, title_files):
                text_path = os.path.join(text_folder, text_file)
                title_path = os.path.join(title_folder, title_file)

                try:
                    with open(
                        text_path, "r", encoding="cp1252", errors="ignore"
                    ) as tf, open(
                        title_path, "r", encoding="cp1252", errors="ignore"
                    ) as tt:
                        text = tf.read().strip()
                        title = tt.read().strip()
                except Exception as e:
                    print(f"Error reading {text_file} or {title_file}: {e}")
                    continue

                data.append({"title": title, "text": text, "label": label})

    # Read Fake and Real data
    read_files(folders["Fake"], folders["Fake_titles"], "Fake")
    read_files(folders["Real"], folders["Real_titles"], "Real")
    read_files(folders["Satire"], folders["Satire_titles"], "Satire")

    # Create a DataFrame
    df = pd.DataFrame(data)
    # Save to CSV
    output_csv = f"{dir}/Horne2017.csv"
    df.to_csv(output_csv, index=False)

    # fake-news-detection-dataset-english
    dir = os.path.join(data_root, splits[2])
    tsv_file = f"{dir}/validation.tsv"
    csv_table = pd.read_table(tsv_file, sep="\t")
    csv_table.to_csv(f"{dir}/validation.csv", index=False)
    # fake-or-real-news
    # dir = os.path.join(data_root, splits[3])
    # nothing to do here
    # gpt-2-output-dataset
    dir = os.path.join(data_root, splits[4])

    def convert_to_csv(file):
        input_file = os.path.join(dir, f"{file}.jsonl")
        output_file = os.path.join(dir, f"{file}.csv")

        json_list = []
        with open(input_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():  # Skip empty lines
                    json_list.append(json.loads(line.strip()))

                    # Write csv
        with open(output_file, "w", newline="", encoding="utf-8") as data_file:
            csv_writer = csv.writer(data_file)

            # Write header row
            if json_list:
                header = json_list[0].keys()
                csv_writer.writerow(header)

                # Write data rows
                for data in json_list:
                    csv_writer.writerow(data.values())

    # Process each dataset
    for ds in [
        "webtext",
        "small-117M",
        "small-117M-k40",
        "medium-345M",
        "medium-345M-k40",
        "large-762M",
        "large-762M-k40",
        "xl-1542M",
        "xl-1542M-k40",
    ]:
        filename = ds + "." + "valid"
        convert_to_csv(filename)

    # grover
    dir = os.path.join(data_root, splits[5])
    # Load Dataset
    ctrl = pd.read_csv(dir + "/new_ctrl.csv")
    gpt = pd.read_csv(dir + "/new_gpt.csv")
    gpt2 = pd.read_csv(dir + "/new_gpt2.csv")
    grover = pd.read_csv(dir + "/new_grover.csv")
    xlm = pd.read_csv(dir + "/new_xlm.csv")
    xlnet = pd.read_csv(dir + "/new_xlnet.csv")
    pplm = pd.read_csv(dir + "/new_pplm.csv")
    human = pd.read_csv(dir + "/new_human.csv")
    em_lm = pd.read_csv(dir + "/new_fair.csv")

    ctrl = ctrl.drop(["Unnamed: 0"], axis=1)
    gpt = gpt.drop(["Unnamed: 0"], axis=1)
    gpt2 = gpt2.drop(["Unnamed: 0"], axis=1)
    grover = grover.drop(["Unnamed: 0"], axis=1)
    xlm = xlm.drop(["Unnamed: 0"], axis=1)
    xlnet = xlnet.drop(["Unnamed: 0"], axis=1)
    pplm = pplm.drop(["Unnamed: 0"], axis=1)
    fair = em_lm.drop(["Unnamed: 0"], axis=1)
    human = human.drop(["Unnamed: 0"], axis=1)

    generate = pd.concat([ctrl, gpt, gpt2, grover, xlm, xlnet, pplm, human, em_lm])
    Class = []
    for i in generate["label"]:
        if i == "human":
            Class.append(0)
        else:
            Class.append(1)
    hvm = pd.DataFrame({"text": generate["Generation"], "class": Class})
    hvm.to_csv(dir + "/hvm.csv")
    # liar
    dir = os.path.join(data_root, splits[6])
    tsv_file = f"{dir}/test.tsv"
    csv_table = pd.read_table(tsv_file, sep="\t")
    csv_table.to_csv(f"{dir}/test.csv", index=False)
    # tweepfake
    # dir = os.path.join(data_root, splits[7])
    # nothing to do here


def clean_up():
    home_dir = os.path.expanduser("~")
    data_root = os.path.join(home_dir, ".transparency_service", "data", "std")
    splits = [
        "FakeNewsCorpus",
        "Horne2017",
        "fake-news-detection-dataset-english",
        "fake-or-real-news",
        "gpt-2-output-dataset",
        "grover",
        "liar",
        "tweepfake",
    ]

    def rm(directory):
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            # remove all but .csv
            if os.path.isfile(file_path) and not filename.endswith(".csv"):
                os.remove(file_path)  # Remove the file

    # FakeNewsCorpus
    dir = os.path.join(data_root, splits[0])
    rm(dir)
    # Horne2017
    dir = os.path.join(data_root, splits[1])
    rm(dir)
    shutil.rmtree(f"{dir}/Public Data")
    # fake-news-detection-dataset-english
    dir = os.path.join(data_root, splits[2])
    rm(dir)
    # fake-or-real-news
    # dir = os.path.join(data_root, splits[3])
    # nothing to do here
    # gpt-2-output-dataset
    dir = os.path.join(data_root, splits[4])
    rm(dir)
    # grover
    # dir = os.path.join(data_root, splits[5])
    # nothing to do here
    # liar
    dir = os.path.join(data_root, splits[6])
    rm(dir)
    # tweepfake
    # dir = os.path.join(data_root, splits[7])
    # nothing to do here


def get_data(set: str, tags: List[str]) -> pd.DataFrame:
    # 0 = True, 1 = Fake
    home_dir = os.path.expanduser("~")
    data_root = os.path.join(home_dir, ".transparency_service", "data", "std")
    if set == "FakeNewsCorpus":
        # Paths to the CSV files
        fake_news_path = f"{data_root}/{set}/news_cleaned_2018_02_13.fake.csv"
        reliable_news_path = f"{data_root}/{set}/news_cleaned_2018_02_13.reliable.csv"
        # Load the datasets
        fake_news = pd.read_csv(fake_news_path)
        fake_news["type"] = 1
        reliable_news = pd.read_csv(reliable_news_path)
        reliable_news["type"] = 0
        # There are too many data just pick 5000 for each
        fake_news = fake_news.sample(n=5000, random_state=42)
        reliable_news = reliable_news.sample(n=5000, random_state=42)
        out_pd = pd.DataFrame()
        for t in tags:
            if t == "title":
                out_pd["title"] = pd.concat(
                    [fake_news["title"], reliable_news["title"]], ignore_index=True
                )
            elif t == "content":
                out_pd["content"] = pd.concat(
                    [fake_news["content"], reliable_news["content"]], ignore_index=True
                )
            elif t == "label":
                out_pd["label"] = pd.concat(
                    [fake_news["type"], reliable_news["type"]], ignore_index=True
                )
            else:
                print(f"A tag with name {t} is not implemented")
        return out_pd
    elif set == "Horne2017":
        data_path = f"{data_root}/{set}/Horne2017.csv"
        data_pd = pd.read_csv(data_path, quoting=csv.QUOTE_ALL)
        data_pd["label"] = data_pd["label"].replace({"Fake": 1, "Real": 0, "Satire": 0})
        out_pd = pd.DataFrame()
        for t in tags:
            if t == "title":
                out_pd["title"] = data_pd["title"]
            elif t == "content":
                out_pd["content"] = data_pd["text"]
            elif t == "label":
                out_pd["label"] = data_pd["label"]
            else:
                print(f"A tag with name {t} is not implemented")
        return out_pd
    elif set == "fake-news-detection-dataset-english":
        data_path = f"{data_root}/{set}/validation.csv"
        data_pd = pd.read_csv(data_path)
        data_pd["label"] = data_pd["label"].replace({0: 2})
        data_pd["label"] = data_pd["label"].replace({1: 0})
        data_pd["label"] = data_pd["label"].replace({2: 1})
        out_pd = pd.DataFrame()
        for t in tags:
            if t == "title":
                out_pd["title"] = data_pd["title"]
            elif t == "content":
                out_pd["content"] = data_pd["text"]
            elif t == "label":
                out_pd["label"] = data_pd["label"]
            else:
                print(f"A tag with name {t} is not implemented")
        return out_pd
    elif set == "fake-or-real-news":
        data_path = f"{data_root}/{set}/fake_or_real_news.csv"
        data_pd = pd.read_csv(data_path)
        data_pd["label"] = data_pd["label"].replace({"FAKE": 1, "REAL": 0})
        out_pd = pd.DataFrame()
        for t in tags:
            if t == "title":
                out_pd["title"] = data_pd["title"]
            elif t == "content":
                out_pd["content"] = data_pd["text"]
            elif t == "label":
                out_pd["label"] = data_pd["label"]
            else:
                print(f"A tag with name {t} is not implemented")
        return out_pd
    elif set == "gpt-2-output-dataset":  # This doesn't have labels
        large_762M = f"{data_root}/{set}/large-762M.valid.csv"
        large_762M_k40 = f"{data_root}/{set}/large-762M-k40.valid.csv"
        medium_345M = f"{data_root}/{set}/medium-345M.valid.csv"
        medium_345M_k40 = f"{data_root}/{set}/medium-345M-k40.valid.csv"
        small_117M = f"{data_root}/{set}/small-117M.valid.csv"
        small_117M_k40 = f"{data_root}/{set}/small-117M-k40.valid.csv"
        webtext = f"{data_root}/{set}/webtext.valid.csv"
        xl_1542M = f"{data_root}/{set}/xl-1542M.valid.csv"
        xl_1542M_k40 = f"{data_root}/{set}/xl-1542M-k40.valid.csv"
        # Load the datasets
        webtext_pd = pd.read_csv(webtext)
        webtext_pd["ended"] = webtext_pd["ended"].replace({"True": 0, "False": 1})
        out_pd = pd.DataFrame()
        for t in tags:
            if t == "title":
                out_pd["title"] = [" "] * len(webtext_pd)
            elif t == "content":
                out_pd["content"] = webtext_pd["text"]
            elif t == "label":
                pass
                # out_pd['label'] = webtext_pd['ended']
            else:
                print(f"A tag with name {t} is not implemented")
        return out_pd
    elif set == "grover":
        data_path = f"{data_root}/{set}/hvm.csv"
        hvm_pd = pd.read_csv(data_path)
        out_pd = pd.DataFrame()
        for t in tags:
            if t == "title":
                out_pd["title"] = [" "] * len(hvm_pd)
            elif t == "content":
                out_pd["content"] = hvm_pd["text"]
            elif t == "label":
                out_pd["label"] = hvm_pd["class"]
            else:
                print(f"A tag with name {t} is not implemented")
        return out_pd
    elif set == "liar":  # TODO: to specific. Maybe this is not useful for me
        pass
    elif set == "tweepfake":
        data_path = f"{data_root}/{set}/validation.csv"
        validation_pd = pd.read_csv(data_path, delimiter=";", on_bad_lines="skip")
        validation_pd["account.type"] = validation_pd["account.type"].replace(
            {"human": 0, "bot": 1}
        )
        out_pd = pd.DataFrame()
        for t in tags:
            if t == "title":
                out_pd["title"] = [" "] * len(validation_pd)
            elif t == "content":
                out_pd["content"] = validation_pd["text"]
            elif t == "label":
                out_pd["label"] = validation_pd["account.type"]
            else:
                print(f"A tag with name {t} is not implemented")
        return out_pd
    else:
        print(f"{set} dataset not in data storage")
        return pd.DataFrame()


class EvaluationDataset(Dataset):
    def __init__(self, data_path, tags, tokenizer):
        # Load the CSV file into a pandas DataFrame
        self.data = get_data(
            data_path, tags
        )  # Assumes CSV has 'title' and 'content' columns
        self.tokenizer = tokenizer
        self.tags = tags

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        row_data = self.data.iloc[idx][self.tags]

        # tokenizer
        tokenized_data = self.tokenizer(row_data)

        return [tokenized_data, row_data["label"]]


def run_evaluation(model, tokenizer, device, tuple_id, batch_size, num_workers):
    data_sets = [
        "FakeNewsCorpus",
        "Horne2017",
        "fake-news-detection-dataset-english",
        "fake-or-real-news",
        "grover",
        "tweepfake",
    ]
    accs = []
    aps = []
    lbs = []
    """ THis one doesn't have labels
    print('gpt-2-output-dataset')
    """
    """ This is too specific might not be useful
    print('liar')
    """
    test = [
        (
            g,
            torch.utils.data.DataLoader(
                EvaluationDataset(g, ["title", "content", "label"], tokenizer),
                batch_size=batch_size,
                shuffle=False,
                num_workers=num_workers,
                pin_memory=True,
                drop_last=False,
            ),
        )
        for g in data_sets
    ]

    model.to(device)
    for g, loader in test:
        model.eval()
        y_true = []
        y_score = []
        with torch.no_grad():
            for data in loader:
                text, labels = data
                text, labels = text.to(device), labels.to(device)
                outputs = model(text) if tuple_id is None else model(text)[tuple_id]
                y_true.extend(labels.cpu().numpy().tolist())
                y_score.extend(torch.sigmoid(outputs).cpu().numpy().tolist())
        test_acc = sklearn.metrics.accuracy_score(
            np.array(y_true), np.array(y_score) > 0.5
        )
        test_ap = sklearn.metrics.average_precision_score(y_true, y_score)
        accs.append(test_acc)
        aps.append(test_ap)
        lbs.append(g)
        print(f"{g}:  {test_acc * 100} {test_ap * 100}")
    out = pd.DataFrame({"label": lbs, "acc": accs, "ap": aps})
    out["acc"] = out["acc"] * 100
    out["ap"] = out["ap"] * 100
    return out


def write_md(model_card, eval_pd):
    if model_card is None:
        return
    meanacc = round(eval_pd["acc"].mean(), 1)
    meanap = round(eval_pd["ap"].mean(), 1)
    model_card.json["Quantitative Analysis"][
        "Text"
    ] = f"""Those plots were generated by the transparency service module.
            The mean accuracy is {meanacc} and the mean average precision is {meanap}."""
    model_card.json["Quantitative Analysis"]["SID ACC plot"] = model_card.bar_plot(
        pdata=eval_pd, y="acc", x="label", title="ACC", yaxis_title="Accuracy (%)"
    ).replace("<div>", '<div class="plot-inline-div">')
    model_card.json["Quantitative Analysis"]["SID AP plot"] = model_card.bar_plot(
        pdata=eval_pd,
        y="ap",
        x="label",
        title="AP",
        yaxis_title="Average Precision (%)",
    ).replace("<div>", '<div class="plot-inline-div">')
    model_card.json["Eval Set"][
        "Text"
    ] = """
    <li> <a href="https://github.com/several27/FakeNewsCorpus" target="_blank"> FakeNewsCorpus </a></li>
    <li> <a href="https://arxiv.org/abs/1703.09398" target="_blank"> Horne2017 </a></li>
    <li> <a href="https://huggingface.co/datasets/ErfanMoosaviMonazzah/fake-news-detection-dataset-English/tree/main" target="_blank"> fake-news-detection-dataset-english </a></li>
    <li> <a href="https://www.kaggle.com/datasets/vimlendusharma/fake-or-real-news="_blank"> fake-or-real-news </a></li>
    <li> <a href="https://github.com/rowanz/grover" target="_blank"> grover </a></li>
    <li> <a href="https://arxiv.org/abs/2008.00036" target="_blank"> tweepfake </a></li>
    """


def evaluate(
    model,
    tokenizer,
    device=None,
    tuple_id=None,
    batch_size=64,
    num_workers=12,
    model_card: ModelCard = None,
):
    check_and_download_data()
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    eval_pd = run_evaluation(
        model=model,
        tokenizer=tokenizer,
        device=device,
        tuple_id=tuple_id,
        batch_size=batch_size,
        num_workers=num_workers,
    )

    write_md(model_card, eval_pd)
