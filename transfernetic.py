import re
import time
import pandoc

from mediawiki import mediawiki
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# ============ Wiki.js Client stuff
token = ""
sample_transport=RequestsHTTPTransport(
    url="",
    use_json=True,
    headers={
        "Authorization": token,
        "Content-type": "application/json",
    },
    verify=False,
    retries=5
)

client = Client(
    transport=sample_transport,
    fetch_schema_from_transport=True,
)
# ============

url=""

c = mediawiki.MWClient(
    url=url, 
    user="", 
    password=""
)

def continue_str(data):
    try:
        return data["continue"]["apcontinue"]
    except KeyError as error:
        pass

def get_ap():
    apcontinue = ""
    full_aplist = []
    counter = 1
    while apcontinue is not None:
        print(f"Counter: {counter}")
        print(type(apcontinue))
        apdata = c.allpages(apcontinue=apcontinue).json()
        apcontinue = continue_str(apdata)
        print(type(apcontinue))
        print("hello there")
        aplist = apdata["query"]["allpages"]
        print(len(aplist))
        full_aplist = [*full_aplist, *aplist]
        print(f"full_aplist item count: {len(full_aplist)}")
        counter += 1
        print(apcontinue)

    return full_aplist

def scrub_title(title):
    title = re.sub(r"[^\w\s]", '', title)
    title = re.sub(r"\s+", '-', title)

    return title

ap = get_ap()
limit = 5
for n in range(limit):
    try:
        for page in ap:
            pageid = page["pageid"]
            print(pageid)
            title = page["title"]
            url_title = scrub_title(title)
            wikijs_path = f"/import/{url_title}"
            contents = c.page_contents(pageid=pageid).json()
            wikitext = contents["parse"]["wikitext"]["*"]
            #print(f"[DEBUG] >> {wikitext}")
            read_wikitext = pandoc.read(wikitext, format="mediawiki")
            md_wikitext = pandoc.write(read_wikitext, format="markdown")

            query = gql(fr'''
            mutation PageMutation($content: String!, $path: String!, $title: String!) {{
                pages {{
                    create(
                        content: $content,
                        description: "transfernetic - Mediawiki Import",
                        editor: "markdown",
                        isPublished: true,
                        isPrivate: false,
                        locale: "en",
                        path: $path,
                        publishEndDate: "",
                        publishStartDate: "",
                        tags: ["import"],
                        title: $title
                    ) {{
                      page {{
                        id
                      }}
                    }}
                }}
            }}''')
            print(f"Added page {title} at {wikijs_path}")
            results = client.execute(query, variable_values={"content": str(md_wikitext), "path": str(wikijs_path), "title": str(title)})
            time.sleep(5)
    except Exception as e:
      print(f"Error: {e}")
      continue