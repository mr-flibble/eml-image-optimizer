import io
from email import message_from_binary_file, policy
from email.generator import BytesGenerator
from email.message import EmailMessage
from PIL import Image, ExifTags
import email.encoders

MAX_WIDTH = 1920
MAX_HEIGHT = 1080
JPEG_QUALITY = 90

def fix_exif_orientation(img):
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = img._getexif()
        if exif is not None:
            orientation_value = exif.get(orientation)
            if orientation_value == 3:
                img = img.rotate(180, expand=True)
            elif orientation_value == 6:
                img = img.rotate(270, expand=True)
            elif orientation_value == 8:
                img = img.rotate(90, expand=True)
    except Exception:
        pass
    return img

def resize_image(image_data):
    with Image.open(io.BytesIO(image_data)) as img:
        img = fix_exif_orientation(img)
        original_size = img.size

        # Resize preserving aspect ratio and max width/height
        img.thumbnail((MAX_WIDTH, MAX_HEIGHT), Image.LANCZOS)

        out = io.BytesIO()
        exif_bytes = img.info.get('exif')
        if exif_bytes:
            img.save(out, format="JPEG", optimize=True, quality=JPEG_QUALITY, exif=exif_bytes)
        else:
            img.save(out, format="JPEG", optimize=True, quality=JPEG_QUALITY)

        new_data = out.getvalue()

        print(f"    > Original size: {round(len(image_data)/1024)} KB")
        print(f"    > Resized to: {img.size[0]}x{img.size[1]}")
        print(f"    > New size: {round(len(new_data)/1024)} KB")

        return new_data

from email.mime.base import MIMEBase
from email import encoders

def create_resized_attachment(filename, resized_data):
    part = MIMEBase('image', 'jpeg')
    part.set_payload(resized_data)
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment', filename=filename)
    return part

def process_parts(part, depth=0):
    indent = "  " * depth
    if part.is_multipart():
        subtype = part.get_content_subtype()
        print(f"{indent}📦 Multipart type: {part.get_content_type()}")
        new_container = EmailMessage()
        new_container.set_type(part.get_content_type())

        # Copy relevant headers except some managed by EmailMessage automatically
        for key, value in part.items():
            if key.lower() not in ['content-type', 'mime-version', 'content-transfer-encoding']:
                new_container[key] = value

        for subpart in part.iter_parts():
            new_subpart = process_parts(subpart, depth + 1)
            new_container.attach(new_subpart)

        return new_container
    else:
        ctype = part.get_content_type()
        disp = part.get_content_disposition()
        fname = part.get_filename()

        print(f"{indent}🔍 Part: {ctype} | Disposition: {disp} | Filename: {fname}")

        # Only modify JPEG attachments
        if ctype == "image/jpeg" and disp == "attachment" and fname:
            print(f"{indent}🛠️  Processing attachment: {fname}")
            original_data = part.get_payload(decode=True)
            resized_data = resize_image(original_data)
            return create_resized_attachment(fname, resized_data)

            new_part = EmailMessage()
            new_part.set_content(resized_data, maintype='image', subtype='jpeg')
            # Odstraníme případnou existující hlavičku před přidáním base64
            if 'Content-Transfer-Encoding' in new_part:
                del new_part['Content-Transfer-Encoding']
            new_part.add_header('Content-Disposition', 'attachment', filename=fname)
            email.encoders.encode_base64(new_part)

            return new_part
        else:
            print(f"{indent}✅ Not a target for resizing, keeping original.")
            return part

def process_eml(input_path, output_path):
    print(f"📩 Loading email: {input_path}")
    with open(input_path, 'rb') as f:
        msg = message_from_binary_file(f, policy=policy.default)

    print("🔄 Processing email parts...\n")
    updated_msg = process_parts(msg)

    print("\n💾 Saving modified email...")
    with open(output_path, 'wb') as f:
        BytesGenerator(f).flatten(updated_msg)
    print(f"✅ Saved as: {output_path}")

if __name__ == "__main__":
    process_eml("original.eml", "resized.eml")
