import re
import socket
from urllib.parse import quote

import win32print
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


# ============================================================
# CONFIGURATION
# ============================================================

PRINTER_HOSTNAME = "CSCDGJ244902154"
PRN_FILE = "testing1_brackets.prn"

SERVICENOW_BASE_URL = "https://partnershealthcare.service-now.com"

TASK_SEARCH_URL = (
    SERVICENOW_BASE_URL
    + "/now/nav/ui/classic/params/target/"
      "task_list.do%3Fsysparm_query%3D"
      "active%253Dtrue"
      "%255Estate!%253D6"
      "%255Esys_class_name!%253Dsysapproval_group"
      "%255Eassigned_toISNOTEMPTY"
      "%255Eassignment_group%253D01d2b1e36f3a420021590f1aea3ee4bd"
      "%255EdescriptionLIKE{device}"
      "%255EORcmdb_ciLIKE{device}"
      "%26sysparm_first_row%3D1"
      "%26sysparm_view%3D"
)


# ============================================================
# GENERAL HELPERS
# ============================================================

def clean_text(value: str) -> str:
    """
    Cleans text scraped from ServiceNow.
    """
    if not value:
        return ""

    return " ".join(value.split()).strip()


def safe_inner_text(page, selector: str, timeout: int = 2000) -> str:
    """
    Attempts to get text from a selector.

    Returns an empty string if the element does not exist.
    """
    if not selector:
        return ""

    try:
        return clean_text(
            page.locator(selector).inner_text(timeout=timeout)
        )
    except Exception:
        return ""


def value_by_label(
    page,
    labels,
    fallback_selector: str = "",
    timeout: int = 1500,
) -> str:
    """
    Attempts to find a value in a ServiceNow HTML table based
    on the text of the label cell.

    For example:

        Department: | Research MGH

    If it finds "Department", it returns "Research MGH".

    If no matching label is found, fallback_selector is used.
    """

    for label in labels:
        pattern = re.compile(
            rf"^\s*{re.escape(label)}\s*:?\s*$",
            re.IGNORECASE,
        )

        try:
            matches = page.locator("td").filter(has_text=pattern)

            count = matches.count()

            for i in range(min(count, 10)):
                label_cell = matches.nth(i)

                try:
                    value_cell = label_cell.locator(
                        "xpath=following-sibling::td[1]"
                    )

                    value = clean_text(
                        value_cell.inner_text(timeout=timeout)
                    )

                    if value:
                        return value

                except Exception:
                    continue

        except Exception:
            continue

    return safe_inner_text(page, fallback_selector, timeout)


# ============================================================
# DEVICE PARSING
# ============================================================

def parse_device_info(raw_value: str):
    """
    Attempts to pull the Control ID and Asset Tag out of the
    New/Old device strings returned by ServiceNow.

    Examples it can understand:

        W0231472 P6116632
        W0231472 / P6116632
        W0231472 (P6116632)
        Control ID: W0231472 Asset: P6116632

    Returns:

        ("W0231472", "P6116632")

    If the function cannot identify a Control ID, the entire
    original string is used as the Control ID so that data is
    not accidentally lost.
    """

    raw_value = clean_text(raw_value).upper()

    if not raw_value:
        return "", ""

    # MGB workstation/control ID, e.g. W0231472
    cid_match = re.search(
        r"\bW[A-Z0-9]{6,}\b",
        raw_value,
        re.IGNORECASE,
    )

    # MGB asset tag, e.g. P6116632
    asset_match = re.search(
        r"\bP[A-Z0-9]{6,}\b",
        raw_value,
        re.IGNORECASE,
    )

    cid = cid_match.group(0) if cid_match else ""
    asset = asset_match.group(0) if asset_match else ""

    # Don't throw away data if the exact format was unexpected.
    if not cid:
        cid = raw_value

    return cid, asset


# ============================================================
# ZPL HELPERS
# ============================================================

def zpl_escape(value: str) -> str:
    """
    Escapes characters that could be interpreted as ZPL commands.

    Since the template uses:

        ^FH\\

    hexadecimal escaped characters can be included safely.
    """

    if value is None:
        return ""

    value = str(value)

    # Remove actual CR/LF characters from scraped ServiceNow data.
    value = value.replace("\r", " ")
    value = value.replace("\n", " ")

    # Escape the hex indicator FIRST.
    value = value.replace("\\", r"\5C")

    # Escape ZPL command introducers.
    value = value.replace("^", r"\5E")
    value = value.replace("~", r"\7E")

    return value.strip()


def build_details_block(
    new_device_cid="",
    new_device_asset="",
    old_device_cid="",
    old_device_asset="",
    build="",
    assets="",
    recipient_name="",
    location="",
    department="",
) -> str:
    """
    Creates the dynamic multi-line field block.

    Example result:

        New: W0123456 (P1234567)
        Old: W0765432
        Build: 24H2
        Assets: Monitor, Dock

        Recipient: John Smith
        Location: Bigelow 7/725
        Department: Research MGH

    Missing fields are completely omitted.
    """

    device_lines = []
    recipient_lines = []

    # --------------------------------------------------------
    # NEW DEVICE
    # --------------------------------------------------------

    if new_device_cid or new_device_asset:
        line = "New:"

        if new_device_cid:
            line += f" {zpl_escape(new_device_cid)}"

        if new_device_asset:
            line += f" ({zpl_escape(new_device_asset)})"

        device_lines.append(line)

    # --------------------------------------------------------
    # OLD DEVICE
    # --------------------------------------------------------

    if old_device_cid or old_device_asset:
        line = "Old:"

        if old_device_cid:
            line += f" {zpl_escape(old_device_cid)}"

        if old_device_asset:
            line += f" ({zpl_escape(old_device_asset)})"

        device_lines.append(line)

    # --------------------------------------------------------
    # BUILD
    # --------------------------------------------------------

    if build:
        device_lines.append(
            f"Build: {zpl_escape(build)}"
        )

    # --------------------------------------------------------
    # ADDITIONAL ASSETS
    # --------------------------------------------------------

    if assets:
        device_lines.append(
            f"Assets: {zpl_escape(assets)}"
        )

    # --------------------------------------------------------
    # RECIPIENT
    # --------------------------------------------------------

    if recipient_name:
        recipient_lines.append(
            f"Recipient: {zpl_escape(recipient_name)}"
        )

    # --------------------------------------------------------
    # LOCATION
    # --------------------------------------------------------

    if location:
        recipient_lines.append(
            f"Location: {zpl_escape(location)}"
        )

    # --------------------------------------------------------
    # DEPARTMENT
    # --------------------------------------------------------

    if department:
        recipient_lines.append(
            f"Department: {zpl_escape(department)}"
        )

    # --------------------------------------------------------
    # COMBINE SECTIONS
    # --------------------------------------------------------

    lines = []

    lines.extend(device_lines)

    # Add ONE blank line only when both sections have data.
    if device_lines and recipient_lines:
        lines.append("")

    lines.extend(recipient_lines)

    # In a Zebra ^FB field, \& forces a new line.
    return r"\&".join(lines)


# ============================================================
# SERVICENOW SCRAPING
# ============================================================

def scrape_dwo_print_page(page, task_id: str):
    """
    Opens WOMassPrint for the task and retrieves the data used
    by the label.
    """

    print_url = (
        f"{SERVICENOW_BASE_URL}"
        f"/WOMassPrint?sysparm_taskids={task_id}"
    )

    page.goto(
        print_url,
        wait_until="networkidle",
        timeout=60000,
    )

    # Prevent print dialog if WOMassPrint tries to open it.
    try:
        page.keyboard.press("Escape")
    except Exception:
        pass

    # --------------------------------------------------------
    # TASK NUMBER
    # Existing selector from your script.
    # --------------------------------------------------------

    task = value_by_label(
        page,
        labels=[
            "Task",
            "Task Number",
            "Number",
            "DWO",
        ],
        fallback_selector=(
            "body > table > tbody > tr:nth-child(2) "
            "> td:nth-child(2)"
        ),
    ).upper()

    # --------------------------------------------------------
    # NEW DEVICE
    # Existing selector:
    # row 12, column 2
    # --------------------------------------------------------

    new_raw = value_by_label(
        page,
        labels=[
            "New",
            "New Device",
            "New Computer",
            "New Workstation",
        ],
        fallback_selector=(
            "body > table > tbody > tr:nth-child(12) "
            "> td:nth-child(2)"
        ),
    ).upper()

    # --------------------------------------------------------
    # OLD DEVICE
    # Existing selector:
    # row 13, column 2
    # --------------------------------------------------------

    old_raw = value_by_label(
        page,
        labels=[
            "Old",
            "Old Device",
            "Old Computer",
            "Old Workstation",
        ],
        fallback_selector=(
            "body > table > tbody > tr:nth-child(13) "
            "> td:nth-child(2)"
        ),
    ).upper()

    # --------------------------------------------------------
    # ASSIGNED TECH
    # Existing selector:
    # row 6, column 4
    # --------------------------------------------------------

    assigned_tech = value_by_label(
        page,
        labels=[
            "Assigned to",
            "Assigned To",
            "Assigned",
            "Technician",
        ],
        fallback_selector=(
            "body > table > tbody > tr:nth-child(6) "
            "> td:nth-child(4)"
        ),
    )

    # --------------------------------------------------------
    # RECIPIENT
    # Existing selector:
    # row 8, column 2
    # --------------------------------------------------------

    recipient_name = value_by_label(
        page,
        labels=[
            "Recipient",
            "Requested For",
            "Requested for",
            "User",
        ],
        fallback_selector=(
            "body > table > tbody > tr:nth-child(8) "
            "> td:nth-child(2)"
        ),
    )

    # --------------------------------------------------------
    # LOCATION
    # Existing selector:
    # row 9, column 2
    # --------------------------------------------------------

    location = value_by_label(
        page,
        labels=[
            "Location",
            "Building",
            "Site",
        ],
        fallback_selector=(
            "body > table > tbody > tr:nth-child(9) "
            "> td:nth-child(2)"
        ),
    )

    # --------------------------------------------------------
    # ROOM
    # Existing selector:
    # row 9, column 4
    # --------------------------------------------------------

    room = value_by_label(
        page,
        labels=[
            "Room",
            "Room Number",
        ],
        fallback_selector=(
            "body > table > tbody > tr:nth-child(9) "
            "> td:nth-child(4)"
        ),
    )

    # Combine location and room intelligently.
    if location and room:
        location_room = f"{location}/{room}"
    elif location:
        location_room = location
    elif room:
        location_room = room
    else:
        location_room = ""

    # --------------------------------------------------------
    # BUILD
    #
    # There wasn't a selector for this in the code you sent,
    # so this searches for a table label automatically.
    # --------------------------------------------------------

    build = value_by_label(
        page,
        labels=[
            "Build",
            "Build Type",
            "Image",
            "Image Build",
            "OS Build",
        ],
    )

    # --------------------------------------------------------
    # ASSETS
    #
    # Searches automatically by label.
    # --------------------------------------------------------

    assets = value_by_label(
        page,
        labels=[
            "Assets",
            "Asset",
            "Additional Assets",
            "Additional Equipment",
            "Equipment",
        ],
    )

    # --------------------------------------------------------
    # DEPARTMENT
    #
    # Searches automatically by label.
    # --------------------------------------------------------

    department = value_by_label(
        page,
        labels=[
            "Department",
            "Dept",
            "Department Name",
        ],
    )

    # Parse the New/Old fields.
    new_device_cid, new_device_asset = parse_device_info(
        new_raw
    )

    old_device_cid, old_device_asset = parse_device_info(
        old_raw
    )

    return {
        "task": task,
        "new_device_cid": new_device_cid,
        "new_device_asset": new_device_asset,
        "old_device_cid": old_device_cid,
        "old_device_asset": old_device_asset,
        "assigned_tech": assigned_tech,
        "recipient_name": recipient_name,
        "location": location_room,
        "build": build,
        "assets": assets,
        "department": department,
    }


# ============================================================
# LABEL GENERATION
# ============================================================

def print_dwo_label(task_id: str, data: dict):
    """
    Loads the .prn template, fills the placeholders, and sends
    the completed ZPL to the network printer.
    """

    details_block = build_details_block(
        new_device_cid=data["new_device_cid"],
        new_device_asset=data["new_device_asset"],
        old_device_cid=data["old_device_cid"],
        old_device_asset=data["old_device_asset"],
        build=data["build"],
        assets=data["assets"],
        recipient_name=data["recipient_name"],
        location=data["location"],
        department=data["department"],
    )

    with open(PRN_FILE, "r", encoding="utf-8") as f:
        dwo_label = f.read()

    dwo_label = dwo_label.format(
        task_id=task_id,
        task=zpl_escape(data["task"]),
        assigned_tech=zpl_escape(data["assigned_tech"]),
        details_block=details_block,
    )

    # Helpful for debugging.
    print("\n---------------- LABEL DATA ----------------")
    print(f"Task:              {data['task']}")
    print(f"Assigned tech:     {data['assigned_tech']}")
    print(f"New CID:           {data['new_device_cid']}")
    print(f"New Asset:         {data['new_device_asset']}")
    print(f"Old CID:           {data['old_device_cid']}")
    print(f"Old Asset:         {data['old_device_asset']}")
    print(f"Build:             {data['build']}")
    print(f"Assets:            {data['assets']}")
    print(f"Recipient:         {data['recipient_name']}")
    print(f"Location:          {data['location']}")
    print(f"Department:        {data['department']}")

    print("\nDynamic label block:")
    print(details_block.replace(r"\&", "\n"))

    print("--------------------------------------------\n")

    send_zpl_to_network_printer(
        PRINTER_HOSTNAME,
        dwo_label,
    )


# ============================================================
# NETWORK PRINTING
# ============================================================

def send_zpl_to_network_printer(
    printer_hostname: str,
    zpl_data: str,
):
    """
    Sends raw ZPL directly to a Zebra printer over TCP 9100.
    """

    try:
        with socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        ) as s:

            s.settimeout(10)

            s.connect(
                (printer_hostname, 9100)
            )

            s.sendall(
                zpl_data.encode("utf-8")
            )

        print(
            f"Printing label to network printer "
            f"'{printer_hostname}'."
        )

    except Exception as e:
        print(
            f"Failed to send ZPL to network printer: {e}"
        )


# ============================================================
# OPTIONAL WINDOWS LOCAL PRINTING
# ============================================================

def send_zpl_to_local_printer(
    printer_name: str,
    zpl_data: str,
):
    """
    Sends raw ZPL through the Windows printer spooler.
    """

    try:
        hPrinter = win32print.OpenPrinter(printer_name)

        try:
            win32print.StartDocPrinter(
                hPrinter,
                1,
                (
                    "ZPL Label",
                    None,
                    "RAW",
                ),
            )

            win32print.StartPagePrinter(hPrinter)

            win32print.WritePrinter(
                hPrinter,
                zpl_data.encode("utf-8"),
            )

            win32print.EndPagePrinter(hPrinter)
            win32print.EndDocPrinter(hPrinter)

        finally:
            win32print.ClosePrinter(hPrinter)

        print(
            f"Printing label to '{printer_name}'."
        )

    except Exception as e:
        print(
            f"Failed to send ZPL: {e}"
        )


# ============================================================
# MAIN
# ============================================================

def main():
    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page()

        try:

            while True:
                device = input(
                    "Enter device name (or nothing to quit): "
                ).strip()

                if not device:
                    break

                try:
                    encoded_device = quote(
                        device,
                        safe="",
                    )

                    search_url = TASK_SEARCH_URL.format(
                        device=encoded_device
                    )

                    page.goto(
                        search_url,
                        wait_until="domcontentloaded",
                        timeout=60000,
                    )

                    # ServiceNow's classic UI places the
                    # task list inside gsft_main.
                    frame = page.frame_locator(
                        'iframe[name="gsft_main"]'
                    )

                    task_row = frame.locator(
                        "#task_table > tbody > tr:first-child"
                    )

                    task_row.wait_for(
                        state="attached",
                        timeout=30000,
                    )

                    task_id = task_row.get_attribute(
                        "sys_id"
                    )

                    if not task_id:
                        print(
                            f"No task found for '{device}'."
                        )
                        continue

                    print(f"\nTask ID: {task_id}")

                    task_url = (
                        f"{SERVICENOW_BASE_URL}"
                        f"/nav_to.do?uri=task.do?"
                        f"sys_id={task_id}"
                    )

                    print(f"Task URL: {task_url}")

                    # Get all printable information.
                    data = scrape_dwo_print_page(
                        page,
                        task_id,
                    )

                    # Generate and print the label.
                    print_dwo_label(
                        task_id,
                        data,
                    )

                except PlaywrightTimeoutError:
                    print(
                        f"Timed out while searching for "
                        f"'{device}'."
                    )

                except Exception as e:
                    print(
                        f"An error occurred while processing "
                        f"'{device}': {e}"
                    )

        finally:
            browser.close()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        print("\nExiting...")