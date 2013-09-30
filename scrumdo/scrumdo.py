# -*- coding: utf-8 -*-

import local_settings as settings
import slumber, pprint, re
from datetime import datetime


class ScrumDo:
    
    def __init__(self, user, pwd, iters):
        base_url = "%s/api/v2/" % settings.scrumdo_host
        self.api = slumber.API(base_url, auth=(user, pwd))
        self.organization = self.api.organizations.get()[0]
        self.project = self.api.organizations(self.organization["slug"]).projects.get()[0]
        self.q_iteration_list = self.get_q_iterations_to_date(iters)
        self.categories_as_list()
        
    def pprint_iteration(self):
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(self.q_iteration_list[0])
                
    def print_iteration(self):
        print self.q_iteration_list
        for it in self.q_iteration_list:
            print "Name: %s Start Date: %s - End Date: %s" %\
                    (it["name"], it["start_date"], it["end_date"])
            for st in it["stories"]:
                print "\tStory Name: %s -- Points: %s -- Total Points: %d" % (st["summary"], st["points"], st["points_value"])
                for tsk in st["tasks"]:
                    print "\t\tTask Name: %s -- Tags: %s" % (tsk["summary"], tsk["tags"])

    def fix_task_tags(self, tasks):
        for task in tasks:
            names = []
            if task['tags']:
                text = task['tags']
                task['unplanned'] = False
                tags_list = re.split("/|,| ", text, flags=re.IGNORECASE)
                for tag in tags_list:
                    if tag in settings.names.keys():
                        names.append(settings.names[tag])
                    elif tag == "unplanned":
                        task['unplanned'] = True
                task['names'] = names             
    
    def add_epic(self, epic_id, story):
        epic = self.api.organizations(self.organization["slug"]).\
                projects(self.project['slug']).epics(epic_id).get()
        story["epic"]['summary'] = epic['summary']
        story["epic_summary"] = epic['summary']
        if "epics_list" not in self.project.keys(): 
            self.project["epics_list"] = [epic['summary']]
        elif epic['summary'] not in self.project["epics_list"]:
            self.project["epics_list"].append(epic['summary'])

    def add_tags_header(self, story):
        if story["tags"]:
            if "tags_list" in self.project.keys():
                self.project["tags_list"] = set(self.project["tags_list"]) | set(story["tags_list"])
            else:
                self.project["tags_list"] = set(story["tags_list"])
                                    
    def add_task(self, iteration, story):
        tasks = self.api.organizations(self.organization["slug"]).\
                projects(self.project['slug']).iterations(iteration['id']).\
                stories(story['id']).tasks.get()
        self.fix_task_tags(tasks)
        story["tasks"] = tasks

    
    def add_comment_as_dict(self, story):
        pass
#         comment_list = self.api.comments().story(story["id"]).get()
#         if comment_list:
#             for comment in comment_list:
#                 if comment["comment"].startswith("cycle"):
#                     story["cycle"] = eval(comment["comment"].split(": ")[1])
#                 if comment["comment"].startswith("responsive"):
#                     story["responsive"] = eval(comment["comment"].split(": ")[1])
    
    def get_stories_tasks_iteration(self):
        for iteration in self.q_iteration_list:
            stories = self.api.organizations(self.organization["slug"]).\
            projects(self.project['slug']).iterations(iteration['id']).stories.get()
            iteration["stories"] = stories
            for story in stories:
                self.add_task(iteration, story)
                self.add_epic(story['epic']['id'], story)
                if story["comment_count"] > 0:
                    self.add_comment_as_dict(story)
                self.add_tags_header(story)
                
        self.project["epics_list"] = sorted(self.project["epics_list"])  
        self.project["tags_list"] = sorted(self.project["tags_list"], key=lambda s: s.lower())         
        return self.q_iteration_list
    
    def categories_as_list(self):
        categories_list = self.project['categories']
        self.project["categories_list"] = sorted([cat for cat in categories_list.split(', ')])
        
    def get_q_iterations_to_date(self, iters):
        today = datetime.today()
        iteration_list = self.api.organizations(self.organization["slug"]).\
                         projects(self.project['slug']).iterations.get()
        sprints = []
        for q_id in iters:
            for iteration in iteration_list:
                if q_id in iteration['name'] and datetime.strptime(iteration['end_date'], "%Y-%m-%d") < today:
                    sprints.append(iteration)
#         [iteration for iteration in iteration_list if q_id for q_id in iters\
#                             in iteration['name'] and datetime.strptime(iteration['end_date'],
#                                                                           "%Y-%m-%d") < today]
        
        return sprints
 
if __name__ == '__main__':
    pass
    