import unittest
from contacts_manager import validate_phone, validate_email, search_contacts

class TestContactManager(unittest.TestCase):
    
    def test_phone_validation(self):
        # Valid cases
        self.assertTrue(validate_phone("+1 (234) 567-8900")[0])
        self.assertEqual(validate_phone("123-456-78901")[1], "12345678901")
        
        # Invalid cases
        self.assertFalse(validate_phone("12345")[0])
        self.assertFalse(validate_phone("abcdefghijk")[0])

    def test_email_validation(self):
        self.assertTrue(validate_email("test@example.com"))
        self.assertTrue(validate_email("user.name+tag@domain.co.uk"))
        self.assertFalse(validate_email("invalid-email@"))
        self.assertFalse(validate_email("plain-string"))

if __name__ == '__main__':
    unittest.main()
