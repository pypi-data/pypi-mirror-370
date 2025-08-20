from birth_teller import BTM


def test_weekday():
    btm = BTM()
    info = btm.information(1, "jan", 2000)
    assert info['weekDay'] == 'Saturday'


def test_age_years():
    btm = BTM()
    info = btm.information(1, "jan", 2000)
    assert info['years'] >= 23  # depending on current year
