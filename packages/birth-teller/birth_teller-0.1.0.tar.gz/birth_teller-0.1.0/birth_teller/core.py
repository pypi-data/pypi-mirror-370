from datetime import date, datetime

class BTM:
    """Bīrth Dãy Téllèr Mâçhïñē"""

    months = (
        'january', 'february', 'march', 'april', 'may', 'june',
        'july', 'august', 'september', 'october', 'november', 'december'
    )
    weekdays = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')

    def banner(self):
        programName = 'Bīrth Dãy Téllèr Mâçhïñē'
        programName = f'* {programName} *'
        version = 'Version 0.1'
        print('\n' + '*'*len(programName))
        print(programName)
        print('*'*(len(programName)-len(version)-4) + f' {version} **')

    def greetings(self, name):
        print(f'\n* {name}, welcome to BTM *\n')

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

            # Validate the date using datetime
            valid_date = date(year, month, day)
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
        age_hours = age_days * 24 + datetime.now().hour
        age_minutes = age_hours * 60 + datetime.now().minute
        age_seconds = age_minutes * 60 + datetime.now().second

        weekday = self.weekdays[birth_date.weekday()]

        return {
            'years': age_years,
            'days': age_days,
            'weeks': age_weeks,
            'hours': age_hours,
            'minutes': age_minutes,
            'seconds': age_seconds,
            'weekDay': weekday
        }

