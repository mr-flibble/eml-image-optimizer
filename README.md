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

If you have `.eml` emails with large photo attachments (3–5 MB each), this tool can shrink the total email size by over 90% – perfect for reducing IMAP storage, backups, or long-term archiving.
