import unittest
from datetime import datetime, timezone
from cancellation_policy_pkg.CancellationPolicyLib import CancellationPolicy

class TestCancellationPolicyLib(unittest.TestCase):
    
    def setUp(self):
        self.check_in_date = "2024-06-25T23:00:00"
        self.handler = CancellationPolicy(self.check_in_date)

    def test_format_date_default(self):
        # Test format_date with default argument (current datetime)
        formatted_date = self.handler.format_date()
        self.assertEqual(formatted_date, self.handler.current_datetime.strftime("%Y-%m-%d %H:%M:%S"))

    def test_format_date_given(self):
        # Test format_date with a given date string
        date_str = "2024-06-25T23:00:00"
        formatted_date = self.handler.format_date(date_str)
        expected_date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
        self.assertEqual(formatted_date, expected_date)

    def test_dida_date_format(self):
        # Test dida_date_format
        date_str = "2024-06-25"
        formatted_date = self.handler.dida_date_format(date_str)
        expected_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d %H:%M:%S")
        self.assertEqual(formatted_date, expected_date)

    def test_hp_format_date(self):
        # Test hp_format_date with various formats
        date_str_1 = "2024-06-25T23:00:00Z"
        date_str_2 = "06/25/2024"
        date_str_3 = "25/06/2024"
        expected_date_1 = datetime.strptime(date_str_1, "%Y-%m-%dT%H:%M:%SZ")
        expected_date_2 = datetime.strptime(date_str_2, "%m/%d/%Y")
        expected_date_3 = datetime.strptime(date_str_3, "%d/%m/%Y")

        self.assertEqual(self.handler.hp_format_date(date_str_1), expected_date_1)
        self.assertEqual(self.handler.hp_format_date(date_str_2), expected_date_2)
        self.assertEqual(self.handler.hp_format_date(date_str_3), expected_date_3)

    def test_tbo_format_date(self):
        # Test tbo_format_date
        date_str = "25-06-2024 23:00:00"
        formatted_date = self.handler.tbo_format_date(date_str)
        expected_date = datetime.strptime(date_str, "%d-%m-%Y %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
        self.assertEqual(formatted_date, expected_date)
    # Test parse cancellation policy 
    def test_parse_cancellation_policies(self):
        # Mock input data and expected output
        free_cancellation = True
        total_partner = 100.0
        parsed_policies = [
            {'start': '2024-06-20 00:00:00', 'end': '2024-06-22 00:00:00', 'amount': 0},
            {'start': '2024-06-22 00:00:00', 'end': '2024-07-05 00:00:00', 'amount': 100}
        ]
        expected_output = {
            'type': 'Free cancellation',
            'text': ['Receive a 100% refund for your booking if you cancel before 22 Jun 2024 at 12:00 AM',
                    'If you cancel your reservation after 22 Jun 2024 12:00 AM, you will not receive a refund. The booking will be non-refundable.']
        }
        # Call the method
        result = self.handler.parse_cancellation_policies(free_cancellation, total_partner, parsed_policies)

        # Assert equality
        self.assertEqual(result, expected_output)
    # Test parse_ratehawk_cancellation_policy with sample data
    def test_parse_ratehawk_cancellation_policy(self):
        ratehawk_room_data = [
            {
                "cancellation_penalties": {
                    "policies": [
                        {
                            "start_at": None,
                            "end_at": "2024-06-17T17:00:00",
                            "amount_charge": "0.00",
                            "amount_show": "0.00",
                        },
                        {
                            "start_at": "2024-06-17T17:00:00",
                            "end_at": "2024-06-19T17:00:00",
                            "amount_charge": "0.00",
                            "amount_show": "10.00",
                        },
                        {
                            "start_at": "2024-06-19T17:00:00",
                            "end_at": "2024-06-22T17:00:00",
                            "amount_charge": "0.00",
                            "amount_show": "22.10",
                        }
                    ],
                    "free_cancellation_before": ""
                },
                "currency_code": "USD"
            }
        ]
        expected_output = [
            {
                'start': self.handler.current_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                'end': self.handler.format_date("2024-06-17T17:00:00"),
                'amount': '0.00',
                'currency': "USD"
            },
            {
                'start': self.handler.format_date("2024-06-17T17:00:00"),
                'end': self.handler.format_date("2024-06-19T17:00:00"),
                'amount': '10.00',
                'currency': "USD"
            },
            {
                'start': self.handler.format_date("2024-06-19T17:00:00"),
                'end': self.handler.format_date("2024-06-22T17:00:00"),
                'amount': '22.10',
                'currency': "USD"
            }
        ]
        result = self.handler.parse_ratehawk_cancellation_policy(ratehawk_room_data)
        self.assertEqual(result, expected_output)

    # Test parse_rakuten_cancellation_policy with sample data
    def test_parse_rakuten_cancellation_policy(self):
        rakuten_room_data = {
            'cancellation_policy': {
                'cancellation_policies': [
                    {
                        'date_from': '2024-06-13T17:00:00',
                        'date_to': '2024-06-18T17:00:00',
                        'penalty_percentage': 0
                    },
                    {
                        'date_from': '2024-06-18T17:00:00',
                        'date_to': '2024-06-22T17:00:00',
                        'penalty_percentage': 60
                    }
                ]
            },
            'room_info': {
                'room_rate_currency': 'USD',
                'room_rate': 200.0
            }
        }
       
        rakuten_expected_output = [
            {'start': self.handler.current_datetime.strftime("%Y-%m-%d %H:%M:%S"), 'end': '2024-06-18 17:00:00', 'amount': 0.0, 'currency': 'USD'}, {'start': '2024-06-18 17:00:00', 'end': '2024-06-22 17:00:00', 'amount': 4.0, 'currency': 'USD'}
        ]
        rakuten_result = self.handler.parse_rakuten_cancellation_policy(rakuten_room_data)
        self.assertEqual(rakuten_result, rakuten_expected_output)

    # Test parse_dida_cancellation_policy with sample data
    def test_parse_dida_cancellation_policy(self):
        # Example usage
        dida_pricing = {
            'RatePlanCancellationPolicyList': [
                {'FromDate': '2024-06-16', 'Amount': 0},
                {'FromDate': '2024-06-18', 'Amount': 50},
                {'FromDate': '2024-06-22', 'Amount': 100}
            ],
            'Currency': 'USD'
        }
        total_price = 100
        dida_expected_output = [
            {'start': self.handler.current_datetime.strftime("%Y-%m-%d %H:%M:%S"), 'end': '2024-06-16 00:00:00', 'amount': 0, 'currency': 'USD'}, {'start': '2024-06-16 00:00:00', 'end': '2024-06-18 00:00:00', 'amount': 50, 'currency': 'USD'}, {'start': '2024-06-18 00:00:00', 'end': '2024-06-22 00:00:00', 'amount': 100, 'currency': 'USD'}
        ]
        dida_result = self.handler.parse_dida_cancellation_policy(dida_pricing,total_price)
        self.assertEqual(dida_result, dida_expected_output)

    # Test parse_hp_cancellation_policy with sample data
    def test_parse_hp_cancellation_policy(self):
        # Example usage
        pricing_hp = {
            "nonRefundable": False,
            "freeCancellationCutOff": "",
                "cancelPenalties": [
                    {
                    "deadline": "07/01/2024",
                    "noShow": False,
                    "price": 50,
                    "amount": 50,
                    "text": "Cancel after 06/30/2024 00:00 AM  LOCAL HOTEL TIME: $567.58",
                    "type": "price"
                    },
                    {
                    "deadline": "06/30/2024",
                    "noShow": False,
                    "price": 0,
                    "amount": 0,
                    "text": "Cancel before 06/30/2024 00:00 AM LOCAL HOTEL TIME: FREE",
                    "type": "price"
                    }
                ],
            "text": "Free cancellation before 2024-06-28 12:00:AM",
            "timezoneTag": "LOCAL HOTEL TIME",
            "freeCancellation": False,
            "prePaid": True,
            "currencyCode": "USD"
        }
        total_hp = 100.0
        hp_expected_output = [
            {'start': self.handler.current_datetime.strftime("%Y-%m-%d %H:%M:%S"), 'end': '2024-06-30 00:00:00', 'amount': 0, 'currency': 'USD'}, {'start': '2024-06-30 00:00:00', 'end': '2024-07-01 00:00:00', 'amount': 50.0, 'currency': 'USD'}
        ]
        hp_result = self.handler.parse_hp_cancellation_policy(pricing_hp,total_hp)
        self.assertEqual(hp_result, hp_expected_output)

    # Test parse_tbo_cancellation_policy with sample data
    def test_parse_tbo_cancellation_policy(self):
        # Example usage
        pricing_tbo = [
                {"FromDate": "28-06-2024 00:00:00", "ChargeType": "Percentage", "CancellationCharge": 0.00},
                {"FromDate": "12-07-2024 00:00:00", "ChargeType": "Fixed", "CancellationCharge": 10.00},
                {"FromDate": "15-10-2024 00:00:00", "ChargeType": "Percentage", "CancellationCharge": 100.00}
            ]
        total_tbo = 100.0
        tbo_expected_output = [
            {'start': self.handler.current_datetime.strftime("%Y-%m-%d %H:%M:%S"), 'end': '2024-06-28 00:00:00', 'amount': 0.0, 'currency': 'USD'}, {'start': '2024-06-28 00:00:00', 'end': '2024-07-12 00:00:00', 'amount': 90.0, 'currency': 'USD'}, {'start': '2024-07-12 00:00:00', 'end': '2024-10-15 00:00:00', 'amount': 100.0, 'currency': 'USD'}
        ]
        tbo_result = self.handler.parse_tbo_cancellation_policy(pricing_tbo,total_tbo)
        self.assertEqual(tbo_result, tbo_expected_output)

    def test_parse_tourmind_cancellation_policy(self):
        # Sample tourmind message
        tourmind_room_data = {
            "bedTypeDesc": "2 Twin Bunk Beds",
            "bedTypeDescCN": "2 张单人双层床",
            "RateCode": "153263498",
            "Name": "Family Quadruple Room",
            "NameCN": "家庭四人房",
            "Allotment": 3,
            "CurrencyCode": "USD",
            "TotalPrice": 1609,
            "MealInfo": {
                "MealType": "1",
                "MealCount": 0
            },
            "Refundable": True,
            "CancelPolicyInfos": [
                {
                    "StartDateTime": "2025-03-26",
                    "EndDateTime": "2025-03-27",
                    "Amount": 1609,
                    "CurrencyCode": "CNY",
                    "From": "2025-03-26 00:00:00",
                    "To": "2025-03-27 23:59:59"
                }
            ],
            "DailyPriceInfo": [
                {
                    "Date": "2025-03-27",
                    "Price": 1609,
                    "Count": 3
                }
            ],
            "price_details": {
                "unit_price": 5,
                "price_per_night": 5,
                "price_without_taxes": 5,
                "taxes_included": 5,
                "srp_taxes_included": 5,
                "cn_fees": 5,
                "property_fee": 5,
                "due_at_property": 5,
                "pay_now": 5,
                "no_of_nights": 5
            }
        }

        total_price = 1609
        guest_rate = 1.0
        host_rate = 6.5  # Assuming 1 USD = 6.5 CNY for conversion

        # Expected output
        expected_output = {
            'type': 'Free Cancellation',
            'text': [
                'Receive a 100% refund for your booking if you cancel before 26 Mar 2025 at 12:00 AM',
                'If you cancel your reservation after 26 Mar 2025 12:00 AM, you will not receive a refund. The booking will be non-refundable.'
            ]
        }

        # Call the method
        result = self.handler.parse_tourmind_cancellation_policy(tourmind_room_data, total_price, guest_rate, host_rate)

        # Assert equality
        self.assertEqual(result, expected_output)
    
if __name__ == "__main__":
    unittest.main()
