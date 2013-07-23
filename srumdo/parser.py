from jinja2 import Environment, PackageLoader
from scrumdo import *

class Parser:
    def __init__(self):
        env = Environment(loader=PackageLoader('scrumdo', 'templates'))
        self.tmpl = env.get_template("iterations_template.html")

    def execute(self):
        scrumDo = ScrumDo()
        self.tmpl.stream(iteration_list = scrumDo.getStoriesTasksIteration()
                         ).dump("html/test.html")
        
if __name__ == '__main__':
    Parser().execute()