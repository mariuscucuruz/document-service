import unittest
import json
import responses
import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../")

from Service.Data import graphQuery


class test_data_retrieval(unittest.TestCase):
    def test_fetch_data_host_and_port_is_none(self):
        # no host or port will lead to hasura_endpoint not being set thus a object has no attribute error
        db = graphQuery.Query()
        db.hasura_endpoint = None
        db.refresh_expire = 999999999999
        db.token_expire = 999999999999
        query = "query getUsers {flintstoneuser {firstname}}"

        result = db.exec(query, {})

        self.assertEqual(result, json.dumps({}))

    def test_fetch_data_host_parse_error(self):
        db = graphQuery.Query()
        db.refresh_expire = 999999999999
        db.token_expire = 999999999999
        query = "{}}"
        result = db.exec(query, {})
        self.assertEqual(result, json.dumps({}))

    def test_fetch_data_pass(self):
        with responses.RequestsMock() as request_mock:
            db = graphQuery.Query()
            query = "query getUsers {flintstoneuser {firstname}}"
            db.refresh_expire = 999999999999
            db.token_expire = 999999999999
            mock_response = {
                "data": {
                    "flintstoneuser": [
                        {"firstname": "Human", "email": "real_human_person@maill.com"}
                    ]
                }
            }
            request_mock.add(
                responses.POST, db.hasura_endpoint, json=mock_response, status=200
            )
            result = db.exec(query, {})
            assert result == json.dumps(mock_response, indent=4)


if __name__ == "__main__":
    unittest.main()
