# -*- coding: utf-8 -*-

import local_settings as settings
import slumber, pprint, re, argparse, getpass, os, csv
from datetime import datetime  
from jinja2 import Environment, PackageLoader


class CommandLine(object):
    
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('user', help='ScrumDo user name')
        parser.add_argument('q', help='Qs in which the queries will be performed.'\
                            'Ex: q1, q1-q3. Queries all executed iterations to date on top of current year.'\
                            'Valid iterations are: q1, q2, q3 and q4')
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('-s', '--stories', help='Save the Story Cards in a html file', action='store_true')
        group.add_argument('-c', '--csv', help="generates a CSV file", action='store_true')
        #parser.add_argument('file', help="File to save the result. Either html or csv.")
        args = parser.parse_args()
        
        iters = self.get_iteration_list(args.q.upper())
        
        scrumDo = ScrumDo(args.user, getpass.getpass(), iters)
        iterations_stories_tasks = scrumDo.get_stories_tasks_iteration()
        if args.stories:
            HtmlParser().execute(iterations_stories_tasks)
        elif args.csv:
            proj_categories = scrumDo.get_categories_list()
            CsvParser().execute(iterations_stories_tasks, proj_categories)
#             CsvParser().categories(iterations_stories_tasks, proj_categories)
#             CsvParser().tags(iterations_stories_tasks)
#             CsvParser().epics()
    
    def get_iteration_list(self, q):
        q_args = q.split('-')
        if len(q_args) == 1:
            return [settings.q_iterations[settings.q_iterations.index(q_args[0])]]
        if q_args[0] < q_args[1]:
            i1 = settings.q_iterations.index(q_args[0])
            i2 = settings.q_iterations.index(q_args[1])+1
            return settings.q_iterations[i1:i2]
        else:
            raise Exception("Invalid Arguments for Q range")

class HtmlParser:
    def __init__(self):
        env = Environment(loader=PackageLoader('scrumdo', 'templates'))
        self.tmpl = env.get_template("iterations_template.html")

    def execute(self, storiesTasksIteration, html_file):
        f = os.path.join(os.getcwd(),'scrumdo/html/', html_file)
        self.tmpl.stream(iteration_list = storiesTasksIteration).dump(f)

class CsvParser:
#     def __init__(self):
#         self.csv_path = os.path.join(os.getcwd(),'scrumdo/csv/', csv_file)
#         f = open(self.csv_path, 'wb')
#         self.csv_writer = csv.writer(f)
    
    def execute(self, iterations_stories_tasks, proj_categories):
        self.categories(iterations_stories_tasks, proj_categories)
        self.tags(iterations_stories_tasks)
        self.epics(iterations_stories_tasks)
    
    def create_csv_writer(self, csv_file):
        f = open(os.path.join(os.getcwd(),'scrumdo/csv/', csv_file), 'wb')
        return csv.writer(f)
    
    def csv_categories(self, categories_list):
        self.csv_writer.writerow(categories_list.pop(0))
        for row in categories_list:
            category_row_values = []
            for k in sorted(row[1].keys()):
                category_row_values.append(row[1][k])
            category_row_values.insert(0, row[0])
            self.csv_writer.writerow(category_row_values) 
            
    def csv_tags(self, tags_list):
        tags =  tags_list.pop(0)
        self.csv_writer.writerow(tags)
        for row in tags_list:
            tags_row_values = [0] * (len(tags)-1)
            if row[1].keys():
                for k in sorted(row[1].keys()):
                    tags_row_values[tags.index(k)-1] = row[1][k]
#                    tags_row_values.insert(tags.index(k)-1, row[1][k])
#                 for k in sorted(row[1].keys()):
#                     if k in tags:
#                         tags_row_values.append(row[1][k])
#                     else:
#                         tags_row_values.append(0)
            tags_row_values.insert(0, row[0])
            self.csv_writer.writerow(tags_row_values)
                        
    def tags(self, iterations_stories_tasks):
        row = []
        tags_list = []
        for iteration in iterations_stories_tasks:
            tags_tuple = ()
            tags_dict = {}
            for story in iteration['stories']:
                story_tags_str = story['tags']
                if story_tags_str:
                    story_tags = story_tags_str.split(',')
                    tags_list = sorted(list(set(tags_list) | set(story_tags)))
                    for tag in story_tags:
                        if tag not in tags_dict.keys():
                            tags_dict[tag] = story['points_value']
                        else:
                            tags_dict[tag] = tags_dict[tag] + story['points_value']
            tags_tuple = (iteration['name'], tags_dict)
            row.append(tags_tuple)
        
        tags_list.insert(0, "Sprints")    
        row.insert(0, tags_list)
        
        print row
        self.csv_tags(row)
        
    def categories(self, iterations_stories_tasks, proj_categories):
        categories_list = []
        for iteration in iterations_stories_tasks:
            categories_tuple = ()
            proj_categ_dict = dict(zip(proj_categories, [0 for i in proj_categories]))
            for story in iteration['stories']:
                proj_categ_dict[story['category']] = proj_categ_dict[story['category']] + story['points_value']
            categories_tuple = (iteration["name"], proj_categ_dict)
            categories_list.append(categories_tuple)
        
        proj_categories.insert(0, "Sprints")    
        categories_list.insert(0, proj_categories)  
        
        self.csv_categories(categories_list)
        
    def epics(self, iterations_stories_tasks): 
        for iteration in iterations_stories_tasks:
            for story in iteration['stories']:
                epic_id = story['epic']['id']
                
                

class ScrumDo:
    
    def __init__(self, user, pwd, iters):
        base_url = "%s/api/v2/" % settings.scrumdo_host
        self.api = slumber.API(base_url, auth=(user, pwd))
        self.organization = self.api.organizations.get()[0]
        self.project = self.api.organizations(self.organization["slug"]).projects.get()[0]
        self.q_iteration_list = self.get_q_iterations_to_date(iters)
        
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

    def add_task(self, iteration, story):
        tasks = self.api.organizations(self.organization["slug"]).\
                projects(self.project['slug']).iterations(iteration['id']).\
                stories(story['id']).tasks.get()
        self.fix_task_tags(tasks)
        story["tasks"] = tasks


    def add_comment_as_dict(self, story):
        comment_list = self.api.comments.stories(story["id"]).get()
        if comment_list:
            for comment in comment_list:
                if comment["comment"].startswith("cycle"):
                    story["cycle"] = eval(comment["comment"].split(": ")[1])
                if comment["comment"].startswith("responsive"):
                    story["responsive"] = eval(comment["comment"].split(": ")[1])
    
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
                    
        return self.q_iteration_list
    
    def get_categories_list(self):
        categories = self.project['categories']
        return sorted([cat for cat in categories.split(', ')])
        
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
    CommandLine()
    