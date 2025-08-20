from datetime import datetime, timezone
import os
import shutil
from typing import List, Optional
from pathlib import Path

from flask import Flask, render_template, request, jsonify, send_from_directory

from classto.utils import generate_suffix, sanitize_label, get_next_image_from_folder, log_classification_to_csv, get_next_url


def create_flask_app(
    classes: List[str], 
    delete_button: bool, 
    shuffle: bool, 
    suffix: bool, 
    log_to_csv: bool = False,
    image_folder: Optional[str] = None, 
    urls: Optional[List[str]] = None,
    log_path: Optional[str] = None,
    log_file_name: Optional[str] = None
) -> Flask:
    """
    Create and configure the Flask app for Classto.

    This app provides a web interface for manually classifying images 
    into user-defined categories. Images can come from a local folder or a list of URLs.
    Local images are moved into per-label folders, optionally renamed with a suffix, and optionally logged to a CSV file.
    For URL-based classification, only the classification is logged to a CSV file (no file moving).

    Args:
        classes (List[str]): List of classification labels (e.g. ["Model", "Product Only"]).
        delete_button (bool): Whether to show a delete button in the UI for skipping or removing images.
        shuffle (bool): Whether to present images in random order.
        suffix (bool): Whether to append a random suffix to filenames when saving (applies to local images only).
        log_to_csv (bool, optional): Whether to log classifications to a CSV file (always enabled for URL mode). Defaults to False.
        image_folder (Optional[str]): Path to a folder containing local images (used in local mode).
        urls (Optional[List[str]]): List of image URLs to classify (used in URL mode).
        log_path (Optional[str]): Custom path to the CSV log file. If not provided, 
                               defaults to "<classified_folder>/labels.csv" in folder mode, 
                               or "./labels.csv" in URL mode.
        log_file_name (Optional[str]): File name for the CSV log, if None then set to default with a timestamped name.

    Returns:
        Flask: A configured Flask application ready to run.
    """
    
    package_dir = os.path.dirname(__file__)

    app = Flask(
        __name__,
        static_folder=os.path.join(package_dir, "static"),
        static_url_path="/static",
        template_folder=os.path.join(package_dir, "templates")
    )

    is_url_mode = urls is not None and len(urls) > 0
    if not is_url_mode and not image_folder:
        raise ValueError("Missing input source: Please provide either 'image_folder' or a list of 'urls'.")

    DELETE_LABELS = {"delete", "delete image", "🗑️ delete image"}
    
    if image_folder:
        CLASSIFIED_FOLDER = os.path.join(image_folder, "..", "classified")
        if not os.path.exists(CLASSIFIED_FOLDER):
            os.makedirs(CLASSIFIED_FOLDER)      
    
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%SZ")
    base_dir = Path(log_path) if log_path else Path(os.getcwd() if is_url_mode else CLASSIFIED_FOLDER)
    
    if log_file_name:
        name = Path(log_file_name).with_suffix('.csv').name
    else:
        name = f"labels-{run_id}.csv"
    
    LOG_FILE = str(base_dir / name)

    # Ensure log directory exists
    log_dir = os.path.dirname(LOG_FILE)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    

    @app.route('/')
    def index():
        if is_url_mode:
            image_url = get_next_url(image_urls=urls, shuffle=shuffle)
            return render_template(
                'index.html',
                image_filename=image_url,  # can be a full URL
                classes=classes,
                delete_button=delete_button,
                image_folder=None
            )
        else:        
            image_filename = get_next_image_from_folder(image_folder=image_folder, shuffle=shuffle)
            return render_template(
                'index.html',
                image_filename=image_filename,
                classes=classes,
                delete_button=delete_button,
                image_folder=image_folder
            )

    @app.route('/images/<filename>')
    def serve_image(filename):
        return send_from_directory(image_folder, filename)

    @app.route('/classify', methods=['POST'])
    def classify():
        data = request.json
        label = data.get("label")
        filename = data.get("image")
        
        if is_url_mode:
            # URL Mode - Log to CSV only
            if label.lower() in DELETE_LABELS:      
                label = "DELETED"
                        
            log_classification_to_csv(
                log_file=LOG_FILE, 
                original_filename=filename, 
                final_filename=None,
                label=label
            )
            
            if filename in urls:
                urls.remove(filename)
            
            next_image = get_next_url(image_urls=urls, shuffle=shuffle)
            return jsonify({
                "next_image": next_image,
                "is_url": is_url_mode
            })
        
        # If local folder and not URLs
        src = os.path.join(image_folder, filename)

        # If it's a delete action, remove the image and skip the rest
        if label.lower() in DELETE_LABELS and os.path.exists(src):
            os.remove(src)
            print(f"Deleted image: {filename}")
            
            if log_to_csv:
                log_classification_to_csv(
                    log_file=LOG_FILE, 
                    original_filename=filename, 
                    final_filename=None,
                    label="DELETED"
                )
            
            next_image = get_next_image_from_folder(image_folder=image_folder, shuffle=shuffle)
            return jsonify({
                "next_image": next_image,
                "is_url": is_url_mode
            })

        # Sanitize the label
        safe_label = sanitize_label(label)

        # Create label-specific folder on-demand
        dest_folder = os.path.join(CLASSIFIED_FOLDER, safe_label)
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)

        # Determine destination filename
        if not suffix:
            dst = os.path.join(dest_folder, filename)
            final_filename = None
        else:
            name, ext = os.path.splitext(filename)
            random_suffix = generate_suffix()
            final_filename = f"{name}__{random_suffix}{ext}"
            dst = os.path.join(dest_folder, final_filename)

            while os.path.exists(dst):
                random_suffix = generate_suffix()
                final_filename = f"{name}__{random_suffix}{ext}"
                dst = os.path.join(dest_folder, final_filename)

        # Move image
        if os.path.exists(src):
            shutil.move(src, dst)

            # Optional: Log to CSV
            if log_to_csv:
                log_classification_to_csv(
                    log_file=LOG_FILE, 
                    original_filename=filename, 
                    final_filename=final_filename,
                    label=label
                )

        next_image = get_next_image_from_folder(image_folder=image_folder, shuffle=shuffle)
        return jsonify({
            "next_image": next_image,
            "is_url": is_url_mode
        })


    return app
