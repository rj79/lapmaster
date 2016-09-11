# -*- coding: utf-8 -*-
"""
    htmlgen.py

    Generates HTML pages for result display.

    :copyright: (c) 2016 by Robert Johansson.
    :license: BSD, see LICENSE for more details.
"""

import os
import time
import lmcore

TAIL_SIZE = 20

def time_to_string(t):
    return time.strftime("%H:%M:%S", t)

def laptime_to_string(t):
    return "%(minutes)02d:%(seconds)02d" % {"minutes": t / 60, "seconds":t % 60}

class HTMLGenerator:
    def __init__(self, config, report, outputDir):
        self.Config = config
        self.Report = report
        self.OutputDir = outputDir

    def writeDoc(self, doc, outputFile):
        with open(str(self.OutputDir) + os.sep + outputFile, "w") as f:
            f.write(str(doc))

    def getClassIdsInSizeOrder(self):
        classIds = self.Config.getClassIdList()
        sizes = [(cid, len(self.Config.getTeamIdsInClass(cid))) for cid in classIds]
        return [tup[0] for tup in sorted(sizes, key=lambda tup: tup[1])]

    def getRankText(self, teamId):
        rankText = str(self.Report.getTeamRanking(teamId))
        previousRankText = str(self.Report.getPreviousTeamRanking(teamId))
        return rankText + " (" + previousRankText + ")"

    def createDefaultPage(self, versionStamp):
        doc = lmcore.MarkupNode('html')
        head = doc.addChild('head')
        link = head.addChild('link', "", True)
        link.setAttribute('rel', 'stylesheet')
        link.setAttribute('type', 'text/css')
        link.setAttribute('href', 'lapmaster.css');
        meta2 = head.addChild('meta', "", True)
        meta2.setAttribute('http-equiv', 'Content-type')
        meta2.setAttribute('content', 'text/html')
        meta2.setAttribute('charset', 'UTF-8')
        meta3 = head.addChild('meta', "", True)
        meta3.setAttribute('id', 'versionstamp')
        meta3.setAttribute('versionstamp', versionStamp)
        script = head.addChild('script')
        script.setAttribute('src', '/static/lapmaster.js')

        body = doc.addChild('body')
        body.setAttribute('onload', 'LM.init()')

        self.generateNavigationBar(body)

        return (doc, body)

    def generateNavigationBar(self, root):
        div = root.addChild('div')
        div.setAttribute('class', 'navbar')
        div.setData('Navigation')

        table = div.addChild('table')
        table.setAttribute('class', 'navtable')
        tr = table.addChild('tr')

        td = tr.addChild('td')
        link = td.addChild('a')
        link.setAttribute("href", "index.html")
        link.setData("Resultatlistor")

        td = tr.addChild('td')
        link = td.addChild('a')
        link.setAttribute("href", "logtail.html")
        link.setData("Senaste passager")

        for classId in self.Config.getClassIdList():
            if len(self.Config.getTeamIdsInClass(classId)) == 0:
                # No teams in this class
                continue

            td = tr.addChild('td')
            a = td.addChild('a')
            a.setAttribute('href', 'c' + str(classId) + '.html')
            a.setData("Historik " + self.Config.getClassNameById(classId))

        td = tr.addChild('td')
        link = td.addChild('a')
        link.setAttribute("href", "speaker.html")
        link.setData("Speaker")

        td = tr.addChild('td')
        td.setAttribute('id', 'clock')
        td.setAttribute('style', 'font-weight:bold; text-align:right;')

    def generateLogTail(self, root):
        box = root.addChild('div')
        box.setAttribute('class', 'resultbox')
        p = box.addChild('h2')
        p.setData('Senaste ' + str(TAIL_SIZE) + ' passager')

        table = box.addChild('table')
        table.setAttribute('class', 'resulttable')

        thead = table.addChild('thead')
        tr = thead.addChild('tr')
        th1 = tr.addChild('th', 'Tid')
        th2 = tr.addChild('th', 'Nr')
        th3 = tr.addChild('th')
        th4 = tr.addChild('th')
        th5 = tr.addChild('th')
        th6 = tr.addChild('th')
        th7 = tr.addChild('th')
        th8 = tr.addChild('th')

        th1.setData('Tid')
        th2.setData('Nr')
        th3.setData('Plac')
        th4.setData('Namn')
        th5.setData('Varv')
        th6.setData('Upp')
        th7.setData('Ner')
        th8.setData('Varvtid')

        tbody = table.addChild('tbody')
        log = self.Report.getLapLog()
        tail = log[-TAIL_SIZE:]
        for timestamp, bib in reversed(tail):

            if not bib in self.Config.Persons:
                return

            teamId = self.Config.getTeamIdByBib(bib)

            tr = tbody.addChild('tr')

            col1 = tr.addChild('td')
            col2 = tr.addChild('td')
            col2.setAttribute('class', 'number')
            col3 = tr.addChild('td')
            col4 = tr.addChild('td')
            col5 = tr.addChild('td')
            col6 = tr.addChild('td')
            col7 = tr.addChild('td')
            col8 = tr.addChild('td')

            col1.setData(time_to_string(time.localtime(timestamp)))
            col2.setData(str(bib))
            col3.setData(self.getRankText(teamId))
            link = col4.addChild('a')
            link.setAttribute("href", "p" + str(bib) + ".html")
            personText = self.Config.getPersonNameByBib(bib)
            if not self.Config.isSolo(bib):
                personText += " (" + self.Config.getTeamNameByBib(bib) + ")"
            link.setData(personText)
            lapInfo = self.Report.getLapInfoByTimestamp(self.Config.getTeamIdByBib(bib), timestamp)

            col5.setAttribute('class', 'number')
            col5.setData(str(self.Report.getLapCountByTeamId(teamId)))

            if lapInfo:
                col6.setData(lapInfo.Lag)
                col7.setData(lapInfo.Lead)

            col8.setData(time_to_string(time.gmtime(lapInfo.LapTime)))


    def generateClassStanding(self, classId, root):
        if len(self.Config.getTeamIdsInClass(classId)) == 0:
            # No teams in this class
            return

        box = root.addChild('div')
        box.setAttribute('class', 'resultbox')
        p = box.addChild('h2')
        p.setData(self.Config.getClassNameById(classId))
        table = box.addChild('table')
        table.setAttribute('class', 'resulttable')
        thead = table.addChild('thead')
        tr = thead.addChild('tr')
        tr.addChild('th').setData('Plac')
        tr.addChild('th').setData('Namn')
        tr.addChild('th').setData('V.')
        tr.addChild('th').setData('Tid')
        d = tr.addChild('th')
        d.setData('V.tid')
        d.setAttribute('class', 'number')
        tr.addChild('th').setData('Upp')
        tr.addChild('th').setData('Ner')

        tbody = table.addChild('tbody')

        rankings = self.Report.getTeamRankings(classId)
        rank = 1
        for teamId in rankings:
            lapInfo = self.Report.getLastLapInfo(teamId)
            if not lapInfo:
                break

            tr = tbody.addChild('tr')

            td = tr.addChild('td')
            td.setAttribute('class', 'number')
            td.setData(self.getRankText(teamId))

            td = tr.addChild('td')
            td.setAttribute('class', 'teamname')
            link = td.addChild('a')
            if self.Config.isSoloTeam(teamId):
                link.setAttribute("href", "p" + str(teamId) + ".html")
            else:
                link.setAttribute("href", "p" + str(teamId) + ".html")

            link.setData(self.Config.getTeamNameByTeamId(teamId))

            td = tr.addChild('td')
            td.setAttribute('class', 'number')
            td.setData(str(self.Report.getLapCountByTeamId(teamId)))

            td = tr.addChild('td')
            td.setData(time_to_string(time.localtime(lapInfo.PassTime)))

            td = tr.addChild('td')

            td.setData(laptime_to_string(lapInfo.LapTime))

            td1 = tr.addChild('td')
            td2 = tr.addChild('td')

            if lapInfo:
                td1.setData(lapInfo.Lag)
                td2.setData(lapInfo.Lead)

            rank += 1

    def generatePersonPage(self, bib, versionStamp):
        doc, body = self.createDefaultPage(versionStamp)

        box = body.addChild('div')
        box.setAttribute('class', 'resultbox')

        title = box.addChild('h2')

        titleText = self.Config.getPersonNameByBib(bib) + " (" + str(bib) + ")"

        teamId = self.Config.getTeamIdByBib(bib)

        if not self.Config.isSolo(bib):
            titleText += ", " + self.Config.getTeamNameByBib(bib)

            table = box.addChild('table')
            table.setAttribute('class', 'resulttable')
            thead = table.addChild('thead')
            tr = thead.addChild('tr')
            th = tr.addChild('th')
            th.setData('Nr')
            th = tr.addChild('th')
            th.setData('Namn')
            th = tr.addChild('th')
            th.setData('Varv')

            tbody = table.addChild('tbody')

            teamBibs = self.Config.getTeamBibsByBib(bib)
            for b in teamBibs:
                tr = tbody.addChild('tr')
                td = tr.addChild('td')
                td.setData(str(b))
                td = tr.addChild('td')
                a = td.addChild('a')
                a.setAttribute('href', 'p' + str(b) + ".html")
                a.setData(self.Config.getPersonNameByBib(b))
                td = tr.addChild('td')
                td.setData(self.Report.getLapCountByBib(b))

        title.setData(titleText)

        table = box.addChild('table')
        table.setAttribute('class', 'resulttable')
        tr1 = table.addChild('tr')
        tr2 = table.addChild('tr')
        tr3 = table.addChild('tr')
        tr4 = table.addChild('tr')
        tr5 = table.addChild('tr')
        tr6 = table.addChild('tr')

        tr1.addChild('td').setData('Varv')
        tr2.addChild('td').setData('Varvtid')
        tr3.addChild('td').setData('Plac')
        tr4.addChild('td').setData('Upp')
        tr5.addChild('td').setData('Ner')
        tr6.addChild('td').setData('Tid')

        lapInfoList = self.Report.getLapInfoList(teamId)
        m = 0
        for lapInfo in lapInfoList:
            if lapInfo.LapTime > m:
                m = lapInfo.LapTime
        totalHeight = m / 15 + 20

        lap = 1
        for lapInfo in lapInfoList:
            t = lapInfo.LapTime
            lapBib = lapInfo.Bib
            bottomHeight = t / 15
            topHeight = totalHeight - (bottomHeight)

            td = tr1.addChild('td')
            td.setAttribute('class', 'number')
            td.setData(str(lap))

            td = tr2.addChild('td')

            top = td.addChild('div')
            top.setAttribute('style', "padding:4px; height:" + str(topHeight) + "; vertical-align:bottom;")

            timeStr = "%(minutes)02d:%(seconds)02d" % {"minutes": t / 60, "seconds":t % 60}
            middle = td.addChild('div')
            middle.setData(timeStr)

            link = td.addChild('a')
            link.setAttribute("href", "p" + str(lapBib) + ".html")

            bottom = link.addChild('div')
            if bib == lapBib:
                bottom.setAttribute('style', "height:" + str(bottomHeight) + "; background-color: #ed9797;")
            else:
                bottom.setAttribute('style', "height:" + str(bottomHeight) + "; background-color: #777777;")

            td = tr3.addChild('td')
            td.setAttribute('class', 'number')
            td.setData(str(lapInfo.Rank))

            td = tr4.addChild('td')
            td.setAttribute('class', 'number')
            td.setData(str(lapInfo.Lag))

            td = tr5.addChild('td')
            td.setAttribute('class', 'number')
            td.setData(str(lapInfo.Lead))

            td = tr6.addChild('td')
            td.setData(time_to_string(time.localtime(lapInfo.PassTime)))

            lap += 1

        self.writeDoc(doc, "p" + str(bib) + ".html")

    def generateClassMatrixPage(self, classId, versionStamp):
        doc, body = self.createDefaultPage(versionStamp)

        box = body.addChild('div')
        box.setAttribute('class', 'resultbox')

        table = box.addChild('table')
        table.setAttribute('class', 'resulttable')
        thead = table.addChild('thead')

        teamRanks = self.Report.getTeamRankings(classId)

        if len(teamRanks) == 0:
            return

        lapInfoList = self.Report.getLapInfoList(teamRanks[0])
        maxLaps = len(lapInfoList)

        tr = thead.addChild('tr')
        tr.addChild('th', 'Plac')
        tr.addChild('th', 'Lag')
        lap = 1
        for l in lapInfoList:
            tr.addChild('th', str(lap))
            lap += 1

        tbody = table.addChild('tbody')
        rank = 1
        for teamId in teamRanks:
            lapInfoList = self.Report.getLapInfoList(teamId)
            if len(lapInfoList) == 0:
                break

            lap = 0
            tr = tbody.addChild('tr')

            td = tr.addChild('td')

            td.setData(self.getRankText(teamId))

            td = tr.addChild('td')
            a = td.addChild('a')
            a.setAttribute('href', 'p' + str(teamId) + '.html')
            a.setData(self.Config.getTeamNameByTeamId(teamId))

            for lapInfo in lapInfoList:
                td = tr.addChild('td')
                td.setData(str(lapInfo.Rank))
                lap += 1

            while lap < maxLaps:
                td = tr.addChild('td')
                lap += 1

            rank += 1

        self.writeDoc(doc, "c" + str(classId) + ".html")

    def generateSpeakerPage(self, versionStamp):
        doc, body = self.createDefaultPage(versionStamp)
        log = self.Report.getLapLog()
        div = body.addChild('div')
        div.setAttribute('class', 'resultbox')
        div.addChild('h2', 'Speakerstöd')
        table = div.addChild('table')
        table.setAttribute('class', 'resulttable')
        thead = table.addChild('thead')
        tr = thead.addChild('tr')
        tr.addChild('th', 'Bib')
        tr.addChild('th', 'Namn')
        tr.addChild('th', 'Klass')
        tr.addChild('th', 'Lag')
        tr.addChild('th', 'Plac')
        tr.addChild('th', '')
        tr.addChild('th', 'Varv')
        tr.addChild('th', 'V.Tid')
        tr.addChild('th', 'Jagar')
        tr.addChild('th', 'Upp')
        tr.addChild('th', 'Jagas av')
        tr.addChild('th', 'Ner')

        lastlog = log[-10:]
        tbody = table.addChild('tbody')
        for time, bib in reversed(lastlog):
            teamId = self.Config.getTeamIdByBib(bib)
            classId = self.Config.getClassIdByBib(bib)
            lastLapInfo = self.Report.getLastLapInfo(teamId)
            ranking = lastLapInfo.Rank
            tr = tbody.addChild('tr')
            tr.addChild('td', str(bib))
            tr.addChild('td', self.Config.getPersonNameByBib(bib))
            tr.addChild('td', self.Config.getClassNameById(classId))
            tr.addChild('td', self.Config.getTeamNameByBib(bib))
            tr.addChild('td', ranking)
            tr.addChild('td', "(%s)" % (self.Report.getPreviousTeamRanking(teamId)))
            tr.addChild('td', self.Report.getLapCountByTeamId(teamId))
            tr.addChild('td', laptime_to_string(self.Report.getLastLapTime(teamId)))

            upTeamName = ""
            upTeamLag = ""
            if lastLapInfo.UpTeamId is not None:
                upTeamName = self.Config.getTeamNameByBib(lastLapInfo.UpTeamId)
                upTeamLag = lastLapInfo.Lag

            tr.addChild('td', upTeamName)
            tr.addChild('td', upTeamLag)

            downTeamName = ""
            downTeamLead = ""
            if lastLapInfo.DownTeamId is not None:
                downTeamName = self.Config.getTeamNameByBib(lastLapInfo.DownTeamId)
                downTeamLead = lastLapInfo.Lead

            tr.addChild('td', downTeamName)
            tr.addChild('td', downTeamLead)
        self.writeDoc(doc, "speaker.html")

    def createPages(self, versionStamp):
        versionStamp = str(versionStamp)
        doc, body = self.createDefaultPage(versionStamp)
        flexcontainer = body.addChild('div')
        flexcontainer.setAttribute('class', 'flexcontainer')

        classIdsInSizeOrder = reversed(self.getClassIdsInSizeOrder())
        for classId in classIdsInSizeOrder:
            self.generateClassStanding(classId, flexcontainer)
            self.generateClassMatrixPage(classId, versionStamp)

        for personId in self.Config.getPersonBibList():
            self.generatePersonPage(personId, versionStamp)

        self.writeDoc(doc, 'index.html')

        self.generateSpeakerPage(versionStamp)

        taildoc, tailbody = self.createDefaultPage(versionStamp)
        div = tailbody.addChild('div')

        self.generateLogTail(div)
        self.writeDoc(taildoc, 'logtail.html')
