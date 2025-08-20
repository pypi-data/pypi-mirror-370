from typing import Union
from datetime import datetime, timedelta
import pendulum
import pytz
from .date import LunarDate as Lunar
import dill
import os
from sparrow import load, save, yaml_load, yaml_dump, relp, json_dump


class Mycrony:
    count = 0

    def __init__(self, ):
        self._crony = {}
        self.name = None
        self.load_from_yaml()

    def set_name(self, name):
        self.name = name

    def set_birthday(self, date, lunarORsolar="lunar"):
        """
        --data: a  [year, month, day] list
        --lunarORsolar: "lunar" or "solar"
        """
        self._crony.setdefault(self.name, {})
        self._crony[self.name].setdefault("birthday", {})

        if lunarORsolar == "lunar":
            lunar_date = Lunar(*date)

            self._crony[self.name]["birthday"]["lunar"] = lunar_date
            solar_date = lunar_date.to_datetime()
            self._crony[self.name]["birthday"]["_solar"] = solar_date

        elif lunarORsolar == "solar":
            solar_date = datetime(*date)
            self._crony[self.name]["birthday"]["solar"] = solar_date
            self._crony[self.name]["birthday"][
                "_lunar"] = Lunar.from_datetime(solar_date)
        else:
            raise ValueError("lunarORsolar: lunar or solar")

    def get_current_birthday(self, name, lunarORsolar="lunar", tz="Asia/Shanghai"):
        """
        tz : ""Asia/Shanghai"", or otherwise
        Birth = {"lunar":self._crony[name]["birthday"]["lunar"],
                 "solar":self._crony[name]["birthday"]["solar"]}
        return Birth.get(lunarORsolar, None)
        """
        tz = pytz.timezone(tz)
        solar_now = datetime.now(tz)
        solar_now = solar_now.replace(tzinfo=None)

        lunar_now = Lunar.from_datetime(solar_now)
        if lunarORsolar == "lunar":
            lunar_birthday = self._crony[name]["birthday"]["lunar"]
            year = lunar_now.lunar_year
            return Lunar(year, lunar_birthday.lunar_month,
                         lunar_birthday.lunar_day)
        elif lunarORsolar == "solar":
            solar_birthday = self._crony[name]["birthday"]["solar"]
            year = solar_now.year
            return datetime(year, solar_birthday.month, solar_birthday.day)
        else:
            raise ValueError("lunarORsolar: lunar/solar")


    def get_all_msg(self):
        return self._crony

    def get_all_names(self):
        return list(self._crony.keys())

    def get_all_lunar_birthday(self):
        """
        return [name list, birthday list]
        """
        birthdays = []
        names = self.get_all_names()
        NAME = []
        for i in names:
            try:
                birthdays.append(self._crony[i]["birthday"]["lunar"])
                NAME.append(i)
            except:
                continue
        return [NAME, birthdays]

    @classmethod
    def get_all_solar_birthday(cls):
        """
        return [name list, birthday list]
        """
        birthdays = []
        NAME = []
        names = cls.get_all_names()
        for i in names:
            try:
                birthdays.append(cls._crony[i]["birthday"]["solar"])
                NAME.append(i)
            except:
                continue
        return [NAME, birthdays]

    def get_valid_birthday(self, name):
        """
        return: (name, birthday)
        """
        ludar_birthday = self._crony[name]["birthday"].get("lunar", None)
        if ludar_birthday:
            birthday_date = ludar_birthday
        else:
            solar_birthday = self._crony[name]["birthday"]["solar"]
            birthday_date = solar_birthday
        return name, birthday_date

    def get_all_valid_birthday(self):
        """
        return [(name, birthday), ...]
        """
        birthdays = []
        for name in self.get_all_names():
            try:
                birthdays.append(self.get_valid_birthday(name))
            except:
                continue

        return birthdays

    def get_all_current_birthdays(self):
        """
        return [(name, birthday), ...]
        """
        birthdays = []
        for name in self.get_all_names():
            try:
                date  = self.get_current_birthday(name)
                birthdays.append((name, date))
            except:
                continue

        return birthdays

    def find_name_from_birthday(self, date):
        """
        -- date can be Lunar type or Solar type

        """

        target_names = []
        if isinstance(date, Lunar):
            for i in self.get_all_names():
                try:
                    if self._crony[i]["birthday"]["lunar"] == date:
                        target_names.append(i)
                except:
                    continue
            return target_names

        elif isinstance(date, datetime):
            for i in self.get_all_names():
                try:
                    if self._crony[i]["birthday"]["solar"] == date:
                        target_names.append(i)
                except:
                    continue
            return target_names

        else:
            raise ValueError(
                "The type of '--date' should be LunarDate or datetime")

    def del_brithday(self, name, date):
        """
        :arg date can be lunar or solar
        """
        if isinstance(date, Lunar):
            del self._crony[name]["birthday"]["lunar"]
        elif isinstance(date, datetime):
            del self._crony[name]["birthday"]["solar"]
        else:
            print("'name' or 'date' invalid, nothing changes ")

    def save(self):
        with open(os.path.join(os.path.dirname(__file__), "data"), "wb") as fo:
            dill.dump(self._crony, fo)

    def load_from_yaml(self):
        if relp('data.yaml', return_str=False).exists():
            load_data = yaml_load('data.yaml', rel_path=True)
            for key, value in load_data.items():
                new_value = {}
                for k, v in value.items():
                    if k == 'birthday':
                        new_value['birthday'] = {}
                        for k0, v0 in v.items():
                            if 'lunar' in k0:
                                new_value['birthday'][k0] = Lunar(**v0)
                            else:
                                new_value['birthday'][k0] = v0
                    else:
                        new_value[k] = v
                self._crony[key] = new_value
        else:
            print("data.yaml not exists, nothing changes")

    def save_to_yaml(self):
        disp_crony = {}
        for key, value in self._crony.items():
            new_value = {'birthday': {}}
            for _, v0 in value.items():
                for k, v in v0.items():
                    if isinstance(v, Lunar):
                        new_value['birthday'][k] = v.to_metadict()
                    else:
                        new_value['birthday'][k] = v
            disp_crony[key] = new_value
        yaml_dump('data.yaml', disp_crony, rel_path=True)

    @staticmethod
    def parse_delta_days(delta_days):
        """
        return list[days, hours, minutes, seconds] of a daltatime type data.
        """
        days = delta_days.days
        total_seconds = delta_days.seconds
        hours, res_hour = divmod(total_seconds, 3600)
        minutes, seconds = divmod(res_hour * 3600, 60)
        return {
            "days": days,
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds
        }

    @property
    def crony(self):
        return self._crony


def parse_date(date):
    """
    Parse the date into year, month, and day
    :param date: Lunar date or Solar date
    :return: year, month, day
    """
    if isinstance(date, Lunar):
        year = date.lunar_year
        month = date.lunar_month
        day = date.lunar_day
    elif isinstance(date, datetime):
        year = date.year
        month = date.month
        day = date.day
    else:
        raise ValueError("'date' invalid!")
    return year, month, day


def parse_date2solar(date):
    """parse date to solar date (datetime)
    :return: year, month, day
    """
    if isinstance(date, Lunar):
        date = date.to_datetime()
    year = date.year
    month = date.month
    day = date.day
    return year, month, day


def delta_days(date1, date2):
    """
    return days of (date2 - date1)
    """
    if isinstance(date1, Lunar):
        date1 = date1.to_datetime()
    if isinstance(date2, Lunar):
        date2 = date2.to_datetime()
    # d_dates = date2 - date1
    d_dates = pendulum.from_timestamp(date2.timestamp()) - pendulum.from_timestamp(date1.timestamp())
    return d_dates


def away_from_today(specDate: Union[Lunar, datetime], tz="Asia/Shanghai"):
    """ return how much times is left before that special day
        :param specDate: `Lunar` or `datetime` type date.
    """
    _, specialMonth, specialDay = parse_date2solar(specDate)

    tz = pytz.timezone(tz)
    solar_now = datetime.now(tz)
    solarNow = solar_now.replace(tzinfo=None)
    now_year, now_month, now_day = parse_date(solarNow)

    specialDate_this_year = datetime(now_year, specialMonth, specialDay)
    delta_times = specialDate_this_year - solarNow

    if delta_times.days < -1:
        one_solor_year = (datetime(now_year + 1, specialMonth, specialDay) -
                          specialDate_this_year)
        specialDate_next_year = specialDate_this_year + one_solor_year
        delta_times = specialDate_next_year - solarNow

    return timedelta(
        days=delta_times.days,
        seconds=delta_times.seconds)  # In order not to show milliseconds


def all_in_period(all_date, period=7):
    """
    Args:
        all_date: [(name, date), ...]
    return:
        {name:[delta_days, date]} map dictionary for all_date
    """

    def is_in_period(date, period=7):
        """return (True, delta_time) or (False, None)"""
        delta_time = away_from_today(date)
        if period >= delta_time.days > -2:  # delta_time constant greater than zero

            return True, timedelta_to_dhms(delta_time)
        else:
            return False, {}

    name_days = {}
    for name, date in all_date:
        is_true, delta = is_in_period(date, period=period)
        if is_true:
            name_days[name] = {"delta": delta, "birthday": format_date(date, return_str=True)}
    return name_days


def format_date(date: Lunar | datetime, return_str = False):
    if isinstance(date, Lunar):
        meta_dict = date.to_metadict()
        format_result = {
            'type': 'lunar',
            'year': meta_dict['lunar_year'],
            'month': meta_dict['lunar_month'],
            'day': meta_dict['lunar_day'],
            'leap': meta_dict['leap_month']
        }
    elif isinstance(date, datetime):
        format_result = {
            'type': 'solar',
            'year': date.year,
            'month': date.month,
            'day': date.day,
        }
    else:
        raise TypeError('date should be Lunar or datetime type')
    if return_str:
        if format_result['type'] == 'lunar':
            format_date_str = (f"农历{format_result['year']}年"
                               f"{format_result['month']}月"
                               f"{format_result['day']}日")
        else:
            format_date_str = (f"阳历{format_result['year']}年"
                               f"{format_result['month']}月"
                               f"{format_result['day']}日")
        return format_date_str

    return format_result


def timedelta_to_ymdhms(delta):
    # 确定timedelta是否为负值，并取其绝对值进行计算
    is_negative = delta.days < 0 or (delta.days == 0 and delta.seconds < 0)

    if is_negative:
        delta = -delta

    # 假设每年以365.25天来计算（考虑到闰年）
    # 假设每个月以30天来计算
    days_in_year = 365.25
    days_in_month = 30

    # 总天数和总秒数
    total_days = delta.days
    total_seconds = delta.seconds

    # 计算年、月、日
    years = int(total_days // days_in_year)
    remaining_days = total_days % days_in_year

    months = int(remaining_days // days_in_month)
    remaining_days %= days_in_month

    days = remaining_days

    # 计算小时、分钟、秒
    hours = total_seconds // 3600
    remaining_seconds = total_seconds % 3600

    minutes = remaining_seconds // 60
    seconds = remaining_seconds % 60

    # 应用正负符号
    if is_negative:
        years, months, days, hours, minutes, seconds = [-x for x in [years, months, days, hours, minutes, seconds]]

    return {
        'years': years,
        'months': months,
        'days': days,
        'hours': hours,
        'minutes': minutes,
        'seconds': seconds,
    }


def timedelta_to_dhms(delta):
    # 确定 timedelta 是否为负值，并取其绝对值进行计算
    is_negative = delta.days < 0 or (delta.days == 0 and delta.seconds < 0)

    if is_negative:
        delta = -delta

    # 总天数和总秒数
    total_days = delta.days
    total_seconds = delta.seconds

    # 计算日
    days = total_days

    # 计算小时、分钟、秒
    hours = total_seconds // 3600
    remaining_seconds = total_seconds % 3600

    minutes = remaining_seconds // 60
    seconds = remaining_seconds % 60

    # 应用正负符号
    if is_negative:
        days, hours, minutes, seconds = [-x for x in [days, hours, minutes, seconds]]

    return {
        'days': days,
        'hours': hours,
        'minutes': minutes,
        'seconds': seconds,
    }

if __name__ == "__main__":
    import threading

    mycrocny = Mycrony()

    # mycrocny.save_to_yaml()

    # birthday_date = mycrocny.get_current_birthday('baba', 'lunar')
    # birthday_date = mycrocny.get_current_birthday('yaochen', 'lunar')
    birthday_date = mycrocny.get_current_birthday('王振', 'lunar')
    print(away_from_today(birthday_date))

    all_birthdays = mycrocny.get_all_current_birthdays()
    print(all_birthdays)
    print(all_in_period(all_birthdays, period=30))

    # threading.Thread(target=reminder,kwargs={"period":30, "send_email":False}).start()
    # threading.Thread(target=reminder,kwargs={"period":15, "send_email":False}).start()
    # threading.Thread(target=reminder,kwargs={"period":7, "send_email":False}).start()
    # threading.Thread(target=reminder,kwargs={"period":2, "send_email":False}).start()
    #
