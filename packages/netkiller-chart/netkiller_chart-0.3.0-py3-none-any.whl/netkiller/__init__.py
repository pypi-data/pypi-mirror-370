#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
##############################################
# Home	: https://www.netkiller.cn
# Author: Neo <netkiller@msn.com>
# Data: 2025-08-19
##############################################

__version__ = '0.0.6'
__author__ = 'Neo Chen'

# __all__ = ['docker', '.']
import csv
import io


class Data:
    data = {}

    def __init__(self) -> None:
        pass

    def str2bool(self, string: str):
        if not string.strip():
            raise ValueError("空字符串无法转换为布尔值")
        lower_s = string.strip().lower()

        if lower_s in ('true', '1', 'yes', 'y'):
            return True
        elif lower_s in ('false', '0', 'no', 'n'):
            return False
        else:
            raise ValueError(f"无法将字符串 '{lower_s}' 转换为布尔值")

    def add(self, id: int, name: str, start: str, finish: str, resource: str, progress: int, predecessor: int,
            milestone: bool,
            parent: int):

        if not resource:
            resource = ""
        if not parent:
            parent = 0
        if not milestone:
            milestone = False
        if not predecessor:
            predecessor = 0
        item = {"id": id, "name": name, "start": start, "finish": finish, "resource": resource, "progress": progress,
                "predecessor": predecessor, "milestone": milestone}

        if parent != "" and int(parent) > 0:
            # print(parent)
            if not "subitem" in self.data[parent]:
                self.data[parent]["subitem"] = {}
            self.data[parent]["subitem"][id] = item

        else:
            self.data[id] = item

    def addFromMySQL(self, row):
        # if row['milestone'] == 'TRUE':
        #     row['milestone'] = True
        # else:
        #     row['milestone'] = False

        id = row["id"]
        parent = row["parent"]
        row["start"] = row["start"].strftime("%Y-%m-%d")
        row["finish"] = row["finish"].strftime("%Y-%m-%d")
        if not row["resource"]:
            row["resource"] = ""
        # print(type(parent))
        if parent and parent > 0:
            if not "subitem" in self.data[parent]:
                self.data[parent]["subitem"] = {}
            self.data[parent]["subitem"][id] = row

        else:
            self.data[id] = row

    def addDict(self, item):
        pass

    def csvfile(self, filepath):
        with open(filepath) as csvfile:
            items = csv.DictReader(csvfile)

            for item in items:

                if item["milestone"] == "TRUE":
                    item["milestone"] = True
                else:
                    item["milestone"] = False
                # print(item)
                # tmp.add(item["id"], item["name"], item["start"], item["finish"], item["resource"],
                #         item["predecessor"], item["milestone"], item["parent"])
                self.add(int(item["id"]), item["name"], item["start"], item["finish"], item["resource"],
                         int(item['progress']),
                         int(item["predecessor"]), bool(item["milestone"]), int(item["parent"]))
        return self.data

    def csvtext(self, text):

        with io.StringIO(text) as buffer:
            items = csv.DictReader(buffer)
            for item in items:
                # print(item)
                if item["milestone"] == "TRUE":
                    item["milestone"] = True
                else:
                    item["milestone"] = False

                self.add(int(item["id"]), item["name"], item["start"], item["finish"], item["resource"],
                         int(item['progress']),
                         int(item["predecessor"]), bool(item["milestone"]), int(item["parent"]))
        return self.data
