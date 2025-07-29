import email
from email.message import EmailMessage
from email.generator import BytesGenerator
import io
from PIL import Image, ImageOps
import piexif
import base64
from datetime import datetime

#Description: Resize images in email attachments to a maximum of 1920x1080 pixels while preserving aspect ratio.
def resize_image(data):
    img = Image.open(io.BytesIO(data))
    
    # If the image has an alpha channel (transparency), it will be converted to RGB
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        alpha = img.convert("RGBA").split()[-1]
        bg = Image.new("RGBA", img.size, (255, 255, 255, 255))  # bílé pozadí
        bg.paste(img, mask=alpha)
        img = bg.convert("RGB")
    else:
        img = img.convert("RGB")

    # Load original EXIF data
    try:
        exif_raw = img.info.get('exif')
        exif_dict = piexif.load(exif_raw) if exif_raw else {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
    except Exception as e:
        print(f"⚠️ EXIF load failed: {e}")
        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}

    # Physically rotate image according to EXIF orientation
    img = ImageOps.exif_transpose(img)
    # Remove orientation tag from EXIF (0x0112) as image is now physically oriented
    if '0th' in exif_dict and piexif.ImageIFD.Orientation in exif_dict['0th']:
        exif_dict['0th'].pop(piexif.ImageIFD.Orientation, None)

    # Resize image, max 1920x1080 keeping aspect ratio
    max_size = (1920, 1080)
    img.thumbnail(max_size, Image.LANCZOS)

    out = io.BytesIO()
    exif_bytes = piexif.dump(exif_dict)
    img.save(out, format="JPEG", quality=90, optimize=True, exif=exif_bytes)
    return out.getvalue()

def process_parts(msg, depth=0):
    
    indent = "  " * depth
    if msg.is_multipart():
        print(f"{indent}📦 Multipart type: {msg.get_content_type()}")
        new_parts = []
        for part in msg.get_payload():
            new_part = process_parts(part, depth + 1)
            new_parts.append(new_part)
        msg.set_payload(new_parts)
        return msg
    else:
        ctype = msg.get_content_type()
        disp = msg.get("Content-Disposition", None)
        filename = msg.get_filename()
        print(f"{indent}🔍 Part: {ctype} | Disposition: {disp} | Filename: {filename}")
        if ctype.startswith("image/") and filename:
            is_inline = (disp is None or disp.startswith("inline"))
            content_id = msg.get("Content-ID")

            if (disp and disp.startswith("attachment")) or (is_inline and content_id):
                print(f"{indent}🛠️ Processing image: {filename}")
                original_data = msg.get_payload(decode=True)
                resized_data = resize_image(original_data)
                print(f"{indent}> Original size: {len(original_data)//1024} KB")
                img = Image.open(io.BytesIO(resized_data))
                print(f"{indent}> Resized to: {img.width}x{img.height}")
                print(f"{indent}> New size: {len(resized_data)//1024} KB")
                print(f"{indent}🧪 Policy: {getattr(msg, 'policy', '❌ MISSING')}")


                from email import policy
                new_part = EmailMessage(policy=msg.policy if hasattr(msg, 'policy') else policy.default)


                new_part.set_type(ctype)

                # Disposition
                if disp:
                    new_part.add_header("Content-Disposition", disp.split(";")[0], filename=filename)
                else:
                    new_part.add_header("Content-Disposition", "inline", filename=filename)

                # Content-ID (for inline images)
                if content_id:
                    new_part.add_header("Content-ID", content_id)

                new_part.add_header('Content-Transfer-Encoding', 'base64')
                new_part.set_payload(base64.b64encode(resized_data).decode('ascii'))
                return new_part
        return msg


def process_eml(input_path, output_path):
    print(f"📩 Loading email file: {input_path}")
    with open(input_path, "rb") as f:
        msg = email.message_from_binary_file(f)

    print("🔄 Processing email parts...")
    updated_msg = process_parts(msg)

    print("💾 Saving processed email...")
    updated_msg.add_header(    "X-Resized-By",    f"eml-image-optimizer; {datetime.utcnow().isoformat()}Z; https://github.com/mr-flibble/eml-image-optimizer"
)


    with open(output_path, "wb") as f:
        BytesGenerator(f).flatten(updated_msg)

    print(f"✅ Processed email saved as {output_path}")

if __name__ == "__main__":
    process_eml("original.eml", "resized.eml")
