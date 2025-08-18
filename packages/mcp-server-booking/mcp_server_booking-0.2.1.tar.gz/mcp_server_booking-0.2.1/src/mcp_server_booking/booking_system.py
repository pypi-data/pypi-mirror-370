import requests
import logging
import json
from datetime import datetime, timedelta
import pytz
from urllib3.contrib import pyopenssl
from lxml import etree

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class BookEvent:
    def __init__(self, placeID, startTime, endTime, booker, reason):
        self.placeID = placeID
        self.startTime: datetime = startTime
        self.endTime: datetime = endTime
        self.booker = booker
        self.reason = reason

    def __str__(self):
        return f"Booker: {self.booker}, Start Time: {self.startTime}, End Time: {self.endTime}, Reason: {self.reason}, PlaceID: {self.placeID}"


class BookingSystem:
    field_dict = {
        "badminton": "1097",
        "basketball": "1090",
    }

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.logged_in = False

        pyopenssl.inject_into_urllib3()
        self.session = requests.Session()

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        logger.info(f"BookingSystem instance created for user: {username}")
        self.login()

    def login(self) -> bool:
        if self.logged_in:
            logger.info("User already logged in.")
            return True

        logger.info("Attempting to log in...")
        params = {
            "response_type": "code",
            "client_id": "caf5aded-3f28-4b64-b836-4451312e1ea3",
            "redirect_uri": "https://booking.cuhk.edu.cn/sso/code",
            "client-request-id": "f8739f9e-124f-4096-8b34-0140020000bb"
        }
        data = {
            "UserName": "cuhksz\\" + self.username,
            "Password": self.password,
            "Kmsi": "true",
            "AuthMethod": "FormsAuthentication"
        }
        url = "https://sts.cuhk.edu.cn/adfs/oauth2/authorize"
        r = self.session.post(url, headers=self.headers, params=params, data=data, allow_redirects=True)
        if not ("booking.cuhk.edu.cn" in r.url):
            logger.error("Login failed: Username or password incorrect!")
            raise ValidationError("Username or password incorrect!")
        else:
            self.logged_in = True
            logger.info("Login successful.")
            return True

    def get_field_info(self, field: str, start_time, end_time) -> dict | None:
        """
        Retrieves information for a specific field.
        """
        logger.info(f"Getting field info for '{field}' from {start_time} to {end_time}")
        try:
            if field not in self.field_dict:
                logger.warning(f"Field '{field}' not found in field_dict.")
                return None
            field_id = self.field_dict.get(field)
            logger.debug(f"Found field_id: {field_id} for field: {field}")

            places = self._get_field_places(field_id)
            book_info = self._get_field_booking_details(field_id, start_time, end_time)

            logger.info(f"Successfully retrieved info for field '{field}'.")
            return {
                "field_id": field_id,
                "field_name": field,
                "book_info": book_info,
                "places": places,
            }
        except Exception as e:
            logger.error(f"Error getting field info for '{field}': {e}")
            raise e

    def _get_field_places(self, field_id) -> dict[str, str]:
        logger.debug(f"Getting places for field_id: {field_id}")
        url = "https://booking.cuhk.edu.cn/a/field/client/main"
        data = {
            "id": field_id,
            "bookType": "0",
            "personTag": "Student",
        }
        r = self.session.post(url, data=data, headers=self.headers)
        places = self._parse_field_places(r.text)
        logger.debug(f"Found {len(places)} places for field_id: {field_id}")
        return places

    @staticmethod
    def _parse_field_places(data: str) -> dict:
        places = {}
        html = etree.HTML(data)
        for element in html.xpath("//*[@id='fieldSelect']/option"):
            name = element.xpath("text()")[0]
            place_id = element.xpath("@value")[0]
            if place_id == "":
                continue
            places[place_id] = name
        return places

    def _get_field_booking_details(self, field_id, start_time, end_time) -> list[BookEvent]:
        logger.debug(f"Getting booking details for field_id: {field_id} from {start_time} to {end_time}")
        url = "https://booking.cuhk.edu.cn/a/field/book/bizFieldBookField/eventsV1"
        params = {
            "ftId": field_id,
            "startTime": start_time,
            "endTime": end_time,
            "reBookMainId": "",
            "jsonStr": "[]",
            "fitUseStr": ""
        }
        r = self.session.get(url, params=params, headers=self.headers)
        info_list = self._parse_field_data(r.text)
        logger.debug(f"Found {len(info_list)} booking events for field_id: {field_id}")
        return info_list

    @staticmethod
    def _parse_field_data(data: str) -> list[BookEvent]:
        logger.info(f"Parsing field data: {data}")
        res = json.loads(data)
        event_list = res.get("event", [])
        lock_event_list = res.get("lockEvent", [])

        info_list = []

        for event in event_list:
            start_time = datetime.strptime(event.get("startTime"), "%Y-%m-%d %H:%M:%S")
            end_time = datetime.strptime(event.get("endTime"), "%Y-%m-%d %H:%M:%S")
            booker = event.get("userName")
            reason = event.get("theme")
            placeID = event.get("fId")
            if not placeID:
                continue
            info_list.append(BookEvent(placeID, start_time, end_time, booker, reason))

        for lock_event in lock_event_list:
            start_time = datetime.strptime(lock_event.get("startTime"), "%Y-%m-%d %H:%M")
            end_time = datetime.strptime(lock_event.get("endTime"), "%Y-%m-%d %H:%M")
            booker = "Locked"
            reason = lock_event.get("reasons")
            placeID = lock_event.get("fId")
            if not placeID:
                continue
            info_list.append(BookEvent(placeID, start_time, end_time, booker, reason))

        return info_list

    def get_all_available_slots(self, field_info: dict, start_time: str, end_time: str) -> dict[str, list[tuple[str, str]]]:
        """
        Calculates all available time slots for each place within a given time range.
        """
        logger.info(f"Checking for all available slots for '{field_info['field_name']}' from {start_time} to {end_time}")
        try:
            query_start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
            query_end_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M")

            book_info = field_info['book_info']
            places = field_info['places']

            book_info_by_place = {place_id: [] for place_id in places}
            for book in book_info:
                if book.placeID in book_info_by_place:
                    book_info_by_place[book.placeID].append(book)

            all_available_slots = {}
            for place_id in places:
                bookings_for_place = sorted(book_info_by_place[place_id], key=lambda x: x.startTime)
                
                available_slots_dt = self._get_available_slots_for_place(query_start_dt, query_end_dt, bookings_for_place)
                
                # Format datetime objects back to strings for the final output
                all_available_slots[place_id] = [
                    (s.strftime("%Y-%m-%d %H:%M"), e.strftime("%Y-%m-%d %H:%M"))
                    for s, e in available_slots_dt
                ]

            logger.info(f"Found available slots for {len(all_available_slots)} places.")
            return all_available_slots
        except Exception as e:
            logger.error(f"Error checking available slots: {e}")
            raise e

    def _get_available_slots_for_place(self, query_start_time: datetime, query_end_time: datetime, book_info: list[BookEvent]) -> list[tuple[datetime, datetime]]:
        """
        Finds available time slots, respecting daily 08:00-22:00 booking window.
        """
        all_available_slots = []
        
        # Iterate through each day in the query range
        current_date = query_start_time.date()
        end_date = query_end_time.date()
        
        while current_date <= end_date:
            # Define the booking window for the current day
            day_start_booking_time = datetime.combine(current_date, datetime.min.time()).replace(hour=8)
            day_end_booking_time = datetime.combine(current_date, datetime.min.time()).replace(hour=22)
            
            # Determine the actual time window to check for this day, clamped by the query range
            effective_start_of_day = max(query_start_time, day_start_booking_time)
            effective_end_of_day = min(query_end_time, day_end_booking_time)
            
            # If the effective window is invalid, skip to the next day
            if effective_start_of_day >= effective_end_of_day:
                current_date += timedelta(days=1)
                continue

            # Filter bookings relevant to this day's effective window
            day_bookings = sorted([
                b for b in book_info 
                if b.endTime > effective_start_of_day and b.startTime < effective_end_of_day
            ], key=lambda x: x.startTime)

            # Use the timeline cursor algorithm for the current day's window
            current_time = effective_start_of_day
            
            for book in day_bookings:
                # If there's a gap before this booking starts
                if current_time < book.startTime:
                    slot_end_time = min(book.startTime, effective_end_of_day)
                    if current_time < slot_end_time:
                        all_available_slots.append((current_time, slot_end_time))
                
                # Move the timeline cursor to the end of the current booking
                current_time = max(current_time, book.endTime)

                # If cursor is past the day's window, stop for this day.
                if current_time >= effective_end_of_day:
                    break

            # After checking all bookings, if there's still time left in the day's window
            if current_time < effective_end_of_day:
                all_available_slots.append((current_time, effective_end_of_day))

            # Move to the next day
            current_date += timedelta(days=1)
            
        return all_available_slots
    
    def get_available_places(self, field_info: dict, start_time: str, end_time: str) -> list[str]:
        """
        Checks for available places for a given time range.
        """
        logger.info(f"Checking for available places for '{field_info['field_name']}' from {start_time} to {end_time}")
        try:
            start_time_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
            end_time_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M")

            book_info = field_info['book_info']
            places = field_info['places']

            book_info_by_place = {place_id: [] for place_id in places}
            for book in book_info:
                if book.placeID in book_info_by_place:
                    book_info_by_place[book.placeID].append(book)

            available_places = []
            for place_id in places:
                if self._is_place_available(start_time_dt, end_time_dt, book_info_by_place[place_id]):
                    available_places.append(place_id)
            logger.info(f"Found {len(available_places)} available places.")
            return available_places
        except Exception as e:
            logger.error(f"Error checking available places: {e}")
            raise e

    def _is_place_available(self, start_time: datetime, end_time: datetime, book_info: list[BookEvent]):
        for book in book_info:
            if (book.startTime < start_time < book.endTime or book.startTime < end_time < book.endTime
                    or start_time < book.startTime < end_time or start_time < book.endTime < end_time):
                return False
        return True

    def book(self, field_id: str, place_id: str, start_time: str, end_time: str, telephone: str, reason: str, details: str) -> bool:
        """
        Books a field.
        """
        logger.info(f"Attempting to book place_id: {place_id} from {start_time} to {end_time}")
        try:
            info = self._get_book_form_info(start_time, end_time, place_id)
            logger.info(f"Info: {info}")
            data = {
                "id": info["id"],
                "user.id": info["userId"],
                "serialNo": "",
                "userOrgId": info["userOrgId"],
                "status": "",
                "approvalFlag": "0",
                "bizFieldBookField.id": info["bizFieldBookField.id"],
                "bizFieldBookField.BId": info["bizFieldBookField.BId"],
                "bizFieldBookField.FId": info["bizFieldBookField.FId"],
                "bizFieldBookField.theme": reason,
                "submitTime": "",
                "isNewRecord": "true",
                "extend1": field_id,
                "extend2": "",
                "extend3": "",
                "extend4": "",
                "extend5": "",
                "userJob": "",
                "userGrp": "STUDENTS",
                "userMobile": "",
                "bizFieldBookField.extend3": "",
                "bizFieldBookField.extend4": "",
                "bizFieldBookField.extend5": "",
                "userTag": "Student",
                "bookType": "0",
                "fitBook": "false",
                "user.name": info["userName"],
                "userOrgName": info["userOrgName"],
                "userEmail": info["userEmail"],
                "userPhone": telephone,
                "theme": reason,
                "bizFieldBookField.startTime": start_time,
                "bizFieldBookField.endTime": end_time,
                "bizFieldBookField.joinNums": "2",
                "bizFieldBookField.needRep": "0",
                "bizFieldBookField.extend1": "0",
                "bizFieldBookField.useDesc": details,
            }
            params = {
                "ruleId": "1249"
            }
            print(f"Data: {data}")
            url = "https://booking.cuhk.edu.cn/a/field/book/bizFieldBookMain/saveData?reBookMainId="
            r = self.session.post(url, data=data, headers=self.headers, params=params)
            if r.status_code != 200 or not json.loads(r.text).get("success"):
                logger.error(f"Booking failed for place_id: {place_id}. Response: {r.text}")
                raise Exception(f"Booking failed: {r.text}")
            logger.info(f"Successfully booked place_id: {place_id}")
            return True
        except Exception as e:
            logger.error(f"Error during booking: {e}")
            raise e

    def _get_book_form_info(self, start_time, end_time, place_id):
        logger.debug(f"Getting book form info for place_id: {place_id}")
        param = {
            "fId": place_id,
            "bizFieldBookField.startTime": start_time,
            "bizFieldBookField.endTime": end_time,
            "repFlag": 0,
            "bookType": 0,
            "userTag": "Student",
            "approvalFlag": 0,
            "extend2": "",
            "bookedNum": 0,
            "fitBook": "false",
            "isDeptAdmin": "false",
            "adMost": 1
        }
        url = "https://booking.cuhk.edu.cn/a/field/client/bookForm"
        r = self.session.get(url, params=param, headers=self.headers)
        info = self._parse_book_form_info(r.text)
        logger.debug("Successfully parsed book form info.")
        return info

    def _parse_book_form_info(self, data: str) -> dict:
        html = etree.HTML(data)
        
        # //*[@id="id"]
        id = html.xpath("//*[@id='id']/@value")[0]
        # //*[@id="userId"]
        userId = html.xpath("//*[@id='userId']/@value")[0]
        # //*[@id="userOrgId"]
        userOrgId = html.xpath("//*[@id='userOrgId']/@value")[0]
        # //*[@id="bizFieldBookField.id"]
        bizFieldBookField_id = html.xpath("//*[@id='bizFieldBookField.id']/@value")[0]
        # //*[@id="bizFieldBookField.BId"]
        bizFieldBookField_BId = html.xpath("//*[@id='bizFieldBookField.BId']/@value")[0]
        # //*[@id="bizFieldBookField.FId"]
        bizFieldBookField_FId = html.xpath("//*[@id='bizFieldBookField.FId']/@value")[0]
        # //*[@id="userName"]
        userName = html.xpath("//*[@id='userName']/@value")[0]
        # //*[@id="userOrgName"]
        userOrgName = html.xpath("//*[@id='userOrgName']/@value")[0]
        # //*[@id="userEmail"]
        userEmail = html.xpath("//*[@id='userEmail']/@value")[0]
        # //*[@id="bizFieldBookMainForm"]/div/div/div/div[2]/div[6]/div/div/div/input
        field_type = html.xpath("//*[@id='bizFieldBookMainForm']/div/div/div/div[2]/div[6]/div/div/div/input/@value")[0]
        # //*[@id="bizFieldBookMainForm"]/div/div/div/div[2]/div[7]/div/div/div/input
        field_name = html.xpath("//*[@id='bizFieldBookMainForm']/div/div/div/div[2]/div[7]/div/div/div/input/@value")[0]

        return {
            "id": id,
            "userId": userId,
            "userOrgId": userOrgId,
            "bizFieldBookField.id": bizFieldBookField_id,
            "bizFieldBookField.BId": bizFieldBookField_BId,
            "bizFieldBookField.FId": bizFieldBookField_FId,
            "userName": userName,
            "userOrgName": userOrgName,
            "userEmail": userEmail,
            "field_type": field_type,
            "field_name": field_name
        }