import logging
import requests
import json


from commands.commandbase import CommandBase


log = logging.getLogger("").getChild(__name__)


class Validate(CommandBase):

    def __init__(
        self,
        new_schema: dict,
    ):
        self.new_schema = new_schema

        super(Validate, self).__init__()

    def run(self):
        print("its Validate")
        self.validate()

    def validate(self):
        # https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html
        # https://docs.confluent.io/platform/current/schema-registry/index.html#schemaregistry-intro
        # Backward compatibility

        # TODO: replace with real host
        schema_registry_url: str = "http://localhost:8081"
        subject: str = "my-subject"
        # new_schema: dict = {
        #     "schema": json.dumps(
        #         {
        #             "type": "record",
        #             "name": "TestSchema",
        #             "fields": [{"name": "field1", "type": "string"}],
        #         }
        #     )
        # }

        response: requests.Response = requests.post(
            f"{schema_registry_url}/compatibility/subjects/{subject}/versions/latest",
            headers={"Content-Type": "application/vnd.schemaregistry.v1+json"},
            data=json.dumps(self.new_schema),
        )

        result = response.json()
        if result.get("is_compatible"):
            print("Schema is compatible")
        else:
            print("Schema is NOT compatible")
