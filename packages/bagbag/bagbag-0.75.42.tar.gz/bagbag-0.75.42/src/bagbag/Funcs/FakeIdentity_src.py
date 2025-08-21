import requests
from bs4 import BeautifulSoup

#print("load " + __file__.split('/')[-1])

class fakeIdentityIdent:
    def __init__(self, name, address, street, city, state, zip, motherMaidenName, ssn, coords, phone, countryCode, birthday, birthdayMonth, birthdayDay, birthdayYear, age, zodiac, email, username, password, website, useragent, card, expiration, cvv2, company, occupation, height, heightcm, weight, weightkg, blood, ups, westernunion, moneygram, color, vehicle, guid):
        self.Name:str = name
        self.Address:str = address
        self.Street:str = street
        self.City:str = city
        self.State:str = state
        self.Zip:str = zip
        self.MotherMaidenName:str = motherMaidenName
        self.SSN:str = ssn
        self.Coords:str = coords
        self.Phone:str = phone
        self.CountryCode:str = countryCode
        self.Birthday:str = birthday
        self.BirthdayMonth:str = birthdayMonth
        self.BirthdayYear:str = birthdayYear
        self.BirthdayDay:str = birthdayDay
        self.Age:str = age
        self.Zodiac:str = zodiac
        self.Email:str = email
        self.Username:str = username
        self.Password:str = password
        self.Website:str = website
        self.UserAgent:str = useragent
        self.Card:str = card
        self.Expiration:str = expiration
        self.CVV2:str = cvv2
        self.Company:str = company
        self.Occupation:str = occupation
        self.Height:str = height
        self.Heightcm:str = heightcm
        self.Weight:str = weight
        self.Weightkg:str = weightkg
        self.Blood:str = blood
        self.UPS:str = ups
        self.Westernunion:str = westernunion
        self.Moneygram:str = moneygram
        self.Color:str = color
        self.Vehicle:str = vehicle
        self.GUID:str = guid

    def __repr__(self):
        items = []

        for prop, value in self.__dict__.items():
            item = "%s=%s" % (prop, value)
            items.append(item)

        return "%s(%s)" % (self.__class__.__name__, ' '.join(items))

def FakeIdentity(nameset=["us"], country=["us"], gender="50", minage="19", maxage="85"):
    namesets = ['us', 'ar', 'au', 'br', 'celat', 'ch', 'zhtw', 'hr', 'cs', 'dk', 'nl', 'en', 'er', 'fi', 'fr', 'gr', 'gl', 'sp', 'hobbit', 'hu', 'is', 'ig', 'it', 'jpja', 'tlh', 'ninja', 'no', 'fa', 'pl', 'ru', 'rucyr', 'gd', 'sl', 'sw', 'th', 'vn']

    countries = ['au', 'as', 'bg', 'br', 'ca', 'cyen', 'cygk', 'cz', 'dk', 'ee', 'fi', 'fr', 'gr', 'gl', 'hu', 'is', 'it', 'nl', 'nz', 'no', 'pl', 'pt', 'sl', 'za', 'sp', 'sw', 'sz', 'tn', 'uk', 'us', 'uy']

    #check if args are valid
    if not isinstance(nameset, list):
        raise TypeError("Argument nameset must be list")
    if not isinstance(country, list):
        raise TypeError("Argument country must be list")
    if not isinstance(gender, str):
        raise TypeError("Argument gender must be str")
    if int(gender) > 100:
        raise ValueError("Gender must be less than or equal to 100")
    if int(gender) < 0:
        raise ValueError("Gender must be greater than or equal to 0")
    if not isinstance(minage, str):
        raise TypeError("Argument minage must be str")
    if int(minage) < 0:
        raise ValueError("minage must be greater than or equal to 0")
    if not isinstance(maxage, str):
        raise TypeError("Argument maxage must be str")
    if int(maxage) > 100:
        raise ValueError("maxage nust be less than or equal to 100")
    if int(minage) > int(maxage):
        raise ValueError("minage must be less than maxage")
    
    for i in range(len(nameset)):
        if not nameset[i] in namesets:
            raise ValueError("nameset \'" + nameset[i] + "\' not supported")
        elif not isinstance(nameset[i], str):
            raise TypeError("nameset values must be a str")
    for i in range(len(country)):
        if not country[i] in countries:
            raise ValueError("country \'" + country[i] + "\' not supported")
        elif not isinstance(country[i], str):
            raise TypeError("country values must be a str")
    
    #construct url
    url = "https://www.fakenamegenerator.com/advanced.php?t=country"
    for i in range(len(nameset)):
        url = url + "&n%5B%5D=" + nameset[i]
    for i in range(len(country)):
        url = url + "&c%5B%5D=" + country[i]
    url = url + "&gen=" + gender
    url = url + "&age-min=" + minage
    url = url + "&age-max=" + maxage
    
    #get data
    soup = BeautifulSoup(requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).text, "html.parser")

    name = soup.find("h3").text
    fullAddress = soup.find("div", class_="adr").contents
    address = (fullAddress[0] + ", " + fullAddress[2]).strip()
    street = fullAddress[0].strip()
    city = fullAddress[2].split(", ")[0]
    state = fullAddress[2].split(" ")[1]
    zip = fullAddress[2].split(" ")[2]
    motherMaidenName = soup.find("dd").text
    ssn = soup.find_all("dd")[1].text.split(" ")[0]
    coords = soup.find("a", id="geo").text
    phone = soup.find_all("dd")[3].text
    countryCode = soup.find_all("dd")[4].text
    birthday = soup.find_all("dd")[5].text
    birthdayYear = birthday.split(" ")[2]
    birthdayMonth = birthday.split(" ")[0]
    birthdayDay = birthday.split(" ")[1][:-1]
    age = soup.find_all("dd")[6].text.split(" ")[0]
    zodiac = soup.find_all("dd")[7].text
    email = soup.find_all("dd")[8].contents[0].strip()
    username = soup.find_all("dd")[9].text
    password = soup.find_all("dd")[10].text
    website = soup.find_all("dd")[11].text
    useragent = soup.find_all("dd")[12].text
    card = soup.find_all("dd")[13].text
    expiration = soup.find_all("dd")[14].text
    cvv2 = soup.find_all("dd")[15].text
    company = soup.find_all("dd")[16].text
    occupation = soup.find_all("dd")[17].text
    height = soup.find_all("dd")[18].text.split(" ")[0] + soup.find_all("dd")[18].text.split(" ")[1]
    heightcm = soup.find_all("dd")[18].text.split("(")[1][:-1].split(" ")[0]
    weight = soup.find_all("dd")[19].text
    weightkg = soup.find_all("dd")[19].text
    blood = soup.find_all("dd")[20].text
    ups = soup.find_all("dd")[21].text
    westernunion = soup.find_all("dd")[22].text
    moneygram = soup.find_all("dd")[23].text
    color = soup.find_all("dd")[24].text
    vehicle = soup.find_all("dd")[25].text
    guid = soup.find_all("dd")[26].text
    
    iden = fakeIdentityIdent(name, address, street, city, state, zip, motherMaidenName, ssn, coords, phone, countryCode, birthday, birthdayMonth, birthdayDay, birthdayYear, age, zodiac, email, username, password, website, useragent, card, expiration, cvv2, company, occupation, height, heightcm, weight, weightkg, blood, ups, westernunion, moneygram, color, vehicle, guid)
    return iden

if __name__ == "__main__":
    f = FakeIdentity()
    print(f)