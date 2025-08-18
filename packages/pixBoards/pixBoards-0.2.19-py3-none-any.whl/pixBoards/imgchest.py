import hashlib
import logging
import os

import requests
import yaml
from dotenv import load_dotenv

from pixBoards.arguments import args


def load_config(yml_path="config.yml"):
    with open(yml_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


config = load_config()
tableName = config["tableName"]

logger = logging.getLogger(__name__)

# Load the .env file
load_dotenv()

IMG_CHEST_API_KEY = os.getenv("IMG_CHEST_API_KEY")
HEADERS = {"Authorization": f"Bearer {IMG_CHEST_API_KEY}"}


# def connect_db():
#     return psycopg2.connect(
#         dbname="boards",
#         user="postgres",
#         password="password",
#         host="localhost"
#     )


def create_table_if_not_exists(cursor):
    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {tableName} (
            hash TEXT PRIMARY KEY,
            link TEXT NOT NULL,
            filename TEXT  
        )
    """
    )


# def compute_hash(image_path):
#     with open(image_path, "rb") as f:
#         return hashlib.md5(f.read()).hexdigest()


def compute_hash(filepath, chunk_size=8192):
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def load_link_by_hash(cursor, hash_val):
    cursor.execute(f"SELECT link FROM {tableName} WHERE hash = %s", (hash_val,))
    row = cursor.fetchone()
    return row[0] if row else None


def save_link(cursor, hash_val, link):
    cursor.execute(
        f"""
        INSERT INTO {tableName} (hash, link)
        VALUES (%s, %s)
        ON CONFLICT (hash) DO NOTHING
    """,
        (hash_val, link),
    )


# Based loosely on keikazuki's approach
def upload_image(image_path):
    with open(image_path, "rb") as f:
        files = {"images[]": (os.path.basename(image_path), f, "image/jpeg")}
        data = {"title": os.path.basename(image_path)}
        resp = requests.post(
            "https://api.imgchest.com/v1/post",
            headers=HEADERS,
            files=files,
            data=data,
        )

    resp.raise_for_status()
    post_id = resp.json()["data"]["id"]

    # Now get the image info
    info = requests.get(f"https://api.imgchest.com/v1/post/{post_id}", headers=HEADERS)
    info.raise_for_status()

    image_list = info.json()["data"]["images"]
    if not image_list:
        raise Exception("No images returned in response")

    return image_list[0]["link"]


from concurrent.futures import ThreadPoolExecutor, as_completed

# def process_images(image_paths, conn, max_workers=4):
#     """
#     Optimized image processing:
#     - Uses DB caching by filename and hash
#     - Skips hashing if --useSaved
#     - Parallelizes uploads
#     """
#     link_hash_map = {}
#     results = []

#     cur = conn.cursor()
#     create_table_if_not_exists(cur)

#     # First, check all filenames in one batch
#     filenames = [os.path.basename(p) for p in image_paths]
#     cur.execute(f"SELECT filename, link, hash FROM {tableName} WHERE filename = ANY(%s)", (filenames,))
#     filename_cache = {row[0]: (row[1], row[2]) for row in cur.fetchall()}

#     # Prepare images that need upload/hash check
#     to_upload = []
#     for img_path in image_paths:
#         fname = os.path.basename(img_path)
#         if fname in filename_cache:
#             link, hash_val = filename_cache[fname]
#             results.append(link)
#             if hash_val:
#                 link_hash_map[hash_val] = link
#             continue
#         to_upload.append(img_path)

#     def process_single(img_path):
#         fname = os.path.basename(img_path)
#         hash_val = None
#         cached_link = None

#         if not args.useSaved:
#             hash_val = compute_hash(img_path)
#             cached_link = load_link_by_hash(cur, hash_val)
#             if cached_link:
#                 # backfill filename
#                 cur.execute(
#                     f"UPDATE {tableName} SET filename = %s WHERE hash = %s AND (filename IS NULL OR filename = '')",
#                     (fname, hash_val),
#                 )
#                 link_hash_map[hash_val] = cached_link
#                 return cached_link

#         # Upload if no cached link
#         try:
#             hash_val = compute_hash(img_path)
#             direct_link = upload_image(img_path)
#             cur.execute(
#                 f"INSERT INTO {tableName} (hash, link, filename) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
#                 (hash_val, direct_link, fname),
#             )
#             if hash_val:
#                 link_hash_map[hash_val] = direct_link
#             return direct_link
#         except Exception as e:
#             logger.warning(f"Upload failed for {img_path}: {e}")
#             return None

#     # Use ThreadPoolExecutor to parallelize uploads (I/O bound)
#     with ThreadPoolExecutor(max_workers=max_workers) as executor:
#         future_to_path = {executor.submit(process_single, p): p for p in to_upload}
#         for future in as_completed(future_to_path):
#             res = future.result()
#             if res:
#                 results.append(res)

#     conn.commit()
#     cur.close()
#     return results, link_hash_map

import os
import re

from pathlib import Path

def get_link_from_sidecar(image_path):
    # Ensure image_path is a Path object
    image_path = Path(image_path)
    sidecar_file = image_path.with_suffix(image_path.suffix + ".txt")  # e.g., .jpg → .jpg.txt
    if sidecar_file.exists():
        try:
            with sidecar_file.open("r", encoding="utf-8") as f:
                first_line = f.readline().strip()
                if first_line:
                    match = re.match(r"url:\s*(\S+)", first_line, re.IGNORECASE)
                    if match:
                        return match.group(1)
                    return first_line
        except Exception as e:
            logger.warning(f"Failed to read sidecar file {sidecar_file}: {e}")
    return None



def process_images(image_paths, conn):
    import os

    link_hash_map = {}

    try:
        cur = conn.cursor()
        create_table_if_not_exists(cur)

        results = []
        # print(image_paths)
        for image_path in image_paths:
            filename = os.path.basename(image_path)
            # if not args.useSaved:
            # Check for sidecar text file first
            sidecar_link = None
            if args.sidecar:
                sidecar_link = get_link_from_sidecar(image_path)
            # print(image_path)
            # print(sidecar_link)
            
            if sidecar_link:
                logger.debug(f"🔗 Using link from sidecar file: {image_path} → {sidecar_link}")
                results.append(sidecar_link)
                cached_link = sidecar_link
                continue
            else:
                # First try filename
                cur.execute(
                    f"SELECT link FROM {tableName} WHERE filename = %s",
                    (filename,),
                )
                result = cur.fetchone()
                if result:
                    cached_link = result[0]
                    logger.debug(f" Cached by filename: {image_path} → {cached_link}")
                    results.append(cached_link)
                    # Hash is not needed, so we skip storing hash->link map
                    continue

                # Not found by filename, compute hash and try again
                hash_val = compute_hash(image_path)
                cached_link = load_link_by_hash(cur, hash_val)
            if not cached_link:
                hash_val = compute_hash(image_path)
                cached_link = load_link_by_hash(cur, hash_val)

            if cached_link:
                logger.debug(f" Cached by hash: {image_path} → {cached_link}")
                results.append(cached_link)
                link_hash_map[hash_val] = cached_link

                # Backfill filename
                cur.execute(
                    f"UPDATE {tableName} SET filename = %s WHERE hash = %s AND (filename IS NULL OR filename = '')",
                    (filename, hash_val),
                )
                continue
            if not args.useSaved:
                try:
                    direct_link = upload_image(image_path)
                    logger.debug(f" Uploaded {image_path} → {direct_link}")

                    # Save with both hash and filename
                    cur.execute(
                        f"INSERT INTO {tableName} (hash, link, filename) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                        (hash_val, direct_link, filename),
                    )
                    logger.debug(f" Saved to DB: {hash_val[:10]} → {direct_link}")
                    results.append(direct_link)
                    link_hash_map[hash_val] = direct_link

                except Exception as e:
                    logger.warning(f" Upload error for {image_path}: {e}")

        conn.commit()
        dir = os.path.dirname(image_paths[0])
        logger.info(f"Commit successful for {dir}")
        cur.close()
        return results, link_hash_map

    except Exception as e:
        logger.info(f" Critical DB error: {e}")
        return [], {}


# this one checks for hash.

# def process_images(image_paths, conn):
#     link_hash_map = {}
#     uploaded_links = []
#     try:
#         cur = conn.cursor()
#         create_table_if_not_exists(cur)

#         results = []

#         for image_path in image_paths:
#             hash_val = compute_hash(image_path)
#             cached_link = load_link_by_hash(cur, hash_val)

#             if cached_link:
#                 logger.debug(f"🔁 Cached: {image_path} → {cached_link}")
#                 results.append(cached_link)
#                 link_hash_map[hash_val] = cached_link
#                 continue

#             try:
#                 direct_link = upload_image(image_path)
#                 logger.debug(f" Uploaded {image_path} → {direct_link}")
#                 save_link(cur, hash_val, direct_link)
#                 logger.debug(f" Saved to DB: {hash_val[:10]} → {direct_link}")
#                 results.append(direct_link)
#                 link_hash_map[hash_val] = direct_link
#                 # conn.commit() # if images regularly fail to commit, or you want to quite in between uploading
#             except Exception as e:
#                 logger.warning(f" Upload error for {image_path}: {e}")

#         conn.commit()
#         dir = os.path.dirname(image_paths[0])
#         logger.info(f"Commit successful. for {dir}")
#         cur.close()
#         return results, link_hash_map

#     except Exception as e:
#         logger.info(f" Critical DB error: {e}")
#         return [], {}
