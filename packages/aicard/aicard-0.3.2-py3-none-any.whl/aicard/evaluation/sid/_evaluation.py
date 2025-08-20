import os
import requests
import zipfile
from tqdm import tqdm
import gdown
import sklearn
import numpy as np
from PIL import Image
import pandas as pd
from aicard.card import ModelCard

try:
    import torch
    from torch.utils.data import Dataset
except ImportError:
    pass
try:
    import torchvision
except ImportError:
    pass


def check_and_download_data():
    # Get the home directory and construct the path to the data
    home_dir = os.path.expanduser("~")
    data_dir = os.path.join(home_dir, ".transparency_service", "data", "sid")

    # Check if the directory exists
    if not os.path.exists(data_dir):
        print(f"Directory {data_dir} does not exist. Downloading data...")
        # Call the download function (to be implemented later)
        os.makedirs(data_dir)
        url = "https://huggingface.co/datasets/sywang/CNNDetection/resolve/main/CNN_synth_testset.zip"
        data_dir = os.path.expanduser("~/.transparency_service/data/sid")
        download_and_extract(url, data_dir)
        url = (
            "https://drive.google.com/uc?id=1FXlGIRh_Ud3cScMgSVDbEWmPDmjcrm1t&authuser"
        )
        download_and_extract(url, data_dir)
    else:
        print(f"Directory {data_dir} already exists. No need to download.")


def download_file(url, download_path):
    # Check if the URL is from Google Drive
    if "drive.google.com" in url:
        gdown.download(url, download_path, quiet=False)
    else:
        # Standard URL download (for non-Google Drive)
        response = requests.get(url, stream=True)
        # Get the total file size from the response headers (for progress bar)
        total_size = int(response.headers.get("content-length", 0))
        # Initialize tqdm progress bar for download
        with tqdm(
            total=total_size, unit="B", unit_scale=True, desc="Downloading"
        ) as bar:
            with open(download_path, "wb") as file:
                # Download the file in chunks
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)
                        bar.update(len(chunk))  # Update progress bar with chunk size

    print(f"Download complete: {download_path}")


def download_and_extract(url, data_dir):
    # Step 1: Download the file
    print(f"Downloading {url}...")
    download_path = os.path.join(data_dir, "testset.zip")

    # Download file using the updated function
    download_file(url, download_path)

    # Step 2: Unzip the file
    if download_path.endswith(".zip"):
        print(f"Extracting {download_path}...")
        with zipfile.ZipFile(download_path, "r") as zip_ref:
            # Get the total size of all files inside the ZIP archive
            total_size = sum([file.file_size for file in zip_ref.infolist()])

            # Initialize tqdm progress bar for extraction
            with tqdm(
                total=total_size, unit="B", unit_scale=True, desc="Extracting"
            ) as bar:
                for file_info in zip_ref.infolist():
                    # Extract each file one by one
                    zip_ref.extract(file_info, path=data_dir)
                    bar.update(file_info.file_size)  # Update the progress bar

        print(f"Extraction complete: {data_dir}")

        # Step 3: Remove the zip file
        os.remove(download_path)
        print(f"Removed zip file: {download_path}")
    else:
        print("The downloaded file is not a zip file.")


def get_test_path():
    return [
        "progan",
        "stylegan",
        "stylegan2",
        "biggan",
        "cyclegan",
        "stargan",
        "gaugan",
        "deepfake",
        "seeingdark",
        "san",
        "crn",
        "imle",
        "diffusion_datasets/guided",
        "diffusion_datasets/ldm_200",
        "diffusion_datasets/ldm_200_cfg",
        "diffusion_datasets/ldm_100",
        "diffusion_datasets/glide_100_27",
        "diffusion_datasets/glide_50_27",
        "diffusion_datasets/glide_100_10",
        "diffusion_datasets/dalle",
    ]


class EvaluationDataset(Dataset):
    def __init__(self, generator, transforms=None, perturb=None):
        home_dir = os.path.expanduser("~")
        data_dir = os.path.join(home_dir, ".transparency_service", "data", "sid")
        if generator in ["cyclegan", "progan", "stylegan", "stylegan2"]:

            self.real = [
                (f"{data_dir}/{generator}/{y}/0_real/{x}", 0)
                for y in os.listdir(f"{data_dir}/{generator}")
                for x in os.listdir(f"{data_dir}/{generator}/{y}/0_real")
            ]
            self.fake = [
                (f"{data_dir}/{generator}/{y}/1_fake/{x}", 1)
                for y in os.listdir(f"{data_dir}/{generator}")
                for x in os.listdir(f"{data_dir}/{generator}/{y}/1_fake")
            ]
        elif "diffusion_datasets/guided" in generator:
            self.real = [
                (f"{data_dir}/diffusion_datasets/imagenet/0_real/{x}", 0)
                for x in os.listdir(f"{data_dir}/diffusion_datasets/imagenet/0_real")
            ]
            self.fake = [
                (f"{data_dir}/{generator}/1_fake/{x}", 1)
                for x in os.listdir(f"{data_dir}/{generator}/1_fake")
            ]
        elif (
            "diffusion_datasets/ldm" in generator
            or "diffusion_datasets/glide" in generator
            or "diffusion_datasets/dalle" in generator
        ):
            self.real = [
                (f"{data_dir}/diffusion_datasets/laion/0_real/{x}", 0)
                for x in os.listdir(f"{data_dir}/diffusion_datasets/laion/0_real")
            ]
            self.fake = [
                (f"{data_dir}/{generator}/1_fake/{x}", 1)
                for x in os.listdir(f"{data_dir}/{generator}/1_fake")
            ]
        elif any(
            [
                x in generator
                for x in [
                    "biggan",
                    "stargan",
                    "gaugan",
                    "deepfake",
                    "seeingdark",
                    "san",
                    "crn",
                    "imle",
                ]
            ]
        ):
            self.real = [
                (f"{data_dir}/{generator}/0_real/{x}", 0)
                for x in os.listdir(f"{data_dir}/{generator}/0_real")
            ]
            self.fake = [
                (f"{data_dir}/{generator}/1_fake/{x}", 1)
                for x in os.listdir(f"{data_dir}/{generator}/1_fake")
            ]
        elif any(
            [
                x in generator
                for x in [
                    "dalle2",
                    "dalle3",
                    "stable-diffusion-1-3",
                    "stable-diffusion-1-4",
                    "stable-diffusion-2",
                    "stable-diffusion-xl",
                    "glide",
                    "firefly",
                    "midjourney-v5",
                ]
            ]
        ):
            self.real = [(f"data/RAISEpng/{x}", 0) for x in os.listdir("data/RAISEpng")]
            self.fake = [
                (f"data/synthbuster/{generator}/{x}", 1)
                for x in os.listdir(f"data/synthbuster/{generator}")
                if all([y not in x for y in [".txt", ".py"]])
            ]

        self.images = self.real + self.fake

        self.transforms = transforms
        self.perturb = perturb

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        image_path, target = self.images[idx]
        image = Image.open(image_path).convert("RGB")
        if self.transforms is not None and self.perturb is None:
            image = self.transforms(image)
        # elif self.transforms is not None and self.perturb is not None:
        #    if random.random() < 0.5:
        #        image = perturbation(self.perturb)(image)
        #    else:
        #        image = self.transforms(image)
        return [image, target]


def evaluate(
    model,
    transformer,
    device=None,
    tuple_id=None,
    batch_size=64,
    num_workers=12,
    model_card: ModelCard = None,
):
    check_and_download_data()
    test_path = get_test_path()
    accs = []
    aps = []
    lbs = []
    if (
        "torch" in globals() and "torchvision" in globals()
    ):  # Check if torch is already imported
        if isinstance(model, torch.nn.Module):
            if device is None:
                device = "cuda" if torch.cuda.is_available() else "cpu"
            test = [
                (
                    g,
                    torch.utils.data.DataLoader(
                        EvaluationDataset(g, transforms=transformer),
                        batch_size=batch_size,
                        shuffle=False,
                        num_workers=num_workers,
                        pin_memory=True,
                        drop_last=False,
                    ),
                )
                for g in test_path
            ]
            image_counts = {"label": [], "count": []}
            for g in test_path:
                dataset = EvaluationDataset(g)
                image_counts["label"].append(g.replace("diffusion_datasets/", ""))
                image_counts["count"].append(dataset.images.__len__())
            print(image_counts)
            model.to(device)
            for g, loader in test:
                model.eval()
                y_true = []
                y_score = []
                with torch.no_grad():
                    for data in loader:
                        images, labels = data
                        images, labels = images.to(device), labels.to(device)
                        outputs = (
                            model(images)
                            if tuple_id is None
                            else model(images)[tuple_id]
                        )
                        y_true.extend(labels.cpu().numpy().tolist())
                        y_score.extend(torch.sigmoid(outputs).cpu().numpy().tolist())
                test_acc = sklearn.metrics.accuracy_score(
                    np.array(y_true), np.array(y_score) > 0.5
                )
                test_ap = sklearn.metrics.average_precision_score(y_true, y_score)
                accs.append(test_acc)
                aps.append(test_ap)
                lbs.append(g)
                print(f"{g}:  {test_acc*100} {test_ap*100}")
    out = pd.DataFrame({"label": lbs, "acc": accs, "ap": aps})
    # out = todel # TODEL
    out["acc"] = out["acc"] * 100
    out["ap"] = out["ap"] * 100
    out["label"] = out["label"].str.replace("diffusion_datasets/", "", regex=False)
    meanacc = round(out["acc"].mean(), 1)
    meanap = round(out["ap"].mean(), 1)
    if model_card is not None:
        model_card.text["Quantitative Analysis"][
            "Text"
        ] = f"""Those plots were generated by the transparency service module.
        The mean accuracy is {meanacc} and the mean average precision is {meanap}."""

        model_card.text["Quantitative Analysis"]["SID ACC plot"] = model_card.bar_plot(
            pdata=out, y="acc", x="label", title="ACC", yaxis_title="Accuracy (%)"
        ).replace("<div>", '<div class="plot-inline-div">')
        model_card.text["Quantitative Analysis"]["SID AP plot"] = model_card.bar_plot(
            pdata=out,
            y="ap",
            x="label",
            title="AP",
            yaxis_title="Average Precision (%)",
        ).replace("<div>", '<div class="plot-inline-div">')
        model_card.text["Eval Set"][
            "Text"
        ] = """
        The evaluation set can be found in: 
        <a href="https://huggingface.co/datasets/sywang/CNNDetection/resolve/main/CNN_synth_testset.zip" target="_blank">
    CNN_synth_testset</a> (<a href="https://arxiv.org/abs/1912.11035" target="_blank"> Sheng-Yu Wang et al. </a>) and <a href="https://drive.google.com/file/d/1FXlGIRh_Ud3cScMgSVDbEWmPDmjcrm1t/view" target="_blank">
    diffusion_datasets</a> (<a href="https://arxiv.org/abs/2302.10174" target="_blank">Utkarsh Ojha et al.</a>). They contain
    20 datasets including generated and real images from: 
    <ul>
        <li> <a href="https://arxiv.org/abs/1710.10196" target="_blank"> ProGAN </a></li>
        <li> <a href="doi.org/10.1109/CVPR.2019.00453" target="_blank"> StyleGAN </a></li>
        <li> <a href="https://arxiv.org/abs/1912.04958" target="_blank"> StyleGAN2 </a></li>
        <li> <a href="https://arxiv.org/abs/1809.11096" target="_blank"> BigGAN </a></li>
        <li> <a href="doi.org/10.1109/ICCV.2017.244" target="_blank"> CycleGAN </a></li>
        <li> <a href="https://arxiv.org/abs/1711.09020" target="_blank"> StarGAN </a></li>
        <li> <a href="https://arxiv.org/abs/1903.07291" target="_blank"> GauGAN </a></li>
        <li> <a href="https://arxiv.org/abs/1901.08971" target="_blank"> DeepFake </a></li>
        <li> <a href="https://arxiv.org/abs/1805.01934v1" target="_blank"> SITD </a></li>
        <li> <a href="doi.org/10.1109/CVPR.2019.01132" target="_blank"> SAN </a></li>
        <li> <a href="https://arxiv.org/abs/1707.09405" target="_blank"> CRN </a></li>
        <li> <a href="https://arxiv.org/abs/1811.12373" target="_blank"> IMLE </a></li>
        <li> <a href="https://arxiv.org/abs/2105.05233" target="_blank"> Guided </a></li>
        <li> <a href="https://arxiv.org/abs/2112.10752" target="_blank"> LDM (3 variants) </a></li>
        <li> <a href="https://proceedings.mlr.press/v162/nichol22a.html" target="_blank"> Glide (3 variants) </a></li>
        <li> <a href="https://arxiv.org/abs/2102.12092" target="_blank"> DALL-E </a></li>
    </ul>
"""
        """
        model_card.json['Eval Set']['eval set plot'] = model_card.bar_plot(
            pdata=pd.DataFrame(image_counts),
            y='count',
            x='label',
            title='Number of images for each data set',
            yaxis_title='Number of Images'
        ).replace('<div>', '<div class="plot-inline-div">')
"""
    return out
