import email
from email.message import EmailMessage
from email.generator import BytesGenerator
import io
from PIL import Image, ImageOps
import piexif
import base64

def resize_image(data):
    img = Image.open(io.BytesIO(data))

    # Load original EXIF data
    exif_dict = piexif.load(img.info.get('exif', b''))

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
        if disp and disp.startswith("attachment") and ctype.startswith("image/") and filename:
            print(f"{indent}🛠️ Processing attachment: {filename}")
            original_data = msg.get_payload(decode=True)
            resized_data = resize_image(original_data)
            print(f"{indent}> Original size: {len(original_data)//1024} KB")
            img = Image.open(io.BytesIO(resized_data))
            print(f"{indent}> Resized to: {img.width}x{img.height}")
            print(f"{indent}> New size: {len(resized_data)//1024} KB")

            new_part = EmailMessage()
            new_part.set_type(ctype)
            new_part.add_header("Content-Disposition", "attachment", filename=filename)
            new_part.add_header('Content-Transfer-Encoding', 'base64')
            new_part.set_payload(base64.b64encode(resized_data).decode('ascii'))
            return new_part
        else:
            print(f"{indent}✅ Not an image attachment to resize, leaving unchanged")
            return msg

def process_eml(input_path, output_path):
    print(f"📩 Loading email file: {input_path}")
    with open(input_path, "rb") as f:
        msg = email.message_from_binary_file(f)

    print("🔄 Processing email parts...")
    updated_msg = process_parts(msg)

    print("💾 Saving processed email...")
    with open(output_path, "wb") as f:
        BytesGenerator(f).flatten(updated_msg)

    print(f"✅ Processed email saved as {output_path}")

if __name__ == "__main__":
    process_eml("original.eml", "resized.eml")
