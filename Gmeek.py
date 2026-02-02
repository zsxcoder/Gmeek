# -*- coding: utf-8 -*-
import os
import re
import json
import time
import datetime
import shutil
import urllib
import requests
import argparse
import html
from github import Github
from xpinyin import Pinyin
from feedgen.feed import FeedGenerator
from jinja2 import Environment, FileSystemLoader
from transliterate import translit
from collections import OrderedDict
from Summary import generate_summary
######################################################################################
i18n={"Search":"Search","switchTheme":"switch theme","home":"home","comments":"comments","run":"run ","days":" days","Previous":"Previous","Next":"Next"}
i18nCN={"Search":"搜索","switchTheme":"切换主题","home":"首页","comments":"评论","run":"网站运行","days":"天","Previous":"上一页","Next":"下一页"}
i18nRU={"Search":"Поиск","switchTheme":"Сменить тему","home":"Главная","comments":"Комментарии","run":"работает"," days":" дней","Previous":"Предыдущая","Next":"Следующая"}
IconBase={
    "post":"M0 3.75C0 2.784.784 2 1.75 2h12.5c.966 0 1.75.784 1.75 1.75v8.5A1.75 1.75 0 0 1 14.25 14H1.75A1.75 1.75 0 0 1 0 12.25Zm1.75-.25a.25.25 0 0 0-.25.25v8.5c0 .138.112.25.25.25h12.5a.25.25 0 0 0 .25-.25v-8.5a.25.25 0 0 0-.25-.25ZM3.5 6.25a.75.75 0 0 1 .75-.75h7a.75.75 0 0 1 0 1.5h-7a.75.75 0 0 1-.75-.75Zm.75 2.25h4a.75.75 0 0 1 0 1.5h-4a.75.75 0 0 1 0-1.5Z",
    "link":"m7.775 3.275 1.25-1.25a3.5 3.5 0 1 1 4.95 4.95l-2.5 2.5a3.5 3.5 0 0 1-4.95 0 .751.751 0 0 1 .018-1.042.751.751 0 0 1 1.042-.018 1.998 1.998 0 0 0 2.83 0l2.5-2.5a2.002 2.002 0 0 0-2.83-2.83l-1.25 1.25a.751.751 0 0 1-1.042-.018.751.751 0 0 1-.018-1.042Zm-4.69 9.64a1.998 1.998 0 0 0 2.83 0l1.25-1.25a.751.751 0 0 1 1.042.018.751.751 0 0 1 .018 1.042l-1.25 1.25a3.5 3.5 0 1 1-4.95-4.95l2.5-2.5a3.5 3.5 0 0 1 4.95 0 .751.751 0 0 1-.018 1.042.751.751 0 0 1-1.042.018 1.998 1.998 0 0 0-2.83 0l-2.5 2.5a1.998 1.998 0 0 0 0 2.83Z",
    "about":"M10.561 8.073a6.005 6.005 0 0 1 3.432 5.142.75.75 0 1 1-1.498.07 4.5 4.5 0 0 0-8.99 0 .75.75 0 0 1-1.498-.07 6.004 6.004 0 0 1 3.431-5.142 3.999 3.999 0 1 1 5.123 0ZM10.5 5a2.5 2.5 0 1 0-5 0 2.5 2.5 0 0 0 5 0Z",
    "sun":"M8 10.5a2.5 2.5 0 100-5 2.5 2.5 0 000 5zM8 12a4 4 0 100-8 4 4 0 000 8zM8 0a.75.75 0 01.75.75v1.5a.75.75 0 01-1.5 0V.75A.75.75 0 018 0zm0 13a.75.75 0 01.75.75v1.5a.75.75 0 01-1.5 0v-1.5A.75.75 0 018 13zM2.343 2.343a.75.75 0 011.061 0l1.06 1.061a.75.75 0 01-1.06 1.06l-1.06-1.06a.75.75 0 010-1.06zm9.193 9.193a.75.75 0 011.06 0l1.061 1.06a.75.75 0 01-1.06 1.061l-1.061-1.06a.75.75 0 010-1.061zM16 8a.75.75 0 01-.75.75h-1.5a.75.75 0 010-1.5h1.5A.75.75 0 0116 8zM3 8a.75.75 0 01-.75.75H.75a.75.75 0 010-1.5h1.5A.75.75 0 013 8zm10.657-5.657a.75.75 0 010 1.061l-1.061 1.06a.75.75 0 11-1.06-1.06l1.06-1.06a.75.75 0 011.06 0zm-9.193 9.193a.75.75 0 010 1.06l-1.06 1.061a.75.75 0 11-1.061-1.06l1.06-1.061a.75.75 0 011.061 0z",
    "moon":"M9.598 1.591a.75.75 0 01.785-.175 7 7 0 11-8.967 8.967.75.75 0 01.961-.96 5.5 5.5 0 007.046-7.046.75.75 0 01.175-.786zm1.616 1.945a7 7 0 01-7.678 7.678 5.5 5.5 0 107.678-7.678z",
    "search":"M15.7 13.3l-3.81-3.83A5.93 5.93 0 0 0 13 6c0-3.31-2.69-6-6-6S1 2.69 1 6s2.69 6 6 6c1.3 0 2.48-.41 3.47-1.11l3.83 3.81c.19.2.45.3.7.3.25 0 .52-.09.7-.3a.996.996 0 0 0 0-1.41v.01zM7 10.7c-2.59 0-4.7-2.11-4.7-4.7 0-2.59 2.11-4.7 4.7-4.7 2.59 0 4.7 2.11 4.7 4.7 0 2.59-2.11 4.7-4.7 4.7z",
    "rss":"M2.002 2.725a.75.75 0 0 1 .797-.699C8.79 2.42 13.58 7.21 13.974 13.201a.75.75 0 0 1-1.497.098 10.502 10.502 0 0 0-9.776-9.776.747.747 0 0 1-.7-.798ZM2.84 7.05h-.002a7.002 7.002 0 0 1 6.113 6.111.75.75 0 0 1-1.49.178 5.503 5.503 0 0 0-4.8-4.8.75.75 0 0 1 .179-1.489ZM2 13a1 1 0 1 1 2 0 1 1 0 0 1-2 0Z",
    "upload":"M2.75 14A1.75 1.75 0 0 1 1 12.25v-2.5a.75.75 0 0 1 1.5 0v2.5c0 .138.112.25.25.25h10.5a.25.25 0 0 0 .25-.25v-2.5a.75.75 0 0 1 1.5 0v2.5A1.75 1.75 0 0 1 13.25 14Z M11.78 4.72a.749.749 0 1 1-1.06 1.06L8.75 3.811V9.5a.75.75 0 0 1-1.5 0V3.811L5.28 5.78a.749.749 0 1 1-1.06-1.06l3.25-3.25a.749.749 0 0 1 1.06 0l3.25 3.25Z",
    "github":"M8 0c4.42 0 8 3.58 8 8a8.013 8.013 0 0 1-5.45 7.59c-.4.08-.55-.17-.55-.38 0-.27.01-1.13.01-2.2 0-.75-.25-1.23-.54-1.48 1.78-.2 3.65-.88 3.65-3.95 0-.88-.31-1.59-.82-2.15.08-.2.36-1.02-.08-2.12 0 0-.67-.22-2.2.82-.64-.18-1.32-.27-2-.27-.68 0-1.36.09-2 .27-1.53-1.03-2.2-.82-2.2-.82-.44 1.1-.16 1.92-.08 2.12-.51.56-.82 1.28-.82 2.15 0 3.06 1.86 3.75 3.64 3.95-.23.2-.44.55-.51 1.07-.46.21-1.61.55-2.33-.66-.15-.24-.6-.83-1.23-.82-.67.01-.27.38.01.53.34.19.73.9.82 1.13.16.45.68 1.31 2.69.94 0 .67.01 1.3.01 1.49 0 .21-.15.45-.55.38A7.995 7.995 0 0 1 0 8c0-4.42 3.58-8 8-8Z",
    "home":"M6.906.664a1.749 1.749 0 0 1 2.187 0l5.25 4.2c.415.332.657.835.657 1.367v7.019A1.75 1.75 0 0 1 13.25 15h-3.5a.75.75 0 0 1-.75-.75V9H7v5.25a.75.75 0 0 1-.75.75h-3.5A1.75 1.75 0 0 1 1 13.25V6.23c0-.531.242-1.034.657-1.366l5.25-4.2Zm1.25 1.171a.25.25 0 0 0-.312 0l-5.25 4.2a.25.25 0 0 0-.094.196v7.019c0 .138.112.25.25.25H5.5V8.25a.75.75 0 0 1 .75-.75h3.5a.75.75 0 0 1 .75.75v5.25h2.75a.25.25 0 0 0 .25-.25V6.23a.25.25 0 0 0-.094-.195Z",
    "sync":"M1.705 8.005a.75.75 0 0 1 .834.656 5.5 5.5 0 0 0 9.592 2.97l-1.204-1.204a.25.25 0 0 1 .177-.427h3.646a.25.25 0 0 1 .25.25v3.646a.25.25 0 0 1-.427.177l-1.38-1.38A7.002 7.002 0 0 1 1.05 8.84a.75.75 0 0 1 .656-.834ZM8 2.5a5.487 5.487 0 0 0-4.131 1.869l1.204 1.204A.25.25 0 0 1 4.896 6H1.25A.25.25 0 0 1 1 5.75V2.104a.25.25 0 0 1 .427-.177l1.38 1.38A7.002 7.002 0 0 1 14.95 7.16a.75.75 0 0 1-1.49.178A5.5 5.5 0 0 0 8 2.5Z",
    "copy":"M0 6.75C0 5.784.784 5 1.75 5h1.5a.75.75 0 0 1 0 1.5h-1.5a.25.25 0 0 0-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 0 0 .25-.25v-1.5a.75.75 0 0 1 1.5 0v1.5A1.75 1.75 0 0 1 9.25 16h-7.5A1.75 1.75 0 0 1 0 14.25Z M5 1.75C5 .784 5.784 0 6.75 0h7.5C15.216 0 16 .784 16 1.75v7.5A1.75 1.75 0 0 1 14.25 11h-7.5A1.75 1.75 0 0 1 5 9.25Zm1.75-.25a.25.25 0 0 0-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 0 0 .25-.25v-7.5a.25.25 0 0 0-.25-.25Z",
    "check":"M13.78 4.22a.75.75 0 0 1 0 1.06l-7.25 7.25a.75.75 0 0 1-1.06 0L2.22 9.28a.751.751 0 0 1 .018-1.042.751.751 0 0 1 1.042-.018L6 10.94l6.72-6.72a.75.75 0 0 1 1.06 0Z"
}
######################################################################################
class GMEEK():
    def __init__(self,options):
        self.options=options
        
        self.root_dir='docs/'
        self.static_dir='static/'
        self.post_folder='post/'
        self.backup_dir='backup/'
        self.post_dir=self.root_dir+self.post_folder

        user = Github(self.options.github_token)
        self.repo = self.get_repo(user, options.repo_name)
        self.feed = FeedGenerator()
        self.oldFeedString=''

        self.labelColorDict=json.loads('{}')
        for label in self.repo.get_labels():
            self.labelColorDict[label.name]='#'+label.color
        print(self.labelColorDict)
        self.defaultConfig()
        
    def cleanFile(self):
        workspace_path = os.environ.get('GITHUB_WORKSPACE')
        if os.path.exists(workspace_path+"/"+self.backup_dir):
            shutil.rmtree(workspace_path+"/"+self.backup_dir)

        if os.path.exists(workspace_path+"/"+self.root_dir):
            shutil.rmtree(workspace_path+"/"+self.root_dir)

        if os.path.exists(self.backup_dir):
            shutil.rmtree(self.backup_dir)
            
        if os.path.exists(self.root_dir):
            shutil.rmtree(self.root_dir)

        os.mkdir(self.backup_dir)
        os.mkdir(self.root_dir)
        os.mkdir(self.post_dir)

        if os.path.exists(self.static_dir):
            for item in os.listdir(self.static_dir):
                src = os.path.join(self.static_dir, item)
                dst = os.path.join(self.root_dir, item)
                if os.path.isfile(src):
                    shutil.copy(src, dst)
                    print(f"Copied {item} to docs")
                elif os.path.isdir(src):
                    shutil.copytree(src, dst)
                    print(f"Copied directory {item} to docs")
        else:
            print("static does not exist")

    def defaultConfig(self):
        dconfig={"singlePage":[],"startSite":"","filingNum":"","onePageListNum":15,"commentLabelColor":"#006b75","yearColorList":["#bc4c00", "#0969da", "#1f883d", "#A333D0"],"i18n":"CN","themeMode":"manual","dayTheme":"light","nightTheme":"dark","urlMode":"pinyin","script":"","style":"","head":"","indexScript":"","indexStyle":"","bottomText":"","showPostSource":1,"iconList":{},"UTC":+8,"rssSplit":"sentence","exlink":{},"needComment":1,"allHead":"","enableAISummary":0}
        config=json.loads(open('config.json', 'r', encoding='utf-8').read())
        self.blogBase={**dconfig,**config}.copy()
        self.blogBase["postListJson"]=json.loads('{}')
        self.blogBase["singeListJson"]=json.loads('{}')
        self.blogBase["labelColorDict"]=self.labelColorDict
        if "displayTitle" not in self.blogBase:
            self.blogBase["displayTitle"]=self.blogBase["title"]

        if "faviconUrl" not in self.blogBase:
            self.blogBase["faviconUrl"]=self.blogBase["avatarUrl"]

        if "ogImage" not in self.blogBase:
            self.blogBase["ogImage"]=self.blogBase["avatarUrl"]

        if "primerCSS" not in self.blogBase:
            self.blogBase["primerCSS"]="<link href='https://mirrors.sustech.edu.cn/cdnjs/ajax/libs/Primer/21.0.7/primer.css' rel='stylesheet' />"

        if "homeUrl" not in self.blogBase:
            if str(self.repo.name).lower() == (str(self.repo.owner.login) + ".github.io").lower():
                self.blogBase["homeUrl"] = f"https://{self.repo.name}"
            else:
                self.blogBase["homeUrl"] = f"https://{self.repo.owner.login}.github.io/{self.repo.name}"
        print("GitHub Pages URL: ", self.blogBase["homeUrl"])

        if self.blogBase["i18n"]=="CN":
            self.i18n=i18nCN
        elif self.blogBase["i18n"]=="RU":
            self.i18n=i18nRU
        else:
            self.i18n=i18n
        
        self.TZ=datetime.timezone(datetime.timedelta(hours=self.blogBase["UTC"]))

    def get_repo(self,user:Github, repo:str):
        return user.get_repo(repo)

    def markdown2html(self, mdstr):
        payload = {"text": mdstr, "mode": "gfm"}
        headers = {"Authorization": "token {}".format(self.options.github_token)}
        try:
            response = requests.post("https://api.github.com/markdown", json=payload, headers=headers)
            response.raise_for_status()  # Raises an exception if status code is not 200
            return response.text
        except requests.RequestException as e:
            raise Exception("markdown2html error: {}".format(e))

    def renderHtml(self,template,blogBase,postListJson,htmlDir,icon):
        file_loader = FileSystemLoader('templates')
        env = Environment(loader=file_loader)
        template = env.get_template(template)
        output = template.render(blogBase=blogBase,postListJson=postListJson,i18n=self.i18n,IconList=icon)
        f = open(htmlDir, 'w', encoding='UTF-8')
        f.write(output)
        f.close()

    def createPostHtml(self,issue):
        mdFileName=re.sub(r'[<>:/\\\\|?*"\'|\\0-\\31]', '-', issue["postTitle"])
        mdFilePath=self.backup_dir+mdFileName+".md"
        f = open(mdFilePath, 'r', encoding='UTF-8')
        md_content=f.read()
        post_body=self.markdown2html(md_content)
        f.close()

        postBase=self.blogBase.copy()

        if '<math-renderer' in post_body:
            post_body=re.sub(r'<math-renderer.*?>','',post_body)
            post_body=re.sub(r'</math-renderer>','',post_body)
            issue["script"]=issue["script"]+'<script>MathJax = {tex: {inlineMath: [["$", "$"]]}};</script><script async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>'
        
        if '<p class="markdown-alert-title">' in post_body:
            issue["style"]=issue["style"]+'<style>.markdown-alert{padding:0.5rem 1rem;margin-bottom:1rem;border-left:.25em solid var(--borderColor-default,var(--color-border-default));}.markdown-alert .markdown-alert-title {display:flex;font-weight:var(--base-text-weight-medium,500);align-items:center;line-height:1;}.markdown-alert>:first-child {margin-top:0;}.markdown-alert>:last-child {margin-bottom:0;}</style>'
            alerts = {
                'note': 'accent',
                'tip': 'success',
                'important': 'done',
                'warning': 'attention',
                'caution': 'danger'
            }

            for alert, style in alerts.items():
                if f'markdown-alert-{alert}' in post_body:
                    issue["style"] += (
                        f'<style>.markdown-alert.markdown-alert-{alert} {{'
                        f'border-left-color:var(--borderColor-{style}-emphasis, var(--color-{style}-emphasis));'
                        f'background-color:var(--color-{style}-subtle);}}'
                        f'.markdown-alert.markdown-alert-{alert} .markdown-alert-title {{'
                        f'color: var(--fgColor-{style},var(--color-{style}-fg));}}</style>'
                    )

        if '<code class="notranslate">Gmeek-html' in post_body:
            post_body = re.sub(r'<code class="notranslate">Gmeek-html(.*?)</code>', lambda match: html.unescape(match.group(1)), post_body, flags=re.DOTALL)

        postBase["postTitle"]=issue["postTitle"]
        postBase["postUrl"]=self.blogBase["homeUrl"]+"/"+issue["postUrl"]
        
        if self.blogBase.get("enableAISummary", 0) == 1 and not issue.get("description"):
            print(f"Generating AI summary for: {issue['postTitle']}")
            ai_summary = generate_summary(md_content)
            if ai_summary:
                issue["description"] = ai_summary
                print(f"AI summary generated: {ai_summary[:50]}...")
        
        postBase["description"]=issue.get("description", "")
        postBase["ogImage"]=issue["ogImage"]
        postBase["postBody"]=post_body
        postBase["commentNum"]=issue["commentNum"]
        postBase["style"]=issue["style"]
        postBase["script"]=issue["script"]
        postBase["head"]=issue["head"]
        postBase["top"]=issue["top"]
        postBase["postSourceUrl"]=issue["postSourceUrl"]
        postBase["repoName"]=options.repo_name
        
        if issue["labels"][0] in self.blogBase["singlePage"]:
            postBase["bottomText"]=''

        if '<pre class="notranslate">' in post_body:
            keys=['sun','moon','sync','home','github','copy','check']
            if '<div class="highlight' in post_body:
                postBase["highlight"]=1
            else:
                postBase["highlight"]=2
        else:
            keys=['sun','moon','sync','home','github']
            postBase["highlight"]=0

        postIcon=dict(zip(keys, map(IconBase.get, keys)))
        self.renderHtml('post.html',postBase,{},issue["htmlDir"],postIcon)
        print("create postPage title=%s file=%s " % (issue["postTitle"],issue["htmlDir"]))

    def createPlistHtml(self):
        self.blogBase["postListJson"]=dict(sorted(self.blogBase["postListJson"].items(),key=lambda x:(x[1]["top"],x[1]["createdAt"]),reverse=True))#使列表由时间排序
        keys=list(OrderedDict.fromkeys(['sun', 'moon','sync', 'search', 'rss', 'upload', 'post'] + self.blogBase["singlePage"]))
        plistIcon={**dict(zip(keys, map(IconBase.get, keys))),**self.blogBase["iconList"]}
        keys=['sun','moon','sync','home','search','post']
        tagIcon=dict(zip(keys, map(IconBase.get, keys)))

        postNum=len(self.blogBase["postListJson"])
        pageFlag=0
        while True:
            topNum=pageFlag*self.blogBase["onePageListNum"]
            print("topNum=%d postNum=%d"%(topNum,postNum))
            if postNum<=self.blogBase["onePageListNum"]:
                if pageFlag==0:
                    onePageList=dict(list(self.blogBase["postListJson"].items())[:postNum])
                    htmlDir=self.root_dir+"index.html"
                    self.blogBase["prevUrl"]="disabled"
                    self.blogBase["nextUrl"]="disabled"
                else:
                    onePageList=dict(list(self.blogBase["postListJson"].items())[topNum:topNum+postNum])
                    htmlDir=self.root_dir+("page%d.html" % (pageFlag+1))
                    if pageFlag==1:
                        self.blogBase["prevUrl"]="/index.html"
                    else:
                        self.blogBase["prevUrl"]="/page%d.html" % pageFlag
                    self.blogBase["nextUrl"]="disabled"

                self.renderHtml('plist.html',self.blogBase,onePageList,htmlDir,plistIcon)
                print("create "+htmlDir)
                break
            else:
                onePageList=dict(list(self.blogBase["postListJson"].items())[topNum:topNum+self.blogBase["onePageListNum"]])
                postNum=postNum-self.blogBase["onePageListNum"]
                if pageFlag==0:
                    htmlDir=self.root_dir+"index.html"
                    self.blogBase["prevUrl"]="disabled"
                    self.blogBase["nextUrl"]="/page2.html"
                else:
                    htmlDir=self.root_dir+("page%d.html" % (pageFlag+1))
                    if pageFlag==1:
                        self.blogBase["prevUrl"]="/index.html"
                    else:
                        self.blogBase["prevUrl"]="/page%d.html" % pageFlag
                    self.blogBase["nextUrl"]="/page%d.html" % (pageFlag+2)

                self.renderHtml('plist.html',self.blogBase,onePageList,htmlDir,plistIcon)
                print("create "+htmlDir)

            pageFlag=pageFlag+1

        self.renderHtml('tag.html',self.blogBase,onePageList,self.root_dir+"tag.html",tagIcon)
        print("create tag.html")

    def createFeedXml(self):
        self.blogBase["postListJson"]=dict(sorted(self.blogBase["postListJson"].items(),key=lambda x:x[1]["createdAt"],reverse=False))#使列表由时间排序
        feed = FeedGenerator()
        feed.title(self.blogBase["title"])
        feed.description(self.blogBase["subTitle"])
        feed.link(href=self.blogBase["homeUrl"])
        feed.image(url=self.blogBase["avatarUrl"],title="avatar", link=self.blogBase["homeUrl"])
        feed.pubDate(time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()))
        feed.copyright(self.blogBase["title"])
        feed.managingEditor(self.blogBase["title"])
        feed.webMaster(self.blogBase["title"])
        feed.ttl("60")
        if self.blogBase["rssSplit"]=="sentence":
            feed.description(f"{self.blogBase['subTitle']}{feed.description()}")

        for listJsonName in ["singeListJson", "postListJson"]:
            for num in self.blogBase[listJsonName]:
                item=feed.add_item()
                item.guid(self.blogBase["homeUrl"]+"/"+self.blogBase[listJsonName][num]["postUrl"],permalink=True)
                item.title(self.blogBase[listJsonName][num]["postTitle"])
                item.description(self.blogBase[listJsonName][num]["description"])
                item.link(href=self.blogBase["homeUrl"]+"/"+self.blogBase[listJsonName][num]["postUrl"])
                item.pubDate(time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime(self.blogBase[listJsonName][num]["createdAt"])))
                if self.blogBase["rssSplit"]=="sentence":
                    item.description(f"{self.blogBase['subTitle']} | {item.description()}")
        try:
            feed.rss_file(self.root_dir+'rss.xml')
        except Exception as e:
            print(f"Error creating RSS feed: {e}")

    def createOembedXml(self, issue):
        endpoint=self.blogBase["homeUrl"]+"/"+self.post_folder+str(issue["number"])+".html"
        type= "article"
        title=issue["postTitle"]
        author_name=issue["author"]
        author_url=f"https://github.com/{issue['author']}"
        provider_name=self.blogBase["title"]
        provider_url=self.blogBase["homeUrl"]
        solution_url=self.blogBase["homeUrl"]+"/"+self.post_folder+str(issue["number"])+".html"
        thumbnail_url=issue["ogImage"]
        date_published=datetime.datetime.fromtimestamp(issue["createdAt"], tz=self.TZ).isoformat()
        oembed_json= json.dumps({"type": type, "title": title, "author_name": author_name, "author_url": author_url, "provider_name": provider_name, "provider_url": provider_url, "solution_url": solution_url, "thumbnail_url": thumbnail_url, "date_published": date_published, "version": "1.0"})
        oembed_xml=f'''<?xml version="1.0" encoding="UTF-8" ?>
<oembed>
<type>{type}</type>
<title>{title}</title>
<author_name>{author_name}</author_name>
<author_url>{author_url}</author_url>
<provider_name>{provider_name}</provider_name>
<provider_url>{provider_url}</provider_url>
<solution_url>{solution_url}</solution_url>
<thumbnail_url>{thumbnail_url}</thumbnail_url>
<date_published>{date_published}</date_published>
<version>1.0</version>
</oembed>'''
        print(f"create oembed xml file:{self.root_dir}oembed/{issue['number']}.xml")
        if not os.path.exists(self.root_dir+"oembed"):
            os.makedirs(self.root_dir+"oembed")
        with open(self.root_dir+f"oembed/{issue['number']}.xml", 'w', encoding='utf-8') as f:
            f.write(oembed_xml)
        with open(self.root_dir+f"oembed/{issue['number']}.json", 'w', encoding='utf-8') as f:
            f.write(oembed_json)

    def gerHarderStatusNum(self, issue):
        num=0
        for label in issue["labels"]:
            if label in self.blogBase["yearColorList"]:
                num+=1
        if num>0:
            num= len(self.blogBase["yearColorList"])-num
        else:
            num= len(self.blogBase["yearColorList"])
        return num

    def addOnePostJson(self,issue):
        if self.repo.owner.name != issue["author"]:
            print("Non-owner created issue, skip")
            return

        mdFileName=re.sub(r'[<>:/\\\\|?*"\'|\\0-\\31]', '-', issue["postTitle"])
        issue["htmlDir"]=self.post_dir+f'{issue["number"]}.html'
        issue["postUrl"]=urllib.parse.quote(self.post_folder+f'{issue["number"]}.html')
        issue["postSourceUrl"]="https://github.com/"+options.repo_name+"/issues/"+str(issue["number"])
        issue["ogImage"]=self.blogBase["avatarUrl"]
        if issue["labels"][0] in self.blogBase["singlePage"]:
            listJsonName='singeListJson'
            issue["htmlDir"]=self.root_dir+issue["labels"][0]+".html"
            issue["postUrl"]=urllib.parse.quote(issue["labels"][0]+".html")
            if "avatarUrl" in issue and issue["avatarUrl"]!='':
                issue["ogImage"]=issue["avatarUrl"]
        else:
            listJsonName='postListJson'

        if issue["top"]=="1":
            listJsonName='postListJson'

        self.blogBase[listJsonName]["P"+str(issue["number"])]=issue

    def run(self):
        self.cleanFile()
        try:
            open(self.root_dir+"postList.json", 'r', encoding='UTF-8')
            with open(self.root_dir+"postList.json", 'r', encoding='UTF-8') as postListJsonFile:
                self.blogBase["postListJson"]=json.load(postListJsonFile)
            print("postList.json loaded")
        except Exception as e:
            print("postList.json not found or error: ", e)

        try:
            open(self.root_dir+"singeList.json", 'r', encoding='UTF-8')
            with open(self.root_dir+"singeList.json", 'r', encoding='UTF-8') as singeListJsonFile:
                self.blogBase["singeListJson"]=json.load(singeListJsonFile)
            print("singeList.json loaded")
        except Exception as e:
            print("singeList.json not found or error: ", e)

        issue_number = self.options.issue_number
        if issue_number:
            issue = self.repo.get_issue(int(issue_number))
            if issue.pull_request:
                print("This is a pull request, not an issue")
                return
            if issue.state == "closed":
                print("This issue is closed")
                return

            labels=[label.name for label in issue.labels]
            top=0
            for label in labels:
                if "置顶" == label:
                    top=1
                    break

            p = Pinyin()
            postTitle=issue.title
            fileName=p.get_pinyin(postTitle,'')

            description = issue.body[:200] if issue.body else ""

            issue_dict={
                "labels":labels,
                "postTitle":postTitle,
                "description":description,
                "createdAt":int(time.mktime(issue.created_at.timetuple())),
                "updatedAt":int(time.mktime(issue.updated_at.timetuple())),
                "number":issue.number,
                "top":top,
                "ogImage":self.blogBase["avatarUrl"],
                "commentNum":issue.get_comments().totalCount,
                "author":issue.user.login,
                "style":"",
                "script":"",
                "head":"",
                "postUrl":"",
                "htmlDir":"",
                "postSourceUrl":"",
                "repoName":options.repo_name
            }

            with open(self.backup_dir+str(issue.number)+'-'+fileName+".md", 'w', encoding='UTF-8') as f:
                f.write(f"---\ntitle: {postTitle}\n---\n\n"+issue.body)

            if self.blogBase["urlMode"]=="pinyin":
                self.addOnePostJson(issue_dict)
            elif self.blogBase["urlMode"]=="hash":
                issue_dict["postUrl"]=urllib.parse.quote(self.post_folder+f'{issue.number}.html')
                self.addOnePostJson(issue_dict)
            elif self.blogBase["urlMode"]=="title":
                issue_dict["postUrl"]=urllib.parse.quote(fileName+".html")
                self.addOnePostJson(issue_dict)

            self.createPostHtml(issue_dict)
            self.createOembedXml(issue_dict)

            with open(self.root_dir+"postList.json", 'w', encoding='utf-8') as f:
                json.dump(self.blogBase["postListJson"], f, ensure_ascii=False, indent=4)
            with open(self.root_dir+"singeList.json", 'w', encoding='utf-8') as f:
                json.dump(self.blogBase["singeListJson"], f, ensure_ascii=False, indent=4)
        else:
            for issue in self.repo.get_issues(state="closed", sort="updated", direction="desc"):
                if issue.pull_request:
                    continue

                createdDate=datetime.datetime.strptime(str(issue.created_at.date()), "%Y-%m-%d")
                nowDate=datetime.datetime.strptime(str(datetime.datetime.now(self.TZ).date()), "%Y-%m-%d")
                days=nowDate-createdDate
                createdDateTimestamp=int(time.mktime(issue.created_at.timetuple()))
                updatedDateTimestamp=int(time.mktime(issue.updated_at.timetuple()))

                if issue.body is None:
                    issue_body=""
                else:
                    issue_body=issue.body

                labels=[label.name for label in issue.labels]
                if "post" not in labels and "page" not in labels and len(self.blogBase["singlePage"])==0:
                    print(f"no post/page label found for issue #{issue.number}, skip")
                    continue

                if "page" in labels and issue["labels"][0]!="page" or issue["labels"][0] in self.blogBase["singlePage"]:
                    if "page" in labels:
                        labels.remove("page")

                if issue["labels"][0] in self.blogBase["singlePage"] and "page" in labels:
                    labels.remove("page")
                    labels.append(issue["labels"][0])
                    issue["labels"][0]=issue["labels"][0]

                p = Pinyin()
                postTitle=issue.title
                fileName=p.get_pinyin(postTitle,'')
                if self.blogBase["urlMode"]=="hash":
                    postUrl=urllib.parse.quote(self.post_folder+f'{issue.number}.html')
                elif self.blogBase["urlMode"]=="title":
                    postUrl=urllib.parse.quote(fileName+".html")
                elif self.blogBase["urlMode"]=="pinyin":
                    postUrl=urllib.parse.quote(self.post_folder+f'{issue.number}.html')

                top=0
                for label in labels:
                    if "置顶" == label:
                        top=1
                        break

                description = issue_body[:200] if issue_body else ""
                if self.blogBase["rssSplit"]=="sentence":
                    if issue_body is None:
                        issue_body=""
                    sentences = re.split(r'(?<=[^A-Z].[.?]) +', issue_body)
                    if len(sentences) > 0:
                        description=sentences[0]

                issue_dict={
                    "labels":labels,
                    "postTitle":postTitle,
                    "description":description,
                    "createdAt":createdDateTimestamp,
                    "updatedAt":updatedDateTimestamp,
                    "number":issue.number,
                    "top":top,
                    "ogImage":self.blogBase["avatarUrl"],
                    "commentNum":issue.get_comments().totalCount,
                    "author":issue.user.login,
                    "style":"",
                    "script":"",
                    "head":"",
                    "postUrl":postUrl,
                    "htmlDir":"",
                    "postSourceUrl":"",
                    "repoName":options.repo_name
                }

                with open(self.backup_dir+str(issue.number)+'-'+fileName+".md", 'w', encoding='UTF-8') as f:
                    f.write(f"---\ntitle: {postTitle}\n---\n\n"+issue_body)

                if self.blogBase["urlMode"]=="pinyin":
                    self.addOnePostJson(issue_dict)
                elif self.blogBase["urlMode"]=="hash":
                    self.addOnePostJson(issue_dict)
                elif self.blogBase["urlMode"]=="title":
                    self.addOnePostJson(issue_dict)

            self.createPlistHtml()
            self.createFeedXml()
            for issueNumber in self.blogBase["postListJson"]:
                self.createPostHtml(self.blogBase["postListJson"][issueNumber])
                self.createOembedXml(self.blogBase["postListJson"][issueNumber])
            for issueNumber in self.blogBase["singeListJson"]:
                self.createPostHtml(self.blogBase["singeListJson"][issueNumber])
                self.createOembedXml(self.blogBase["singeListJson"][issueNumber])

            with open(self.root_dir+"postList.json", 'w', encoding='utf-8') as f:
                json.dump(self.blogBase["postListJson"], f, ensure_ascii=False, indent=4)
            with open(self.root_dir+"singeList.json", 'w', encoding='utf-8') as f:
                json.dump(self.blogBase["singeListJson"], f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('github_token', help='github_token')
    parser.add_argument('repo_name', help='repo_name')
    parser.add_argument('--issue_number', help='issue_number', default='')
    options = parser.parse_args()
    gm = GMEEK(options)
    gm.run()
