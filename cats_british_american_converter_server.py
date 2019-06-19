
# -*- coding: utf-8 -*-
import time,mwclient, json, configparser,re,sys
from time import sleep
from mwclient import errors

name_from = ""
name_to = ""
switching_from_to = {}

def call_home(site):
    #page = site.Pages['User:' + config.get('enwiki','username') + "/status"]
    h_page = site.Pages['User:TheSandBot/status']
    text = h_page.text()
    return bool(json.loads(text)["run"]["british_american_move_converter"])


def move_page(old_title,new_title):
    page = site.Pages[old_title]
    edit_summary = """[[WP:Bots/Requests for approval/TheSandBot 4|Task #4]]: Moving category per result of [[Special:Diff/897445174#RFC:_What_disambiguation_should_shows_from_the_United_States_and_United_Kingdom_use?|RfC on NCTV naming format]]. Questions? [[User talk:TheSandDoctor|msg TSD!]]"""
    if page.exists and not site.Pages[new_title].exists and page.redirects_to() == None:

        return page.move(new_title,reason=edit_summary,move_talk=True, no_redirect=False)
    return False


def move_cat_contents(old_title, new_title, site):
    text = site.Pages[old_title] # check category page itself
    global switching_from_to
    for prev, to in switching_from_to.items(): # https://stackoverflow.com/questions/14156473/can-you-write-a-str-replace-using-dictionary-values-in-python
        text = text.replace(prev,to)
    for page in site.Categories[old_title[:9]]: # go through category contents
        text = page.text()
        text = text.replace(old_title, new_title)
        try:
            page.save(text, summary="[[WP:Bots/Requests for approval/TheSandBot 4|Task 4]]: Moving page from [[:" + old_title + "]] to [[:" + new_title + "]]")
        except [[EditError]]:
            print("Error")
            continue
        except [[ProtectedPageError]]:
            print('Could not edit ' + page.page_title + ' due to protection')
            continue

def rename_backlinks(old_title, new_title, site):
    page = site.Pages[old_title]
    for p in page.backlinks():
        text = p.text()
        text = text.replace(old_title, new_title)
        try:
            page.save(text, summary="[[WP:Bots/Requests for approval/TheSandBot 4|Task 4]]: Updating references from [[:" + old_title + "]] to [[:" + new_title + "]]")
        except [[EditError]]:
            print("Error")
            continue
        except [[ProtectedPageError]]:
            print('Could not edit ' + page.page_title + ' due to protection')
            continue



if __name__ == "__main__":
    try:
        site = mwclient.Site(('https','en.wikipedia.org'), '/w/')
        #login stuff
        config = configparser.RawConfigParser()
        config.read('credentials.txt')
        try:
            site.login(config.get('enwiki_sandbot','username'), config.get('enwiki_sandbot', 'password'))
        except errors.LoginError as e:
            print(e)
            raise ValueError("Login failed.")
        source_page = site.Pages['User:Alex 21/sandbox2']
        text = source_page.text()
        match = re.findall(r"\* \[\[:(.*)\]\] -> \[\[:(.*)\]\]",text)
        counter = 0
        fh = open("cats_british_american_results.txt","w")
        global switching_from_to
        for mat in match:
            switching_from_to[mat[0]] = mat[1] # need this list first
        for mat in match:
            global name_from
            global name_to
            name_from = mat[0]
            name_to = mat[1]

            #   continue
            if not call_home(site):#config):
                raise ValueError("Kill switch on-wiki is false. Terminating program.")
            elif move_page(mat[0],mat[1]):
                move_cat_contents(mat[0], mat[1], site)
                rename_backlinks(mat[0], mat[1], site)
                fh.write("Converted " + mat[0] + " ----> " + mat[1] + "\n")
                print("Converted " + mat[0] + " ----> " + mat[1] + "\n")
            #counter +=1
            else:
                fh.write("CONVERTION FAILED " + mat[0] + " to " + mat[1])
                print("CONVERTION FAILED " + mat[0] + " to " + mat[1])
                continue
            counter += 1
            if counter >= 1:
                break
        print("DONE")
        fh.close()
except KeyboardInterrupt:
    print('Interrupted')
    sys.exit(0)
