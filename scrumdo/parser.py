from jinja2 import Environment, PackageLoader
import os, csv

class HtmlParser:
    def __init__(self):
        env = Environment(loader=PackageLoader('scrumdo', 'templates'))
        self.tmpl = env.get_template("iterations_template.html")

    def execute(self, storiesTasksIteration, html_file):
        f = os.path.join(os.getcwd(),'scrumdo/html/', html_file)
        self.tmpl.stream(iteration_list = storiesTasksIteration).dump(f)

class CsvParser:
    def __init__(self):
        pass
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