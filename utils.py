from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean
from sqlalchemy.orm import sessionmaker
from dateutil.parser import parse

engine = create_engine('sqlite:////tmp/listings.db', echo=False)

Base = declarative_base()

class Listing(Base):
    """
    A table to store data on craigslist listings.
    """

    __tablename__ = 'listings'

    id = Column(Integer, primary_key=True)
    link = Column(String, unique=True)
    created = Column(DateTime)
    geotag = Column(String)
    lat = Column(Float)
    lon = Column(Float)
    name = Column(String)
    price = Column(Float)
    location = Column(String)
    cl_id = Column(Integer, unique=True)
    area = Column(String)
    bart_stop = Column(String)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

#define geolocating function
def in_area(coords, box):
    if box[0][0] < coords[1] < box[1][0] and box[1][1] < coords[0] < box[0][1]:
        return True
    return False

def check_for_record(result):
    if session.query(Listing).filter_by(cl_id=result["id"]).first() is None:
        return False
    return True

def store_in_db(result):
    price = 0
    try:
        price = float(result["price"].replace("$", ""))
    except Exception:
        pass
    # Create the listing object.
    listing = Listing(
        link=result["url"],
        created=parse(result["datetime"]),
        name=result["name"],
        price=price,
        location=result["where"],
        cl_id=result["id"]#,
        #area=result["area"],
    )

    # Save the listing so we don't grab it again.
    session.add(listing)
    session.commit()
