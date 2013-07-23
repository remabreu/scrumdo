'''
Created on Jul 15, 2013

@author: rodrigo.abreu
'''

import local_settings as settings
import slumber, pprint, re
from datetime import datetime 

class ScrumDo:
    
    def __init__(self):
        base_url = "%s/api/v2/" % settings.scrumdo_host
        self.api = slumber.API(base_url, auth=(settings.scrumdo_username, 
                                          settings.scrumdo_password))
        self.organization = self.api.organizations.get()[0]
        self.project = self.api.organizations(self.organization["slug"]).projects.get()[0]
        self.q_iteration_list = self.getQIterationsToDate("Q3")
        
    def main(self):
                
#        story_list = api.organizations(organization["slug"]).projects(project['slug']).iterations(iteration['id']).stories.get()
    #     for iteration in iteration_list:
    #         print "\t\t%s %s to %s" % (iteration['name'], 
    #                                 iteration['start_date'], 
    #                                 iteration['end_date'])
        #TODO: set quartil as program parameter
        
        self.getStoriesTasksIteration()
        #self.printIteration()
        self.pprintIteration()
    
#     def getIterations(self):
#         for it in self.q_iteration_list:
    def pprintIteration(self):
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(self.q_iteration_list[0])
                
    def printIteration(self):
        print self.q_iteration_list
        for it in self.q_iteration_list:
            print "Name: %s Start Date: %s - End Date: %s" %\
                    (it["name"], it["start_date"], it["end_date"])
            for st in it["stories"]:
#                 print st.keys()
                print "\tStory Name: %s -- Points: %s -- Total Points: %d" % (st["summary"], st["points"], st["points_value"])
                for tsk in st["tasks"]:
                    print "\t\tTask Name: %s -- Tags: %s" % (tsk["summary"], tsk["tags"])

    def fixTaskTags(self, tasks):
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
                
    def getStoriesTasksIteration(self):
        for iteration in self.q_iteration_list:
            stories = self.api.organizations(self.organization["slug"]).\
            projects(self.project['slug']).iterations(iteration['id']).stories.get()
            iteration["stories"] = stories
            for story in stories:
                tasks = self.api.organizations(self.organization["slug"]).\
                        projects(self.project['slug']).iterations(iteration['id']).\
                        stories(story['id']).tasks.get()
                self.fixTaskTags(tasks)
                story["tasks"] = tasks
        
        return self.q_iteration_list
        
    def getQIterationsToDate(self, q_id):
        today = datetime.today()
        iteration_list = self.api.organizations(self.organization["slug"]).projects(self.project['slug']).iterations.get()
        return [iteration for iteration in iteration_list if q_id \
               in iteration['name'] and datetime.strptime(iteration['end_date'],
               "%Y-%m-%d") < today]
#         for iteration in self.iteration_list:
#             if q_id in iteration['name'] and datetime.strptime(iteration['end_date'],
#                                                                "%Y-%m-%d") < today:
#                 
#                 start_date = datetime.strptime(iteration['start_date'],"%Y-%m-%d") 
#                 end_date = datetime.strptime(iteration['end_date'],"%Y-%m-%d")
#                 print "%s %s (%s) to %s (%s)" % (iteration['name'],
#                                     iteration['start_date'],    
#                                     start_date.strftime("%A"), 
#                                     iteration['end_date'],
#                                     end_date.strftime("%A"))
#     
        
    #     print organization_list
    #     
    #     for organization in organization_list:
    #         project_list = api.organizations(organization["slug"]).projects.get()
    #         
    #         for project in project_list:
    #             
                    
 
if __name__ == '__main__':
    ScrumDo().main()
    