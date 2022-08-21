import requests
import json 
import os
import time
import sys
from slack_sdk.webhook import WebhookClient

def gitscan(keyword, gitkey, slack):
    for i in range(1,100):
        url = "https://api.github.com/search/code?q="+ keyword +"&per_page=100&page=" + str(i)
        
        headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': 'token ' + gitkey
        }
        payload = {}

        response = requests.request("GET", url, headers=headers, data=payload)

        out_list = json.loads(response.text)

        if(len(out_list['items']) == 0):
            return 0

        for out in out_list['items']:
            git_type = out['repository']['owner']['type']

            if(git_type == 'Organization'):
                path = out['path']
                fullname = out['repository']['full_name']
                downloadcode(fullname, path, slack)
                time.sleep(2)

def downloadcode(fullname, path, slack):

    url = "https://api.github.com/repos/" + fullname + "/contents/" + path

    payload={}
    headers = {
    'Accept': 'application/vnd.github.v3.raw',
    'Cookie': '_octo=GH1.1.1444945424.1659588367; logged_in=no'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    open('out.txt','w+').write(response.text)

    cmd = "trufflehog filesystem --fail --only-verified --directory=."
    flag = os.system(cmd)
    if(flag != 0 and slack == 'slack'):
        sendslackalert(url)

def sendslackalert(giturl):
    url = str(os.environ['slack_token'])
    webhook = WebhookClient(url)
    webhook.send(
        text="fallback",
        blocks = [
		{
			"type": "section",
			"text": {
				"type": "plain_text",
				"text": "Alert 🚨 Verified Key Found"
			}
		},
		{
			"type": "section",
			"text": {
				"type": "plain_text",
				"text": "URL of the found key: " + giturl
			}
		}
	    ]
    )                                                                                                                                                    

if __name__ == "__main__":
    gitscan(sys.argv[1], sys.argv[2], sys.argv[3])
