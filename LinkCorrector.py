import random
import string

def build_short_link(long_link):
    while True:
        try:
            short_link = "".join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in
                                 range(random.randrange(5, 8)))
            return short_link
        except:
            pass

#def check_url(long_link):
#    try:
#        request


if __name__ == '__main__':
    long_link = 'https://start.avito.ru/?_ga=2.18143345.917930497.1599991360-1903642690.1595682715'
    short_link = build_short_link(long_link)
    print(short_link)

    