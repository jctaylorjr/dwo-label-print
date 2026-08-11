import win32print
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        # Channel can be "chrome", "msedge", "chrome-beta", "msedge-beta" or "msedge-dev".
        # browser = p.chromium.launch(channel="msedge", headless=False)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        device = input("Enter device name (or nothing to quit): ")
        while device:
            try:
                # https://partnershealthcare.service-now.com/now/nav/ui/classic/params/target/task_list.do%3Fsysparm_query%3Dactive%253Dtrue%255Estate!%253D6%255Esys_class_name!%253Dsysapproval_group%255Eassigned_toISNOTEMPTY%255Eassignment_group%253D01d2b1e36f3a420021590f1aea3ee4bd%255Ecmdb_ci.nameLIKEDIM7YJN3J4%26sysparm_first_row%3D1%26sysparm_view%3D

                # doesn't work if the configuration item isnt set
                # page.goto(f"https://partnershealthcare.service-now.com/now/nav/ui/classic/params/target/task_list.do%3Fsysparm_query%3Dactive%253Dtrue%255Estate!%253D6%255Esys_class_name!%253Dsysapproval_group%255Eassigned_toISNOTEMPTY%255Eassignment_group%253D01d2b1e36f3a420021590f1aea3ee4bd%255Ecmdb_ci.nameLIKE{device}%26sysparm_first_row%3D1%26sysparm_view%3D")

                page.goto(f"https://partnershealthcare.service-now.com/now/nav/ui/classic/params/target/task_list.do%3Fsysparm_query%3Dactive%253Dtrue%255Estate!%253D6%255Esys_class_name!%253Dsysapproval_group%255Eassigned_toISNOTEMPTY%255Eassignment_group%253D01d2b1e36f3a420021590f1aea3ee4bd%255EdescriptionLIKE{device}%255EORcmdb_ciLIKE{device}%26sysparm_first_row%3D1%26sysparm_view%3D")
                # document.querySelector("#row_task_4ebc0a473be5c710eb520931a3e45a84 > td:nth-child(3) > a")
                # task_url = page.locator('iframe[name="gsft_main"]').content_frame.locator("#task_table > tbody > tr:first-child > td:nth-child(3) > a").get_attribute("href")
                task_id = page.locator('iframe[name="gsft_main"]').content_frame.locator("#task_table > tbody > tr:first-child").get_attribute("sys_id")
                # https://partnershealthcare.service-now.com/nav_to.do?uri=task.do?sys_id=4ebc0a473be5c710eb520931a3e45a84
                print(f"Task ID: {task_id}")
                task_url = f"https://partnershealthcare.service-now.com/nav_to.do?uri=task.do?sys_id={task_id}"
                # page.goto(task_url)
                print_url = f"https://partnershealthcare.service-now.com/WOMassPrint?sysparm_taskids={task_id}"
                page.goto(print_url, wait_until="networkidle")
                page.keyboard.press("Escape")
                #sys_display\.ni\.VEc7acc68feb650b107ed8fb989dc0cd85
                # New: body > table > tbody > tr:nth-child(12) > td:nth-child(2)
                # Old: body > table > tbody > tr:nth-child(13) > td:nth-child(2)
                # Assigned to body > table > tbody > tr:nth-child(6) > td:nth-child(4)
                task = page.locator("body > table > tbody > tr:nth-child(2) > td:nth-child(2)").inner_text().upper()
                new = page.locator("body > table > tbody > tr:nth-child(12) > td:nth-child(2)").inner_text().upper()
                old = page.locator("body > table > tbody > tr:nth-child(13) > td:nth-child(2)").inner_text().upper()
                assigned_to = page.locator("body > table > tbody > tr:nth-child(6) > td:nth-child(4)").inner_text()
                recipient = page.locator("body > table > tbody > tr:nth-child(8) > td:nth-child(2)").inner_text()
                location_room = f"{page.locator("body > table > tbody > tr:nth-child(9) > td:nth-child(2)").inner_text()}/{page.locator("body > table > tbody > tr:nth-child(9) > td:nth-child(4)").inner_text()}"
                print(f"New: {new}")
                print(f"Old: {old}")
                print(f"Assigned to: {assigned_to}")
                print(f"Recipient: {recipient}")
                print(f"Location/Room: {location_room}")
                print_dwo_label(task_url, task, new, old, assigned_to, recipient, location_room)
                # page.pause()

            except Exception as e:
                print(f"An error occurred: {e}")
            device = input("Enter device name (or nothing to quit): ")

def print_dwo_label(url, task, new_device, old_device, assigned_to, recipient, location_room):
    # URL to filter for the device and grab task url
    # https://partnershealthcare.service-now.com/now/nav/ui/classic/params/target/task_list.do%3Fsysparm_query%3Dactive%253Dtrue%255Estate!%253D6%255Esys_class_name!%253Dsysapproval_group%255Eassigned_toISNOTEMPTY%255Eassignment_group%253D01d2b1e36f3a420021590f1aea3ee4bd%255Ecmdb_ci.nameLIKEDIM7YJN3J4%26sysparm_first_row%3D1%26sysparm_view%3D
    # document.querySelector("#row_task_4ebc0a473be5c710eb520931a3e45a84 > td:nth-child(3) > a")

    # asset_tag = input("Enter the asset tag: ")
    # serial_number = input("Enter the serial number: ")
    # send_zpl_to_printer(f"ZDesigner TLP 2824", "~JC^XA^FO40,40^BAN,40,Y,Y,N,N^FD>:{P6116632}^FS^FO40,130^BAN,40,Y,Y,N,N^FD>:{7NQJDC4}^FS^XZ")
    # send_zpl_to_printer(f"ZDesigner TLP 2824", "^XA^FO50,50^BXN,6,200,18,18^FD1jt1280@partners.org^FS^XZ")
    dwo_label = f"""
                ^XA
                ^FO20,10
                ^ADN,37,20
                ^FD{assigned_to}^FS
                ^FO20,40
                ^BQN,2,2
                ^FDQA,{url}^FS
                ^FO140,50
                ^ADN,15,12
                ^FD{task}^FS
                ^FO140,70
                ^ADN,15,12
                ^FDNew:^FS
                ^FO140,90
                ^ADN,15,12
                ^FD{new_device}^FS
                ^FO140,110
                ^ADN,15,12
                ^FDOld:^FS
                ^FO140,130
                ^ADN,15,12
                ^FD{old_device}^FS
                ^FO140,150
                ^ADN,15,12
                ^FD{recipient}^FS
                ^FO20,170
                ^ADN,15,12
                ^TBN,400,40
                ^FD{location_room}^FS
                ^XZ
                """
    # send_zpl_to_local_printer(f"ZDesigner TLP 2824", dwo_label)
    send_zpl_to_network_printer("CSCDGJ244902154", dwo_label)
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
            s.connect((printer_hostname, 9100))  # Port 9100 is standard for Zebra printers
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

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting...")
