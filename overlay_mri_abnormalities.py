# overlay_mri_abnormalities.py
import os
from pathlib import Path
import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage import morphology, measure, exposure
from tqdm import tqdm

def ensure_dir(d):
    Path(d).mkdir(parents=True, exist_ok=True)

def load_image(path):
    # load in color (BGR) then convert to RGB
    img_bgr = cv2.imdecode(np.fromfile(str(path), dtype=np.uint8), cv2.IMREAD_UNCHANGED)
    if img_bgr is None:
        img_bgr = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if img_bgr is None:
        raise ValueError(f"Can't read image: {path}")
    if img_bgr.ndim == 2:
        # grayscale -> convert to 3-channel
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_GRAY2RGB)
    elif img_bgr.shape[2] == 4:
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGRA2RGB)
    else:
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    return img_rgb

def overlay_mask_on_image(img_rgb, mask, color=(255, 255, 0), alpha=0.45):
    """
    img_rgb: HxWx3 uint8 (0-255)
    mask: HxW bool or 0/1
    color: RGB tuple for overlay (default yellow)
    alpha: overlay transparency
    """
    overlay = img_rgb.copy().astype(np.float32)
    color_arr = np.array(color, dtype=np.float32).reshape(1,1,3)
    # only apply overlay where mask==True
    overlay[mask] = (1-alpha)*overlay[mask] + alpha*color_arr
    return overlay.astype(np.uint8)

def heuristic_mask_from_image(img_rgb):
    """
    Simple heuristic to find bright/contrasting regions:
    - convert to grayscale
    - apply CLAHE (contrast limited adaptive histogram equalization)
    - gaussian blur
    - Otsu threshold
    - morphological opening + remove small objects
    - keep largest connected components (optional)
    """
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    # CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    gray_eq = clahe.apply(gray)
    # blur to remove tiny noise
    blur = cv2.GaussianBlur(gray_eq, (5,5), 0)
    # Otsu threshold
    _, th = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    th = th.astype(bool)
    # morphological cleaning
    th = morphology.remove_small_objects(th, min_size=200)     # tweak min_size
    th = morphology.remove_small_holes(th, area_threshold=200)
    # keep relatively large connected components (e.g., top 2)
    labels = measure.label(th)
    if labels.max() == 0:
        return th
    props = measure.regionprops(labels)
    # sort by area descending
    props_sorted = sorted(props, key=lambda p: p.area, reverse=True)
    keep_mask = np.zeros_like(th, dtype=bool)
    # keep top N components (1 or 2)
    N = 2
    for p in props_sorted[:N]:
        keep_mask[labels == p.label] = True
    return keep_mask

def process_directory(images_dir, masks_dir=None, output_root="output"):
    images_dir = Path(images_dir)
    masks_dir = Path(masks_dir) if masks_dir else None
    out_overlays = Path(output_root) / "overlays"
    out_masks = Path(output_root) / "masks"
    ensure_dir(out_overlays)
    ensure_dir(out_masks)

    exts = {'.png', '.jpg', '.jpeg', '.tif', '.tiff', '.bmp'}
    files = [p for p in images_dir.rglob("*") if p.suffix.lower() in exts and p.is_file()]
    print(f"[INFO] Found {len(files)} images in {images_dir}")

    saved = []
    for p in tqdm(sorted(files)):
        try:
            img = load_image(p)
            # if mask exists with same name in masks_dir
            mask_path = None
            if masks_dir:
                candidate = masks_dir / p.name
                if candidate.exists():
                    mask_path = candidate

            if mask_path:
                # load mask (single-channel). Any nonzero becomes True
                m_raw = cv2.imdecode(np.fromfile(str(mask_path), dtype=np.uint8), cv2.IMREAD_UNCHANGED)
                if m_raw is None:
                    m_raw = cv2.imread(str(mask_path), cv2.IMREAD_UNCHANGED)
                if m_raw is None:
                    raise ValueError(f"Can't read mask: {mask_path}")
                if m_raw.ndim == 3:
                    # take first channel or convert to grayscale
                    m_gray = cv2.cvtColor(m_raw, cv2.COLOR_BGR2GRAY)
                else:
                    m_gray = m_raw
                mask = (m_gray > 0)
            else:
                # create heuristic mask
                mask = heuristic_mask_from_image(img)

            overlay = overlay_mask_on_image(img, mask, color=(255,255,0), alpha=0.5)

            # save overlay and mask
            out_img_path = out_overlays / p.name
            out_mask_path = out_masks / p.name
            # save with cv2 (convert RGB->BGR)
            cv2.imencode('.png', cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR))[1].tofile(str(out_img_path))
            # save mask as uint8 image
            cv2.imencode('.png', (mask.astype(np.uint8)*255))[1].tofile(str(out_mask_path))

            saved.append((p, out_img_path, out_mask_path, mask.sum()))
        except Exception as e:
            print(f"[WARN] Skipped {p} due to: {e}")

    print(f"[INFO] Saved overlays to: {out_overlays}")
    print(f"[INFO] Saved masks to: {out_masks}")
    return saved

def show_samples(saved_list, n=4):
    # show first n overlays and masks
    n = min(n, len(saved_list))
    plt.figure(figsize=(6*n, 6))
    for i, rec in enumerate(saved_list[:n]):
        orig, overlay_path, mask_path, area = rec
        ov = load_image(overlay_path)
        mask = cv2.imdecode(np.fromfile(str(mask_path), dtype=np.uint8), cv2.IMREAD_UNCHANGED)
        if mask is None:
            mask = cv2.imread(str(mask_path), cv2.IMREAD_UNCHANGED)
        # show overlay
        plt.subplot(2, n, i+1)
        plt.imshow(ov)
        plt.title(f"Overlay: {orig.name}\nMask area: {area}")
        plt.axis('off')
        # show mask
        plt.subplot(2, n, n + i+1)
        if mask is None:
            plt.text(0.5,0.5,"No mask", ha='center')
        else:
            if mask.ndim==3:
                mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
            plt.imshow(mask, cmap='viridis')
        plt.axis('off')
    plt.show()

# ======== Example usage ========
if __name__ == "__main__":
    # point these to your folders
    images_folder = "dataset_fixed"
     # your folder with MRI images (recurses subfolders)
    masks_folder = None                  # set to "masks" if you have mask files with same filenames
    # e.g., masks_folder = "dataset_fixed_masks"
    results = process_directory(images_folder, masks_folder, output_root="output")
    show_samples(results, n=4)
