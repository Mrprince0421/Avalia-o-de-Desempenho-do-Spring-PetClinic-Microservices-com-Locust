import random
from locust import HttpUser, task, between

FIRST_NAMES = ["Carlos", "Ana", "Bruno", "Daniela", "Eduardo", "Fernanda", "Gabriel", "Helena"]
LAST_NAMES = ["Silva", "Santos", "Oliveira", "Souza", "Pereira", "Ferreira", "Almeida", "Ribeiro"]
CITIES = ["Picos", "Teresina", "Parnaiba", "Floriano", "Campo Maior"]

class ReadProfile(HttpUser):
    """
    Perfil 1 — Leitura:
    - GET /api/customer/owners (45%)
    - GET /api/customer/owners/{id} (35%)
    - GET /api/vet/vets (15%)
    - POST /api/customer/owners (5%)
    """
    weight = 1
    wait_time = between(1, 2)

    @task(45)
    def get_owners(self):
        self.client.get("/api/customer/owners", name="GET /owners")

    @task(35)
    def get_owner_by_id(self):
        owner_id = random.randint(1, 100)
        self.client.get(f"/api/customer/owners/{owner_id}", name="GET /owners/{id}")

    @task(15)
    def get_vets(self):
        self.client.get("/api/vet/vets", name="GET /vets")

    @task(5)
    def post_owner(self):
        payload = {
            "firstName": random.choice(FIRST_NAMES),
            "lastName": random.choice(LAST_NAMES),
            "address": "Rua Exemplo, " + str(random.randint(100, 999)),
            "city": random.choice(CITIES),
            "telephone": f"869{random.randint(10000000, 99999999)}"
        }
        self.client.post("/api/customer/owners", json=payload, name="POST /owners")


class WriteProfile(HttpUser):
    """
    Perfil 2 — Escrita:
    - GET /api/customer/owners (20%)
    - GET /api/customer/owners/{id} (20%)
    - GET /api/vet/vets (20%)
    - POST /api/customer/owners (40%)
    """
    weight = 1
    wait_time = between(1, 2)

    @task(20)
    def get_owners(self):
        self.client.get("/api/customer/owners", name="GET /owners")

    @task(20)
    def get_owner_by_id(self):
        owner_id = random.randint(1, 100)
        self.client.get(f"/api/customer/owners/{owner_id}", name="GET /owners/{id}")

    @task(20)
    def get_vets(self):
        self.client.get("/api/vet/vets", name="GET /vets")

    @task(40)
    def post_owner(self):
        payload = {
            "firstName": random.choice(FIRST_NAMES),
            "lastName": random.choice(LAST_NAMES),
            "address": "Rua Nova, " + str(random.randint(100, 999)),
            "city": random.choice(CITIES),
            "telephone": f"869{random.randint(10000000, 99999999)}"
        }
        self.client.post("/api/customer/owners", json=payload, name="POST /owners")
