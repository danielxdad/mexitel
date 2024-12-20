# mexitel

This is a bot that was created with the intention of getting a ticket from the old version of [Citas SRE](https://citas.sre.gob.mx/) ([old version](https://mexitel.sre.gob.mx/citas.webportal/)) emulating a real user.

Have two operational modes

1. Using [Selenium](https://www.selenium.dev/) for controlling a Firefox instance ("master" branch)
2. All request are make from Python through requests lib ("console" branch)

He also was able to processing a email sent to the user's mailbox with a PDF attachment including a alphanumeric token and 8 alphanumerics characters split in same numbers images segments sparse in the doc using Tesseract for OCR.

It was only built for learning and educational purpose.
