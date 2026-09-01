from textwrap import dedent

import win32print
from playwright.sync_api import sync_playwright


class DWO_Label:
    def __init__(
        self,
        task_url,
        task,
        new_device,
        old_device,
        assigned_tech,
        recipient,
        location_room,
        department,
    ):
        self.task_url = task_url
        self.task = task
        self.new_device = new_device
        self.old_device = old_device
        self.assigned_tech = assigned_tech
        self.recipient = recipient
        self.location_room = location_room
        self.department = department


def main():
    with sync_playwright() as p:
        # Channel can be "chrome", "msedge", "chrome-beta", "msedge-beta" or "msedge-dev".
        # browser = p.chromium.launch(channel="msedge", headless=False)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        device = input("Enter device name (or nothing to quit): ")
        while device:
            try:
                # doesn't work if the configuration item isnt set
                # page.goto(f"https://partnershealthcare.service-now.com/now/nav/ui/classic/params/target/task_list.do%3Fsysparm_query%3Dactive%253Dtrue%255Estate!%253D6%255Esys_class_name!%253Dsysapproval_group%255Eassigned_toISNOTEMPTY%255Eassignment_group%253D01d2b1e36f3a420021590f1aea3ee4bd%255Ecmdb_ci.nameLIKE{device}%26sysparm_first_row%3D1%26sysparm_view%3D")

                # page.goto(f"https://partnershealthcare.service-now.com/now/nav/ui/classic/params/target/task_list.do%3Fsysparm_query%3Dactive%253Dtrue%255Estate!%253D6%255Esys_class_name!%253Dsysapproval_group%255Eassigned_toISNOTEMPTY%255Eassignment_group%253D01d2b1e36f3a420021590f1aea3ee4bd%255EdescriptionLIKE{device}%255EORcmdb_ciLIKE{device}%26sysparm_first_row%3D1%26sysparm_view%3D", wait_until="networkidle")
                page.goto(
                    f"https://partnershealthcare.service-now.com/now/nav/ui/classic/params/target/task_list.do%3Fsysparm_query%3Dactive%253Dtrue%255Estate!%253D6%255Esys_class_name!%253Dsysapproval_group%255Eassignment_group%253D01d2b1e36f3a420021590f1aea3ee4bd%255EdescriptionLIKE{device}%255EORcmdb_ciLIKE{device}%26sysparm_first_row%3D1%26sysparm_view%3D",
                    wait_until="networkidle",
                )
                page.locator('iframe[name="gsft_main"]').content_frame.locator(
                    "#task_table > tbody > tr:first-child"
                ).wait_for(timeout=5000)

                # if page.locator('iframe[name="gsft_main"]').content_frame.locator("#task > div.list2_empty-state-list").():
                #     print(f"No tasks found for device '{device}'.")
                #     device = input("Enter device name (or nothing to quit): ")
                #     continue

                task_id = (
                    page.locator('iframe[name="gsft_main"]')
                    .content_frame.locator("#task_table > tbody > tr:first-child")
                    .get_attribute("sys_id")
                )
                # https://partnershealthcare.service-now.com/nav_to.do?uri=task.do?sys_id=4ebc0a473be5c710eb520931a3e45a84
                print(f"Task ID: {task_id}")
                task_url = f"https://partnershealthcare.service-now.com/nav_to.do?uri=task.do?sys_id={task_id}"
                # 3230e71f3be28b14a806e5ac24e45a69
                # https://partnershealthcare.service-now.com/nav_to.do?uri=task.do?sys_id=3230e71f3be28b14a806e5ac24e45a69
                # Monitors no computer DWO
                # 0a3368733bae4b182becf9ac24e45a01
                # page.goto(task_url)
                print_url = f"https://partnershealthcare.service-now.com/WOMassPrint?sysparm_taskids={task_id}"
                page.goto(print_url, wait_until="networkidle")
                page.keyboard.press("Escape")
                # sys_display\.ni\.VEc7acc68feb650b107ed8fb989dc0cd85
                # New: body > table > tbody > tr:nth-child(12) > td:nth-child(2)
                # Old: body > table > tbody > tr:nth-child(13) > td:nth-child(2)
                # Assigned to body > table > tbody > tr:nth-child(6) > td:nth-child(4)
                task = (
                    page.locator(
                        "body > table > tbody > tr:nth-child(2) > td:nth-child(2)"
                    )
                    .inner_text()
                    .upper()
                )
                new = (
                    page.locator(
                        "body > table > tbody > tr:nth-child(12) > td:nth-child(2)"
                    )
                    .inner_text()
                    .upper()
                )
                old = (
                    page.locator(
                        "body > table > tbody > tr:nth-child(13) > td:nth-child(2)"
                    )
                    .inner_text()
                    .upper()
                )
                assigned_tech = page.locator(
                    "body > table > tbody > tr:nth-child(6) > td:nth-child(4)"
                ).inner_text()
                recipient = page.locator(
                    "body > table > tbody > tr:nth-child(8) > td:nth-child(2)"
                ).inner_text()
                location_room = f"{page.locator('body > table > tbody > tr:nth-child(9) > td:nth-child(2)').inner_text()}/{page.locator('body > table > tbody > tr:nth-child(9) > td:nth-child(4)').inner_text()}"
                department = page.locator(
                    "body > table > tbody > tr:nth-child(10) > td:nth-child(2)"
                ).inner_text()
                print(f"New: {new}")
                print(f"Old: {old}")
                print(f"Assigned to: {assigned_tech}")
                print(f"Recipient: {recipient}")
                print(f"Location/Room: {location_room}")
                print(f"Department: {department}")
                dwo_label = DWO_Label(
                    task_url,
                    task,
                    new,
                    old,
                    assigned_tech,
                    recipient,
                    location_room,
                    department,
                )
                print_dwo_label(dwo_label)
                # page.pause()

            except Exception as e:
                print(f"An error occurred: {e}")
            device = input("Enter device name (or nothing to quit): ")


def print_dwo_label(dwo_label: DWO_Label):
    # URL to filter for the device and grab task url
    # https://partnershealthcare.service-now.com/now/nav/ui/classic/params/target/task_list.do%3Fsysparm_query%3Dactive%253Dtrue%255Estate!%253D6%255Esys_class_name!%253Dsysapproval_group%255Eassigned_toISNOTEMPTY%255Eassignment_group%253D01d2b1e36f3a420021590f1aea3ee4bd%255Ecmdb_ci.nameLIKEDIM7YJN3J4%26sysparm_first_row%3D1%26sysparm_view%3D
    # document.querySelector("#row_task_4ebc0a473be5c710eb520931a3e45a84 > td:nth-child(3) > a")

    detail_lines = []

    if dwo_label.new_device:
        detail_lines.append(f"New: {dwo_label.new_device}")

    if dwo_label.old_device:
        detail_lines.append(f"Old: {dwo_label.old_device}" + r"\5C&")

    if dwo_label.recipient:
        detail_lines.append(f"Recipient: {dwo_label.recipient}")

    if dwo_label.location_room:
        detail_lines.append(f"{dwo_label.location_room}")

    if dwo_label.department:
        detail_lines.append(f"Department: {dwo_label.department}")

    details = r"\5C&".join(detail_lines)

    dwo_label_str = dedent(rf"""
    ^XA
    ~TA000
    ~JSN
    ^LT0
    ^MNW
    ^MTT
    ^PON
    ^PMN
    ^LH0,0
    ^JMA
    ^PR6,6
    ~SD25
    ^JUS
    ^LRN
    ^CI27
    ^PA0,1,1,0
    ^XZ

    ^XA
    ^MMT
    ^PW406
    ^LL812
    ^LS0

    ^FT10,819
    ^BQN,2,5
    ^FH\
    ^FDLA,{dwo_label.task_url}
    ^FS

    ^FT206,645
    ^ASN
    ^FH\
    ^CI28
    ^FD{dwo_label.task}
    ^FS
    ^CI27

    ^FO0,10
    ^AUN
    ^FB406,2,5,C
    ^FH\
    ^CI28
    ^FD{dwo_label.assigned_tech}
    ^FS
    ^CI27

    ^FO10,130
    ^ARN
    ^FB386,11,12,L,0
    ^FH\
    ^CI28
    ^FD{details}
    ^FS
    ^CI27

    ^PQ1,0,1,Y
    ^XZ
    """).strip()
    send_zpl_to_network_printer("CSCDGJ244902154", dwo_label_str)
    # send_zpl_to_printer(f"ZDesigner TLP 2824", f"^XA^FO40,40^BQM,6,2^FDQA,https://partnershealthcare.service-now.com/now/nav/ui/classic/params/target/sc_task.do%3Fsys_id%3D{task}^FS^XZ")
    # ^FDQA,https://partnershealthcare.service-now.com/now/nav/ui/classic/params/target/sc_task.do%3Fsys_id%3D{task}%26sysparm_view%3DDWO_view^FS


def send_zpl_to_network_printer(printer_hostname: str, zpl_data: str):
    """
    Sends raw ZPL commands to a Zebra printer over the network.

    :param printer_hostname: The hostname or IP address of the Zebra printer
    :param zpl_data: The ZPL command string to send
    """
    import socket

    try:
        # Create a socket connection to the printer
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(
                (printer_hostname, 9100)
            )  # Port 9100 is standard for Zebra printers
            s.sendall(zpl_data.encode("utf-8"))
        print(f"Printing label to network printer at '{printer_hostname}'.")
    except Exception as e:
        print(f"Failed to send ZPL to network printer: {e}")


def send_zpl_to_local_printer(printer_name: str, zpl_data: str):
    """
    Sends raw ZPL commands to a Zebra printer via Windows spooler.

    :param printer_name: The exact name of the printer as shown in Control Panel > Devices and Printers
    :param zpl_data: The ZPL command string to send
    """
    try:
        # Open printer
        hPrinter = win32print.OpenPrinter(printer_name)
        try:
            # Start a print job
            hJob = win32print.StartDocPrinter(hPrinter, 1, ("ZPL Label", None, "RAW"))
            win32print.StartPagePrinter(hPrinter)

            # Send the ZPL data
            win32print.WritePrinter(hPrinter, zpl_data.encode("utf-8"))

            # End the page and job
            win32print.EndPagePrinter(hPrinter)
            win32print.EndDocPrinter(hPrinter)
        finally:
            win32print.ClosePrinter(hPrinter)

        print(f"Printing label to '{printer_name}'.")

    except Exception as e:
        print(f"Failed to send ZPL: {e}")
        # sys.exit(1)


# def change_hostname():
#     send_zpl_to_network_printer("10.15.8.28", "! U1 setvar \"ip.hostname\" \"CSCD9N262504416\"\n")
if __name__ == "__main__":
    # change_hostname()
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting...")
