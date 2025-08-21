# SEPP
This script covers all backend automations for the customer Oppel.

## Context
Oppel receives transport orders (PDF files) via email from its customers (e.g. Danone, Alnatura, Zott, etc.).
For each transport order, a new entry is created in Oppel's TMS system (Soloplan CarLo) and the PDF order document is attached to it.
For invoicing, Oppel uses the ERP system Datev. As soon as a transport is finished, Oppel will create an invoice in Datev and send it to its customer.

## Automated Transport Order Creation

### 1. Running the project locally and on the Production server

#### For testing and developing, SEPP runs locally. What is needed to set it up first:


- MS-Graph Token for sending emails: Create a Python-file with the code below and save the token. Running this code generates a URL. Click it and register with the mail account. The Auth code is contained in the url of the 404 page (not any of the earlier pages!). Copy it until the first "&" and enter into the console.

```python
from microsoft import MSGraphAPI
#generate new ms refresh token


ms_api.create_access_token()
```
- For testing locally, the mails are sent to **sepp-dev@kolibrain.de**. Since `INBOX_ID`, `ERLEDIGT_ID` and `FAILED_ID` in `.env` have not been updated yet for sepp-dev, moving processed files does not work when testing locally. Do not be confused by that since everything works as it should on the server.

#### For Production, the code runs on the server.

- Velat Gümüs is responsible for updating the server.

- The people from Oppel send their mails to **sepp@spedition-oppel.de**. In order to have both mail addresses opened, right-click Edge, select "Neues InPrivate Fenster" and open the second address in Outlook.
- When pushing requirements.txt: On the server, all packages from Kolibrain are pulled with SSH so the comments from this section of the code have to be removed (and those with HTTP have to be commented) before pushing to the server.
- Set up GitLab for the first time:
    - `git config --global user.email "user@kolibrain.de"`
    - `git config --global user.name "user"`
    - `git remote add soloplan https://gitlab.com/koli-projects/oppel/sepp.git`
- Pushing to GitLab:
    - `git add .` or `git add path/to/file` (press Tab for autocompletion)
    - `git commit -m "Detailed message what has changed"`
    - `git push soloplan dev`

### 2. SEPP Pipeline

#### 2.1 `main_transport_orders.py`

This script is the entry point for running SEPP. First, it loads all required values from `settings.py`, the Soloplan package, other external packages and a couple of functions from `scripts/transportOrderUtils.py`.

1. Read unread mails and iterate over them.
2. Filter mails: Mails with Buchhaltungsnummer (the number is stored in a list and later added to the corresponding business partner in Soloplan)and mails with either a single PDF or a single XLSX file as attachment for further processing. XLSX files are converted to PDF with `excel_to_pdf` from `scripts/transportOrderUtils.py`. Mails with no attachment are not processed and an error message is sent. If a mail has two attachments, only the first PDF is processed. **TODO**: Modify `load_pdf` from `scripts/transportOrderUtils.py` so that mails with multiple attachments can be processed.
3. The data from the PDF is extracted by ChatGPT with `pdf_to_json` from `scripts/transportOrderUtils.py`. If Oppel is found as a customer, `pdf_to_json` is executed again to avoid this possible error. **TODO**: Sometimes ChatGPT has trouble to generate the json (or SEPP runs out of money) what causes an error.
4. Connecting to the VPN: After the json is created, SEPP connects to Soloplan CarLo. When running locally, the connection to the VPN has to be made manually. The code asks "Connect to the VPN to continue" and after the connection is made (see `soloplan-vpn-carlo-dokumentation.pdf`) press any key and Enter.
5. If it was a mail with a Buchhaltungsnummer: The number is added to the corresponding business partner with `update_Buchhaltungsnummer_Soloplan` from the Soloplan package.
6. The order is then booked in Soloplan CarLo with `create_order` from the Soloplan package.
7. Delete images: For the previous step of data extraction with ChatGPT, the PDF pages are also saved as jpg files. In order to keep the server tidy, those images are deleted when they are not needed anymore.
8. Disconnect from VPN when working locally: Since the VPN blocks the internet connection, the VPN needs to be disconnected manually. The code asks "Disconnect from VPN" and after disconnecting press any key and enter.
9. Sending mails: As soon as the internet connection is available again, SEPP sends out a range of emails: For success (`send_successMail` from `scripts/transportOrderUtils.py`), for failure (`send_FailMail` from `scripts/transportOrderUtils.py`) and for newly created contacts to the Buchhaltung of Oppel (`send_Mail_To_Buchhaltung` from `scripts/transportOrderUtils.py`).
10. If not manually interrupted (with Strg+c), SEPP waits for a minute and then starts again with checking for new mails.
11. Throughout the main method are a couple of lines of code for writing various stages of the pipeline into `sepp-dokumentation.csv`. Each run gets a new row, and the stages are written to the columns.

Useful hints for debugging:
- SEPP writes each run into a log file. The log files are created newly each day and are stored in the folder `logs`.
- Furthermore consider the print messages when testing locally. This is especially helpful when debugging the LCS algorithm (see Soloplan package). If an empty contact_match "{}" is printed, the search result for the business partner search and contact_info can be copypasted into `scripts/lcsMatchCustomer.py`. This script contains the same LCS-algorithm as the one in the Soloplan package.

#### 2.2 Soloplan Package

The Soloplan package contains all functions making the connection to Soloplan CarLo but also all functions related to creating an order. In the project, this package is found under `venv/Lib/site-packages/soloplan/connectors/api.py`.
Changes to the package have to be committed manually in GitLab.

- `create_order` is called in `main_transport_orders.py` to book an order (see step 6 above).
    1. Checking whether all important data is provided by the json created by ChatGPT.
    2. Hardcoding certain clients for Transporeon orders: In orders which were made with the booking system Transporeon, only the name of the client is given. There is the function `matchTransporeonContact` in this package but since it does not work reliably in a few cases, it is better to keep the hardcoded values.
    3. Get client data from Soloplan CarLo with `get_business_partner`.
    4. If client does not exist, create it newly in Soloplan CarLo with `create_business_partner`.
    5. Loop over each transport listed in the order:
        - Get sender data from Soloplan CarLo with `get_business_partner_lcs_from_Stammdaten_csv`, if this was not successful then try again with `get_business_partner` and if it still does not exist, create it newly in Soloplan CarLo with `create_business_partner`.
        - Get receiver data from Soloplan CarLo with `get_business_partner_lcs_from_Stammdaten_csv`, if this was not successful then try again with `get_business_partner` and if it still does not exist, create it newly in Soloplan CarLo with `create_business_partner`.
        - Get loadingStart, loadingEnd, deliveryStart and deliveryEnd and correct the date format with `validate_date`.
    6. Prepare the json for posting the order.
    7. Post the order to Soloplan CarLo.
- `get_business_partner_lcs_from_Stammdaten_csv` returns the data of a business partner from `StammdatenOppel_aktuell.csv`
    1. In order to make the pipeline more robust, this function was added to replace `get_business_partner`. It is based on `StammdatenOppel_aktuell.csv` generated with `scripts/download_Stammdaten_on_Server.py` which pulls the data each 12h from Soloplan CarLo.
    2. Filter `StammdatenOppel_aktuell.csv` based on zip or city.
    3. Select the corresponding business partner from Soloplan CarLo based on the Longest Common Subsequence (LCS) with `match_business_partner_lcs`.
    4. Return match.

- `get_business_partner` returns the data of a business partner from Soloplan CarLo.
    1. Handle clients from orders made with Transporeon with `matchTransporeonContact` if they have not been hardcoded (it is safer to hardcode them).
    2. Get data from Soloplan CarLo with all contacts with the same zip (PLZ) as the given business partner with `make_request` (At a previous stage of the code, there was the problem that SEPP was creating new contacts for business partners which already existed. Later, it was found that this was caused by the behavior of  Soloplan Carlo to return a maximum of 50 contacts by default if not specified otherwise. Currently, the limit has been increased to top=300. Please change it it if there should occur any issue with larger cities).
    3. After getting the data, `make_request` selects the corresponding business partner from Soloplan CarLo based on the Longest Common Subsequence (LCS) with `match_business_partner_lcs` (previously, contact matching was done with Levenshtein distance in `match_business_partner`. At the moment, `make_request` contains many print statements and it is highly recommended to leave them there for debugging `match_business_partner_lcs` as it was explained earlier).
    4. If the search based on zip brought no result, `make_request` is called again based on the city name instead of the zip.

- `match_business_partner_lcs`
    1. Normalization of streetname (strasse) with removal of umlauts and punctuation; splitting of housenumber from streetname.
    2. Loop over decreasing string length thresholds for the lcs-string (7, 6, 5, 4, 3).
        - Loop over the list of possible business partners.
        - If a partner with identical streetname and identical (or no) housenumber was found: Get lcs with `lcs` and if the length of the resulting lcs string is longer or equal to the given threshold, the contact is returned as a match.
    3. The approach in step 2. depends on the streetname but if the streetname has typos or is missing, another approach was needed to catch these cases.
        - Loop again over the list of possible business partners if no match was found in 2.
        - If names are equal, return a match.
        - If the lcs-string has 5 or more characters and is contained in both names, return a match (the condition that the lcs-string has to be contained in both names makes sure that no mismatches occur due to chance like "aaaaa" if two otherwise unrelated names would contain 5 As)
        - If the lcs-string has 10 or more characters, return a match (this was needed for slightly diverging names due to typos not caught by the previous if-statement; the big length also makes sure that this is not due to chance since Soloplan also has a character-limit of 40 on name1).
        - Hardcoded exceptions: There are some cases which are not caught by any of the above conditions which need to match nevertheless. Those are handled with a list of lcs-strings ["rewe", "aldi", "btk", "nagelse", "dachserse", "lidl"] which are automatically matches (This cannot be handled safely in any other way what becomes clear when looking at such a short sequence as "btk". Furthermore if a contact ends up here, there was already some issue with the streetname plus a mismatch between the names what is quite rare. All in all, `match_business_partner_lcs` is a very finely balanced algorithm: Making it too strict causes the creation of unnecessary new contacts and making it not strict enough leads to mismatches. A lot of testing went into finding optimal values for the thresholds in each place, thus it is discouraged to play further around with them.)
- `lcs` This is the core LCS-algorithm
    1. Cleaning the two input strings before calculation:
        - Remove certain frequent "business terms" such as GmbH, Firma, etc... with `replace_special_chars`. This function cleans the two strings based on the list `replacements_lcs` (if any generic term causes mismatches, just add it to this list in lowercase but watch out for the order of the items!).
        - Remove the city name if it is in any of the two strings.
    2. Calculate and return the lcs-string.

- `create_business_partner` if no match was found.
    1. Get country of the contact: The function checks for variants of countrynames for Germany, Poland, Italy and Austria and raises a Value Error if a new country needs to be added. The country is also validated with `validate_address`, however this gives the log warning *Failed to resolve 'nominatim.openstreetmap.org'* when testing locally since SEPP has no access to the internet at this stage.
    2. The json is filled with the information from the new contact. name1 is restricted to 40 characters due to the built-in limit of Soloplan CarLo and name2 is set to "Kontakt wurde von SEPP neu angelegt." what is helpful to identify all contacts which were created by SEPP (however it is also possible to search for SEPP as an author of a contact when searching manually in Soloplan CarLo).
    3. Post json to Soloplan CarLo.
    4. If Soloplan CarLo refuses to create the contact since it already exists, this is due to the contact lacking a required role (client or sender/receiver). If this is the case, the missing role is added.

- `update_Buchhaltungsnummer_Soloplan`
    Post new Buchhaltungsnummer as number to Soloplan CarLo.

#### 2.3 `scripts/transportOrderUtils.py`

`scripts/transportOrderUtils.py` basically contains all mail-related and ChatGPT-related functions of the project.
The two functions `save_pdf_as_image` and `run_model` are for the donut model which will be used in a later stage of the project.

- `waitForVPN` and `disconnectVPN` These functions are only relevant for testing locally. After the json is returned by ChatGPT, `waitForVPN` pauses the code and gives you time to manually connect to the Forticlient VPN. If the connection is made, press any key + Enter. After the order has been booked (or failed) `disconnectVPN` pauses the code until the VPN is disconnected. Again, press any key + Enter.

##### **ChatGPT code**
- `pdf_to_json` This function is called by `main_transport_orders.py` to get the json from the PDF with ChatGPT. The raw text of the PDF is obtained with `extract_text_from_pdf` and in the case of an Image-PDF (Buckl, Henglein) raw text is set to an empty string. To improve the output of ChatGPT, the entities of an order (client, sender, receiver, carrier) are identified with `extract_entities_from_text` and are passed to `generate_json_with_retry` together with the raw text and the path to the PDF. `generate_json_with_retry` fulfills the purpose to repeat the call to ChatGPT in `generate_json_from_text` up to 3 times if it is not successful at first try.
- `generate_json_from_text`
    1. Prepare prompts with `get_client` and `get_transports` (when there is something wrong with the ChatGPT-Output or if certain orders (like Transporeon) need special treatment, modify the prompts here; ChatGPT can also help with that).
    2. Convert PDF to image with `convert_pdf_to_image`.
    3. Call ChatGPT with `openai.chat.completions.create`.
    4. Correct output json if needed.

##### **E-Mail code**
The mail-related functions are based on the **Microsoft package** which is found in the project under `venv/Lib/site-packages/microsoft/connectors/api.py` and on GitLab under https://gitlab.com/koli-module/connectors/microsoft/-/blob/dev/src/microsoft/connectors/api.py?ref_type=heads. Should it be necessary to modify any of the functions from the Microsoft package, they have to be committed manually (like for the Soloplan package). **But keep in mind that this package is also used in a range of other projects (like Paravan) so make sure that your new code does not affect the work of your colleagues in a negative way. When in doubt, please ask first!**

- `load_pdf` Returns the data and name from a mail with a single PDF or XLSX file. **TODO** Handle mails with multiple attachments and mails where the order is in the text of the mail.
- `moveFailedMail` This function prevents SEPP from running infinitely over failed mails by moving them to the folder "Failed". Moving to the folder does not work (yet) when running locally since this would require to get the folder path for (it is also more practical for testing if the mails are not moved).
- `send_successMail` This function sends out a mail to the sender of the mail when an order was successfully processed and moves the mail into the folder "Erledigt".
- `send_FailMail` If a mail was not successfully processed, the sender of the mail receives an error message instead. This function also allows to specify in a short text what went wrong. **If there is the need to add more detailed error messages for Oppel, discuss this with Lyth in advance!**
- `log_error` More detailed error messages are provided to us by this function which also adds the error to the log file.
- `send_Mail_To_Buchhaltung` If a new client was created during a run of SEPP, it is necessary to have a "Buchhaltungsnummer" created for it. `write_csv_for_Buchhaltung` creates a table with the data which can be appended to the Debitoren file (so that the people at Oppel do not have to type this themselves). Furthermore, it sends the mail to the Buchhaltung and asks them to send the newly created "Buchhaltungsnummer" in response.

#### 2.4 Saving data for training the donut model

Gathering test data for replacing ChatGPT with the donut model (to make it more consistent and to save money) in a later stage of the project.
- PDFs in `transport_orders_imgs`.
- ChatGPT-Output jsons with the same name as the PDFs in `modelResults`.
- `scripts/download_orders_for_server.py` Based on `sepp-dokumentation.csv`, this script pulls the jsons from all orders older than 5 days to the folder `correctedJSONSoloplan` (the limit of 5 days ensures that it only pulls orders which were manually corrected by the staff of Oppel in case SEPP made an error).



## SEPP weekly maintenance
1. Check "Failed" folder of sepp@kolibrain.de.
2. Save the order attached to each mail and send each order in a separate mail to sepp-dev@kolibrain.de.
3. If there are several mails: Set them first to "read" and then test them one by one by setting to "unread".
4. Run SEPP locally and consider both logs and print messages. Typical errors are issues with ChatGPT (incomplete json; no json), LCS-contact matching (no match; mismatch) or refusal of the Soloplan API to carry out an action (like creating a new contact because one with that name exists in other places, see RKW SE or Kölle/Fressnapf).
5. If the error does not occur again it was very likely an issue related to ChatGPT (in this case consider logs and print messages from the server).
6. Debug, push and run on server and also test on server again.
