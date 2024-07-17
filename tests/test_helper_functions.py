import unittest
from helpers import extract_ids, is_valid_uuid


class test_helper_functions(unittest.TestCase):
    def test_is_valid_uuid_valid(self):
        test_data = "e817acd5-e32a-4116-8525-aefaffffa81c"
        expected_output = True

        actual_output = is_valid_uuid(test_data)

        self.assertEqual(expected_output, actual_output, "outputs are not equal")

    def test_is_valid_uuid_invalid(self):
        test_data = "c9bf9e58"
        expected_output = False

        actual_output = is_valid_uuid(test_data)

        self.assertEqual(expected_output, actual_output, "outputs are not equal")

    def test_is_valid_uuid_invalid_int(self):
        test_data = 123
        expected_output = False

        actual_output = is_valid_uuid(test_data)

        self.assertEqual(expected_output, actual_output, "outputs are not equal")

    def test_extract_ids_cache_invoice_response(self):
        expected_output = (
            "e13138c2-00d7-48b8-8820-f1b381a0b880",
            "e817acd5-e32a-4116-8525-aefaffffa81c",
        )

        test_data = """
        	mutation cacheInvoice {
                InvoiceResponse(objects: {invoice_id: "e13138c2-00d7-48b8-8820-f1b381a0b880", invoice_uuid: "e817acd5-e32a-4116-8525-aefaffffa81c"}) {
                    returning {
                        InvoiceResponse {
                            invoice_uuid
                        }
                    }
                }
            }
        """

        actual_output = extract_ids(test_data, "invoice_id", "invoice_uuid")

        self.assertEqual(expected_output, actual_output, "outputs are not equal")

if __name__ == "__main__":
    unittest.main()
