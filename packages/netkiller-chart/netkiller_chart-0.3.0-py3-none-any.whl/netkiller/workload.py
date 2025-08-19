#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
##############################################
# Home	: http://netkiller.github.io
# Author: Neo <netkiller@msn.com>
# Data: 2025-08-06
##############################################
import csv
import json
import sys
from optparse import OptionParser, OptionGroup

from netkiller.gantt import Gantt

from src.netkiller.gantt import Data


class Workload(Gantt):
    def __init__(self) -> None:
        super().__init__()
        self.workloadData = {}
        self.minDate = []
        self.maxDate = []
        self.resourceTextSize = 0

    def __gantt2workload(self, data):
        # self.workloadData = dict()
        for key, item in data.items():
            if "subitem" in item:
                self.__gantt2workload(item["subitem"])

            if not "resource" in item:
                continue
            elif not item["resource"]:
                item["resource"] = "null"

            start = datetime.strptime(item["start"], "%Y-%m-%d").date()
            finish = datetime.strptime(item["finish"], "%Y-%m-%d").date()

            self.minDate.append(start)
            self.maxDate.append(finish)

            length = self.getTextSize(item["resource"])
            # print(self.resourceTextSize,length)
            if self.resourceTextSize < length:
                self.resourceTextSize = length

            if item["resource"] in self.workloadData.keys():
                # if data.has_key(item['resource']):

                # if not 'start' in self.workloadData[item['resource']]:
                # self.workloadData[item['resource']]['start']=''
                # if datetime.strptime(self.data[item['resource']]['start'], '%Y-%m-%d').date() > start:
                #     self.workloadData[item['resource']]['start'] = item['start']
                # if datetime.strptime(self.data[item['resource']]['finish'], '%Y-%m-%d').date() < finish:
                #     self.workloadData[item['resource']]['finish'] = item['finish']

                # print(self.workloadData)

                if self.workloadData[item["resource"]]["start"] > start:
                    self.workloadData[item["resource"]]["start"] = start
                if self.workloadData[item["resource"]]["finish"] < finish:
                    self.workloadData[item["resource"]]["finish"] = finish
            else:
                self.workloadData[item["resource"]] = {"resource": item["resource"], "start": start, "finish": finish}
        return self.workloadData

    def workload(self, title):
        self.data = self.__gantt2workload(self.data)

        self.startPosition = self.resourceTextSize + 300
        left = self.startPosition

        self.beginDate = min(self.minDate)
        self.endDate = max(self.maxDate)

        lineNumber = len(self.data)

        days = self.endDate - self.beginDate
        self.canvasWidth = self.startPosition + self.columeWidth * days.days + days.days + self.columeWidth + 2
        self.canvasHeight = self.canvasTop + self.rowHeight * 5 + self.rowHeight * lineNumber + lineNumber + 15
        # print(self.canvasTop, self.canvasHeight)

        self.draw = draw.Drawing(self.canvasWidth, self.canvasHeight)

        self.title(title)

        top = self.rowHeight * 4 - 10
        chart = draw.Group(id="workload")

        table = draw.Group(id="table")
        table.append_title("表格")
        # 封顶
        table.append(draw.Line(1, self.canvasTop, self.canvasWidth, self.canvasTop, stroke="black"))
        table.append(draw.Text("资源", 20, 5, top + 20, fill="#555555"))
        table.append(draw.Line(self.resourceTextSize, top, self.resourceTextSize, self.canvasHeight, stroke="grey"))
        table.append(draw.Text("开始日期", 20, self.resourceTextSize + +5, top + 20, fill="#555555"))
        table.append(
            draw.Line(self.resourceTextSize + 100, top, self.resourceTextSize + 100, self.canvasHeight, stroke="grey"))
        table.append(draw.Text("截止日期", 20, self.resourceTextSize + 100 + 5, top + 20, fill="#555555"))
        table.append(
            draw.Line(self.resourceTextSize + 200, top, self.resourceTextSize + 200, self.canvasHeight, stroke="grey"))
        table.append(draw.Text("工时", 20, self.resourceTextSize + 200 + 5, top + 20, fill="#555555"))
        # table.append(draw.Line(self.resourceTextSize + 400, top,                               self.resourceTextSize + 400, self.canvasHeight, stroke='grey'))

        chart.append(table)

        # for key, value in self.__month(top).items():
        #     chart.append(value)
        for key, value in super().calendarYear(self.canvasTop).items():
            chart.append(value)

        # print(self.dayPosition)

        # for key, value in self.__weekday(top).items():
        #     background.append(value)
        # 月线
        chart.append(draw.Line(self.startPosition, self.canvasTop + self.rowHeight, self.canvasWidth,
                               self.canvasTop + self.rowHeight, stroke="grey"))
        # 周线
        chart.append(
            draw.Line(1, self.canvasTop + self.rowHeight * 2, self.canvasWidth, self.canvasTop + self.rowHeight * 2,
                      stroke="grey"))

        chart.append(
            draw.Line(1, self.canvasTop + self.rowHeight * 3, self.canvasWidth, self.canvasTop + self.rowHeight * 3,
                      stroke="black"))
        # 竖线
        chart.append(draw.Line(left, self.canvasTop, left, self.canvasHeight, stroke="grey"))

        # begin = datetime.strptime(line['begin'], '%Y-%m-%d').day
        # # end = datetime.strptime(line['end'], '%Y-%m-%d').day
        #

        # left += self.columeWidth * (begin - 1) + (1 * begin)
        # # 日宽度 + 竖线宽度
        self.canvasTop = self.rowHeight * 5 - 10
        for resource, row in self.data.items():
            # # 工时
            top = self.canvasTop + self.itemLine * self.rowHeight + self.splitLine * self.itemLine
            # print(resource, row, top)
            # end = (datetime.strptime(row['finish'], '%Y-%m-%d').date() -
            #        datetime.strptime(row['start'], '%Y-%m-%d').date()).days
            end = (row["finish"] - row["start"]).days
            # end = (row['finish'] - row['start']).days
            right = self.columeWidth * (end + 1) + (1 * end)

            chart.append(draw.Text(resource, self.fontSize, 5, top + 20, text_anchor="start"))
            chart.append(
                draw.Text(row["start"].strftime("%Y-%m-%d"), self.fontSize, self.resourceTextSize + 5, top + 20,
                          text_anchor="start"))
            chart.append(
                draw.Text(row["finish"].strftime("%Y-%m-%d"), self.fontSize, self.resourceTextSize + 100 + 5, top + 20,
                          text_anchor="start"))

            chart.append(
                draw.Text(str(end + 1), self.fontSize, self.resourceTextSize + 200 + 5, top + 20, text_anchor="start"))

            left = self.dayPosition[row["start"].strftime("%Y-%m-%d")]
            r = draw.Rectangle(left, top + 4, right, self.barHeight, fill="blue")
            r.append_title(resource)
            chart.append(r)

            chart.append(draw.Line(1, top + self.rowHeight, self.canvasWidth, top + self.rowHeight, stroke="grey"))

            self.itemLine += 1

        self.draw.append(chart)
        # self.draw.append(draw.Rectangle(1, 1, self.canvasWidth,
        #                                 self.canvasHeight, fill='none', stroke='black'))
        self.legend()

    def workloadChart(self, title):
        self.workload(title)

    def main(self):
        self.parser = OptionParser("usage: %prog [options] ")

        self.parser.add_option("", "--stdin", action="store_true", dest="stdin",
                               help="cat gantt.json | gantt -s file.svg")
        self.parser.add_option("-c", "--csv", dest="csv", help="/path/to/gantt.csv", default=None,
                               metavar="/path/to/gantt.csv")
        self.parser.add_option("-l", "--load", dest="load", help="load data from file.", default=None,
                               metavar="/path/to/gantt.json")

        # group = OptionGroup(self.parser, "loading data from mysql")
        # group.add_option("-H", "--host", dest="host", help="", default=None, metavar="localhost")
        # group.add_option("-u", "--username", dest="username", help="", default=None, metavar="root")
        # group.add_option("-p", "--password", dest="password", help="", default=None, metavar="")
        # group.add_option("-D", "--database", dest="database", help="", default=None, metavar="test")
        # self.parser.add_option_group(group)

        group = OptionGroup(self.parser, "Workload")
        group.add_option("-t", "--title", dest="title", help="标题", default="标题", metavar="项目标题")
        group.add_option("-n", "--name", dest="name", help="项目名称", default="Netkiller Python 手札",
                         metavar="Netkiller Python 手札")
        group.add_option("-W", "--workweeks", dest="workweeks", help="workweeks default 5", default=5, metavar="5")
        group.add_option("-o", "--odd-even", action="store_true", dest="oddeven", default=False, help="odd-even weeks")
        # group.add_option("-g", "--gantt", action="store_true", dest="gantt", default=True, help="Gantt chart")
        # group.add_option("-w", "--workload", action="store_true", dest="workload", help="Workload chart")
        group.add_option("-s", "--save", dest="save", help="save file", default=None, metavar="/path/to/gantt.svg")
        self.parser.add_option_group(group)
        self.parser.add_option("-d", "--debug", action="store_true", dest="debug", help="debug mode")

        (options, args) = self.parser.parse_args()
        if options.stdin:
            self.data = json.loads(sys.stdin.read())
        elif options.csv:
            with open(options.csv) as csvfile:
                items = csv.DictReader(csvfile)
                tmp = Data()
                for item in items:
                    if item["milestone"] == "TRUE":
                        item["milestone"] = True
                    else:
                        item["milestone"] = False

                    tmp.add(item["id"], item["name"], item["start"], item["finish"], item["resource"],
                            item["predecessor"], item["milestone"], item["parent"])
                self.data = tmp.data
        # elif options.host:
        #     config = {"host": options.host, "user": options.username, "password": options.password,
        #               "database": options.database, "raise_on_warnings": True}
        #     self.loadFromMySQL(config)
        if options.debug:
            print(options, args)
            print(json.dumps(self.data, ensure_ascii=False))

        if not self.data:
            self.usage()

        if options.save:
            file = options.save
        else:
            if options.workload:
                file = "workload.svg"
            elif options.gantt:
                file = "gantt.svg"

        if options.workweeks:
            workweeks = options.workweeks

        if options.workload:
            workload = Workload()
            workload.load(self.data)
            workload.name(options.name)
            workload.setWorkweeks(workweeks, False)
            workload.workloadChart(options.title)
            workload.save(file)

        elif options.gantt:
            self.gantt = Gantt()
            # self.gantt.hideTable()
            self.gantt.load(self.data)
            self.gantt.name(options.name)
            self.gantt.setWorkweeks(workweeks, options.oddeven)
            self.gantt.ganttChart(options.title)
            self.gantt.save(file)
            # self.gantt.export(file)


def main():
    try:
        workload = Workload()
        workload.main()
    except KeyboardInterrupt as e:
        print(e)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
