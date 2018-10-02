from database_setup import Base, Catagory, Item
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# database im using
engine = create_engine('sqlite:///catalogproject.db')
Base.metadata.bind = engine
DBSession = sessionmaker (bind = engine)

session = DBSession()

firstCatagory = Catagory(name = "Video Game System")
session.add(firstCatagory)
session.commit()

secondCatagory = Catagory(name = "Video Game")
session.add(secondCatagory)
session.commit()

thirdCatagory = Catagory(name = "Disneyworld Parks")
session.add(thirdCatagory)
session.commit()

fourthCatagory = Catagory(name = "Disney Movies")
session.add(fourthCatagory)
session.commit()

fifthCatagory = Catagory(name = "Sci-Fi Movies")
session.add(fifthCatagory)
session.commit()

firstItem = Item(name = "X-BOX ONE", description = "Microsoft Console", catagory_id = "1")
session.add(firstItem)
session.commit()

secondItem = Item(name = "Hollywood Studios", description = "Theme park with Star Wars", catagory_id = "3")
session.add(secondItem)
session.commit()

thirdItem = Item(name = "Aliens", description = "Colony over run", catagory_id = "5")
session.add(thirdItem)
session.commit()

fourthItem = Item(name = "Spider-Man", description = "PS4 Game", catagory_id = "2")
session.add(fourthItem)
session.commit()

fifthItem = Item(name = "Mulan", description = "Mushu and Mulan", catagory_id = "4")
session.add(fifthItem)
session.commit()
