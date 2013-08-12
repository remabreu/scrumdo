from jinja2 import Environment, PackageLoader
import os, csv

class HtmlParser:
    def __init__(self, stories_tasks_iteration):
        self.stories_tasks_iteration = stories_tasks_iteration
        env = Environment(loader=PackageLoader('scrumdo', 'templates'))
        self.tmpl = env.get_template("iterations_template.html")
        
    def execute(self, ):
        f = os.path.join(os.getcwd(), 'iteration_cards.html')
        self.tmpl.stream(iteration_list = self.stories_tasks_iteration).dump(f)

class CsvParser:
    def __init__(self, iterations_stories_tasks):
        self.iterations_stories_tasks = iterations_stories_tasks
    
    def execute(self, scrumdo_project):
        self.build_categories_csv_list(scrumdo_project["categories_list"])
#        self.build_tags_csv_list(scrumdo_project["tags_list"])
#        self.build_epics_csv_list(scrumdo_project["epics_list"])
    
    def create_csv_writer(self, csv_file):
        f = open(os.path.join(os.getcwd(), csv_file), 'wb')
        return csv.writer(f)
    
    def write_csv_categories(self, categories_list):
        categories_csv_writer = self.create_csv_writer("categories.csv")
        categories_csv_writer.writerow(categories_list.pop(0))
        for row in categories_list:
            category_row_values = []
            for k in sorted(row[1].keys()):
                category_row_values.append(row[1][k])
            category_row_values.insert(0, row[0])
            categories_csv_writer.writerow(category_row_values)
            categories_csv_writer.close() 
            
    def write_csv_tags(self, tags_list):
        tags_csv_writer = self.create_csv_writer("build_tags_csv_list.csv")
        tags =  tags_list.pop(0)
        tags_csv_writer.writerow(tags)
        for row in tags_list:
            tags_row_values = [0] * (len(tags)-1)
            if row[1].keys():
                for k in sorted(row[1].keys()):
                    tags_row_values[tags.index(k)-1] = row[1][k]
#                    tags_row_values.insert(build_tags_csv_list.index(k)-1, row[1][k])
#                 for k in sorted(row[1].keys()):
#                     if k in build_tags_csv_list:
#                         tags_row_values.append(row[1][k])
#                     else:
#                         tags_row_values.append(0)
            tags_row_values.insert(0, row[0])
            tags_csv_writer.writerow(tags_row_values)
            tags_csv_writer.close()
                        
    def build_tags_csv_list(self, tags_list):
        row = []
        tags_list = []
        for iteration in self.iterations_stories_tasks:
            tags_tuple = ()
            tags_dict = {}
            for story in iteration['stories']:
                story_tags_str = story['tags_list']
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
        self.write_csv_tags(row)
        
    def init_dict_content(self, header_list):
        return dict(zip(header_list, [0 for i in header_list]))
    
    def build_dict_content(self, stories, csv_type, dictionary):
        print dictionary
        for story in stories:
            dictionary[story[csv_type]] = dictionary[story[csv_type]] + story['points_value']
        return dictionary
    
    def append_dict(self, iteration_name, dictionary, csv_list):
        csv_tuple = (iteration_name, dictionary)
        return csv_list.append(csv_tuple)
        
    
    def build_categories_csv_list(self, categories_list):
        categories = []
        for iteration in self.iterations_stories_tasks:
            categories_dict = {}
            categories_dict = self.init_dict_content(categories_list)
            categories_dict = self.build_dict_content(iteration["stories"], "category", categories_dict)
#            categories = self.append_dict(iteration["name"], categories_dict, categories_list)
            categories_tuple = (iteration["name"], categories_dict)
            categories.append(categories_tuple)
        
        categories_list.insert(0, "Sprints")    
        categories.insert(0, categories_list)  
        
        print categories
        self.write_csv_categories(categories)
        

    def build_epics_csv_list(self, epics_list): 
        pass
#         for iteration in iterations_stories_tasks:
#             for story in iteration['stories']:
#                 epic_id = story['epic']['summary']
                
                
                
                