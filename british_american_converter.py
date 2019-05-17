#!/usr/bin/env python3.6
import time,mwclient, json, configparser,re,sys
from time import sleep

def call_home(site):
    #page = site.Pages['User:' + config.get('enwiki','username') + "/status"]
    h_page = site.Pages['User:TheSandBot/status']
    text = h_page.text()
    return bool(json.loads(text)["run"]["british_american_move_converter"])
def move_page(old_title,new_title):
    page = site.Pages[old_title]
    edit_summary = """Moving page per result of [[Special:Diff/897445174#RFC:_What_disambiguation_should_shows_from_the_United_States_and_United_Kingdom_use?|RfC on NCTV naming format]]. Questions? See [[Special:Diff/897445174#RFC:_What_disambiguation_should_shows_from_the_United_States_and_United_Kingdom_use?|the RfC]] or [[User talk:TheSandDoctor|msg TSD!]] ([[Wikipedia:Bots/Requests for approval/TheSandBot 3|BRFA in trial]]; please mention that this is task #3!))"""
# return page.move(new_title,reason=edit_summary,move_talk=True, no_redirect=False) if page.exists and page.redirects_to() == None else None
# if site.Pages[new_title].exists:
#     return None
    if page.exists and not site.Pages[new_title].exists and page.redirects_to() == None:

        return page.move(new_title,reason=edit_summary,move_talk=True, no_redirect=False)
    return False

if __name__ == "__main__":
    try:
        site = mwclient.Site(('https','en.wikipedia.org'), '/w/')
        #login stuff
        config = configparser.RawConfigParser()
        config.read('credentials.txt')
        try:
            site.login(config.get('enwiki_sandbot','username'), config.get('enwiki_sandbot', 'password'))
        except errors.LoginError as e:
                #print(e[1]['reason'])
            print(e)
            raise ValueError("Login failed.")
        source_page = site.Pages['User:Alex 21/sandbox2']
        text = source_page.text()
        match = re.findall(r"\* \[\[(.*)\]\] -> \[\[(.*)\]\]",text)
        counter = 0
        fh = open("british_american_results.txt","w")
        for mat in match:
            #if counter < 113:
            #   counter += 113
            #   continue
            if not call_home(site):#config):
                raise ValueError("Kill switch on-wiki is false. Terminating program.")
            elif move_page(mat[0],mat[1]):
                fh.write("Converted " + mat[0] + " ----> " + mat[1] + "\n")
                print("Converted " + mat[0] + " ----> " + mat[1] + "\n")
            #counter +=1
            else:
                fh.write("CONVERTION FAILED " + mat[0] + " to " + mat[1])
                print("CONVERTION FAILED " + mat[0] + " to " + mat[1])
        print("DONE")
        fh.close()
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)
