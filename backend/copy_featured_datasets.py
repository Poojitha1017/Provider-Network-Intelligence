import os
import shutil

src_dir = r"C:\Users\HP\Downloads\UC05_PREPROCESSED_FEATURED_DATA\UC05_PREPROCESSED_FEATURED"
fe_src = r"C:\Users\HP\Downloads\UC05_NETWORK_ADEQUACY_2000_EACH\UC05_FEATURE_ENGINEERED_DATASET.csv"
dst_dir = r"C:\Users\HP\Downloads\frontend\backend\data"

os.makedirs(dst_dir, exist_ok=True)

print("Copying 2,000-row preprocessed and feature-engineered datasets to backend/data/...")

for fname in os.listdir(src_dir):
    if fname.endswith(".csv"):
        src_path = os.path.join(src_dir, fname)
        dst_path = os.path.join(dst_dir, fname)
        shutil.copyfile(src_path, dst_path)
        print(f"  Copied: {fname} -> {dst_path}")

if os.path.exists(fe_src):
    dst_fe_path = os.path.join(dst_dir, "UC05_FEATURE_ENGINEERED_DATASET.csv")
    shutil.copyfile(fe_src, dst_fe_path)
    print(f"  Copied: UC05_FEATURE_ENGINEERED_DATASET.csv -> {dst_fe_path}")

print("Dataset copy complete!")
