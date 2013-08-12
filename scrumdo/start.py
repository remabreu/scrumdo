import argparse, getpass
from scrumdo import ScrumDo
from parser import HtmlParser, CsvParser
import local_settings as settings

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
            HtmlParser(iterations_stories_tasks).execute()
        elif args.csv:
            CsvParser(iterations_stories_tasks).execute(scrumDo.project)
    
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
        
if __name__ == '__main__':
    CommandLine()
