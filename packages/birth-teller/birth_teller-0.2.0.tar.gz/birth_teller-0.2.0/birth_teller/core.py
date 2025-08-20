from datetime import date, datetime


class BTM:

    months = (
        'january', 'february', 'march', 'april', 'may', 'june',
        'july', 'august', 'september', 'october', 'november', 'december'
    )
    weekdays = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')

    def banner(self):
        programName = 'Bīrth Dãy Téllèr Mâçhïñē'
        programName = f'* {programName} *'
        version = 'Version 0.2'
        print('\n' + '*'*len(programName))
        print(programName)
        print('*'*(len(programName)-len(version)-4) + f' {version} **')

    def greetings(self, name=None):
        if not name:
            name = "User"
        print(f'\n* {name}, welcome to BTM *\n')
    
    def zodiac_sign(self, day, month):
        
        zodiac_dates = [
        ("Capricorn", (12, 22), (1, 19)),
        ("Aquarius", (1, 20), (2, 18)),
        ("Pisces", (2, 19), (3, 20)),
        ("Aries", (3, 21), (4, 19)),
        ("Taurus", (4, 20), (5, 20)),
        ("Gemini", (5, 21), (6, 20)),
        ("Cancer", (6, 21), (7, 22)),
        ("Leo", (7, 23), (8, 22)),
        ("Virgo", (8, 23), (9, 22)),
        ("Libra", (9, 23), (10, 22)),
        ("Scorpio", (10, 23), (11, 21)),
        ("Sagittarius", (11, 22), (12, 21)),
        ]

        for sign, (start_month, start_day), (end_month, end_day) in zodiac_dates:
            if (month == start_month and day >= start_day) or (month == end_month and day <= end_day):
                return sign
        
        return "Invalid date"

    def validate_date(self, day, month, year):
        # Create mapping for full month names and 3-letter abbreviations
        month_mapping = {m: i+1 for i, m in enumerate(self.months)}
        month_mapping.update({m[:3]: i+1 for i, m in enumerate(self.months)})

        try:
            # Convert month input
            if isinstance(month, str):
                month_lower = month.lower()
                if month_lower in month_mapping:
                    month = month_mapping[month_lower]
                else:
                    month = int(month_lower)  # numeric string like "2"
            elif isinstance(month, int):
                if not (1 <= month <= 12):
                    raise ValueError
            else:
                raise ValueError

            day = int(day)
            year = int(year)

        except (ValueError, KeyError):
            raise ValueError(f"Invalid date: {day}-{month}-{year}")

        return day, month, year

    def information(self, day, month, year):
        self.birthDay, self.birthMonth, self.birthYear = self.validate_date(day, month, year)
        
        today = date.today()
        birth_date = date(self.birthYear, self.birthMonth, self.birthDay)
        age_days = (today - birth_date).days
        age_years = today.year - self.birthYear - ((today.month, today.day) < (self.birthMonth, self.birthDay))
        age_weeks = age_days // 7
        zodiacSign = self.zodiac_sign(self.birthDay, self.birthMonth)

        weekday = self.weekdays[birth_date.weekday()]

        return {
            'years': age_years,
            'days': age_days,
            'weeks': age_weeks,
            'weekDay': weekday,
            'zodiac sign': zodiacSign
        }
