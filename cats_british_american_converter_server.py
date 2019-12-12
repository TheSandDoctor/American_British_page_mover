# -*- coding: utf-8 -*-
import configparser
import json
import mwclient
import re
import sys
from mwclient import errors

switching_from_to = {}


def call_home(site_obj):
    h_page = site_obj.Pages['User:TheSandBot/status']
    status_text = h_page.text()
    return bool(json.loads(status_text)["run"]["british_american_move_converter"])


def move_page(old_title, new_title):
    page = site.Pages[old_title]
    edit_summary = """[[WP:Bots/Requests for approval/TheSandBot 4|Task #4]]: Moving category per result of [[
    Special:Diff/897445174#RFC:_What_disambiguation_should_shows_from_the_United_States_and_United_Kingdom_use?|RfC 
    on NCTV naming format]]. Questions? [[User talk:TheSandDoctor|msg TSD!]] """
    if page.exists and not site.Pages[new_title].exists and page.redirects_to() == None:
        return page.move(new_title, reason=edit_summary, move_talk=True, no_redirect=False)
    return False


def move_cat_contents(old_title, new_title, site_obj):
    page_text = site_obj.Pages[old_title]  # check category page itself
    global switching_from_to
    # https://stackoverflow.com/questions/14156473/can-you-write-a-str-replace-using-dictionary-values-in-python
    for prev, to in switching_from_to.items():
        page_text = page_text.replace(prev, to)
    for page in site_obj.Categories[old_title[:9]]:  # go through category contents
        page_text = page.text()
        page_text = page_text.replace(old_title, new_title)
        try:
            page.save(page_text,
                      summary='[[WP:Bots/Requests for approval/TheSandBot 4|Task 4]]: Moving page from [[:' + old_title + ']] to [[:' + new_title + ']]')
        except errors.EditError:
            print("Error")
            continue
        except errors.ProtectedPageError:
            print('Could not edit ' + page.page_title + ' due to protection')
            continue


def rename_backlinks(old_title, new_title, site):
    page = site.Pages[old_title]
    for p in page.backlinks():
        page_text = p.text()
        page_text = page_text.replace(old_title, new_title)
        try:
            page.save(page_text,
                      summary='[[WP:Bots/Requests for approval/TheSandBot 4|Task 4]]: Updating references from [[:' + old_title + ']] to [[:' + new_title + ']]')
        except errors.ProtectedPageError:
            print('Could not edit ' + page.page_title + ' due to protection')
            continue
        except errors.EditError:
            print("Error")
            continue


if __name__ == "__main__":
    try:
        site = mwclient.Site(('https', 'en.wikipedia.org'), '/w/')
        # Login stuff
        config = configparser.RawConfigParser()
        config.read('credentials.txt')
        try:
            site.login(config.get('enwiki_sandbot', 'username'), config.get('enwiki_sandbot', 'password'))
        except errors.LoginError as e:
            print(e)
            raise ValueError("Login failed.")
        # End login stuff

        source_page = site.Pages['User:Alex 21/sandbox2']
        text = source_page.text()
        # Locate all pages that are to be renamed. Format is "Old -> New".
        match = re.findall(r"\* \[\[:(.*)\]\] -> \[\[:(.*)\]\]", text)
        counter = 0  # Keep track of how many we have done
        fh = open("cats_british_american_results.txt", "w")
        global switching_from_to
        for mat in match:
            switching_from_to[mat[0]] = mat[1]  # Need this list first
        for mat in match:
            if not call_home(site):
                raise ValueError('Kill switch on-wiki is false. Terminating program.')
            elif move_page(mat[0], mat[1]):
                move_cat_contents(mat[0], mat[1], site)
                rename_backlinks(mat[0], mat[1], site)
                fh.write('Converted ' + mat[0] + ' ----> ' + mat[1] + '\n')
                print('Converted ' + mat[0] + ' ----> ' + mat[1] + '\n')
            # counter +=1
            else:
                fh.write('CONVERSION FAILED ' + mat[0] + ' to ' + mat[1])
                print('CONVERSION FAILED ' + mat[0] + ' to ' + mat[1])
                continue
            counter += 1
            if counter >= 1:
                break
        print("DONE")
        fh.close()
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)
