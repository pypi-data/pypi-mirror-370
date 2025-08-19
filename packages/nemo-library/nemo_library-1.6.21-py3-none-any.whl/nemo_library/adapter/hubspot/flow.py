from prefect import flow, task

from nemo_library.adapter.hubspot.adapter import HubspotAdapter
from nemo_library.adapter.hubspot.util import ACTIVITY_TYPES

class HubspotFlow:
    def __init__(self):
        self.adapter = HubspotAdapter()

    @flow(name="Hubspot ETL Flow")
    def flow(self):
                
        # extract data from HubSpot
        # deals and deal history
        # self.extract_deals()
        # self.extract_dealhistory()

        # companies associated with deals
        # self.extract_company_associations()
        # self.extract_company_details()
                
        # activities associated with deals (not just ALL activities)
        # self.extract_activity_associations() # first the associations with deals then the activities themselves
        # self.extract_activities()
        
        # TRANSFORM
        self.transform_deals()
        
    @task
    def extract_deals(self):
        """
        Task to extract deals from HubSpot.        
        """
        self.adapter.extract_deals()
        
    @task
    def extract_dealhistory(self):
        """
        Task to extract deal history from HubSpot.
        """
        self.adapter.extract_deal_history()        
    
    @task
    def extract_company_associations(self):
        """
        Task to extract company associations from HubSpot.
        """
        self.adapter.extract_company_associations()
        
    @task
    def extract_company_details(self):
        """
        Task to extract company details from HubSpot.
        """
        self.adapter.extract_company_details()
                
    @task
    def extract_activity_associations(self):
        """
        Task to extract deal history from HubSpot.
        """
        for activity_type in ACTIVITY_TYPES:
            self.extract_activity_association_type(activity_type)
        
    @task
    def extract_activity_association_type(self,activity_type: str):
        """
        Task to extract activities from HubSpot.
        """
        self.adapter.extract_activity_association_type(activity_type)
    
    
    @task
    def extract_activities(self):
        """
        Task to extract activities from HubSpot.
        """
        for activity_type in ACTIVITY_TYPES:
            self.extract_activities_type(activity_type)  
            
    @task
    def extract_activities_type(self,activity_type: str):
        """
        Task to extract activities from HubSpot.
        """
        self.adapter.extract_activities_type(activity_type)

    @task
    def transform_deals(self):
        """
        Task to transform deals data.
        """
        self.adapter.transform_deals()