import unittest
from messagedb import Message, MessageDB


class TestMessageDBClass(unittest.TestCase):

    def setUp(self):
        # Initialize the database with a test database
        self.db = MessageDB(":memory:")
        self.db.create_tables()

    def tearDown(self):
        # Close the database connection after each test
        self.db.close()

    def test_add_and_get_phone_number(self):
        phone_id = self.db.add_phone_number("+1234567890")
        self.assertIsNotNone(phone_id)

        retrieved_phone_number = self.db.get_phone_number(phone_id)
        self.assertEqual(retrieved_phone_number, "+1234567890")

    def test_add_and_get_messages_for_phone_number(self):
        self.db.add_phone_number("+1111111111")
        self.db.add_phone_number("+2222222222")

        self.db.add_message("SID123", "+1111111111", "+2222222222", "Hello, how are you?")
        self.db.add_message("SID456", "+2222222222", "+1111111111", "I'm good. How about you?")
        self.db.add_message("SID789", "+1111111111", "+2222222222", "I'm doing great!")

        messages = self.db.get_messages_for_phone_number("+1111111111")
        self.assertEqual(len(messages), 3)
        self.assertEqual(messages[0].body, "Hello, how are you?")
        self.assertEqual(messages[1].body, "I'm good. How about you?")
        self.assertEqual(messages[2].body, "I'm doing great!")
        
    def test_add_and_get_system_prompt(self):
        system_prompt_id = self.db.add_system_prompt("Please say your name.")
        self.assertIsNotNone(system_prompt_id)

        retrieved_system_prompt = self.db.get_system_prompt(system_prompt_id)
        self.assertEqual(retrieved_system_prompt, "Please say your name.")

    def test_add_and_get_settings_for_phone_number(self):
        self.db.add_phone_number("+1234567890")
        system_prompt_id = self.db.add_system_prompt("Please say your name.")
        settings_id = self.db.add_settings("+1234567890", system_prompt_id=system_prompt_id, stop_sequence="!end", max_tokens=100, temperature=0.7)
        self.assertIsNotNone(settings_id)

        settings = self.db.get_settings_for_phone_number("+1234567890")
        self.assertIsNotNone(settings)
        self.assertEqual(settings["system_prompt"], "Please say your name.")
        self.assertEqual(settings["stop_sequence"], "!end")
        self.assertEqual(settings["max_tokens"], 100)
        self.assertEqual(settings["temperature"], 0.7)

    def test_update_settings_for_phone_number(self):
        self.db.add_phone_number("+1234567890")
        system_prompt_id = self.db.add_system_prompt("Please say your name.")
        settings_id = self.db.add_settings("+1234567890", system_prompt_id=system_prompt_id, stop_sequence="!end", max_tokens=100, temperature=0.7)
        self.assertIsNotNone(settings_id)

        self.db.update_settings_for_phone_number("+1234567890", stop_sequence="!end!", max_tokens=200, temperature=0.8)

        settings = self.db.get_settings_for_phone_number("+1234567890")
        self.assertIsNotNone(settings)
        self.assertEqual(settings["system_prompt"], "Please say your name.")
        self.assertEqual(settings["stop_sequence"], "!end!")
        self.assertEqual(settings["max_tokens"], 200)
        self.assertEqual(settings["temperature"], 0.8)
        

if __name__ == "__main__":
    unittest.main()
