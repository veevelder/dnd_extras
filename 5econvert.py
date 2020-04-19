import json
import string
import random
import os
import re
import string
import argparse
import urllib.request
import math
import inflect

area_lookup = {}

def gen_id():
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))

f_sort = 100000
j_sort = 100000
journals = []
spells = []
items = []
actors = []
maps = []
default_folders = {"PC": gen_id(),"NPC": gen_id()}
folders = []

def download_image(url, output):
    req = urllib.request.Request(
        url,
        data = None,
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        }
    )
    image = urllib.request.urlopen(req)
    with open(output, "wb") as f:
        f.write(image.read())

def find_in_db(db_file, find_name):
    find_name = string.capwords(find_name).strip()
    find_name_no_paren = None
    found_id = ""
    
    if "(" in find_name and ")" in find_name:
        find_name_no_paren = re.sub("[\(\[].*?[\)\]]", "", find_name).strip().lower().translate(str.maketrans('', '', string.punctuation)).replace("’", "")
    
    tmp_find_name = find_name.lower().translate(str.maketrans('', '', string.punctuation)).replace("’", "")
        
    with open(db_file, "rb") as f:
        found = False
        for line in f:
            f_item = json.loads(line)
            tmp_db_name = f_item["name"].lower().translate(str.maketrans('', '', string.punctuation)).replace("’", "")
            if tmp_db_name == tmp_find_name:
                found = True
                find_name = f_item["name"]
                found_id = f_item["_id"]
                break
            elif find_name_no_paren:
                if find_name_no_paren == tmp_db_name:
                    found = True
                    find_name = f_item["name"]
                    found_id = f_item["_id"]
                    break

    if not found:
        print("not found in compendium: {}, {}".format(find_name, db_file))

    return found_id, find_name

# @Compendium[dnd5e.spells._id]{name}

def fixup_text(old_str):
    # any actor or item look up, normalize to lowercase and then use the name from the compendium if it exists
    
    global area_lookup, spells, items, actors
    new_str = old_str
    for found_str in re.findall(r"{@.*?}", old_str):
        if found_str.startswith("{@i "):
            new_str = new_str.replace(found_str, "<em>" + found_str[4:-1] + "</em>")
        elif found_str.startswith("{@b "):
            new_str = new_str.replace(found_str, "<strong>" + found_str[4:-1] + "</strong>")
        elif found_str.startswith("{@book "):
            tmp_str = found_str[7:-1].split("|")
            # name = 0
            # book abbreviasion = 1
            # chapter = 2
            # section = 3
            # possbily create a journal entry for each book that then will make this link work
            # but for now just return the name
            new_str = new_str.replace(found_str, "@JournalEntry[" + string.capwords(tmp_str[0]) + "]")
        elif found_str.startswith("{@adventure "):
            # link to journal entry
            new_str = new_str.replace(found_str, "@JournalEntry[" + found_str[12:-1].split("|")[0] + "]")
        elif found_str.startswith("{@area "):
            # look up chapter heading if it exists
            tmp_str = found_str[7:-1].split("|")
            if tmp_str[1] in area_lookup.keys():
                new_str = new_str.replace(found_str, "@JournalEntry[" + area_lookup[tmp_str[1]] + "]")
        elif found_str.startswith("{@creature "):
            monster_id, monster = find_in_db(monsters_db, string.capwords(found_str[11:-1].split("|")[0]))
            new_str = new_str.replace(found_str, "@Compendium[dnd5e.monsters." + monster_id + "]{" + monster + "}")
        elif found_str.startswith("{@spell "):
            spell_id, spell_name = find_in_db(spells_db, found_str[8:-1].split("|")[0])
            new_str = new_str.replace(found_str, "@Compendium[dnd5e.spells." + spell_id + "]{" + spell_name + "}")
        elif found_str.startswith("{@skill "):
            # need to add another lookup compendium
            # add it to the game somehow
            new_str = new_str.replace(found_str, found_str[8:-1])
        elif found_str.startswith("{@item "):
            item_name = found_str[7:-1].split("|")[0]
            if "spell scroll" in found_str.lower():
                item_name = item_name.replace("(", "").replace(")", "")
            #elif "(" in item_name and ")" in item_name:
            #    item_name = re.sub("[\(\[].*?[\)\]]", "", item_name).strip()
            item_id, item_name = find_in_db(items_db, item_name)
            new_str = new_str.replace(found_str, "@Compendium[dnd5e.items." + item_id + "]{" + item_name + "}")
        elif found_str.startswith("{@condition "):
            # need to add another lookup compendium
            # need to add it to the game somehow
            new_str = new_str.replace(found_str, found_str[11:-1].split("|")[0])
        elif found_str.startswith("{@dice "):
            new_str = new_str.replace(found_str, found_str[7:-1].split("|")[0])
        elif found_str.startswith("{@race "):
            # need to add another lookup compendium make another actor compendium for races
            # need to add it to the game somehow
            new_str = new_str.replace(found_str, found_str[7:-1].split("|")[0])
        elif found_str.startswith("{@filter "):
            new_str = new_str.replace(found_str, found_str[9:-1].split("|")[0])
        elif found_str.startswith("{@object "):
            monster_id, monster = find_in_db(monsters_db, string.capwords(found_str[9:-1].split("|")[0]))
            new_str = new_str.replace(found_str, "@Compendium[dnd5e.monsters." + monster_id + "]{" + monster + "}")
        elif found_str.startswith("{@action "):
            # would like to make this a link to something
            new_str = new_str.replace(found_str, found_str[9:-1])
        elif found_str.startswith("{@class "):
            class_id, class_name = find_in_db(class_db, string.capwords(found_str[8:-1]))
            new_str = new_str.replace(found_str, "@Compendium[dnd5e.classes." + class_id + "]{" + class_name + "}")
        elif found_str.startswith("{@5etools "):
            new_str = new_str.replace(found_str, found_str[10:-1].split("|")[0])
        elif found_str.startswith("{@disease "):
            new_str = new_str.replace(found_str, "@JournalEntry[" + found_str[10:-1].split("|")[0] + "]")
        elif found_str.startswith("{@hazard "):
            new_str = new_str.replace(found_str, "@JournalEntry[" + found_str[9:-1].split("|")[0] + "]")
        else:
            print(found_str)

    return new_str

def parse_data(data, par_id = None, make_j = True, is_book = False):
    global f_sort, j_sort, folders, journals, area_lookup, maps
    content = ""
    for items in data:
        f_sort += 1
        j_sort += 1
        if type(items) == str:
            content += "\n<p>" + fixup_text(items) + "</p>";
        elif items["type"] == "insetReadaloud":
            content += "\n<blockquote>" + parse_data(items["entries"], is_book = is_book) + "</blockquote>"
        elif items["type"] == "image":
            # add alt text if name
            title = ""
            if "title" in items.keys():
                title = items["title"]
            # if title looks like to have some mapping info
            if "maps" in title.lower() or "players" in title.lower():
                add = True
                for m in maps:
                    if m["name"] == title:
                        add = False
                        break
                if add:
                    maps.append({"name": title, "img": items["href"]["path"]})
            # it title name has DM, Maps, Players in the name then add it to the list of possible maps to create
            content += "\n<p><img src=\"https://5e.tools/img/" + items["href"]["path"] + "\" alt=\"" + title + "\" width=\"" + str(items["width"]) + "\" height=\"" + str(items["height"]) + "\" />"
        elif items["type"] == "section":
            if not is_book:
                area_lookup[items["id"]] = items["name"]
            # if folder is titled maps then dont create it instead get all images and add them to possible maps to create
            folder = {
                "_id": gen_id(),
                "name": items["name"],
                "type": "JournalEntry",
                "sort": f_sort,
                "flags": {},
                "parent": par_id,
                "color": ""}
            folders.append(folder)
            journal = {
                "_id": gen_id(),
                "name": items["name"],
                "permission": {"default": 0},
                "folder": folder["_id"],
                "sort": j_sort,
                "flags": {},
                "content": ""
            }
            journal["content"] = parse_data(items["entries"], folder["_id"], True, is_book = is_book)
            journals.append(journal)
        elif items["type"] == "entries":
            if "name" in items.keys():
                if items["name"] == "Maps":
                    for entry in items["entries"]:
                        if type(entry) == dict:
                            if "DM" not in entry["title"]:
                                add = True
                                for m in maps:
                                    if m["name"] == entry["title"]:
                                        add = False
                                        break
                                if add:
                                    maps.append({"name": entry["title"], "img": entry["href"]["path"]})
                if make_j:
                    if not is_book:
                        area_lookup[items["id"]] = items["name"]
                    journal = {
                        "_id": gen_id(),
                        "name": items["name"],
                        "permission": {"default": 0},
                        "folder": par_id,
                        "sort": j_sort,
                        "flags": {},
                        "content": ""
                    }
                    journal["content"] = parse_data(items["entries"], par_id, False, is_book)
                    journals.append(journal)
                else:
                    content += "<h3>" + items["name"] + "</h3>\n" + parse_data(items["entries"], par_id, False, is_book)
            else:
               content += parse_data(items["entries"], par_id, False)
        elif items["type"] == "inset":
            if "name" in items.keys():
                content += "\n<section class=\"inset\">\n<h2>" + items["name"] + "</h2>\n" + parse_data(items["entries"], par_id, False, is_book) + "</section>"
            else:
                content += "\n<blockquote>" + parse_data(items["entries"], is_book = is_book) + "</blockquote>"
        elif items["type"] == "list":
            content += "<ul>\n"
            for item in items["items"]:
                if type(item) == str:
                    content += "<li>" + fixup_text(item) + "</li>\n"
                elif type(item) == dict:
                    content += "<li><strong>" + item["name"] + "</strong> " + item["entry"] + "</li>"
            content += "</ul>"
        elif items["type"] == "gallery":
            content += parse_data(items["images"], par_id, False, is_book)
        elif items["type"] == "table":
            # get alignments
            styles = []
            for style in items["colStyles"]:
                tmp_style = ""
                if "text-center" in style:
                    tmp_style += "text-align: center;"
                if "text-left" in style:
                    tmp_style += "text-align: left;"
                if "text-right" in style:
                    tmp_style += "text-align: right;"
                styles.append(tmp_style)
            if "caption" in items.keys():
                content += "<table bolder=\"1\"><caption>" + items["caption"] + "</caption>\n"
            else:
                content += "<table bolder=\"1\">\n"
            # create headers
            if "colLabels" in items.keys():
                content += "<thead>\n<tr>\n"
                for i, header in enumerate(items["colLabels"]):
                    if styles[i]:
                        content += "<td style=\"" + styles[i] + "\">"
                    else:
                        content += "<td>"
                    content += header + "</td>\n"
                content += "</thead>\n<tbody>\n";
            # create content
            for row in items["rows"]:
                content += "<tr>"
                if type(row) == list:
                    for i, cell in enumerate(row):
                        if styles[i]:
                            content += "<td style=\"" + styles[i] + "\">"
                        else:
                            content += "<td>"
                        if type(cell) == str:
                            content += fixup_text(cell) + "</td>";
                        elif type(cell) == int:
                            content += str(cell) + "</td>";
                        elif type(cell) == list:
                            for i in cell:
                                content += "<td>" + fixup_text(i) + "</td>"
                        elif type(cell) == dict:
                            if cell["type"] == "entries":
                                for i in cell["entries"]:
                                   content += "<tr><td>" + fixup_text(i) + "</td></tr>"
                            else:
                                print("table cell unknown type {}".format(cell))
                        else:
                            print("table unknown cell type for {}, {}".format(cell, row))
                elif type(row) == dict:
                    if row["type"] == "row":
                        style = ""
                        index = 0
                        if row["style"] == 'row-indent-first':
                            style = "    "
                            index = 0
                        for i, rw in enumerate(row["row"]):
                            content += "<td>"
                            if i == index:
                                content += style
                            content += fixup_text(rw) + "</td>"
                else:
                    print("table row unknown option for {}".format(row))
                content += "</tr>\n"
                       
            content += "</tbody>\n</table>\n"
        elif items["type"] == "quote":
            content += "<p>"
            for entry in items["entries"]:
                content += "<em>" + entry + "</em><br>\n"
            content += "<p style=\"text-align: right;\">- " + items["by"] + "</p>\n"
        elif items["type"] == "inlineBlock":
            content += parse_data(items["entries"], par_id, False, is_book)
        elif items["type"] == "link":
            # would ideally like to link to something here but not sure what
            content += items["text"]
        elif items["type"] == "tableGroup":
            content += "<h4>" + items["name"] + "</h4>\n" + parse_data(items["tables"], par_id, False, is_book)
        elif items["type"] == "inline":
            content += parse_data(items["entries"], par_id, False, is_book)
        elif items["type"] == "abilityGeneric":
            content += "<p style=\'text-align: center\'>" + items["text"] + "</p>";
        else:
            print(items, "\n")
    
    return content

def conv_stats(stat_list):
    stats = []
    for stat in stat_list:
        if stat == "str":
            stats.append("Strength")
        elif stat == "con":
            stats.append("Constitution")
        elif stat == "dex":
            stats.append("Dexterity")
        elif stat == "int":
            stats.append("Intelligence")
        elif stat == "wis":
            stats.append("Wisdom")
        elif stat == "cha":
            stats.append("Charisma")
        
    return ", ".join(stats)

def apped_list(item_list):
    items = []
    for item in item_list:
        items.append("@JournalEntry[" + string.capwords(item) + "]")
        
    return ", ".join(items)
    
def num_to_words(num):
    if num == 0:
        return "zero"
    if num == 1:
        return "one"
    if num == 2:
        return "two"
    if num == 3:
        return "three"
    if num == 4:
        return "four"

def format_entries(entries, newline = True):
    for entry in entries:
        if type(entry) == str:
            print("<p>" + fixup_text(entry) + "</p>")
        elif type(entry) == dict:
            if "name" in entry.keys():
                if newline:
                    print("<strong>" + entry["name"] + "</strong>")
                else:
                    print("<strong>" + entry["name"] + "</strong> ", end="")
            if "type" in entry.keys():
                if entry["type"] == "entries":
                    format_entries(entry["entries"], newline)
                elif entry["type"] == "list":
                    format_list(entry["items"])
                elif entry["type"] == "abilityDc":
                    format_dc(entry["name"], entry["attributes"])
                elif entry["type"] == "abilityAttackMod":
                    format_attk_dc(entry["name"], entry["attributes"])
                elif entry["type"] == "options":
                    format_entries(entry["entries"], False)
                elif entry["type"] == "table":
                    format_table(entry)
                elif entry["type"] == "inset":
                    print("<section class='inset'>")
                    format_entries(entry["entries"])
                    print("</section>")
                elif entry["type"] == "inlineBlock":
                    format_entries(entry["entries"])
                elif entry["type"] == "patron":
                    format_entries(entry["entries"])
                else:
                    print("UNKOWN!", entry)
            elif "entries" in entry.keys():
                format_entries(entry["entries"], newline)
            else:
                print("UNKOWN!", entry)

def format_list(items):
    print("<ul>")
    for item in items:
        if type(item) == str:
            print("<li>" + fixup_text(item) + "</li>")
        elif type(item) == dict:
            print("<li><strong>" + item["name"] + "</strong> " + fixup_text(item["entry"]) + "</li>") 
        else:
            print("UNKOWN!", item)
    print("</ul>")

def format_table(table):
    if "caption" in table.keys():
        print("<table border='1'><caption>" + table["caption"] + "</caption>")
    else:
        print("<table border='1'>")
    print("<tr>")
    for lable in table["colLabels"]:
        print("<td><strong>" + lable + "</strong></td>")
    print("</tr>")
    for row in table["rows"]:
        print("<tr>")
        for col in row:
            print("<td>" + fixup_text(str(col)) + "</td>")
        print("</tr>")
    print("</table>")
    print("<p>&nbsp;</p>")
    
def format_dc(name, attributes):
    print("<p style='text-align: center;'><strong>" + name + " save DC</strong> = 8 + your proficiency bonus + your " + conv_stats(attributes) + " modifier</p>")
    
def format_attk_dc(name, attributes):
    print("<p style='text-align: center;'><strong>" + name + " attack modifier</strong> = your proficiency bonus + your " + conv_stats(attributes) + " modifier</p>")

def parse_class(dnd_class):
    p = inflect.engine()
    print("Name:   " + dnd_class["name"])
    print("Source: " + dnd_class["source"] + " pg. " + str(dnd_class["page"]))
    
    for item in dnd_class["fluff"]:
        if item["source"] == "PHB":
            format_entries(item["entries"])
            print("<p>&nbsp;</p>")
    
    print("<h2>Class Features</h2>")
    print("<p>As a " + dnd_class["name"].lower() + ", you gain the following class features</p>")
    print("<h3><strong>Hit Points</strong><h3>")
    print("<p><strong>Hit Dice:</strong> " + str(dnd_class["hd"]["number"]) + "d" + str(dnd_class["hd"]["faces"]) + " per " + dnd_class["name"].lower() + " level</p>")
    print("<p><strong>Hit Points at 1st Level:</strong> " + str(dnd_class["hd"]["faces"]) + " your Constitution modifier</p>")
    print("<p><strong>Hit Points at Higher Levels:</strong> " + str(dnd_class["hd"]["number"]) + "d" + str(dnd_class["hd"]["faces"]) + " (or " + str(math.ceil((dnd_class["hd"]["number"] + dnd_class["hd"]["faces"])/ 2)) + ") + your Constitution modifier per " + dnd_class["name"].lower() + " level after 1st</p>")
    print("<p>&nbsp;</p>")
    print("<h3><strong>Proficiencies</strong></h3>")
    if "armor" in dnd_class["startingProficiencies"].keys():
        print("<p><strong>Armor:</strong> " + " armor, ".join(dnd_class["startingProficiencies"]["armor"]) + "</p>")
    else:
        print("<p><strong>Armor:</strong> None</p>")
    print("<p><strong>Weapons:</strong> " + " weapons, ".join(dnd_class["startingProficiencies"]["weapons"]) + " weapons</p>")
    print("<p><strong>Tools:</strong> " + ("None" if "tools" not in dnd_class["startingProficiencies"].keys() else ", ".join(dnd_class["startingProficiencies"]["weapons"])) + "</p>")
    print("<p><strong>Saving Throws:</strong> " + conv_stats(dnd_class["proficiency"]) + "</p>")
    print("<p><strong>Skills:</strong> Choose " + num_to_words(dnd_class["startingProficiencies"]["skills"][0]["choose"]["count"]) + " from " + apped_list(dnd_class["startingProficiencies"]["skills"][0]["choose"]["from"]) + "</p>")
    print("<p>&nbsp;</p>")
    print("<h3><strong>Equipment</strong></h3>")
    print("<p> You start with the following equipment, in addition to the equipment granted by your background:</p>")
    print("<ul>")
    for se in dnd_class["startingEquipment"]["default"]:
        print("<li>" + fixup_text(se) + "</li>")
    print("</ul>")
    print("<p>&nbsp;</p>")
    for cf in dnd_class["classFeatures"]:
        for cf_list in cf:
            if "source" in cf_list.keys():
                continue
            print("<h2>" + cf_list["name"] + "</h2>")
            format_entries(cf_list["entries"])
            print("<p>&nbsp;</p>")
    print("<h1>" + dnd_class["subclassTitle"] + "</h1>")
    for sc in dnd_class["subclasses"]:
        if sc["source"] == "PHB":
            print("<h2>" + sc["name"] + "</h2>")
            for sc_feats in sc["subclassFeatures"]:
                for ssc_feats in sc_feats:
                    format_entries(ssc_feats["entries"])
                    print("<p>&nbsp;</p>")
                    
def parse_background(dnd_background):
    for background in dnd_background["background"]:
        if background["source"] == "PHB":
            print("<h2>" + background["name"] + "</h2>")
            if "entries" in background.keys():
                format_entries(background["entries"])
            elif "_mod" in background.keys():
                format_entries(background["_mod"]["entries"]["items"]["entries"])

def parse_feat(dnd_feats):
    for feat in dnd_feats:
        if feat["source"] == "PHB":
            print("<h2>" + feat["name"] + "</h2>")
            format_entries(feat["entries"])
            print("<p>&nbsp;</p>")
            


# python 5econvert.py --adventure "C:\Users\Matt\Desktop\5etools\data\adventure\adventure-tftyp-tsc.json"
# python 5econvert.py --dnd_class "C:\Users\Matt\Desktop\5etools\data\class\class-fighter.json"

if __name__ == "__main__":
    global spells_db, items_db, monsters_db, class_db
    
    parser = argparse.ArgumentParser(description="Convert a 5e Tools Adventure to Foundry VTT. Must Have FoundryVTT installed and a world created.")
    parser.add_argument("--book", help="Path to book file")
    parser.add_argument("--bg", help="Path to background file")
    parser.add_argument("--feet", help="Path to feet file")
    parser.add_argument("--adventure", help="Path to adventure file")
    parser.add_argument("--dnd_class", help="Path to class file")
    parser.add_argument("--system", help="Path to FoundryVTT system directory", default=r"C:\Users\Matt\AppData\Local\FoundryVTT\Data\systems\dnd5e")
    parser.add_argument("--world", help="Path to FoundryVTT world directory", default=r"C:\Users\Matt\AppData\Local\FoundryVTT\Data\worlds\test")
    parser.add_argument("--name", help="The name of the adventure/book")

    args = parser.parse_args()
    
    if not os.path.exists(args.system):
        print("cannot locate FoundryVTT systems directory {}".format(args.systems))
        exit()
        
    if not os.path.exists(args.world):
        print("cannot locate FoundryVTT world directory {}".format(args.world))
        exit()
    
    spells_db = os.path.join(args.system, "packs", "spells.db")
    if not os.path.exists(spells_db):
        print("cannot locate spells database")
        exit()
    
    items_db = os.path.join(args.system, "packs", "items.db")
    if not os.path.exists(items_db):
        print("cannot locate items database")
        exit()
    
    monsters_db = os.path.join(args.system, "packs", "monsters.db")
    if not os.path.exists(monsters_db):
        print("cannot locate monsters_db")
    
    class_db = os.path.join(args.system, "packs", "classes.db")
    if not os.path.exists(class_db):
        print("cannot locate class_db")
    
    journal_db = os.path.join(args.world, "data", "journal.db")
    if not os.path.exists(journal_db):
        print("cannot locate journal_db")

    folders_db = os.path.join(args.world, "data", "folders.db")
    if not os.path.exists(folders_db):
        print("cannot locate folders_db")

    scenes_db = os.path.join(args.world, "data", "scenes.db")
    if not os.path.exists(scenes_db):
        print("cannot locate scenes_db")
    
    if args.book:
        if not os.path.exists(args.book):
            print("cannot locate book file {}".format(args.book))
            exit()
            
        book_folder = gen_id()
        folders.append({"_id": book_folder,"name": args.name, "type": "JournalEntry", "sort": f_sort, "flags": {},"parent": None,"color": ""})
        with open(args.book, "rb") as f:
            book = json.load(f)
            parse_data(book["data"], book_folder, is_book = True)
        with open(folders_db, "w") as f:
            for fl in folders:
                f.write(json.dumps(fl))
                f.write("\n")

        with open(journal_db, "w") as f:
            for jl in journals:
                # need to go back through all texts to do fixup_text again just to make sure
                jl["content"] = fixup_text(jl["content"])
                f.write(json.dumps(jl))
                f.write("\n")
    elif args.adventure:
        if not os.path.exists(args.adventure):
            print("cannot locate adventure file {}".format(args.adventure))
            exit()

        campaign_folder = gen_id()
        folders = [
            {"_id": campaign_folder,"name": args.name,"type": "JournalEntry","sort": f_sort,"flags": {},"parent": None,"color": ""},
            {"_id": default_folders["PC"],"name": "PC","type": "Actor","sort": None,"flags": {},"parent": None,"color": ""},
            {"_id": default_folders["NPC"],"name": "NPC","type": "Actor","sort": None,"flags": {},"parent": None,"color": ""}
        ]
        with open(args.adventure, "rb") as f:
            adventure = json.load(f)
            parse_data(adventure["data"], campaign_folder)

        with open(scenes_db, "w") as f:
            s_sort = 100000
            nav_order = 10000
            for m in maps:
                m["name"] = m["name"].replace(" Players", "")
                map_fname = m["img"].rsplit("/", 1)[-1]
                download_image("https://5e.tools/img/" + m["img"], os.path.join(args.world, "scenes", map_fname))
                scene = {
                    "_id": gen_id(),
                    "name": m["name"],
                    "permission": {"default": 0},
                    "folder": "", "sort": s_sort, "flags": {},
                    "description": "", "navigation": True, "navOrder": nav_order,
                    "navName": m["name"], "active": True, "initial": None,
                    "img": "worlds/test/scenes/" + map_fname,
                    "thumb": "", "width": 0, "height": 0, "backgroundColor": "#999999",
                    "tiles": [], "gridType": 1, "grid": 100, "shiftX": 0,
                    "shiftY": 0, "gridColor": "#000000", "gridAlpha": 0, "gridDistance": 5,
                    "gridUnits": "ft", "tokens": [], "walls": [], "tokenVision": True,
                    "fogExploration": True, "lights": [], "globalLight": True,
                    "darkness": 1, "playlist": "", "sounds": [], "templates": [], 
                    "journal": "", "notes": [], "weather": "", "drawings": []}
                s_sort += 1
                nav_order += 1
                
                f.write(json.dumps(scene))
                f.write("\n")
        with open(folders_db, "w") as f:
            for fl in folders:
                f.write(json.dumps(fl))
                f.write("\n")

        with open(journal_db, "w") as f:
            for jl in journals:
                # need to go back through all texts to do fixup_text again just to make sure
                jl["content"] = fixup_text(jl["content"])
                f.write(json.dumps(jl))
                f.write("\n")
    elif args.dnd_class:
        with open(args.dnd_class, "rb") as f:
            parse_class(json.load(f)["class"][0])
    elif args.bg:
        with open(args.bg, "rb") as f:
            parse_background(json.load(f))
    elif args.feet:
        with open(args.feet, "rb") as f:
            parse_feat(json.load(f)["feat"])