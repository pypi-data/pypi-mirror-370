import json
from datetime import datetime
from pprint import pprint
from bson import ObjectId

from pollenisatorgui.core.components.apiclient import APIClient
from pollenisatorgui.pollenisator import consoleConnect


def nucleiresults(apiclient):
    tags_data = apiclient.findInDb(apiclient.getCurrentPentest(), "tags", { "tags.name": "used-nuclei" }, multi=True)
    ip_ids = []
    if tags_data is not None:
        for tag in tags_data:
            if tag.get("item_type","") == "ips":
                ip_ids.append(tag.get("item_id",""))
    if not ip_ids:  # No IPs tagged with "used-nuclei"
        return []
    list_of_ips = apiclient.findInDb(apiclient.getCurrentPentest(), "ips", { "_id": { "$in": ip_ids } }, multi=True)
    if list_of_ips is None:
        return []
    headerVulnerabilities = []
    for ip in list_of_ips:
        ip_infos = ip.get("infos", {})
        if ip_infos.get("plugin", "").lower() not in ["nuclei", "nuclei.py"]:
            continue
        for finding in ip_infos.get("findings", {}):
            if finding["template-id"] == "http-missing-security-headers":
                headerVulnerabilities.append({
                    "ip": finding.get("ip", ""),
                    "port": finding.get("port", ""),
                    "host": finding.get("host", ""),
                    "header": finding.get("matcher-name", "")
                })
    let ip_objects = ips.data;
    
    return {"vulnTable": vulnDataList, "allDataForExcel": completeData, "newTLSDefectForReport": newTLSDefect}

def updateTLSDefect(defectTLS, new_defect, defect_to_keep, fixes_to_keep):
    defectTLS_description = defectTLS[0]["description"]
    if new_defect.get("description", "") == "":
        new_defect["description"] = defectTLS_description.split("\r\n\r\n")[0] + "\r\n\r\n"
    lignes = defectTLS_description.split("\r\n\r\n")
    title = ""
    for ligne in lignes:
        if ligne.startswith("#"):
            title = ligne.strip("#").strip()
            if title == defect_to_keep:
                new_defect["description"] += ligne + "\r\n\r\n"
                continue
        if title == defect_to_keep:
            new_defect["description"] += ligne + "\r\n\r\n"
            continue
    fixes_to_keep = fixes_to_keep.split(",")
    defectTLS_fixes = defectTLS[0]["fixes"]
    for fix in defectTLS_fixes:
        if str(fix["id"]) in fixes_to_keep and not fix in new_defect["fixes"]:
            new_defect["fixes"].append(fix)
    return new_defect
    
def generateDefect(apiclient, newTLSDefect):
    # Function to generate a defect in the report
    # This function should be implemented to handle the defect creation logic
    print("Generating defect with data:", newTLSDefect)
    defectTLS = apiclient.searchDefect("Défauts d'implémentation du TLS")[0]
    new_TLS_defect = {}
    new_TLS_defect["description"] = ""
    new_TLS_defect["fixes"] = []
    for d in newTLSDefect:
        new_TLS_defect = updateTLSDefect(defectTLS, new_TLS_defect, d[0], d[1])
    defectTLS[0]["description"] = new_TLS_defect["description"]
    defectTLS[0]["fixes"] = new_TLS_defect["fixes"]
    new_defect = defectTLS[0]
    all_defects = apiclient.getDefectTable()
    for d in all_defects:
        if d["title"] == new_defect["title"]:
            print("Defect already exists, updating it.")
            if "_id" in new_defect:
                del new_defect["_id"]
            apiclient.updateInDb(apiclient.getCurrentPentest(), "defects", {"_id":ObjectId(d["_id"])}, {"$set": new_defect})
            return {"status": "success", "data": new_defect}
    apiclient.insertInDb(apiclient.getCurrentPentest(), "defects", new_defect)
    return {"status": "success", "data": new_defect}


def main(apiclient, *args, **kwargs):
    # Example usage of the parseTestSSL function
    results = nucleiresults(apiclient)
    
apiclient = APIClient.getInstance()  # Assuming APIClient is defined elsewhere
apiclient.tryConnection()
res = apiclient.tryAuth()
if not res:
    consoleConnect()
if apiclient.isConnected() is False or apiclient.getCurrentPentest() == "":
    print("You must be connected to a pentest to run this script.")

main(apiclient)
