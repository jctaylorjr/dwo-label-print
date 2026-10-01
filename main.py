import win32print
from playwright.sync_api import sync_playwright
from textwrap import dedent

class DWO_Label:
    def __init__(self, task_url, task, new_device, new_asset, old_device, old_asset, assigned_tech, recipient, location_room, department):
        self.task_url = task_url
        self.task = task
        self.new_device = new_device
        self.new_asset = new_asset
        self.old_device = old_device
        self.old_asset = old_asset
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

                page.goto(f"https://partnershealthcare.service-now.com/now/nav/ui/classic/params/target/task_list.do%3Fsysparm_query%3Dactive%253Dtrue%255Estate!%253D6%255Esys_class_name!%253Dsysapproval_group%255Eassigned_toISNOTEMPTY%255Eassignment_group%253D01d2b1e36f3a420021590f1aea3ee4bd%255EdescriptionLIKE{device}%255EORcmdb_ciLIKE{device}%26sysparm_first_row%3D1%26sysparm_view%3D", wait_until="networkidle")
                # page.goto(f"https://partnershealthcare.service-now.com/now/nav/ui/classic/params/target/task_list.do%3Fsysparm_query%3Dactive%253Dtrue%255Estate!%253D6%255Esys_class_name!%253Dsysapproval_group%255Eassignment_group%253D01d2b1e36f3a420021590f1aea3ee4bd%255EdescriptionLIKE{device}%255EORcmdb_ciLIKE{device}%26sysparm_first_row%3D1%26sysparm_view%3D", wait_until="networkidle")
                page.locator('iframe[name="gsft_main"]').content_frame.locator("#task_table > tbody > tr:first-child").wait_for(timeout=5000)

                # if page.locator('iframe[name="gsft_main"]').content_frame.locator("#task > div.list2_empty-state-list").():
                #     print(f"No tasks found for device '{device}'.")
                #     device = input("Enter device name (or nothing to quit): ")
                #     continue

                task_id = page.locator('iframe[name="gsft_main"]').content_frame.locator("#task_table > tbody > tr:first-child").get_attribute("sys_id")
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
                #sys_display\.ni\.VEc7acc68feb650b107ed8fb989dc0cd85
                # New: body > table > tbody > tr:nth-child(12) > td:nth-child(2)
                # Old: body > table > tbody > tr:nth-child(13) > td:nth-child(2)
                # Assigned to body > table > tbody > tr:nth-child(6) > td:nth-child(4)
                task = page.locator("body > table > tbody > tr:nth-child(2) > td:nth-child(2)").inner_text().upper()
                try:
                    new, new_asset = tuple(page.locator("body > table > tbody > tr:nth-child(12) > td:nth-child(2)").inner_text().upper().split(" "))
                    new_asset = new_asset.replace("(", "").replace(")", "")
                except ValueError:
                    new, new_asset = None, None
                try:
                    old, old_asset = tuple(page.locator("body > table > tbody > tr:nth-child(13) > td:nth-child(2)").inner_text().upper().split(" "))
                    old_asset = old_asset.replace("(", "").replace(")", "")
                except ValueError:
                    old, old_asset = None, None
                try:
                    assigned_tech = page.locator("body > table > tbody > tr:nth-child(6) > td:nth-child(4)").inner_text()
                    if assigned_tech:
                        assigned_tech = assigned_tech.split(" ")
                        if len(assigned_tech) > 1:
                            for s in assigned_tech:
                                if "(" in s:
                                    assigned_tech.remove(s)
                        assigned_tech = " ".join(assigned_tech)
                except Exception as e:
                    assigned_tech = None
                recipient = page.locator("body > table > tbody > tr:nth-child(8) > td:nth-child(2)").inner_text()
                location_room = f"{page.locator("body > table > tbody > tr:nth-child(9) > td:nth-child(2)").inner_text()}/{page.locator("body > table > tbody > tr:nth-child(9) > td:nth-child(4)").inner_text()}"
                department = page.locator("body > table > tbody > tr:nth-child(10) > td:nth-child(2)").inner_text()
                print(f"New: {new}")
                print(f"New Asset: {new_asset}")
                print(f"Old: {old}")
                print(f"Old Asset: {old_asset}")
                print(f"Assigned to: {assigned_tech}")
                print(f"Recipient: {recipient}")
                print(f"Location/Room: {location_room}")
                print(f"Department: {department}")
                dwo_label = DWO_Label(task_url, task, new, new_asset, old, old_asset, assigned_tech, recipient, location_room, department)
                print_dwo_label(dwo_label)
                # page.pause()

            except Exception as e:
                print(f"An error occurred: {e}")
            device = input("Enter device name (or nothing to quit): ")

def print_dwo_label(dwo_label: DWO_Label):
    new_device_section = ""
    if dwo_label.new_device and dwo_label.new_asset:
        new_device_section = dedent(f"""
        ^FO0,96^GFA,01536,01536,00016,:Z64:
        eJxjYBh84D8UPIBw5WH8/w1gvj2cfwBF+f//H0BcRqgyBgb+H2D+D5i5EBbzA7hFNSCC/QCcb4eV3wDny2Hj86PzGUb5o/yRy2dH5zcQ4B+A87HmP/T8ip6fGRH5HyKDVh5glBfo5cmIBgASd2m/:65D4
        ^FT185,136^A0N,37,36^FH\\^FD{dwo_label.new_device}^FS
        ^FT117,181^BQN,2,3
        ^FH\\^FDLA,{dwo_label.new_device}^FS
        ^FT185,174^A0N,37,36^FH\\^FD{dwo_label.new_asset}^FS
        ^FT25,159^A0N,42,45^FH\\^FDNew^FS
        """).strip()

    old_device_section = ""
    if dwo_label.old_device and dwo_label.old_asset:
        old_device_section = dedent(f"""
        ^FO0,192^GFA,02048,02048,00016,:Z64:
        eJxjYBgFQw38h4IHEK48jP+/Acy3h/MPoCj///8DiMsIVcbAwP8DzP8BMxfCYn4At6gGRLAfgPPtsPIb4Hw5bHx+dD7DKH+UP3L57Oj8BgL8A3A+1vyHnl/R8zMjIv9DZNDKA4zyAr08GQXDGAAAoBtpvw==:8851
        ^FT185,250^A0N,37,36^FH\\^FD{dwo_label.old_device}^FS
        ^FT117,295^BQN,2,3
        ^FH\\^FDLA,{dwo_label.old_device}^FS
        ^FT33,273^A0N,42,45^FH\\^FDOld^FS
        ^FT185,288^A0N,37,36^FH\\^FD{dwo_label.old_asset}^FS
        """).strip()

    label2 = dedent(f"""
        CT~~CD,~CC^~CT~
        ^XA~TA000~JSN^LT0^MNW^MTT^PON^PMN^LH0,0^JMA^PR4,4~SD15^JUS^LRN^CI0^XZ
        ^XA
        ^MMT
        ^PW406
        ^LL0812
        ^LS0
        ^FO32,544^GFA,00256,00256,00008,:Z64:
        eJxjYEAH//+DKfb//x+AaP7//3+AaPkGhhoQbcPAIAeiLRgY+JDpCihdMEC0AZp7YLQMAwMP2P3///9B9g/UfwAX9xvH:EAF1
        ^FO160,544^GFA,00256,00256,00008,:Z64:
        eJxjYEAH9v8PgCjG//9/gGjm////gWj2BwzyIJofyGwA0nxAKWRaDkrLDBDNg+YeGM0OpMHu////P7J/oP4DAKhaH1o=:C753
        ^FO256,480^GFA,00512,00512,00008,:Z64:
        eJxjYBjqgPH/PzDN////ARAt////BxBtz8DwA0RXMDDYgOgCBgYZZPoDlH4wQHQCmntgtAUDgwTY/f///0D2D8x/1AUAaFslnw==:CDC0
        ^FO256,544^GFA,00256,00256,00008,:Z64:
        eJxjYMAA//+DKfb//x+AaP7//3+AaPkGhhoQbcPAIAeiLRgY+JDpCihdMEC0AZp7YLQMAwMP2P3///9B9g/EfwD8IhvH:FAAF
        ^FO32,480^GFA,00512,00512,00008,:Z64:
        eJxjYBjqoP5/A4hi/v//A4hm////D4jmP8BgB6LlgEwQLQOUQqZtoLTFANESaO6B0XwMDGxg9////w/ZPzD/URkAAOL7Fts=:732A
        ^FO160,480^GFA,00512,00512,00008,:Z64:
        eJxjYBjqoP5/A4hi/v//A4hm////D4jmP8BgB6LlgEwQLQOUQqZtoLTFANESaO6B0XwMDGxg9////w/ZPzD/URkAAOL7Fts=:732A
        ^FO0,320^GFA,00512,00512,00016,:Z64:
        eJzN0LEKwjAQBuADwUm41enyCo4OpX2tCEIrCo63dvJJukiHjn0Fiy/QzQ4h8XK2Fbq6eEOSD8L9lwD8Za0BduNx5WVBACvbJjp8naiL+b66KeY2H596w2RtivtQRp9dxuRszsdQidtrlbNx9sVeHZAGNunh2d6SbcxH6pFITNrPo1eH0e3CDYL6gaP5ov16Ju1XN07zAlMW8+pa5jGDzEMm+t4NRiJthoTl9BJafNCvnuoNr4BTeA==:B779
        ^FO0,96^GFA,01536,01536,00016,:Z64:
        eJxjYBh84D8UPIBw5WH8/w1gvj2cfwBF+f//H0BcRqgyBgb+H2D+D5i5EBbzA7hFNSCC/QCcb4eV3wDny2Hj86PzGUb5o/yRy2dH5zcQ4B+A87HmP/T8ip6fGRH5HyKDVh5glBfo5cmIBgASd2m/:65D4
        ^FO0,192^GFA,02048,02048,00016,:Z64:
        eJxjYBgFQw38h4IHEK48jP+/Acy3h/MPoCj///8DiMsIVcbAwP8DzP8BMxfCYn4At6gGRLAfgPPtsPIb4Hw5bHx+dD7DKH+UP3L57Oj8BgL8A3A+1vyHnl/R8zMjIv9DZNDKA4zyAr08GQXDGAAAoBtpvw==:8851
        ^FO224,608^GFA,04608,04608,00024,:Z64:
        eJztlztOw0AQhtexrCAaVxGlD0DBDYiPQIFFmStQEFEhu8wxItEgOIILfAQKWqSUKVNQRE7iZXfjmJnxTIHkIiKeKMnm06/xPLzriVK9nbhd89jTPA/1muWp3nHY11ovGB4ZvmK4tpa1cOD4R4uPHa8o9lLHWymEe9xKYVJzkoINXj/bjzniF4ZsVdpKwSqX7iIVTMGzPN5/FYBfmd9lnQSMKK11Q3cZ5H7vl9TI/Pp2iwin3MTtU37wOiF8Wa9C4h9kAvVlsxwj/pskuotgUaB/WMQIrOdg7avuTUP7K8868nME/o/NklvlJTdqlMQqSQA3+9yePpE5UHB9KrNVVoYXZutgvV/rKZf0Q9b/tjP/xxq/7uPvxP/Jxl9RP7V+i3kT/1rQrzBv/M95/ZOifK9HD3gQf0z0B//o+fL4oILpvRpNY8xnM3Xm3qY2YaZYi3g8EKapocDf+fM5ICPN4C3PN5s814Tfsee/GziY8/8wLVF9CDDsbwQ4mU8aWwu8EHjGczRfAf5C+O7LWawwfx0o+7KVghzMkR7gcD6B/ZXmkwX0qVgT+nsuPH8npI+XfB8Dvl9SQaEc6sdCf+HtgPYjsKXAY56jCV2QA15mmH8iXcNLjoq9UK2/CbUVAs8E3ltv/8R+ADBAwUY=:9033
        ^FT81,64^A0N,48,48^FH\^FD{dwo_label.assigned_tech}^FS
        ^FT14,808^BQN,2,5
        ^FH\^FDLA,{dwo_label.task_url}^FS
        ^FT209,608^A0R,33,33^FH\^FD{dwo_label.task}^FS
        ^FT76,568^A0N,18,16^FH\^FDPrinters^FS
        ^FT205,568^A0N,18,16^FH\^FDLWS^FS
        ^FT307,526^A0N,18,16^FH\^FDPortal^FS
        ^FT307,568^A0N,18,16^FH\^FDWLAN^FS
        ^FT76,526^A0N,18,16^FH\^FDWindows^FS
        ^FT205,526^A0N,18,16^FH\^FDDell^FS
        ^FO20,82^GB365,0,2^FS
        ^FO20,194^GB365,0,2^FS
        ^FO20,310^GB365,0,2^FS
        ^FT20,375^A@N,23,22,TT0003M_^FH\^CI17^F8^FD{dwo_label.recipient}^FS^CI0
        ^FT20,411^A0N,23,24^FH\^FDLocation:^FS
        ^FO20,439^A@N,23,22,TT0003M_^FB370,2,5,L,0\^CI17^F8^FD{dwo_label.location_room}^FS^CI0
        ^FO20,588^GB365,0,2^FS
        ^FT185,136^A0N,37,36^FH\^FD{dwo_label.new_device}^FS
        ^FT117,181^BQN,2,3
        ^FH\^FDLA,{dwo_label.new_device}^FS
        ^FT185,174^A0N,37,36^FH\^FD{dwo_label.new_asset}^FS
        ^FT25,159^A0N,42,45^FH\^FDNew^FS
        ^FT185,250^A0N,37,36^FH\^FD{dwo_label.old_device}^FS
        ^FT117,295^BQN,2,3
        ^FH\^FDLA,{dwo_label.old_device}^FS
        ^FT33,273^A0N,42,45^FH\^FDOld^FS
        ^FT185,288^A0N,37,36^FH\^FD{dwo_label.old_asset}^FS
        ^PQ1,0,1,Y^XZ
        """).strip()
    send_zpl_to_network_printer("DFJ240906078", label2)

def print_dwo_label_old(dwo_label: DWO_Label):
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
    send_zpl_to_network_printer("DFJ240906078", dwo_label_str)
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

# def change_hostname():
#     send_zpl_to_network_printer("10.15.8.28", "! U1 setvar \"ip.hostname\" \"CSCD9N262504416\"\n")
if __name__ == "__main__":
    # change_hostname()
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting...")


