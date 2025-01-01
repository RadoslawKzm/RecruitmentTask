import random

from locust import HttpUser, task


class LocustTestAPI(HttpUser):
    @task
    def test_get_project(self):
        project_id = random.randint(11,60)
        self.client.get(f"/project/{project_id}")

    @task
    def test_get_projects(self):
        query_params = {"page": 2, "size": 10}
        self.client.get(f"/projects/list", params=query_params)