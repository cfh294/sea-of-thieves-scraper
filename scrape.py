import bs4
import requests
import itertools
import json
import pathlib
import argparse

_home_dir = pathlib.Path(__file__).parent.absolute()
_base_url = "https://seaofthieves.fandom.com/wiki"
_header = ["image", "name", "source", "cost", "requires", "set", "description"]

_categories = (
    "belt",
    "boots",
    "costumes",
    "dress",
    "gloves",
    "hat",
    "jacket",
    "shirt",
    "bottoms",
    "underwear"
)

def cmd_line(f):
    def with_args(*args, **kwargs):
        ap = argparse.ArgumentParser(description="Scraper for Sea of Thieves data.")
        ap.add_argument("-c", "--categories", type=str, nargs="*", default=_categories, help="The pages you want to scrape.")
        ap.add_argument("-o", "--output-file", type=str, default=(_home_dir / "data.json"), help="Output file path.")
        ap.add_argument("-i", "--indent", type=int, default=None, help="Optional indent spaces for output file.")
        return f(ap.parse_args(), *args, **kwargs)
    return with_args


@cmd_line
def main(cmd_line):
    pages = {}
    for category in cmd_line.categories:
        data = requests.get(
            f"{_base_url}/{str(category).lower().capitalize()}"
        )
        if data.status_code == 200:
            soup = bs4.BeautifulSoup(data.text, features="html.parser")
            table = soup.find("table", {"class": ["wikitable", "sortable", "list", "jquery-tablesorter"]})
            out_data = []
            for i, row in enumerate(table.find("tbody").find_all("tr")):

                # skip first row because tbody selector not skipping thead
                if i:
                    this_out_row = {}
                    for j, col in enumerate(row.find_all(recursive=False)):
                        this_column_text = _header[j]
                        if this_column_text == "image":
                            if (a := col.find("a")):
                                text = str(a["href"]).strip()
                            else:
                                text = None
                        else:
                            text = str(col.text).replace("\"", "").strip()
                            if text == "n/a":
                                text = None
                        this_out_row[this_column_text] = text
                    out_data.append(this_out_row)
            pages[category] = out_data

    if pages:
        with open(cmd_line.output_file, "w") as f:
            if cmd_line.indent:
                json.dump(pages, f, indent=cmd_line.indent)
            else:
                json.dump(pages, f)


if __name__ == "__main__":
    main()
