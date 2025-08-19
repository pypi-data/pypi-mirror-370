import json
import time
import requests
from datetime import datetime, timedelta, timezone
class TelemetryLogger:
    def __init__(self, loki_url, user, password, default_env="production", org_id="cuddlynest"):
        self.loki_url = loki_url
        self.auth = (user, password)
        self.default_env = default_env
        self.org_id = org_id

    def log_error(self, action, error_code, message, http_status, response=None, job="cancellation-policy"):
        data = {
            "event": "cancellation-policy",
            "action": action,
            "error_code": error_code,
            "error_message": message,
            "http_status": http_status,
            "timestamp": datetime.utcnow().isoformat(),
            "job": job,
            "response_data": response  # Add response data to error logs
        }
        self._log("error", data)

    def log_response_time(self, action, duration_ms, http_status, response=None, job="cancellation_policy"):
        data = {
            "event": "api_response_time",
            "action": action,
            "response_time_ms": duration_ms,
            "data_source": "real_time",
            "http_status": http_status,
            "timestamp": datetime.utcnow().isoformat(),
            "job": job,
            "response_data": response  # Add response data to success logs
        }
        self._log("info", data)

    def _log(self, level, data):
        timestamp = str(int(time.time() * 1e9))
        stream = {
            "cancellation_api": data.get("job", "cancellation-policy"),
            "env": self.default_env,
            "level": level,
            "action": data.get("action", "unknown")
        }
        entry = {
            "stream": stream,
            "values": [[timestamp, json.dumps(data)]]
        }
        self._send_to_loki([entry])

    def _send_to_loki(self, streams):
        payload = json.dumps({"streams": streams})
        headers = {
            "Content-Type": "application/json",
            "X-Scope-OrgID": self.org_id
        }
        try:
            response = requests.post(
                self.loki_url, data=payload,
                headers=headers, auth=self.auth, timeout=5
            )
            if not response.ok:
                print(f"Loki responded with HTTP {response.status_code}: {response.text}")
        except requests.RequestException as e:
            print(f"Loki log error: {str(e)}")

# Initialize TelemetryLogger (you'll need to provide your credentials)
telemetry_logger = TelemetryLogger(
    loki_url="https://loki.cuddlynest.com/loki/api/v1/push",
    user="admin",
    password="a3LJuB91Xk1P"
)
from datetime import datetime, timedelta, timezone
# import pytz
from typing import List, Dict, Any, Optional
from dateutil import parser
import json
import os
import pytz
import sys


class CancellationPolicy:
    def __init__(self, check_in_date: str, countryname: str = None):
        try:
            self.countryname = countryname.title() if countryname else None
            aliases = ["us", "usa", "united states", "united states of america", "u.s.", "Us"]
            if self.countryname and self.countryname.strip().lower() in aliases:
                self.countryname = "USA"
            current_datetime_utc = datetime.now(timezone.utc)
            self.current_datetime = current_datetime_utc
            self.current_datetime = self.current_datetime.strftime("%Y-%m-%d %H:%M:%S")
            self.free_cancellation_policy = None
            self.check_in_date = check_in_date + "T23:00:00"
            self.partner_cp = []
            self.cn_polices = []
            self.country_timezone_min = None
            self.country_timezone_hour = 0
            self.all_timezones = {
                "UTC": "UTC",
                "UTC+01:00": "+1",
                "UTC+01:30": "+1:30",
                "UTC+02:00": "+2",
                "UTC+02:300": "+2:30",
                "UTC+03:00": "+3",
                "UTC+03:30": "+3:30",
                "UTC+04": "+4",
                "UTC+04:00": "+4",
                "UTC+04:30": "+4:30",
                "UTC+05:00": "+5",
                "UTC+05:30": "+5:30",
                "UTC+05:45": "+5:45",
                "UTC+06:00": "+6",
                "UTC+06:30": "+6:30",
                "UTC+07:00": "+7",
                "UTC+07:30": "+7:30",
                "UTC+08:00": "+8",
                "UTC+08:30": "+8:30",
                "UTC+08:45": "+8:45",
                "UTC+09:00": "+9",
                "UTC+09:30": "+9:30",
                "UTC+10:00": "+10",
                "UTC+10:30": "+10:30",
                "UTC+11:00": "+11",
                "UTC+11:30": "+11:30",
                "UTC+12:00": "+12",
                "UTC+12:30": "+12:30",
                "UTC+12:45": "+12:45",
                "UTC+13:00": "+13",
                "UTC+13:30": "+13:30",
                "UTC+14:00": "+14",
                "UTC-01:00": "-1",
                "UTC-01:30": "-1:30",
                "UTC-02:00": "-2",
                "UTC-02:30": "-2:30",
                "UTC-03:00": "-3",
                "UTC-03:30": "-3:30",
                "UTC-04:00": "-4",
                "UTC-04:30": "-4:30",
                "UTC-05:00": "-5",
                "UTC-05:30": "-5:30",
                "UTC-05:45": "-5:45",
                "UTC-06:00": "-6",
                "UTC-06:30": "-6:30",
                "UTC-07:00": "-7",
                "UTC-07:30": "-7:30",
                "UTC-08:00": "-8",
                "UTC-08:30": "-8:30",
                "UTC-09:00": "-9",
                "UTC-09:30": "-9:30",
                "UTC-10:00": "-10",
                "UTC-10:30": "-10:30",
                "UTC-11:00": "-11",
                "UTC-11:30": "-11:30",
                "UTC-12:00": "-12",
                "UTC-12:30": "-12:30",
                "UTC-13:00": "-13",
                "UTC-13:30": "-13:30",
                "UTC-14:00": "-14",
                "UTC-15:00": "-15",
                "UTC-16:00": "-16",
            }

            # List of possible input date formats
            self.possible_date_formats = [
                "%Y-%m-%d %H:%M:%S",
                "%Y/%m/%d %H:%M:%S",
                "%d-%m-%Y %H:%M:%S",
                "%d/%m/%Y %H:%M:%S",
                "%m-%d-%Y %H:%M:%S",
                "%m/%d/%Y %H:%M:%S",
                "%m/%d/%Y %H:%M",
                "%Y-%m-%dT%H:%M:%SZ",
                "%m/%d/%Y",
                "%Y-%m-%d",
                "%d-%m-%Y",
                "%y-%m-%d",
                "%d-%m-%y",
                "%Y-%m-%dT%H:%M:%S",
            ]
            self.get_country_timezone(self.countryname)
        except Exception as e:
            telemetry_logger.log_error("CancellationPolicy_init", "INIT_ERROR", str(e), 500, job="cancellation-policy")
            raise

    def country_list(self):
        try:
            return [{"Afghanistan": {"timezones": "UTC+04:30", "alt_spellings": "AF"}},
                {"Akrotiri and Dhekelia": {"timezones": "UTC+03:30", "alt_spellings": "AK"}},
                {"Western Sahara": {"timezones": "UTC+01:00", "alt_spellings": "Western Sahara"}},
                {"Vietnam": {"timezones": "UTC+07:00", "alt_spellings": "Vietnam"}},
                {"Albania": {"timezones": "UTC+02:00", "alt_spellings": "AL"}},
                {"Algeria": {"timezones": "UTC+01:00", "alt_spellings": "DZ"}},
                {"American Samoa": {"timezones": "UTC-11:00", "alt_spellings": "AS"}},
                {"Andorra": {"timezones": "UTC+02:00", "alt_spellings": "AD"}},
                {"Angola": {"timezones": "UTC+01:00", "alt_spellings": "AO"}},
                {"Anguilla": {"timezones": "UTC-04:00", "alt_spellings": "AI"}},
                {"Antarctica": {"timezones": "UTC+08:00", "alt_spellings": "AQ"}},
                {"Antarctica": {"timezones": "UTC+07:00", "alt_spellings": "AQ"}},
                {"Antarctica": {"timezones": "UTC+10:00", "alt_spellings": "AQ"}},
                {"Antarctica": {"timezones": "UTC+05:00", "alt_spellings": "AQ"}},
                {"Antarctica": {"timezones": "UTC+12:00", "alt_spellings": "AQ"}},
                {"Antarctica": {"timezones": "UTC-03:00", "alt_spellings": "AQ"}},
                {"Antarctica": {"timezones": "UTC-03:00", "alt_spellings": "AQ"}},
                {"Antarctica": {"timezones": "UTC+03:00", "alt_spellings": "AQ"}},
                {"Antarctica": {"timezones": "UTC+02:00", "alt_spellings": "AQ"}},
                {"Antarctica": {"timezones": "UTC+05:00", "alt_spellings": "AQ"}},
                {"Antigua and Barbuda": {"timezones": "UTC-04:00", "alt_spellings": "AG"}},
                {"Argentina": {"timezones": "UTC-03:00", "alt_spellings": "AR"}},
                {"Argentina": {"timezones": "UTC-03:00", "alt_spellings": "AR"}},
                {"Argentina": {"timezones": "UTC-03:00", "alt_spellings": "AR"}},
                {"Argentina": {"timezones": "UTC-03:00", "alt_spellings": "AR"}},
                {"Argentina": {"timezones": "UTC-03:00", "alt_spellings": "AR"}},
                {"Czechia": {"timezones": "UTC+02:00", "alt_spellings": "Czechia"}},
                {"Argentina": {"timezones": "UTC-03:00", "alt_spellings": "AR"}},
                {"Argentina": {"timezones": "UTC-03:00", "alt_spellings": "AR"}},
                {"Argentina": {"timezones": "UTC-03:00", "alt_spellings": "AR"}},
                {"Argentina": {"timezones": "UTC-03:00", "alt_spellings": "AR"}},
                {"Argentina": {"timezones": "UTC-03:00", "alt_spellings": "AR"}},
                {"Argentina": {"timezones": "UTC-03:00", "alt_spellings": "AR"}},
                {"Argentina": {"timezones": "UTC-03:00", "alt_spellings": "AR"}},
                {"Armenia": {"timezones": "UTC+04:00", "alt_spellings": "AM"}},
                {"Aruba": {"timezones": "UTC-04:00", "alt_spellings": "AW"}},
                {"Australia": {"timezones": "UTC+10:00", "alt_spellings": "AU"}},
                {"Australia": {"timezones": "UTC+09:30", "alt_spellings": "AU"}},
                {"Australia": {"timezones": "UTC+10:00", "alt_spellings": "AU"}},
                {"Australia": {"timezones": "UTC+09:30", "alt_spellings": "AU"}},
                {"Australia": {"timezones": "UTC+09:30", "alt_spellings": "AU"}},
                {"Australia": {"timezones": "UTC+08:45", "alt_spellings": "AU"}},
                {"Australia": {"timezones": "UTC+10:00", "alt_spellings": "AU"}},
                {"Australia": {"timezones": "UTC+10:00", "alt_spellings": "AU"}},
                {"Australia": {"timezones": "UTC+10:30", "alt_spellings": "AU"}},
                {"Australia": {"timezones": "UTC+10:00", "alt_spellings": "AU"}},
                {"Australia": {"timezones": "UTC+08:00", "alt_spellings": "AU"}},
                {"Australia": {"timezones": "UTC+10:00", "alt_spellings": "AU"}},
                {"Austria": {"timezones": "UTC+02:00", "alt_spellings": "AT"}},
                {"Azerbaijan": {"timezones": "UTC+04:00", "alt_spellings": "AZ"}},
                {"Bahamas": {"timezones": "UTC-04:00", "alt_spellings": "BS"}},
                {"Bahrain": {"timezones": "UTC+03:00", "alt_spellings": "BH"}},
                {"Bangladesh": {"timezones": "UTC+06:00", "alt_spellings": "BD"}},
                {"Barbados": {"timezones": "UTC-04:00", "alt_spellings": "BB"}},
                {"Belarus": {"timezones": "UTC+03:00", "alt_spellings": "BY"}},
                {"Belgium": {"timezones": "UTC+02:00", "alt_spellings": "BE"}},
                {"Belize": {"timezones": "UTC-06:00", "alt_spellings": "BZ"}},
                {"Benin": {"timezones": "UTC+01:00", "alt_spellings": "BJ"}},
                {"Bermuda": {"timezones": "UTC-03:00", "alt_spellings": "BM"}},
                {"Bhutan": {"timezones": "UTC+06:00", "alt_spellings": "BT"}},
                {"Bolivia, Plurinational State of": {"timezones": "UTC-04:00", "alt_spellings": "BO"}},
                {"Bonaire, Sint Eustatius and Saba": {"timezones": "UTC-04:00", "alt_spellings": "BQ"}},
                {"Bosnia and Herzegovina": {"timezones": "UTC+02:00", "alt_spellings": "BA"}},
                {"Botswana": {"timezones": "UTC+02:00", "alt_spellings": "BW"}},
                {"Brazil": {"timezones": "UTC-03:00", "alt_spellings": "BR"}},
                {"Brazil": {"timezones": "UTC-03:00", "alt_spellings": "BR"}},
                {"Brazil": {"timezones": "UTC-03:00", "alt_spellings": "BR"}},
                {"Brazil": {"timezones": "UTC-04:00", "alt_spellings": "BR"}},
                {"Brazil": {"timezones": "UTC-04:00", "alt_spellings": "BR"}},
                {"Brazil": {"timezones": "UTC-04:00", "alt_spellings": "BR"}},
                {"Brazil": {"timezones": "UTC-05:00", "alt_spellings": "BR"}},
                {"Brazil": {"timezones": "UTC-03:00", "alt_spellings": "BR"}},
                {"Brazil": {"timezones": "UTC-03:00", "alt_spellings": "BR"}},
                {"Brazil": {"timezones": "UTC-04:00", "alt_spellings": "BR"}},
                {"Brazil": {"timezones": "UTC-02:00", "alt_spellings": "BR"}},
                {"Brazil": {"timezones": "UTC-04:00", "alt_spellings": "BR"}},
                {"Brazil": {"timezones": "UTC-03:00", "alt_spellings": "BR"}},
                {"Brazil": {"timezones": "UTC-05:00", "alt_spellings": "BR"}},
                {"Brazil": {"timezones": "UTC-03:00", "alt_spellings": "BR"}},
                {"Brazil": {"timezones": "UTC-03:00", "alt_spellings": "BR"}},
                {"British Indian Ocean Territory": {"timezones": "UTC+06:00", "alt_spellings": "IO"}},
                {"Brunei Darussalam": {"timezones": "UTC+08:00", "alt_spellings": "BN"}},
                {"Bulgaria": {"timezones": "UTC+03:00", "alt_spellings": "BG"}},
                {"Burkina Faso": {"timezones": "UTC", "alt_spellings": "BF"}},
                {"Burundi": {"timezones": "UTC+02:00", "alt_spellings": "BI"}},
                {"Cambodia": {"timezones": "UTC+07:00", "alt_spellings": "KH"}},
                {"Cameroon": {"timezones": "UTC+01:00", "alt_spellings": "CM"}},
                {"Canada": {"timezones": "UTC-05:00", "alt_spellings": "CA"}},
                {"Canada": {"timezones": "UTC-04:00", "alt_spellings": "CA"}},
                {"Canada": {"timezones": "UTC-06:00", "alt_spellings": "CA"}},
                {"Canada": {"timezones": "UTC-07:00", "alt_spellings": "CA"}},
                {"Canada": {"timezones": "UTC-07:00", "alt_spellings": "CA"}},
                {"Canada": {"timezones": "UTC-07:00", "alt_spellings": "CA"}},
                {"Canada": {"timezones": "UTC-06:00", "alt_spellings": "CA"}},
                {"Canada": {"timezones": "UTC-07:00", "alt_spellings": "CA"}},
                {"Canada": {"timezones": "UTC-03:00", "alt_spellings": "CA"}},
                {"Canada": {"timezones": "UTC-03:00", "alt_spellings": "CA"}},
                {"Canada": {"timezones": "UTC-03:00", "alt_spellings": "CA"}},
                {"Canada": {"timezones": "UTC-06:00", "alt_spellings": "CA"}},
                {"Canada": {"timezones": "UTC-04:00", "alt_spellings": "CA"}},
                {"Canada": {"timezones": "UTC-03:00", "alt_spellings": "CA"}},
                {"Canada": {"timezones": "UTC-05:00", "alt_spellings": "CA"}},
                {"Canada": {"timezones": "UTC-06:00", "alt_spellings": "CA"}},
                {"Canada": {"timezones": "UTC-05:00", "alt_spellings": "CA"}},
                {"Canada": {"timezones": "UTC-02:30", "alt_spellings": "CA"}},
                {"Canada": {"timezones": "UTC-06:00", "alt_spellings": "CA"}},
                {"Canada": {"timezones": "UTC-04:00", "alt_spellings": "CA"}},
                {"Canada": {"timezones": "UTC-07:00", "alt_spellings": "CA"}},
                {"Canada": {"timezones": "UTC-07:00", "alt_spellings": "CA"}},
                {"Canada": {"timezones": "UTC-05:00", "alt_spellings": "CA"}},
                {"Cape Verde": {"timezones": "UTC-01:00", "alt_spellings": "CV"}},
                {"Cayman Islands": {"timezones": "UTC-05:00", "alt_spellings": "KY"}},
                {"Central African Republic": {"timezones": "UTC+01:00", "alt_spellings": "CF"}},
                {"Chad": {"timezones": "UTC+01:00", "alt_spellings": "TD"}},
                {"Chile": {"timezones": "UTC-03:00", "alt_spellings": "CL"}},
                {"Chile": {"timezones": "UTC-04:00", "alt_spellings": "CL"}},
                {"Chile": {"timezones": "UTC-06:00", "alt_spellings": "CL"}},
                {"China": {"timezones": "UTC+08:00", "alt_spellings": "CN"}},
                {"China": {"timezones": "UTC+06:00", "alt_spellings": "CN"}},
                {"Christmas Island": {"timezones": "UTC+07:00", "alt_spellings": "CX"}},
                {"Cocos (Keeling) Islands": {"timezones": "UTC+06:30", "alt_spellings": "CC"}},
                {"Colombia": {"timezones": "UTC-05:00", "alt_spellings": "CO"}},
                {"Comoros": {"timezones": "UTC+03:00", "alt_spellings": "KM"}},
                {"Congo": {"timezones": "UTC+01:00", "alt_spellings": "CG"}},
                {"Congo, the Democratic Republic of the": {"timezones": "UTC+01:00", "alt_spellings": "CD"}},
                {"Congo, the Democratic Republic of the": {"timezones": "UTC+02:00", "alt_spellings": "CD"}},
                {"Cook Islands": {"timezones": "UTC-10:00", "alt_spellings": "CK"}},
                {"Costa Rica": {"timezones": "UTC-06:00", "alt_spellings": "CR"}},
                {"Croatia": {"timezones": "UTC+02:00", "alt_spellings": "HR"}},
                {"Cuba": {"timezones": "UTC-04:00", "alt_spellings": "CU"}},
                {"CuraÃ§ao": {"timezones": "UTC-04:00", "alt_spellings": "CW"}},
                {"Cyprus": {"timezones": "UTC+03:00", "alt_spellings": "CY"}},
                {"Cyprus": {"timezones": "UTC+03:00", "alt_spellings": "CY"}},
                {"Czech Republic": {"timezones": "UTC+02:00", "alt_spellings": "CZ"}},
                {"CÃ´te dIvoire": {"timezones": "UTC", "alt_spellings": "CI"}},
                {"Denmark": {"timezones": "UTC+02:00", "alt_spellings": "DK"}},
                {"Djibouti": {"timezones": "UTC+03:00", "alt_spellings": "DJ"}},
                {"Dominica": {"timezones": "UTC-04:00", "alt_spellings": "DM"}},
                {"Dominican Republic": {"timezones": "UTC-04:00", "alt_spellings": "DO"}},
                {"Ecuador": {"timezones": "UTC-05:00", "alt_spellings": "EC"}},
                {"Ecuador": {"timezones": "UTC-06:00", "alt_spellings": "EC"}},
                {"Egypt": {"timezones": "UTC+03:00", "alt_spellings": "EG"}},
                {"El Salvador": {"timezones": "UTC-06:00", "alt_spellings": "SV"}},
                {"Equatorial Guinea": {"timezones": "UTC+01:00", "alt_spellings": "GQ"}},
                {"Eritrea": {"timezones": "UTC+03:00", "alt_spellings": "ER"}},
                {"Estonia": {"timezones": "UTC+03:00", "alt_spellings": "EE"}},
                {"Ethiopia": {"timezones": "UTC+03:00", "alt_spellings": "ET"}},
                {"Falkland Islands (Malvinas)": {"timezones": "UTC-03:00", "alt_spellings": "FK"}},
                {"Faroe Islands": {"timezones": "UTC+01:00", "alt_spellings": "FO"}},
                {"Fiji": {"timezones": "UTC+12:00", "alt_spellings": "FJ"}},
                {"Finland": {"timezones": "UTC+03:00", "alt_spellings": "FI"}},
                {"France": {"timezones": "UTC+02:00", "alt_spellings": "FR"}},
                {"French Guiana": {"timezones": "UTC-03:00", "alt_spellings": "GF"}},
                {"French Polynesia": {"timezones": "UTC-09:00", "alt_spellings": "PF"}},
                {"French Polynesia": {"timezones": "UTC-09:30", "alt_spellings": "PF"}},
                {"French Polynesia": {"timezones": "UTC-10:00", "alt_spellings": "PF"}},
                {"French Southern Territories": {"timezones": "UTC+05:00", "alt_spellings": "TF"}},
                {"Gabon": {"timezones": "UTC+01:00", "alt_spellings": "GA"}},
                {"Gambia": {"timezones": "UTC", "alt_spellings": "GM"}},
                {"Georgia": {"timezones": "UTC+04:00", "alt_spellings": "GE"}},
                {"Germany": {"timezones": "UTC+02:00", "alt_spellings": "DE"}},
                {"Germany": {"timezones": "UTC+02:00", "alt_spellings": "DE"}},
                {"Ghana": {"timezones": "UTC", "alt_spellings": "GH"}},
                {"Gibraltar": {"timezones": "UTC+02:00", "alt_spellings": "GI"}},
                {"Greece": {"timezones": "UTC+03:00", "alt_spellings": "GR"}},
                {"Greenland": {"timezones": "UTC", "alt_spellings": "GL"}},
                {"Greenland": {"timezones": "UTC-01:00", "alt_spellings": "GL"}},
                {"Greenland": {"timezones": "UTC-01:00", "alt_spellings": "GL"}},
                {"Greenland": {"timezones": "UTC-03:00", "alt_spellings": "GL"}},
                {"Grenada": {"timezones": "UTC-04:00", "alt_spellings": "GD"}},
                {"Guadeloupe": {"timezones": "UTC-04:00", "alt_spellings": "GP"}},
                {"Guam": {"timezones": "UTC+10:00", "alt_spellings": "GU"}},
                {"Guatemala": {"timezones": "UTC-06:00", "alt_spellings": "GT"}},
                {"Guernsey": {"timezones": "UTC+01:00", "alt_spellings": "GG"}},
                {"Guinea": {"timezones": "UTC", "alt_spellings": "GN"}},
                {"Guinea-Bissau": {"timezones": "UTC", "alt_spellings": "GW"}},
                {"Guyana": {"timezones": "UTC-04:00", "alt_spellings": "GY"}},
                {"Haiti": {"timezones": "UTC-04:00", "alt_spellings": "HT"}},
                {"Holy See (Vatican City State)": {"timezones": "UTC+02:00", "alt_spellings": "VA"}},
                {"Honduras": {"timezones": "UTC-06:00", "alt_spellings": "HN"}},
                {"Hong Kong": {"timezones": "UTC+08:00", "alt_spellings": "HK"}},
                {"Hungary": {"timezones": "UTC+02:00", "alt_spellings": "HU"}},
                {"Iceland": {"timezones": "UTC", "alt_spellings": "IS"}},
                {"India": {"timezones": "UTC+05:30", "alt_spellings": "IN"}},
                {"Indonesia": {"timezones": "UTC+07:00", "alt_spellings": "ID"}},
                {"Indonesia": {"timezones": "UTC+09:00", "alt_spellings": "ID"}},
                {"Indonesia": {"timezones": "UTC+08:00", "alt_spellings": "ID"}},
                {"Indonesia": {"timezones": "UTC+07:00", "alt_spellings": "ID"}},
                {"Iran, Islamic Republic of": {"timezones": "UTC+03:30", "alt_spellings": "IR"}},
                {"Iraq": {"timezones": "UTC+03:00", "alt_spellings": "IQ"}},
                {"Ireland": {"timezones": "UTC+01:00", "alt_spellings": "IE"}},
                {"Isle of Man": {"timezones": "UTC+01:00", "alt_spellings": "IM"}},
                {"Israel": {"timezones": "UTC+03:00", "alt_spellings": "IL"}},
                {"Italy": {"timezones": "UTC+02:00", "alt_spellings": "IT"}},
                {"Jamaica": {"timezones": "UTC-05:00", "alt_spellings": "JM"}},
                {"Japan": {"timezones": "UTC+09:00", "alt_spellings": "JP"}},
                {"Jersey": {"timezones": "UTC+01:00", "alt_spellings": "JE"}},
                {"Jordan": {"timezones": "UTC+03:00", "alt_spellings": "JO"}},
                {"Kazakhstan": {"timezones": "UTC+05:00", "alt_spellings": "KZ"}},
                {"Kazakhstan": {"timezones": "UTC+05:00", "alt_spellings": "KZ"}},
                {"Kazakhstan": {"timezones": "UTC+05:00", "alt_spellings": "KZ"}},
                {"Kazakhstan": {"timezones": "UTC+05:00", "alt_spellings": "KZ"}},
                {"Kazakhstan": {"timezones": "UTC+05:00", "alt_spellings": "KZ"}},
                {"Kazakhstan": {"timezones": "UTC+05:00", "alt_spellings": "KZ"}},
                {"Kazakhstan": {"timezones": "UTC+05:00", "alt_spellings": "KZ"}},
                {"Kenya": {"timezones": "UTC+03:00", "alt_spellings": "KE"}},
                {"Kiribati": {"timezones": "UTC+13:00", "alt_spellings": "KI"}},
                {"Kiribati": {"timezones": "UTC+14:00", "alt_spellings": "KI"}},
                {"Kiribati": {"timezones": "UTC+12:00", "alt_spellings": "KI"}},
                {"Korea, Democratic Peoples Republic of": {"timezones": "UTC+09:00", "alt_spellings": "KP"}},
                {"Korea, Republic of": {"timezones": "UTC+09:00", "alt_spellings": "KR"}},
                {"Kuwait": {"timezones": "UTC+03:00", "alt_spellings": "KW"}},
                {"Kyrgyzstan": {"timezones": "UTC+06:00", "alt_spellings": "KG"}},
                {"Lao Peoples Democratic Republic": {"timezones": "UTC+07:00", "alt_spellings": "LA"}},
                {"Latvia": {"timezones": "UTC+03:00", "alt_spellings": "LV"}},
                {"Lebanon": {"timezones": "UTC+03:00", "alt_spellings": "LB"}},
                {"Lesotho": {"timezones": "UTC+02:00", "alt_spellings": "LS"}},
                {"Liberia": {"timezones": "UTC", "alt_spellings": "LR"}},
                {"Libya": {"timezones": "UTC+02:00", "alt_spellings": "LY"}},
                {"Liechtenstein": {"timezones": "UTC+02:00", "alt_spellings": "LI"}},
                {"Lithuania": {"timezones": "UTC+03:00", "alt_spellings": "LT"}},
                {"Luxembourg": {"timezones": "UTC+02:00", "alt_spellings": "LU"}},
                {"Macao": {"timezones": "UTC+08:00", "alt_spellings": "MO"}},
                {"Macedonia, the Former Yugoslav Republic of": {"timezones": "UTC+02:00", "alt_spellings": "MK"}},
                {"Madagascar": {"timezones": "UTC+03:00", "alt_spellings": "MG"}},
                {"Malawi": {"timezones": "UTC+02:00", "alt_spellings": "MW"}},
                {"Malaysia": {"timezones": "UTC+08:00", "alt_spellings": "MY"}},
                {"Malaysia": {"timezones": "UTC+08:00", "alt_spellings": "MY"}},
                {"Maldives": {"timezones": "UTC+05:00", "alt_spellings": "MV"}},
                {"Mali": {"timezones": "UTC", "alt_spellings": "ML"}},
                {"Malta": {"timezones": "UTC+02:00", "alt_spellings": "MT"}},
                {"Marshall Islands": {"timezones": "UTC+12:00", "alt_spellings": "MH"}},
                {"Marshall Islands": {"timezones": "UTC+12:00", "alt_spellings": "MH"}},
                {"Martinique": {"timezones": "UTC-04:00", "alt_spellings": "MQ"}},
                {"Mauritania": {"timezones": "UTC", "alt_spellings": "MR"}},
                {"Mauritius": {"timezones": "UTC+04:00", "alt_spellings": "MU"}},
                {"Mayotte": {"timezones": "UTC+03:00", "alt_spellings": "YT"}},
                {"Mexico": {"timezones": "UTC-06:00", "alt_spellings": "MX"}},
                {"Mexico": {"timezones": "UTC-05:00", "alt_spellings": "MX"}},
                {"Mexico": {"timezones": "UTC-06:00", "alt_spellings": "MX"}},
                {"Mexico": {"timezones": "UTC-06:00", "alt_spellings": "MX"}},
                {"Mexico": {"timezones": "UTC-07:00", "alt_spellings": "MX"}},
                {"Mexico": {"timezones": "UTC-05:00", "alt_spellings": "MX"}},
                {"Mexico": {"timezones": "UTC-07:00", "alt_spellings": "MX"}},
                {"Mexico": {"timezones": "UTC-06:00", "alt_spellings": "MX"}},
                {"Mexico": {"timezones": "UTC-06:00", "alt_spellings": "MX"}},
                {"Mexico": {"timezones": "UTC-06:00", "alt_spellings": "MX"}},
                {"Mexico": {"timezones": "UTC-05:00", "alt_spellings": "MX"}},
                {"Mexico": {"timezones": "UTC-07:00", "alt_spellings": "MX"}},
                {"Micronesia, Federated States of": {"timezones": "UTC+10:00", "alt_spellings": "FM"}},
                {"Micronesia, Federated States of": {"timezones": "UTC+11:00", "alt_spellings": "FM"}},
                {"Micronesia, Federated States of": {"timezones": "UTC+11:00", "alt_spellings": "FM"}},
                {"Moldova, Republic of": {"timezones": "UTC+03:00", "alt_spellings": "MD"}},
                {"Monaco": {"timezones": "UTC+02:00", "alt_spellings": "MC"}},
                {"Mongolia": {"timezones": "UTC+08:00", "alt_spellings": "MN"}},
                {"Mongolia": {"timezones": "UTC+07:00", "alt_spellings": "MN"}},
                {"Mongolia": {"timezones": "UTC+08:00", "alt_spellings": "MN"}},
                {"Montenegro": {"timezones": "UTC+02:00", "alt_spellings": "ME"}},
                {"Montserrat": {"timezones": "UTC-04:00", "alt_spellings": "MS"}},
                {"Morocco": {"timezones": "UTC+01:00", "alt_spellings": "MA"}},
                {"Morocco": {"timezones": "UTC+01:00", "alt_spellings": "MA"}},
                {"Mozambique": {"timezones": "UTC+02:00", "alt_spellings": "MZ"}},
                {"Myanmar": {"timezones": "UTC+06:30", "alt_spellings": "MM"}},
                {"Namibia": {"timezones": "UTC+02:00", "alt_spellings": "NA"}},
                {"Nauru": {"timezones": "UTC+12:00", "alt_spellings": "NR"}},
                {"Nepal": {"timezones": "UTC+05:45", "alt_spellings": "NP"}},
                {"Netherlands": {"timezones": "UTC+02:00", "alt_spellings": "NL"}},
                {"New Caledonia": {"timezones": "UTC+11:00", "alt_spellings": "NC"}},
                {"New Zealand": {"timezones": "UTC+12:00", "alt_spellings": "NZ"}},
                {"New Zealand": {"timezones": "UTC+12:45", "alt_spellings": "NZ"}},
                {"Nicaragua": {"timezones": "UTC-06:00", "alt_spellings": "NI"}},
                {"Niger": {"timezones": "UTC+01:00", "alt_spellings": "NE"}},
                {"Nigeria": {"timezones": "UTC+01:00", "alt_spellings": "NG"}},
                {"Niue": {"timezones": "UTC-11:00", "alt_spellings": "NU"}},
                {"Norfolk Island": {"timezones": "UTC+11:00", "alt_spellings": "NF"}},
                {"Northern Mariana Islands": {"timezones": "UTC+10:00", "alt_spellings": "MP"}},
                {"Norway": {"timezones": "UTC+02:00", "alt_spellings": "NO"}},
                {"Oman": {"timezones": "UTC+04:00", "alt_spellings": "OM"}},
                {"Pakistan": {"timezones": "UTC+05:00", "alt_spellings": "PK"}},
                {"Paksitan": {"timezones": "UTC+05:00", "alt_spellings": "PK"}},
                {"Palau": {"timezones": "UTC+09:00", "alt_spellings": "PW"}},
                {"Palestine, State of": {"timezones": "UTC+03:00", "alt_spellings": "PS"}},
                {"Palestine, State of": {"timezones": "UTC+03:00", "alt_spellings": "PS"}},
                {"Palestine": {"timezones": "UTC+03:00", "alt_spellings": "PS"}},
                {"Panama": {"timezones": "UTC-05:00", "alt_spellings": "PA"}},
                {"Papua New Guinea": {"timezones": "UTC+11:00", "alt_spellings": "PG"}},
                {"Papua New Guinea": {"timezones": "UTC+10:00", "alt_spellings": "PG"}},
                {"Paraguay": {"timezones": "UTC-04:00", "alt_spellings": "PY"}},
                {"Peru": {"timezones": "UTC-05:00", "alt_spellings": "PE"}},
                {"Philippines": {"timezones": "UTC+08:00", "alt_spellings": "PH"}},
                {"Pitcairn": {"timezones": "UTC-08:00", "alt_spellings": "PN"}},
                {"Poland": {"timezones": "UTC+02:00", "alt_spellings": "PL"}},
                {"Portugal": {"timezones": "UTC", "alt_spellings": "PT"}},
                {"Portugal": {"timezones": "UTC+01:00", "alt_spellings": "PT"}},
                {"Portugal": {"timezones": "UTC+01:00", "alt_spellings": "PT"}},
                {"Puerto Rico": {"timezones": "UTC-04:00", "alt_spellings": "PR"}},
                {"Qatar": {"timezones": "UTC+03:00", "alt_spellings": "QA"}},
                {"Romania": {"timezones": "UTC+03:00", "alt_spellings": "RO"}},
                {"Russian Federation": {"timezones": "UTC+12:00", "alt_spellings": "RU"}},
                {"Russian Federation": {"timezones": "UTC+07:00", "alt_spellings": "RU"}},
                {"Russian Federation": {"timezones": "UTC+09:00", "alt_spellings": "RU"}},
                {"Russian Federation": {"timezones": "UTC+08:00", "alt_spellings": "RU"}},
                {"Russian Federation": {"timezones": "UTC+12:00", "alt_spellings": "RU"}},
                {"Russian Federation": {"timezones": "UTC+09:00", "alt_spellings": "RU"}},
                {"Russian Federation": {"timezones": "UTC+07:00", "alt_spellings": "RU"}},
                {"Russian Federation": {"timezones": "UTC+11:00", "alt_spellings": "RU"}},
                {"Russian Federation": {"timezones": "UTC+07:00", "alt_spellings": "RU"}},
                {"Russian Federation": {"timezones": "UTC+07:00", "alt_spellings": "RU"}},
                {"Russian Federation": {"timezones": "UTC+06:00", "alt_spellings": "RU"}},
                {"Russian Federation": {"timezones": "UTC+11:00", "alt_spellings": "RU"}},
                {"Russian Federation": {"timezones": "UTC+11:00", "alt_spellings": "RU"}},
                {"Russian Federation": {"timezones": "UTC+07:00", "alt_spellings": "RU"}},
                {"Russian Federation": {"timezones": "UTC+10:00", "alt_spellings": "RU"}},
                {"Russian Federation": {"timezones": "UTC+10:00", "alt_spellings": "RU"}},
                {"Russian Federation": {"timezones": "UTC+09:00", "alt_spellings": "RU"}},
                {"Russian Federation": {"timezones": "UTC+05:00", "alt_spellings": "RU"}},
                {"Russian Federation": {"timezones": "UTC+04:00", "alt_spellings": "RU"}},
                {"Russian Federation": {"timezones": "UTC+02:00", "alt_spellings": "RU"}},
                {"Russian Federation": {"timezones": "UTC+03:00", "alt_spellings": "RU"}},
                {"Russian Federation": {"timezones": "UTC+03:00", "alt_spellings": "RU"}},
                {"Russian Federation": {"timezones": "UTC+04:00", "alt_spellings": "RU"}},
                {"Russian Federation": {"timezones": "UTC+04:00", "alt_spellings": "RU"}},
                {"Russian Federation": {"timezones": "UTC+04:00", "alt_spellings": "RU"}},
                {"Russian Federation": {"timezones": "UTC+03:00", "alt_spellings": "RU"}},
                {"Rwanda": {"timezones": "UTC+02:00", "alt_spellings": "RW"}},
                {"RÃ©union": {"timezones": "UTC+04:00", "alt_spellings": "RE"}},
                {"Saint BarthÃ©lemy": {"timezones": "UTC-04:00", "alt_spellings": "BL"}},
                {"Saint Helena, Ascension and Tristan da Cunha": {"timezones": "UTC", "alt_spellings": "SH"}},
                {"Saint Kitts and Nevis": {"timezones": "UTC-04:00", "alt_spellings": "KN"}},
                {"Saint Lucia": {"timezones": "UTC-04:00", "alt_spellings": "LC"}},
                {"Saint Martin (French part)": {"timezones": "UTC-04:00", "alt_spellings": "MF"}},
                {"Saint Pierre and Miquelon": {"timezones": "UTC-02:00", "alt_spellings": "PM"}},
                {"Saint Vincent and the Grenadines": {"timezones": "UTC-04:00", "alt_spellings": "VC"}},
                {"Samoa": {"timezones": "UTC+13:00", "alt_spellings": "WS"}},
                {"San Marino": {"timezones": "UTC+02:00", "alt_spellings": "SM"}},
                {"Sao Tome and Principe": {"timezones": "UTC", "alt_spellings": "ST"}},
                {"Saudi Arabia": {"timezones": "UTC+03:00", "alt_spellings": "SA"}},
                {"Senegal": {"timezones": "UTC", "alt_spellings": "SN"}},
                {"Serbia": {"timezones": "UTC+02:00", "alt_spellings": "RS"}},
                {"Seychelles": {"timezones": "UTC+04:00", "alt_spellings": "SC"}},
                {"Sierra Leone": {"timezones": "UTC", "alt_spellings": "SL"}},
                {"Singapore": {"timezones": "UTC+08:00", "alt_spellings": "SG"}},
                {"Sint Maarten (Dutch part)": {"timezones": "UTC-04:00", "alt_spellings": "SX"}},
                {"Slovakia": {"timezones": "UTC+02:00", "alt_spellings": "SK"}},
                {"Slovenia": {"timezones": "UTC+02:00", "alt_spellings": "SI"}},
                {"Solomon Islands": {"timezones": "UTC+11:00", "alt_spellings": "SB"}},
                {"Somalia": {"timezones": "UTC+03:00", "alt_spellings": "SO"}},
                {"South Africa": {"timezones": "UTC+02:00", "alt_spellings": "ZA"}},
                {"South Georgia and the South Sandwich Islands": {"timezones": "UTC-02:00", "alt_spellings": "GS"}},
                {"South Sudan": {"timezones": "UTC+02:00", "alt_spellings": "SS"}},
                {"Spain": {"timezones": "UTC+02:00", "alt_spellings": "ES"}},
                {"Spain": {"timezones": "UTC+01:00", "alt_spellings": "ES"}},
                {"Spain": {"timezones": "UTC+02:00", "alt_spellings": "ES"}},
                {"Sri Lanka": {"timezones": "UTC+05:30", "alt_spellings": "LK"}},
                {"Sudan": {"timezones": "UTC+02:00", "alt_spellings": "SD"}},
                {"Suriname": {"timezones": "UTC-03:00", "alt_spellings": "SR"}},
                {"Svalbard and Jan Mayen": {"timezones": "UTC+02:00", "alt_spellings": "SJ"}},
                {"Swaziland": {"timezones": "UTC+02:00", "alt_spellings": "SZ"}},
                {"Sweden": {"timezones": "UTC+02:00", "alt_spellings": "SE"}},
                {"Switzerland": {"timezones": "UTC+02:00", "alt_spellings": "CH"}},
                {"Syrian Arab Republic": {"timezones": "UTC+03:00", "alt_spellings": "SY"}},
                {"Taiwan, Province of China": {"timezones": "UTC+08:00", "alt_spellings": "TW"}},
                {"Tajikistan": {"timezones": "UTC+05:00", "alt_spellings": "TJ"}},
                {"Tanzania, United Republic of": {"timezones": "UTC+03:00", "alt_spellings": "TZ"}},
                {"Thailand": {"timezones": "UTC+07:00", "alt_spellings": "TH"}},
                {"Timor-Leste": {"timezones": "UTC+09:00", "alt_spellings": "TL"}},
                {"Togo": {"timezones": "UTC", "alt_spellings": "TG"}},
                {"Tokelau": {"timezones": "UTC+13:00", "alt_spellings": "TK"}},
                {"Tonga": {"timezones": "UTC+13:00", "alt_spellings": "TO"}},
                {"Trinidad and Tobago": {"timezones": "UTC-04:00", "alt_spellings": "TT"}},
                {"Tunisia": {"timezones": "UTC+01:00", "alt_spellings": "TN"}},
                {"Turkey": {"timezones": "UTC+03:00", "alt_spellings": "TR"}},
                {"Turkmenistan": {"timezones": "UTC+05:00", "alt_spellings": "TM"}},
                {"Turks and Caicos Islands": {"timezones": "UTC-04:00", "alt_spellings": "TC"}},
                {"Tuvalu": {"timezones": "UTC+12:00", "alt_spellings": "TV"}},
                {"Uganda": {"timezones": "UTC+03:00", "alt_spellings": "UG"}},
                {"Ukraine": {"timezones": "UTC+03:00", "alt_spellings": "UA"}},
                {"Ukraine": {"timezones": "UTC+03:00", "alt_spellings": "UA"}},
                {"United Arab Emirates": {"timezones": "UTC+04:00", "alt_spellings": "AE"}},
                {"United Kingdom": {"timezones": "UTC+01:00", "alt_spellings": "GB"}},
                {"United States": {"timezones": "UTC-04:00", "alt_spellings": "US"}},
                {"United State": {"timezones": "UTC-04:00", "alt_spellings": "US"}},
                {"United States of America": {"timezones": "UTC-04:00", "alt_spellings": "US"}},
                {"USA": {"timezones": "UTC-04:00", "alt_spellings": "US"}},
                {"United States": {"timezones": "UTC-04:00", "alt_spellings": "US"}},
                {"USA": {"timezones": "UTC-04:00", "alt_spellings": "US"}},
                {"United States Minor Outlying Islands": {"timezones": "UTC-11:00", "alt_spellings": "UM"}},
                {"United States Minor Outlying Islands": {"timezones": "UTC+12:00", "alt_spellings": "UM"}},
                {"Uruguay": {"timezones": "UTC-03:00", "alt_spellings": "UY"}},
                {"Uzbekistan": {"timezones": "UTC+05:00", "alt_spellings": "UZ"}},
                {"Uzbekistan": {"timezones": "UTC+05:00", "alt_spellings": "UZ"}},
                {"Vanuatu": {"timezones": "UTC+11:00", "alt_spellings": "VU"}},
                {"Venezuela, Bolivarian Republic of": {"timezones": "UTC-04:00", "alt_spellings": "VE"}},
                {"Viet Nam": {"timezones": "UTC+07:00", "alt_spellings": "VN"}},
                {"Virgin Islands, British": {"timezones": "UTC-04:00", "alt_spellings": "VG"}},
                {"Virgin Islands, U.S.": {"timezones": "UTC-04:00", "alt_spellings": "VI"}},
                {"Wallis and Futuna": {"timezones": "UTC+12:00", "alt_spellings": "WF"}},
                {"Yemen": {"timezones": "UTC+03:00", "alt_spellings": "YE"}},
                {"Zambia": {"timezones": "UTC+02:00", "alt_spellings": "ZM"}},
                {"Zimbabwe": {"timezones": "UTC+02:00", "alt_spellings": "ZW"}},
                {"Ãland Islands": {"timezones": "UTC+03:00", "alt_spellings": "AX"}}]
        except Exception as e:
            telemetry_logger.log_error("country_list", "COUNTRY_LIST_ERROR", str(e), 500, job="cancellation-policy")
            raise
    def get_country_timezone(self, countryname):
        if not countryname:
            telemetry_logger.log_response_time("get_country_timezone", 0, 200, job="cancellation-policy")
            return None
        try:
            # Assuming self.country_list() returns a list of dictionaries
            data = self.country_list()
            for item in data:
                if countryname in item:
                    # Retrieve timezones list for the country
                    country_timezone = item[countryname].get('timezones', [])

                    if country_timezone == "UTC":
                        self.country_timezone_hour = 0
                        self.country_timezone_min = 0
                        return True

                    if country_timezone:
                        # Join the list of timezones into a single string
                        country_time = self.all_timezones.get(country_timezone)  # Assuming you want the first timezone

                        if country_time:
                            if len(country_time) > 3:
                                hours, minutes = country_time.split(':')
                                self.country_timezone_hour = int(hours)
                                self.country_timezone_min = int(minutes)
                            else:
                                self.country_timezone_hour = int(country_time)
                                self.country_timezone_min = 0  # Default to 0 if no minutes are specified
                        else:
                            print(f"Timezone {country_timezone[0]} not found in all_timezones.")
                            error_msg = f"Timezone {country_timezone[0]} not found in all_timezones."
                            telemetry_logger.log_error("get_country_timezone", "TIMEZONE_NOT_FOUND", error_msg, 404, job="cancellation-policy")
                            return None

                    return None
            # print(f"Country '{countryname}' not found.")
            error_msg = f"Country '{countryname}' not found."
            telemetry_logger.log_error("get_country_timezone", "COUNTRY_NOT_FOUND", error_msg, 404, job="cancellation-policy")
            return None

        except FileNotFoundError:
            print("The country_list.json file was not found.")
            error_msg = "The country_list.json file was not found."
            telemetry_logger.log_error("get_country_timezone", "FILE_NOT_FOUND", error_msg, 404, job="cancellation-policy")
        except json.JSONDecodeError:
            print("Error decoding the JSON file.")
            error_msg = "Error decoding the JSON file."
            telemetry_logger.log_error("get_country_timezone", "JSON_DECODE_ERROR", error_msg, 400, job="cancellation-policy")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            error_msg = f"An unexpected error occurred: {e}"
            telemetry_logger.log_error("get_country_timezone", "UNKNOWN_ERROR", error_msg, 500, job="cancellation-policy")
        return None

    def convert_listing_timezone(self, chag_datetime):
        naive_datetime = datetime.strptime(chag_datetime, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
        country_timezone_hour = int(self.country_timezone_hour)
        country_timezone_min = int(self.country_timezone_min) if self.country_timezone_min is not None else 0
        target_offset = timezone(timedelta(hours=country_timezone_hour, minutes=country_timezone_min))
        target_datetime = naive_datetime.astimezone(target_offset)
        telemetry_logger.log_response_time("convert_listing_timezone", 0, 200, job="cancellation-policy")
        return target_datetime.strftime('%Y-%m-%d %H:%M:%S')
        # # datetime that needs to convert
        # #  if datetime is UTC then no need to convert
        # naive_datetime = datetime.strptime(chag_datetime, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
        # if int(self.country_timezone_hour) == 0:
        #     target_offset = timezone(timedelta(hours=0))
        #     target_timezone = naive_datetime.astimezone(target_offset)
        #     target_timezone = target_timezone + timedelta(hours=0.5)
        #     convert_time = target_timezone.strftime('%Y-%m-%d %H:%M:%S')
        #     return convert_time

        # # if timezone is diffrent Convert into target timezone
        # if self.country_timezone_min is not None:
        #     if self.country_timezone_hour > 0:
        #         target_offset = timezone(timedelta(hours=self.country_timezone_hour, minutes=30))
        #     else:
        #         target_offset = timezone(timedelta(hours=self.country_timezone_hour, minutes=-30))
        # else:
        #     self.country_timezone_hour = int(self.country_timezone_hour)
        #     target_offset = timezone(timedelta(hours=self.country_timezone_hour))
        # target_timezone = naive_datetime.astimezone(target_offset)
        # target_timezone = target_timezone + timedelta(hours=0.5)
        # convert_time = target_timezone.strftime('%Y-%m-%d %H:%M:%S')
        # return convert_time

    def convert_dida_time_to_utc(self, dida_time):
        beijing_tz = pytz.timezone('Asia/Shanghai')
        utc_tz = pytz.utc
        beijing_time = datetime.strptime(dida_time, '%Y-%m-%d %H:%M:%S')
        # Localize the Beijing time
        beijing_time = beijing_tz.localize(beijing_time)
        # Convert to UTC
        utc_time = beijing_time.astimezone(utc_tz)
        telemetry_logger.log_response_time("convert_dida_time_to_utc", 0, 200, job="cancellation-policy")
        return utc_time.strftime('%Y-%m-%d %H:%M:%S')
    
    def convert_webbeds_time_to_utc(self, webbeds_time):
        eastern = pytz.timezone('America/New_York')
        utc_tz = pytz.utc
        # Get current time in Eastern Time
        eastern_time = datetime.strptime(webbeds_time, '%Y-%m-%d %H:%M:%S')
        # Localize the  (Orlando, FL), EST.
        eastern_time = eastern.localize(eastern_time)
        utc_time = eastern_time.astimezone(utc_tz)
        telemetry_logger.log_response_time("convert_webbeds_time_to_utc", 0, 200, job="cancellation-policy")
        return utc_time.strftime('%Y-%m-%d %H:%M:%S')
    
    def convert_hxpro_time_to_utc(self, hxpro_time):
        beijing_tz = pytz.timezone('Etc/GMT+3')
        utc_tz = pytz.utc
        beijing_time = datetime.strptime(hxpro_time, '%Y-%m-%d %H:%M:%S')
        # Localize the Beijing time
        beijing_time = beijing_tz.localize(beijing_time)
        # Convert to UTC
        utc_time = beijing_time.astimezone(utc_tz)
        telemetry_logger.log_response_time("convert_hxpro_time_to_utc", 0, 200, job="cancellation-policy")
        return utc_time.strftime('%Y-%m-%d %H:%M:%S')

    def convert_dida_listing_timezone(self, chag_datetime):
        # datetime that needs to convert
        #  if datetime is UTC then no need to convert
        beijing_offset = timezone(timedelta(hours=8))
        naive_datetime = datetime.strptime(chag_datetime, '%Y-%m-%d %H:%M:%S')
        naive_datetime = naive_datetime.replace(tzinfo=beijing_offset)
        if int(self.country_timezone_hour) == 0:
            target_offset = timezone(timedelta(hours=0))
            target_timezone = naive_datetime.astimezone(target_offset)
            target_timezone = target_timezone + timedelta(hours=0.5)
            convert_time = target_timezone.strftime('%Y-%m-%d %H:%M:%S')
            telemetry_logger.log_response_time("convert_dida_listing_timezone", 0, 200, job="cancellation-policy")
            return convert_time

        # if timezone is diffrent Convert into target timezone
        if self.country_timezone_min is not None:
            if self.country_timezone_hour > 0:
                target_offset = timezone(timedelta(hours=self.country_timezone_hour, minutes=30))
            else:
                target_offset = timezone(timedelta(hours=self.country_timezone_hour, minutes=-30))
        else:
            self.country_timezone_hour = int(self.country_timezone_hour)
            target_offset = timezone(timedelta(hours=self.country_timezone_hour))
        target_timezone = naive_datetime.astimezone(target_offset)
        target_timezone = target_timezone + timedelta(hours=0.5)
        convert_time = target_timezone.strftime('%Y-%m-%d %H:%M:%S')
        telemetry_logger.log_response_time("convert_dida_listing_timezone", 0, 200, job="cancellation-policy")
        return convert_time

    def date_format_in_obj(self, date_str):
        for fmt in self.possible_date_formats:
            try:
                # Parse date_str into datetime object
                return datetime.strptime(date_str, fmt)
            except ValueError:
                telemetry_logger.log_error("date_format_in_obj", "DATE_FORMAT_ERROR", str(date_str), 400, job="cancellation-policy")
                continue
        # If no formats match, return the original string or raise an error
        raise ValueError(f"Date format for {date_str} not recognized")

    def format_date(self, date_str: str) -> str:
        if date_str is None:
            telemetry_logger.log_response_time("format_date", 0, 500, job="cancellation-policy")
            return self.current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        for fmt in self.possible_date_formats:
            try:
                # Parse date_str into datetime object
                dt = datetime.strptime(date_str, fmt)
                # Format datetime object into desired format
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue
        # If no formats match, return the original string or raise an error
        telemetry_logger.log_error("format_date", "DATE_FORMAT_ERROR", str(date_str), 400, job="cancellation-policy")
        raise ValueError(f"Date format for {date_str} not recognized")

    def get_check_in_date(self) -> str:
        return self.check_in_date

    def check_deadline_format(self, deadline):
        formats = ["%m/%d/%Y %H:%M", "%m/%d/%Y", "%m/%d/%Y %H:%M:%S", "%m/%d/%Y %H:%M:%S:%A", "%Y-%m-%dT%H:%M:%SZ"]
        for fmt in formats:
            try:
                datetime.strptime(deadline, fmt)
                return fmt
            except ValueError:
                continue
        telemetry_logger.log_error("check_deadline_format", "DEADLINE_FORMAT_ERROR", "Unknown format", 400, job="cancellation-policy")
        return "Unknown format"
    def match_total_with_addition(self,total_price,penlity_amount):
        # Try adding 1, 2, or 3 to penlity_amount to see if it can match total_price
        added_amount = 0
        for i in range(1, 4):  # i = 1, 2, 3
            if penlity_amount + i == total_price:
                added_amount = i
                break

        # Final amount to use
        final_amount = penlity_amount + added_amount if added_amount > 0 else penlity_amount
        return final_amount
    
    def round_time(self, time_str):
        # Parse the time string into a datetime object
        dt = datetime.strptime(time_str, '%I:%M %p')

        # Round the time to the nearest half-hour
        rounded_minute = (dt.minute // 30) * 30
        rounded_dt = dt.replace(minute=rounded_minute, second=0, microsecond=0)
        # If rounding up would exceed current time, round down instead
        if rounded_dt > dt:
            rounded_dt -= timedelta(minutes=30)
        return rounded_dt.strftime('%I:%M %p')
    def filter_first_zero_only(self, records):
        if not records:
            telemetry_logger.log_response_time("filter_first_zero_only", 0, 200, job="cancellation-policy")
            return []
        
        filtered_records = []
        prev_amount = None
        prev_record = None
        
        for record in records:
            current_amount = record['amount']
            
            # If this is the first record or amount has changed
            if prev_amount is None or current_amount != prev_amount:
                filtered_records.append(record)
                prev_amount = current_amount
                prev_record = record
            else:
                # Amount is same as previous - update the end time of the previous record
                prev_record['end'] = record['end']
        return filtered_records
    
    def parse_cancellation_policies(self, total_partner: float, is_tool_tip_required: bool = True) -> Dict[str, Any]:
        try:
            cancellation_policies_text = []
            new_cancellation_policy_array = []
            self.partner_cp = self.filter_first_zero_only(self.partner_cp)
            parsed_policies = self.partner_cp
            free_cancellation = self.free_cancellation_policy
            if self.free_cancellation_policy:
                cancellation_type = "Free Cancellation"
            else:
                cancellation_type = "Non-Refundable"

            partial_booking = False
            cp_dates_added = []
            cp_i = 0
            end_policy = False
            first_free_sts = False
            if parsed_policies and len(parsed_policies) > 0:
                for key, policy in enumerate(parsed_policies):
                    ref_amt = 100 - ((total_partner - float(policy['amount'])) / total_partner) * 100
                    ref_amt = round(ref_amt)
                    if ref_amt == 0:
                        if first_free_sts:
                            cancellation_policies_text.pop()
                        ref_amt = 100
                        free_cancellation = True
                        first_free_sts = True
                        cancellation_type = "Free Cancellation"
                    elif ref_amt == 100:
                        ref_amt = 0
                        end_policy = True
                    if ref_amt > 0:
                        partial_booking = True

                    replace_start = str(policy['start'])
                    time_start = datetime.strptime(replace_start, '%Y-%m-%d %H:%M:%S').strftime('%I:%M %p')
                    time_start = self.round_time(time_start)
                    date_start = datetime.strptime(replace_start, '%Y-%m-%d %H:%M:%S').strftime('%d %b %Y')

                    replace_end = str(policy['end'])
                    time_end = datetime.strptime(replace_end, '%Y-%m-%d %H:%M:%S').strftime('%I:%M %p')
                    time_end = self.round_time(time_end)
                    date_end = datetime.strptime(replace_end, '%Y-%m-%d %H:%M:%S').strftime('%d %b %Y')

                    start_date_str = date_start + ' ' + time_start
                    end_date_str = date_end + ' ' + time_end

                    if free_cancellation and cp_i == 0:
                        new_cancellation_policy_array.append({
                            'start_date_time':None,
                            'end_date_time':f" {date_end} {time_end}",
                            'amount': policy['amount'],
                            'refund_percentage': ref_amt,
                            'currency':'USD'
                        })
                        cancellation_policies_text.append(
                            f"Receive a {ref_amt}% refund for your booking if you cancel before {date_end} at {time_end}")
                    elif cp_i == 0:
                        new_cancellation_policy_array.append({
                            'start_date_time':None,
                            'end_date_time':f" {date_end} {time_end}",
                            'amount': policy['amount'],
                            'refund_percentage': ref_amt,
                            'currency':'USD'
                        })
                        cancellation_policies_text.append(
                            f"Receive a {ref_amt}% refund for your booking if you cancel before {date_end} at {time_end}")
                    else:
                        if ref_amt != 0:
                            new_cancellation_policy_array.append({
                                'start_date_time':start_date_str,
                                'end_date_time':end_date_str,
                                'amount': policy['amount'],
                                'refund_percentage': ref_amt,
                                'currency':'USD'
                            })
                            cancellation_policies_text.append(
                                f"Receive a {ref_amt}% refund for your booking if you cancel between {start_date_str} and {end_date_str}")
                    cp_i += 1

                if end_policy:
                    new_cancellation_policy_array.append({
                        'start_date_time':start_date_str,
                        'end_date_time':None,
                        'amount': policy['amount'],
                        'refund_percentage': ref_amt,
                        'currency':'USD'
                    })
                    cancellation_policies_text.append(
                        f"If you cancel your reservation after {start_date_str}, you will not receive a refund. The booking will be non-refundable.")
                else:
                    new_cancellation_policy_array.append({
                        'start_date_time':end_date_str,
                        'end_date_time':None,
                        'amount': policy['amount'],
                        'refund_percentage': ref_amt,
                        'currency':'USD'
                    })
                    cancellation_policies_text.append(
                        f"If you cancel your reservation after {end_date_str}, you will not receive a refund. The booking will be non-refundable.")

                if not partial_booking and not free_cancellation:
                    new_cancellation_policy_array.append({
                        'start_date_time':None,
                        'end_date_time':None,
                        'amount': 0,
                        'refund_percentage': 0,
                        'currency':'USD'
                    })
                    cancellation_type = "Non-Refundable"
                    cancellation_policies_text = ["You won't be refunded if you cancel this booking"]
                elif not free_cancellation and partial_booking:
                    cancellation_type = "Partial refund"
            else:
                cancellation_type = "Non-Refundable"
                new_cancellation_policy_array.append({
                    'start_date_time':None,
                    'end_date_time':None,
                    'amount': 0,
                    'refund_percentage': 0,
                    'currency':'USD'
                })
                cancellation_policies_text = ["You won't be refunded if you cancel this booking"]

            self.cn_polices = {
                'type': cancellation_type,
                'text': cancellation_policies_text,
                'partner_cp': self.partner_cp,
                'partner_cp_new':new_cancellation_policy_array
            }
            if is_tool_tip_required and cancellation_type != "Non-Refundable" and len(self.cn_polices['text']) > 0:
                self.cn_polices['text'].append("The cancellation policy time zone is in the property’s local time zone.")
            telemetry_logger.log_response_time("parse_cancellation_policies", 0, 200, job="cancellation-policy")
            return self.cn_polices
        except Exception as ex:
            print(f"Exception : {str(ex)}")
            telemetry_logger.log_error("parse_cancellation_policies", "PARSE_ERROR", str(ex), 500,response=self.cn_polices, job="cancellation-policy")
            self.cn_polices = {
                'type': '',
                'text': '',
                'partner_cp': '',
                'partner_cp_new':''
            }
            return self.cn_polices

    # parse ratehawk cancellation policy
    def parse_ratehawk_cancellation_policy(self, pricing: List[Dict[str, Any]], total_price: float) -> List[
        Dict[str, Any]]:
        try:
            cp = []
            
            first_end_date = None
            # ratehawk is providing cancellation policy in UTC timezone
            if 'cancellation_penalties' in pricing[0] and 'policies' in pricing[0]['cancellation_penalties']:
                check_in_date = self.get_check_in_date()
                i = 0
                last_date = None
                # first policy
                if pricing[0]['cancellation_penalties']['free_cancellation_before'] is None:
                    cancellation_policy = self.parse_cancellation_policies(total_price)
                    return cancellation_policy
                first_policy_date = pricing[0]['cancellation_penalties']['policies'][0]['start_at']
                if first_policy_date is not None:
                    first_policy_date = self.format_date(first_policy_date)
                    first_end_date = self.format_date(first_policy_date)
                    first_amount = int(
                        round(float(pricing[0]['cancellation_penalties']['policies'][0]['amount_show']), 0))
                    first_policy_amount = first_amount
                    first_start_date = self.current_datetime
                    first_start_date_obj = datetime.strptime(self.current_datetime, "%Y-%m-%d %H:%M:%S")
                    first_end_at_obj = datetime.strptime(first_end_date, "%Y-%m-%d %H:%M:%S")
                    if (first_end_at_obj > first_start_date_obj):
                        # first data
                        if first_policy_amount != 0:
                            self.partner_cp.append({
                                'start': self.convert_listing_timezone(first_start_date),
                                # date format (2021-07-11 00:00:00)
                                'end': self.convert_listing_timezone(first_end_date),
                                'amount': 0,
                                'currency': 'USD'
                            })
                            if first_policy_amount == 0 and self.free_cancellation_policy is None:
                                self.free_cancellation_policy = True
                    else:
                        cancellation_policy = self.parse_cancellation_policies(total_price)
                        return cancellation_policy
                i = 0
                for policy in pricing[0]['cancellation_penalties']['policies']:
                    if i == 0:
                        if first_end_date is not None:
                            start_at = first_end_date
                        else:
                            start_at = policy.get('start_at',
                                                  datetime.strptime(self.current_datetime, "%Y-%m-%d %H:%M:%S"))
                            if start_at is None:
                                start_at = self.current_datetime
                    else:
                        start_at = end_at
                        start_at = policy.get('start_at', datetime.strptime(self.current_datetime, "%Y-%m-%d %H:%M:%S"))
                    end_at = policy.get('end_at', check_in_date)
                    if start_at is None and end_at is None:
                        continue
                    if (end_at is None):
                        end_at = check_in_date
                    last_date = end_at
                    i += 1
                    p_amount = int(round(float(policy['amount_show']), 0))
                    if p_amount == 0:
                        amount_rtn = 0
                    elif p_amount == total_price:
                        amount_rtn = total_price
                    else:
                        if total_price > p_amount:
                            p_amount = self.match_total_with_addition(total_price,p_amount)
                            amount_rtn = total_price - p_amount
                            if amount_rtn <= 0:
                                amount_rtn = total_price
                        else:
                            amount_rtn = total_price
                    start_at = self.format_date(start_at)
                    end_at = self.format_date(end_at)
                    if start_at > end_at:
                        continue
                    self.partner_cp.append({
                        'start': self.convert_listing_timezone(start_at),
                        'end': self.convert_listing_timezone(end_at),
                        'amount': amount_rtn,
                        'currency': pricing[0]['currency_code'] if 'currency_code' in pricing[0] else "USD"
                    })
                    free_cancellation_before = pricing[0]["cancellation_penalties"]["free_cancellation_before"]
                    if free_cancellation_before is None or free_cancellation_before == "":
                        free_cancellation_before = None
                    if policy[
                        'amount_show'] == '0.00' and free_cancellation_before is not None and self.free_cancellation_policy is None:
                        self.free_cancellation_policy = True
            
            cancellation_policy = self.parse_cancellation_policies(total_price)
            telemetry_logger.log_response_time("ratehawk_cancellation_policy", 0, 200,response=self.partner_cp, job="cancellation-policy")
            return cancellation_policy
        except Exception as ex:
            print(f"Exception : {str(ex)}")
            telemetry_logger.log_error("parse_ratehawk_cancellation_policy", "PARSE_ERROR", str(ex), 500, job="cancellation-policy")
            cancellation_policy = self.parse_cancellation_policies(total_price)
            return cancellation_policy

            # Rakuten provide in UTC timezone

    def parse_rakuten_cancellation_policy(self, room_data: Dict[str, Any], total_price: float) -> List[Dict[str, Any]]:
        try:
            #  Rakuten provide cancellation policy in UTC timezone
            cancellation_policies = []
            policy_rules = room_data['cancellation_policy']
            currency_code = room_data['room_rate_currency']
            policies = policy_rules['cancellation_policies']
            # first policy
            first_policy_date = policies[0]['date_from']
            first_end_date = self.format_date(first_policy_date)
            first_policy_amount = policies[0]['penalty_percentage']
            first_start_date = self.current_datetime
            first_start_date_obj = datetime.strptime(self.current_datetime, "%Y-%m-%d %H:%M:%S")

            first_end_at_obj = datetime.strptime(first_end_date, "%Y-%m-%d %H:%M:%S")

            if (first_end_at_obj > first_start_date_obj):
                # first data
                if first_policy_amount != 0:
                    self.partner_cp.append({
                        'start': self.convert_listing_timezone(first_start_date),  # date format (2021-07-11 00:00:00)
                        'end': self.convert_listing_timezone(first_end_date),
                        'amount': 0,
                        'currency': room_data['room_rate_currency']
                    })
                    if first_policy_amount == 0 and self.free_cancellation_policy is None:
                        self.free_cancellation_policy = True
            # end policy
            for rule_data in policies:

                if 'date_from' in rule_data and rule_data['date_from']:
                    start_date = self.format_date(rule_data['date_from'])
                    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
                    if start_date_obj < datetime.strptime(self.current_datetime, "%Y-%m-%d %H:%M:%S"):
                        start_date = self.current_datetime
                else:
                    start_date = self.current_datetime
                    start_date_obj = self.current_datetime

                if 'date_to' in rule_data and rule_data['date_to']:
                    end_date = self.format_date(rule_data['date_to'])
                    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
                else:
                    end_date = self.current_datetime
                    end_date_obj = self.current_datetime
                # case 1 as per rakuten cancellation_policy will regularly return a date that is already in the past (i.e. 1999-01-01T17:47:00Z) This indicates that the penalty_percentage applies from the time of booking
                if start_date_obj < datetime.strptime(self.current_datetime,
                                                      "%Y-%m-%d %H:%M:%S") and end_date_obj < datetime.strptime(
                    self.current_datetime, "%Y-%m-%d %H:%M:%S"):
                    continue
                if start_date_obj > datetime.strptime(self.current_datetime,
                                                      "%Y-%m-%d %H:%M:%S") and end_date_obj <= datetime.strptime(
                    self.current_datetime, "%Y-%m-%d %H:%M:%S"):
                    end_date = self.format_date(self.get_check_in_date())

                room_price = total_price
                if rule_data['penalty_percentage'] == 0:
                    percentage = 0
                elif rule_data['penalty_percentage'] == 100:
                    percentage = 100
                else:
                    percentage = 100 - rule_data['penalty_percentage']
                amount_percentage = room_price / 100
                percentage_amount = int(round(amount_percentage * percentage))
                if start_date > end_date:
                    continue
                self.partner_cp.append({
                    'start': self.convert_listing_timezone(start_date),
                    'end': self.convert_listing_timezone(end_date),
                    'amount': percentage_amount,
                    'currency': currency_code
                })
                if rule_data['penalty_percentage'] == 0 and self.free_cancellation_policy is None:
                    self.free_cancellation_policy = True
            cancellation_policy = self.parse_cancellation_policies(total_price)
            telemetry_logger.log_response_time("parse_rakuten_cancellation_policy", 0, 200,response=self.partner_cp, job="cancellation-policy")
            return cancellation_policy
        except Exception as ex:
            print(f"Exception : {str(ex)}")
            telemetry_logger.log_error("parse_rakuten_cancellation_policy", "PARSE_ERROR", str(ex), 500, job="cancellation-policy")
            cancellation_policy = self.parse_cancellation_policies(total_price)
            return cancellation_policy

    # please be kindly note all the cancelation are based on Beijing time
    def parse_dida_cancellation_policy(self, pricing: Dict[str, Any], total_price: float) -> List[Dict[str, Any]]:
        try:
            #  Dida provide cancellation policy in Bejing timezone
            cp = []
            check_in_date = self.format_date(self.get_check_in_date())
            # pricing["RatePlanCancellationPolicyList"] = [
            #     entry for entry in pricing["RatePlanCancellationPolicyList"]
            #     if self.date_format_in_obj(entry["FromDate"]) and self.date_format_in_obj(
            #         entry["FromDate"]) >= datetime.strptime(self.current_datetime, "%Y-%m-%d %H:%M:%S")
            # ]
            beijing_tz = pytz.timezone("Asia/Shanghai")
            # Get current time in Beijing
            beijing_time = datetime.now(beijing_tz)
            # Print formatted time
            current_datetime_bejing =  beijing_time.strftime("%Y-%m-%d %H:%M:%S")
            for entry in pricing["RatePlanCancellationPolicyList"]:
                if self.date_format_in_obj(entry["FromDate"]):
                    from_date = self.date_format_in_obj(entry["FromDate"])
                    current_date = datetime.strptime(current_datetime_bejing, "%Y-%m-%d %H:%M:%S")
                    
                    # If FromDate is less than current_date, update it
                    if from_date < current_date:
                        entry["FromDate"] = self.current_datetime

            # Keep only valid entries (after modification)
            pricing["RatePlanCancellationPolicyList"] = [
                entry for entry in pricing["RatePlanCancellationPolicyList"]
                if self.date_format_in_obj(entry["FromDate"])
            ]
            if 'RatePlanCancellationPolicyList' in pricing and len(pricing['RatePlanCancellationPolicyList']) > 0:
                temp_array = []
                i = 0
                last_date = None
                # check first date
                first_policy_date = pricing["RatePlanCancellationPolicyList"][0]['FromDate']
                first_policy_date = self.convert_dida_time_to_utc(first_policy_date)
                first_policy_amount = int(round(pricing["RatePlanCancellationPolicyList"][0]['Amount'], 0))
                first_start_date    = self.format_date(self.current_datetime)
                first_end_at        = self.format_date(first_policy_date)
                if (first_end_at > first_start_date):
                    # first data
                    if first_policy_amount > 0:

                        self.partner_cp.append({
                            'start': self.convert_listing_timezone(first_start_date),
                            # date format (2021-07-11 00:00:00)
                            'end': self.convert_listing_timezone(first_end_at),
                            'amount': 0,
                            'currency': pricing['Currency']
                        })
                        if first_policy_amount == 0 and self.free_cancellation_policy is None:
                            self.free_cancellation_policy = True
                #  first policy end

                for k, policy in enumerate(pricing['RatePlanCancellationPolicyList']):
                    if i == 0:
                        start_at = first_end_at
                    else:
                        start_at = end_at
                    if k + 1 < len(pricing['RatePlanCancellationPolicyList']):
                        next_policy = pricing['RatePlanCancellationPolicyList'][k + 1]
                        end_at = next_policy.get('FromDate', check_in_date)
                        end_at = self.convert_dida_time_to_utc(end_at)
                    else:
                        end_at = check_in_date
                    end_at = self.format_date(end_at)
                    end_date_obj = datetime.strptime(end_at, "%Y-%m-%d %H:%M:%S")
                    if end_date_obj < datetime.strptime(self.current_datetime, "%Y-%m-%d %H:%M:%S"):
                        continue
                        # end_at = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

                    last_date = end_at
                    i += 1
                    p_amount = int(round(policy['Amount'], 0))
                    total_price = int(round(total_price))
                    if p_amount == 0:
                        amount_rtn = 0
                    elif p_amount == total_price:
                        amount_rtn = total_price
                    else:
                        if total_price / p_amount == 2:
                            amount_rtn = total_price - p_amount
                        elif  total_price > p_amount:
                            p_amount = self.match_total_with_addition(total_price,p_amount)
                            amount_rtn = total_price - p_amount
                            if amount_rtn <= 0:
                                amount_rtn = total_price
                        else:
                            amount_rtn = total_price

                    if start_at > end_at:
                        continue
                    self.partner_cp.append({
                        'start': self.convert_listing_timezone(start_at),  # date format (2021-07-11 00:00:00)
                        'end': self.convert_listing_timezone(end_at),
                        'amount': amount_rtn,
                        'currency': pricing['Currency']
                    })
                    if policy['Amount'] == 0 and self.free_cancellation_policy is None:
                        self.free_cancellation_policy = True
            cancellation_policy = self.parse_cancellation_policies(total_price)
            telemetry_logger.log_response_time("parse_dida_cancellation_policy", 0, 200,response=self.partner_cp, job="cancellation-policy")
            return cancellation_policy
        except Exception as ex:
            print(f"Exception : {str(ex)}")
            telemetry_logger.log_error("parse_dida_cancellation_policy", "PARSE_ERROR", str(ex), 500, job="cancellation-policy")
            cancellation_policy = self.parse_cancellation_policies(total_price)
            return cancellation_policy

    # Hp provide in UTC timezone
    def parse_hp_cancellation_policy(self, pricing: Dict[str, Any], total_hp: float, pernight_amount: float) -> List[
        Dict[str, Any]]:
        try:
            global free_cancellation_policy
            cancellation_policies = []
            temp_array = []
            s_end_date = None
            hp_check_in_date = self.format_date(self.check_in_date)
            free_cut_off = None
            nonRefundable = pricing.get('nonRefundable', None)
            last_date = None
            
            if nonRefundable == True:
                return self.parse_cancellation_policies(total_hp)
                
            # Process deadline formats for all penalties
            for penalty in pricing['cancelPenalties']:
                penalty['format'] = self.check_deadline_format(penalty['deadline'])
            
            # Sort penalties by deadline
            pricing['cancelPenalties'] = sorted(
                pricing['cancelPenalties'],
                key=lambda x: datetime.strptime(x['deadline'], x['format'])
            )
            
            # Handle non-refundable case
            if nonRefundable is None or nonRefundable is True:
                return self.parse_cancellation_policies(total_hp)
                
            # Handle free cancellation period
            if pricing.get('freeCancellation', False) and 'freeCancellationCutOff' in pricing and pricing['freeCancellationCutOff']:
                s_start_at = self.current_datetime
                s_end_date = self.format_date(pricing['freeCancellationCutOff'])
                last_date  = s_end_date
                
                if s_end_date > self.current_datetime:
                    self.partner_cp.append({
                        'start': self.convert_listing_timezone(s_start_at),
                        'end': self.convert_listing_timezone(s_end_date),
                        'amount': 0,
                        'currency': pricing.get('currencyCode', 'USD')
                    })
                    free_cut_off = True
                    if self.free_cancellation_policy is None:
                        self.free_cancellation_policy = True
            # Process first policy
            if not pricing['cancelPenalties']:
                return self.parse_cancellation_policies(total_hp)
                
            first_policy = pricing['cancelPenalties'][0]
            first_policy_date = first_policy['deadline'].replace(',', '')
            first_end_date = self.format_date(first_policy_date)
            
            # Determine amount based on case (type/amount vs price)
            if 'type' in first_policy and 'amount' in first_policy:
                # Case 1: Has type and amount
                if first_policy['type'] == 'price':
                    first_amount = first_policy.get('amount', 0)
                else:
                    no_of_night = first_policy.get('nights', 1)
                    first_amount = no_of_night * pernight_amount
            elif 'type' in first_policy and 'price' in first_policy:
                if first_policy['type'] == 'price':
                    first_amount = first_policy.get('price', 0)
                else:
                    no_of_night = first_policy.get('nights', 1)
                    first_amount = no_of_night * pernight_amount
            elif 'price' in first_policy:
                first_amount = first_policy.get('price', 0)
            else:
                first_amount = first_policy.get('amount', 0)
            if last_date is not None:
                first_start_date = last_date
                first_start_date_obj = first_start_date
            else:
                first_start_date = self.current_datetime
                first_start_date_obj = datetime.strptime(first_start_date, "%Y-%m-%d %H:%M:%S")
            first_end_at_obj = datetime.strptime(first_end_date, "%Y-%m-%d %H:%M:%S")
            first_start_date_obj = datetime.strptime(first_start_date, "%Y-%m-%d %H:%M:%S")
            if free_cut_off is None and first_end_at_obj > first_start_date_obj and first_amount != 0:
                last_date = first_end_date
                self.partner_cp.append({
                    'start': self.convert_listing_timezone(first_start_date),
                    'end': self.convert_listing_timezone(first_end_date),
                    'amount': 0,
                    'currency': 'USD'
                })
                if first_amount == 0 and self.free_cancellation_policy is None:
                    self.free_cancellation_policy = True
            if len(pricing['cancelPenalties']) == 1:
                return self.parse_cancellation_policies(total_hp)
            for k, policy in enumerate(pricing['cancelPenalties']):
                # Determine start and end dates
                start_at = last_date
                if k + 1 < len(pricing['cancelPenalties']):
                    next_policy = pricing['cancelPenalties'][k + 1]
                    end_at_str = next_policy.get('deadline', hp_check_in_date).replace(',', '')
                    end_at = self.format_date(end_at_str)
                else:
                    end_at = hp_check_in_date
                    next_policy = policy

                if end_at == start_at or end_at < self.current_datetime:
                    continue
                  
                last_date = end_at
                if 'type' in next_policy and 'amount' in next_policy:
                    # Case 1: Has type and amount
                    if next_policy['type'] == 'price':
                        amount = next_policy.get('amount', 0)
                    else:
                        no_of_night = next_policy.get('nights', 1)
                        amount = no_of_night * pernight_amount
                elif 'type' in next_policy and 'price' in next_policy:
                    if next_policy['type'] == 'price':
                        amount = next_policy.get('price', 0)
                    else:
                        no_of_night = next_policy.get('nights', 1)
                        amount = no_of_night * pernight_amount
                elif 'price' in next_policy:
                    amount = next_policy.get('price', 0)
                else:
                    amount = next_policy.get('amount', 0)
                # Skip if dates are invalid
                start_date_obj = datetime.strptime(start_at, "%Y-%m-%d %H:%M:%S") if isinstance(start_at, str) else \
                    datetime.strptime(start_at.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
                end_date_obj = datetime.strptime(end_at, "%Y-%m-%d %H:%M:%S") if isinstance(end_at, str) else \
                    datetime.strptime(end_at.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
                    
                if end_date_obj < start_date_obj:
                    continue
                   
                # Calculate return amount
                if amount == 0:
                    ret_amount = 0
                else:
                    if total_hp > amount:
                        amount = self.match_total_with_addition(total_hp,amount)
                        ret_amount = total_hp - amount
                        if ret_amount <= 0:
                            ret_amount = total_hp
                    else:
                        ret_amount = total_hp
                
                # Format dates
                date_strt = self.format_date(start_at) if isinstance(start_at, str) else start_at.strftime("%Y-%m-%d %H:%M:%S")
                date_end = self.format_date(end_at) if isinstance(end_at, str) else end_at.strftime("%Y-%m-%d %H:%M:%S")
                
                if date_strt > date_end:
                    continue
                    
                self.partner_cp.append({
                    'start': self.convert_listing_timezone(date_strt),
                    'end': self.convert_listing_timezone(date_end),
                    'amount': ret_amount,
                    'currency': pricing.get('currencyCode', 'USD')
                })
                
                if ret_amount == 0 and self.free_cancellation_policy is None:
                    self.free_cancellation_policy = True
            telemetry_logger.log_response_time("parse_hp_cancellation_policy", 0, 200,response=self.partner_cp, job="cancellation-policy")        
            return self.parse_cancellation_policies(total_hp)
        
        except Exception as ex:
            print(f"Exception in parse_hp_cancellation_policy: {str(ex)}")
            telemetry_logger.log_error("parse_hp_cancellation_policy", "PARSE_ERROR", str(ex), 500, job="cancellation-policy")
            return self.parse_cancellation_policies(total_hp)

    # Tbo cancellation policy method
    # please be kindly note all the cancelation are based on Beijing time
    def parse_tbo_cancellation_policy(self, pricing: Dict[str, Any], total_tbo: float) -> List[Dict[str, Any]]:
        try:
            #  TBO provide cancellation policy in UTC timezone
            global free_cancellation_policy
            cp = []
            total_tbo = int(round(total_tbo))
            check_in_date = self.format_date(self.get_check_in_date())
            # Sort the cancelPenalties using the determined formats
            pricing = sorted(pricing, key=lambda x: datetime.strptime(x['FromDate'], '%d-%m-%Y %H:%M:%S'))
            #  remove past date
            pricing = [entry for entry in pricing if
                       self.date_format_in_obj(entry["FromDate"]) and self.date_format_in_obj(
                           entry["FromDate"]) >= datetime.strptime(self.current_datetime, "%Y-%m-%d %H:%M:%S")]
            if len(pricing) > 0:
                temp_array = []
                i = 0
                last_date = None
                # check first date
                first_policy_date = pricing[0]['FromDate']
                first_end_at = self.format_date(first_policy_date)
                first_policy_amount = int(round(pricing[0]['CancellationCharge']))
                first_start_date = self.format_date(self.current_datetime)
                first_start_date_obj = datetime.strptime(first_start_date, "%Y-%m-%d %H:%M:%S")
                first_end_at_obj = datetime.strptime(first_end_at, "%Y-%m-%d %H:%M:%S")

                if first_end_at_obj > first_start_date_obj:
                    if first_policy_amount > 0:
                        self.partner_cp.append({
                            'start': self.convert_listing_timezone(first_start_date),
                            # date format (2021-07-11 00:00:00)
                            'end': self.convert_listing_timezone(first_end_at),
                            'amount': 0,
                            'currency': 'USD'
                        })
                    if first_policy_amount == 0 and self.free_cancellation_policy is None:
                        self.free_cancellation_policy = True
                # print(self.partner_cp)
                for k, policy in enumerate(pricing):
                    if i == 0:
                        start_at = first_end_at
                    else:
                        start_at = last_date
                    if k + 1 < len(pricing):
                        next_policy = pricing[k + 1]
                        end_at = next_policy.get('FromDate', check_in_date)
                    else:
                        end_at = check_in_date

                    end_at = self.format_date(end_at)
                    end_date_obj = datetime.strptime(end_at, "%Y-%m-%d %H:%M:%S")

                    if end_date_obj < datetime.strptime(self.current_datetime, "%Y-%m-%d %H:%M:%S"):
                        continue
                        # end_at = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
                    last_date = end_at
                    i += 1

                    if policy['ChargeType'] == 'Fixed':
                        if int(round(policy['CancellationCharge'])) == total_tbo:
                            can_amount = total_tbo
                            continue
                        elif int(round(policy['CancellationCharge'])) == 0:
                            can_amount = 0
                        else:
                            can_amount = total_tbo - int(round(policy['CancellationCharge']))
                    else:
                        percentage = int(round(policy['CancellationCharge']))
                        percentage = int(round(percentage))
                        percentage = int(round((percentage / 100) * total_tbo))
                        if percentage == total_tbo:
                            can_amount = total_tbo
                            continue
                        elif percentage == 0:
                            can_amount = 0
                        else:
                            if total_tbo > percentage:
                                percentage = self.match_total_with_addition(total_tbo,percentage)
                                can_amount = total_tbo - percentage
                                if can_amount <= 0:
                                    can_amount = total_tbo
                            else:
                                can_amount = total_tbo
                            # can_amount = total_tbo - percentage
                    if start_at > end_at:
                        continue
                    self.partner_cp.append({
                        'start': self.convert_listing_timezone(start_at),  # date format (2021-07-11 00:00:00)
                        'end': self.convert_listing_timezone(end_at),
                        'amount': can_amount,
                        'currency': 'USD'
                    })
                    if can_amount == 0 and self.free_cancellation_policy is None:
                        self.free_cancellation_policy = True
            cancellation_policy_data = self.parse_cancellation_policies(total_tbo)
            telemetry_logger.log_response_time("parse_tbo_cancellation_policy", 0, 200,response=self.partner_cp, job="cancellation-policy")
            return cancellation_policy_data
        except Exception as ex:
            print(f"Exception : {str(ex)}")
            telemetry_logger.log_error("parse_tbo_cancellation_policy", "PARSE_ERROR", str(ex), 500, job="cancellation-policy")
            cancellation_policy = self.parse_cancellation_policies(total_tbo)
            return cancellation_policy

    #  hxpro provide cancellation in GMT+3
    def parse_hxpro_cancellation_policy(self, pricing: Dict[str, Any], total_hxpro: float) -> List[Dict[str, Any]]:
        try:
            # Clear the partner cancellation policies list
            self.partner_cp = []
            # hx pro provide cancellation policy into GMT+3 so first we will convert current datetime into GMT+3

            # Check if cancellation is supported
            if pricing.get('supports_cancellation', False):
                # Retrieve the policy details
                policies = pricing.get('policies', [])
                i = 0
                last_end_date = self.current_datetime
                # Process each policy
                for policy in policies:
                    current_datetime_hxpro_start = self.convert_hxpro_time_to_utc(self.current_datetime)
                    check_in_date = self.get_check_in_date()
                    current_datetime_hxpro = datetime.strptime(check_in_date, "%Y-%m-%dT%H:%M:%S")
                    days_remaining = policy.get('days_remaining', 0)
                    ratio = float(policy.get('ratio', '0.00'))

                    # Calculate the end date for each policy
                    if i == 0:
                        start_date = self.current_datetime
                    else:
                        start_date = last_end_date
                    end_date = current_datetime_hxpro - timedelta(days=days_remaining)
                    last_data = end_date.strftime('%Y-%m-%d %H:%M:%S')
                    s_end_date = end_date

                    # s_end_date = s_end_date.strftime("%Y-%m-%d %H:%M:%S")
                    if last_data > self.format_date(self.current_datetime):
                        # Calculate the refund amount
                        refund_amount = total_hxpro * (1 - ratio)
                        # Append to the partner cancellation policy list
                        if start_date > last_data:
                            continue
                        if i == 0 and int(ratio) == 0:
                            self.partner_cp.append({
                                'start': self.convert_listing_timezone(start_date),
                                'end': self.convert_listing_timezone(last_data),
                                'amount': 0,
                                'currency': 'USD'
                            })
                        else:
                            self.partner_cp.append({
                                'start': self.convert_listing_timezone(start_date),
                                'end': self.convert_listing_timezone(last_data),
                                'amount': refund_amount,
                                'currency': 'USD'
                            })
                        i = i + 1
                        # Update the current date to the end date for the next iteration
                        last_end_date = last_data
                        # Check for free cancellation
                        if ratio == 1.0 and self.free_cancellation_policy is None:
                            self.free_cancellation_policy = True
            # Parse and return the cancellation policies
            cancellation_policy = self.parse_cancellation_policies(total_hxpro)
            telemetry_logger.log_response_time("parse_hxpro_cancellation_policy", 0, 200,response=self.partner_cp, job="cancellation-policy")
            return cancellation_policy
        except Exception as ex:
            print(f"Exception: {str(ex)}")
            telemetry_logger.log_error("parse_hxpro_cancellation_policy", "PARSE_ERROR", str(ex), 500, job="cancellation-policy")
            cancellation_policy = self.parse_cancellation_policies(total_hxpro)
            return cancellation_policy

    # please be kindly note all the cancelation are based UTC timezone
    def parse_hotelbeds_cancellation_policy(self, pricing: Dict[str, Any], total_hotelbed: float) -> List[
        Dict[str, Any]]:
        try:
            #  Hotel provide cancellation policy in UTC timezone
            global free_cancellation_policy
            pricing = pricing.get("cancellationPolicies", [])
            total_hotelbed = int(round(total_hotelbed))
            check_in_date = self.format_date(self.get_check_in_date())
            # Sort the list based on the 'from' date
            pricing = sorted(pricing, key=lambda x: datetime.fromisoformat(x['from']))
            if len(pricing) > 0:
                temp_array = []
                i = 0
                last_date = None
                # check first date
                first_policy_date = pricing[0]['from']
                dt = datetime.fromisoformat(first_policy_date.replace("Z", "+00:00"))
                # Ensure the datetime object is in UTC
                first_policy_date = dt.astimezone(pytz.utc)
                first_policy_date = first_policy_date.strftime('%Y-%m-%d %H:%M:%S')
                first_end_at = self.format_date(first_policy_date)
                first_policy_amount = int(round(float(pricing[0]['amount'])))
                first_start_date = self.format_date(self.current_datetime)
                first_start_date_obj = datetime.strptime(first_start_date, "%Y-%m-%d %H:%M:%S")
                first_end_at_obj = datetime.strptime(first_end_at, "%Y-%m-%d %H:%M:%S")

                if first_end_at_obj > first_start_date_obj:
                    if first_policy_amount > 0:
                        self.partner_cp.append({
                            'start': self.convert_listing_timezone(first_start_date),
                            # date format (2021-07-11 00:00:00)
                            'end': self.convert_listing_timezone(first_end_at),
                            'amount': 0,
                            'currency': 'USD'
                        })
                    if first_policy_amount == 0 and self.free_cancellation_policy is None:
                        self.free_cancellation_policy = True
                # print(self.partner_cp)
                for k, policy in enumerate(pricing):
                    if i == 0:
                        start_at = first_end_at
                    else:
                        start_at = last_date
                    if k + 1 < len(pricing):
                        next_policy = pricing[k + 1]
                        end_at = next_policy.get('from', check_in_date)
                        dt = datetime.fromisoformat(end_at.replace("Z", "+00:00"))
                        # Ensure the datetime object is in UTC
                        end_at = dt.astimezone(pytz.utc)
                        end_at = end_at.strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        end_at = check_in_date

                    end_at = self.format_date(end_at)
                    end_date_obj = datetime.strptime(end_at, "%Y-%m-%d %H:%M:%S")

                    if end_date_obj < datetime.strptime(self.current_datetime, "%Y-%m-%d %H:%M:%S"):
                        continue
                        # end_at = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
                    last_date = end_at
                    i += 1

                    if int(round(float(policy['amount']))) > total_hotelbed:
                        continue
                    else:
                        can_amount = total_hotelbed - int(round(float(policy['amount'])))
                        if can_amount == 0:
                            can_amount = total_hotelbed
                    if start_at > end_at:
                        continue
                    self.partner_cp.append({
                        'start': self.convert_listing_timezone(start_at),  # date format (2021-07-11 00:00:00)
                        'end': self.convert_listing_timezone(end_at),
                        'amount': can_amount,
                        'currency': 'USD'
                    })
                    if can_amount == 0 and self.free_cancellation_policy is None:
                        self.free_cancellation_policy = True
            cancellation_policy_data = self.parse_cancellation_policies(total_hotelbed)
            telemetry_logger.log_response_time("parse_htoelbeds_cancellation_policy", 0, 200,response=self.partner_cp, job="cancellation-policy")
            return cancellation_policy_data
        except Exception as ex:
            print(f"Exception : {str(ex)}")
            telemetry_logger.log_error("parse_htoelbeds_cancellation_policy", "PARSE_ERROR", str(ex), 500, job="cancellation-policy")
            cancellation_policy = self.parse_cancellation_policies(total_hotelbed)
            return cancellation_policy
    
    def parse_hibeds_cancellation_policy(self, pricing: Dict[str, Any], total_hibeds: float) -> List[Dict[str, Any]]:
        try:
            #  Hibeds provide cancellation policy in UTC timezone
            global free_cancellation_policy
            cp = []
            total_hibeds = int(round(total_hibeds))
            check_in_date = self.format_date(self.get_check_in_date())
            if pricing:
                if pricing['cancellationType'] == '1':
                    first_policy_date = pricing['cancellationWindowDate']
                    first_end_at = self.format_date(first_policy_date)
                    first_policy_amount = int(total_hibeds)
                    first_start_date = self.format_date(self.current_datetime)
                    if first_end_at > self.current_datetime:
                        first_start_date_obj = datetime.strptime(first_start_date, "%Y-%m-%d %H:%M:%S")
                        first_end_at_obj = datetime.strptime(first_end_at, "%Y-%m-%d %H:%M:%S")
                        self.partner_cp.append({
                            'start': self.convert_listing_timezone(first_start_date),
                            # date format (2021-07-11 00:00:00)
                            'end': self.convert_listing_timezone(first_end_at),
                            'amount': 0,
                            'currency': 'USD'
                        })
                        if pricing['cancellationType'] == '1' and self.free_cancellation_policy is None:
                            self.free_cancellation_policy = True
                    cancellation_policy = self.parse_cancellation_policies(total_hibeds)
                elif pricing['cancellationType'] == '0':
                    cancellation_policy = self.parse_cancellation_policies(total_hibeds)
                else:
                   cancellation_policy = self.parse_cancellation_policies(total_hibeds)
            else:
                cancellation_policy = self.parse_cancellation_policies(total_hibeds)
            telemetry_logger.log_response_time("parse_hibeds_cancellation_policy", 0, 200,response=self.partner_cp, job="cancellation-policy")
            return cancellation_policy
        except Exception as ex:
            print(f"Exception : {str(ex)}")
            telemetry_logger.log_error("parse_hibeds_cancellation_policy", "PARSE_ERROR", str(ex), 500, job="cancellation-policy")
            cancellation_policy = self.parse_cancellation_policies(total_hibeds)
            return cancellation_policy
    # this method will convert property cancellation policy according to the property timezone
    # def convert_to_timezone(self, date_str, from_tz_str, to_tz_str):
    #     try:
    #         from_tz = pytz.timezone(from_tz_str)
    #         to_tz = pytz.timezone(to_tz_str)

    #         # Parse the date string
    #         naive_datetime = datetime.strptime(date_str, '%d %b %Y %I:%M %p')
    #         # Localize to the from_tz
    #         localized_datetime = from_tz.localize(naive_datetime)
    #         # Convert to the target timezone
    #         converted_datetime = localized_datetime.astimezone(to_tz)
    #         return converted_datetime
    #     except Exception as ex:
    #         print(f"Exception : {str(ex)}")
    #         return []
    def parse_tourmind_cancellation_policy(self, room_data, total_price, guest_rate = 0, host_rate = 0):
        try:
            policy_info = room_data['CancelPolicyInfos']
            currency_code = policy_info[0]['CurrencyCode']
            first_policy_amount = policy_info[0]['Amount']
            
            # first_policy_date = policy_info[0]['From']
            # first_end_date = self.format_date(first_policy_date)
            # first_start_date = self.current_datetime
            if policy_info[0]['From']:
                first_policy_date = self.format_date(policy_info[0]['From'])
                first_end_date    = first_policy_date
                first_policy_amount = float(policy_info[0]['Amount'])
                first_start_date = self.current_datetime
                first_start_date_obj = datetime.strptime(self.current_datetime, "%Y-%m-%d %H:%M:%S")
                first_end_at_obj = datetime.strptime(first_end_date, "%Y-%m-%d %H:%M:%S")
                if (first_end_at_obj > first_start_date_obj):
                    # first data
                    if first_policy_amount == 0:
                        self.partner_cp.append({
                            'start': self.convert_listing_timezone(first_start_date),  # date format (2021-07-11 00:00:00)
                            'end': self.convert_listing_timezone(first_end_date),
                            'amount': 0,
                            'currency': currency_code
                        })
                        if first_policy_amount == 0 and room_data['isRefundable'] == True and self.free_cancellation_policy is None:
                            self.free_cancellation_policy = True
                            
                    if len(policy_info) == 1:
                        self.partner_cp.append({
                            'start': self.convert_listing_timezone(first_start_date),  # date format (2021-07-11 00:00:00)
                            'end': self.convert_listing_timezone(first_end_date),
                            'amount': 0,
                            'currency': currency_code
                        })
            for rule_data in policy_info:
                p_amount = int(round(rule_data['Amount'], 0))
                if 'From' in rule_data and rule_data['From']:
                    start_date = self.format_date(rule_data['From'])
                    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
                    if start_date_obj < datetime.strptime(self.current_datetime, "%Y-%m-%d %H:%M:%S"):
                        start_date = self.current_datetime
                else:
                    start_date = self.current_datetime
                    start_date_obj = self.current_datetime
                if 'To' in rule_data and rule_data['To']:
                    end_date = self.format_date(rule_data['To'])
                    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
                else:
                    end_date = self.format_date(self.check_in_date)
                    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
                curr_time = datetime.strptime(self.current_datetime, "%Y-%m-%d %H:%M:%S")
                if start_date_obj < curr_time and end_date_obj < curr_time:
                    continue
                if start_date_obj > curr_time >= end_date_obj:
                    end_date = self.format_date(self.get_check_in_date())
                if start_date > end_date:
                    continue
                total_price = int(round(total_price))
                if p_amount == 0:
                    amount_rtn = 0
                elif p_amount == total_price:
                    amount_rtn = total_price
                else:
                    if total_price / p_amount == 2:
                        amount_rtn = total_price - p_amount
                    elif  total_price > p_amount:
                        p_amount = self.match_total_with_addition(total_price,p_amount)
                        amount_rtn = total_price - p_amount
                        if amount_rtn <= 0:
                            amount_rtn = total_price
                    else:
                        amount_rtn = total_price
                self.partner_cp.append({
                    'start': self.convert_listing_timezone(start_date),
                    'end': self.convert_listing_timezone(end_date),
                    'amount': amount_rtn,
                    'currency': currency_code
                })
                if amount_rtn == 0 and self.free_cancellation_policy is None:
                    self.free_cancellation_policy = True
            cancellation_policy = self.parse_cancellation_policies(total_price)
            telemetry_logger.log_response_time("parse_tourmind_cancellation_policy", 0, 200,response=self.partner_cp, job="cancellation-policy")
            return cancellation_policy
        except Exception as e:
            print(f"Exception: {str(e)}")
            telemetry_logger.log_error("parse_tourmind_cancellation_policy", "PARSE_ERROR", str(e), 500, job="cancellation-policy")
            cancellation_policy = self.parse_cancellation_policies(total_price)
            return cancellation_policy

    def parse_webbeds_cancellation_policy(self, room_data, total_price, guest_rate = 0, host_rate = 0):
        try:
            # First ensure we have the country timezone set
            if self.countryname:
                self.get_country_timezone(self.countryname)
            policy_info = room_data['cancellationRules']['rule']
            currency_code = 'USD'
            last_end_date_obj = None
            for rule_data in policy_info:
                p_amount = round(float(rule_data['charge']['text']))
                if 'fromDate' in rule_data and rule_data['fromDate']['text']:
                    if last_end_date_obj is None:
                        start_date = self.convert_webbeds_time_to_utc(rule_data['fromDate']['text'])
                    else:
                        start_date = last_end_date_obj
                    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
                    if start_date_obj < datetime.strptime(self.current_datetime, "%Y-%m-%d %H:%M:%S"):
                        start_date = self.current_datetime
                else:
                    start_date = self.current_datetime
                    start_date_obj = datetime.strptime(self.current_datetime, "%Y-%m-%d %H:%M:%S")
                if 'toDate' in rule_data and rule_data['toDate']['text']:
                    end_date = self.convert_webbeds_time_to_utc(rule_data['toDate']['text'])
                    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
                else:
                    end_date = self.format_date(self.check_in_date)
                    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
                curr_time = datetime.strptime(self.current_datetime, "%Y-%m-%d %H:%M:%S")
                if start_date_obj < curr_time and end_date_obj < curr_time:
                    continue
                if start_date_obj > curr_time >= end_date_obj:
                    end_date = self.format_date(self.get_check_in_date())
                if start_date > end_date:
                    continue
                total_price = int(round(total_price))
                if p_amount == 0:
                    amount_rtn = 0
                elif p_amount == total_price:
                    amount_rtn = total_price
                else:
                    if total_price / p_amount == 2:
                        amount_rtn = total_price - p_amount
                    elif  total_price > p_amount:
                        p_amount = self.match_total_with_addition(total_price,p_amount)
                        amount_rtn = total_price - p_amount
                        if amount_rtn <= 0:
                            amount_rtn = total_price
                    else:
                        amount_rtn = total_price
                last_end_date_obj = end_date
                cp = {
                    'start': self.convert_listing_timezone(start_date),
                    'end': self.convert_listing_timezone(end_date),
                    'amount': amount_rtn,
                    'currency': currency_code
                }
                self.partner_cp.append(cp)
                if amount_rtn == 0 and self.free_cancellation_policy is None:
                    self.free_cancellation_policy = True
            cancellation_policy = self.parse_cancellation_policies(total_price)
            telemetry_logger.log_response_time("parse_webbeds_cancellation_policy", 0, 200,response=self.partner_cp, job="cancellation-policy")
            return cancellation_policy
        except Exception as e:
            print(f"Exception: {str(e)}")
            telemetry_logger.log_error("parse_webbeds_cancellation_policy", "PARSE_ERROR", str(e), 500, job="cancellation-policy")
            cancellation_policy = self.parse_cancellation_policies(total_price)
            return cancellation_policy

    def parse_traveloka_cancellation_policy(self, room_data, total_price, guest_rate = 0, host_rate = 0):
        try:
            policy_info = room_data['policies']
            currency_code = 'USD'

            for rule_data in policy_info:
                p_amount = round(float(rule_data['cancellationCharge']['amount']))
                if 'startCancelDateTime' in rule_data and rule_data['startCancelDateTime']:
                    dt = parser.parse(rule_data['startCancelDateTime'])  # Parses with timezone
                    parsed_date = str(dt.replace(tzinfo=None))  # Remove timezone
                    # start_date = self.format_date(rule_data['startCancelDateTime'])
                    start_date = self.format_date(parsed_date)
                    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
                    if start_date_obj < datetime.strptime(self.current_datetime, "%Y-%m-%d %H:%M:%S"):
                        start_date = self.current_datetime
                else:
                    start_date = self.current_datetime
                    start_date_obj = datetime.strptime(self.current_datetime, "%Y-%m-%d %H:%M:%S")
                if 'endCancelDateTime' in rule_data and rule_data['endCancelDateTime']:
                    dt = parser.parse(rule_data['endCancelDateTime'])  # Parses with timezone
                    parsed_date = str(dt.replace(tzinfo=None))  # Remove timezone
                    end_date = self.format_date(parsed_date)
                    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
                else:
                    end_date = self.format_date(self.check_in_date)
                    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
                curr_time = datetime.strptime(self.current_datetime, "%Y-%m-%d %H:%M:%S")
                if start_date_obj < curr_time and end_date_obj < curr_time:
                    continue
                if start_date_obj > curr_time >= end_date_obj:
                    end_date = self.format_date(self.get_check_in_date())
                if start_date > end_date:
                    continue
                
                total_price = int(round(total_price))
                if p_amount == 0:
                    amount_rtn = 0
                elif p_amount == total_price:
                    amount_rtn = total_price
                else:
                    if total_price / p_amount == 2:
                        amount_rtn = total_price - p_amount
                    elif  total_price > p_amount:
                        p_amount = self.match_total_with_addition(total_price,p_amount)
                        amount_rtn = total_price - p_amount
                        if amount_rtn <= 0:
                            amount_rtn = total_price
                    else:
                        amount_rtn = total_price
                cp = {
                    'start': self.convert_listing_timezone(start_date),
                    'end': self.convert_listing_timezone(end_date),
                    'amount': amount_rtn,
                    'currency': currency_code
                }
                self.partner_cp.append(cp)
                if amount_rtn == 0 and self.free_cancellation_policy is None:
                    self.free_cancellation_policy = True
            cancellation_policy = self.parse_cancellation_policies(total_price)
            telemetry_logger.log_response_time("parse_traveloka_cancellation_policy", 0, 200,response=self.partner_cp, job="cancellation-policy")
            return cancellation_policy
        except Exception as e:
            print(f"Exception: {str(e)}")
            telemetry_logger.log_error("parse_traveloka_cancellation_policy", "PARSE_ERROR", str(e), 500, job="cancellation-policy")
            cancellation_policy = self.parse_cancellation_policies(total_price)
            return cancellation_policy

    @staticmethod
    def convert_amount_by_rates(amount, from_rate, to_rate):
        telemetry_logger.log_response_time("convert_amount_by_rates", 0, 200, job="cancellation-policy")
        conv_amount = float(amount) / float(from_rate) * float(to_rate)
        return round(conv_amount, 2)
