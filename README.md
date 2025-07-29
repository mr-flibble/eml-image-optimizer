# eml-image-optimizer
Resize and compress image attachments in .eml files to reduce email size without losing content.

This Python script processes `.eml` email files and reduces the size of embedded image attachments (JPEG) by resizing and compressing them. Ideal for archiving or reducing email storage without losing the original message structure.

## Features

- Resizes images to a maximum of 1920×1080 (customizable)
- Compresses JPEGs with adjustable quality
- Keeps all headers and body content intact
- Processes multipart email structures correctly
- Outputs a modified `.eml` file with reduced attachment sizes

## Use Case

If you have `.eml` emails with large photo attachments (3–5 MB each) or large inline (embedded) images, this tool can shrink the total email size by over 90% – perfect for reducing IMAP storage, backups, or long-term archiving.

Dependencies:
pip install pillow piexif




## 🛠️ Workflow: How to Use
**1. Export the email**
Drag an email out of your email client (e.g. Thunderbird, Outlook) and drop it into a folder on your computer as a .eml file.
Make sure it’s named like original.eml.

**2. Run the script**
python python email_resizer.py
This will:

Load original.eml

Resize all image attachments (if needed)

Save a new email file: resized.eml

**3. Replace the email in your client**
Delete the original email (optional, to save space)

Import resized.eml back into your email client (e.g., drag it into a folder)

📝 Notes
Only works on .eml files (RFC 822 format, supported by most clients)

The body, subject, sender, and all text content remain unchanged

EXIF metadata is preserved, and image orientation is corrected


**🔒 Why This Matters**

Cloud email providers (like Gmail, Outlook.com) do not provide easy tools to reduce email size. They may even make it intentionally difficult to modify existing emails, especially if you're reaching storage limits. This tool gives you back control.



| Original                            | After Resize                            |
| ----------------------------------- | --------------------------------------- |
| 26 MB `.eml` with 6 full-res photos | 2.1 MB `.eml`, identical appearance     |
| Images: 4000x3000, 3–4 MB each      | Resized to 1920x1080, \~100–200 KB each |


## Example saving 
![image](https://github.com/user-attachments/assets/a0e2f9cb-c344-4eaa-b69a-e2df820768ff)


## Example output 
   > 📩 Loading email: original.eml

   > 🔄 Processing email parts...

   >📦 Multipart type: multipart/mixed

    > 📦 Multipart type: multipart/alternative

     >  🔍 Part: text/plain | Disposition: None | Filename: None

     >  ✅ Not a target for resizing, keeping original.

      > 🔍 Part: text/html | Disposition: None | Filename: None

      > ✅ Not a target for resizing, keeping original.

     >🔍 Part: image/jpeg | Disposition: attachment | Filename: P2290832.JPG

     >🛠️  Processing attachment: P2290832.JPG

    > Original size: 3573 KB

    > Resized to: 1440x1080

    > New size: 90 KB

     >🔍 Part: image/jpeg | Disposition: attachment | Filename: P2290835.JPG

     >🛠️  Processing attachment: P2290835.JPG

    > Original size: 3014 KB

    > Resized to: 1440x1080

    > New size: 176 KB

     >🔍 Part: image/jpeg | Disposition: attachment | Filename: P2290836.JPG

     >🛠️  Processing attachment: P2290836.JPG

    > Original size: 3101 KB

    > Resized to: 1440x1080

    > New size: 204 KB

     >🔍 Part: image/jpeg | Disposition: attachment | Filename: P2290824.JPG

     >🛠️  Processing attachment: P2290824.JPG

    > Original size: 3042 KB

    > Resized to: 1440x1080

    > New size: 191 KB

     >🔍 Part: image/jpeg | Disposition: attachment | Filename: P2290825.JPG

     >🛠️  Processing attachment: P2290825.JPG
    > Original size: 2991 KB
    > Resized to: 1440x1080

    > New size: 196 KB

     >🔍 Part: image/jpeg | Disposition: attachment | Filename: P2290829.JPG

     >🛠️  Processing attachment: P2290829.JPG
    > Original size: 2978 KB
    > Resized to: 1440x1080
    > New size: 169 KB
