# Volan-Route-PDF-Scraper
A Python-based web scraper that automatically downloads route schedules as PDF files from the MÁV-Volán website into a dedicated folder.

### Usage

This program automatically creates a case-sensitive folder named **PDFs** to store all downloaded files by default. If you wish to save the documents to a different location, you must specify the new directory using the `SavePath` attribute within the `DownloadPdf` function.