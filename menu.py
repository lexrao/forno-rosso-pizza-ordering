"""The whole menu lives here. Edit a price or a name, push to GitHub, and Vercel redeploys with it.

Each row is (type, id, name, price in PHP, extras). Types: size, crust, sauce, cheese, topping, product (fixed-price
items such as drinks and sides) and pizza (the named pizzas). A named pizza is priced for Medium; `top` lists the
toppings it comes with. To mark something sold out without editing this file, set the SOLD_OUT environment variable.
"""

SEED = [  # type, id, name, price (PHP), meta
    ("size", "s", "Small 10″", 129, {"k": 0.8}),
    ("size", "m", "Medium 12″", 179, {"k": 0.9}),
    ("size", "l", "Large 14″", 279, {"k": 1}),
    ("crust", "thin", "Thin crust", 0, {"r": 142}),
    ("crust", "classic", "Classic crust", 0, {"r": 130}),
    ("crust", "stuffed", "Cheese-stuffed crust", 70, {"r": 118}),
    ("sauce", "tomato", "Tomato sauce", 0, {"c": "#c2321f"}),
    ("sauce", "white", "Garlic cream sauce", 30, {"c": "#f1e6c6"}),
    ("sauce", "pesto", "Pesto sauce", 30, {"c": "#6f9a3d"}),
    ("sauce", "none", "No sauce", 0, {"c": "#e8c372"}),
    ("cheese", "reg", "Mozzarella", 0, {}),
    ("cheese", "extra", "Extra cheese", 50, {}),
    ("cheese", "none", "No cheese", 0, {}),
    ("topping", "pep", "Pepperoni", 60, {"c": 12}),
    ("topping", "saus", "Sausage", 60, {"c": 9}),
    ("topping", "mush", "Mushroom", 45, {"c": 9}),
    ("topping", "olive", "Olives", 40, {"c": 14}),
    ("topping", "onion", "Red onion", 30, {"c": 12}),
    ("topping", "pepper", "Green pepper", 35, {"c": 11}),
    ("topping", "pine", "Pineapple", 40, {"c": 10}),
    ("topping", "ham", "Ham", 55, {"c": 8}),
    ("topping", "bacon", "Bacon", 60, {"c": 8}),
    ("topping", "beef", "Ground beef", 60, {"c": 12}),
    ("topping", "shrimp", "Shrimp", 75, {"c": 8}),
    ("topping", "tuna", "Tuna", 50, {"c": 10}),
    ("topping", "tomato", "Tomato", 25, {"c": 9}),
    ("topping", "cheddar", "Cheddar", 45, {"c": 10}),
    ("topping", "parm", "Parmesan", 45, {"c": 12}),
    ("topping", "cream", "Cream cheese", 50, {"c": 9}),
    ("topping", "garlic", "Roasted garlic", 25, {"c": 10}),
    ("topping", "basil", "Basil", 25, {"c": 9}),
    ("product", "fried-2", "Fried chicken (2 pcs)", 159, {"cat": "Chicken", "d": "Crispy and juicy, with gravy"}),
    ("product", "fried-4", "Fried chicken (4 pcs)", 299, {"cat": "Chicken", "d": "Good for sharing, with gravy"}),
    ("product", "wings-bq", "Buffalo wings (6 pcs)", 199, {"cat": "Chicken", "d": "Hot and tangy, with ranch dip"}),
    ("product", "wings-hg", "Honey garlic wings (6 pcs)", 199, {"cat": "Chicken", "d": "Sweet, sticky and garlicky"}),
    ("product", "tenders", "Chicken tenders (4 pcs)", 169, {"cat": "Chicken", "d": "Breaded strips, honey mustard dip"}),
    ("product", "fries-r", "French fries", 79, {"cat": "Sides", "d": "Regular, lightly salted"}),
    ("product", "fries-l", "French fries (large)", 119, {"cat": "Sides", "d": "Big enough to share"}),
    ("product", "fries-c", "Cheesy fries", 129, {"cat": "Sides", "d": "Topped with warm cheese sauce"}),
    ("product", "garlic-bread", "Garlic bread", 89, {"cat": "Sides", "d": "4 slices, buttery and herby"}),
    ("product", "mozz-sticks", "Mozzarella sticks (5 pcs)", 139, {"cat": "Sides", "d": "Crisp outside, stretchy inside"}),
    ("product", "caesar", "Caesar salad", 119, {"cat": "Sides", "d": "Romaine, parmesan, croutons"}),
    ("product", "spaghetti", "Baked spaghetti", 149, {"cat": "Pasta", "d": "Meat sauce, topped with cheese"}),
    ("product", "lasagna", "Beef lasagna", 189, {"cat": "Pasta", "d": "Layered and baked until bubbly"}),
    ("product", "mac", "Baked mac and cheese", 139, {"cat": "Pasta", "d": "Creamy with a golden top"}),
    ("product", "lava", "Choco lava cake", 99, {"cat": "Desserts", "d": "Warm with a molten centre"}),
    ("product", "brownie", "Warm brownie", 89, {"cat": "Desserts", "d": "Fudgy, served warm"}),
    ("product", "coke", "Coke (can)", 65, {"cat": "Drinks", "d": "330 ml"}),
    ("product", "sprite", "Sprite (can)", 65, {"cat": "Drinks", "d": "330 ml"}),
    ("product", "coke-15", "Coke (1.5 L)", 109, {"cat": "Drinks", "d": "For the table"}),
    ("product", "iced-tea", "Iced tea (glass)", 55, {"cat": "Drinks", "d": "Freshly brewed, lightly sweet"}),
    ("product", "lemonade", "Lemonade (glass)", 65, {"cat": "Drinks", "d": "Sharp and refreshing"}),
    ("product", "tea-pitcher", "Iced tea (pitcher)", 129, {"cat": "Drinks", "d": "Serves 3 to 4"}),
    ("product", "water", "Bottled water", 35, {"cat": "Drinks", "d": "500 ml"}),
]


def _p(id_, name, price, cat, d, top, sauce="tomato", cheese="reg"):
    """Named pizza: price is for Medium; `top` are the included toppings (whole pizza)."""
    return ("pizza", id_, name, price, {"cat": cat, "d": d, "top": {t: "all" for t in top.split()},
                                        "sauce": sauce, "cheese": cheese, "crust": "classic"})


CL, SP, CH = "Classic Pizzas", "Special Pizzas", "Cheese Specials"
SEED += [
    _p("hawaiian", "Hawaiian", 199, CL, "Ham and pineapple", "ham pine"),
    _p("pepperoni", "Pepperoni", 229, CL, "Loaded with pepperoni", "pep"),
    _p("cheese-lovers", "Cheese Lovers", 219, CL, "Double mozzarella, nothing else", "", cheese="extra"),
    _p("ham-cheese", "Ham & Cheese", 199, CL, "Ham with melty cheddar", "ham cheddar"),
    _p("bacon", "Bacon Pizza", 239, CL, "Crispy bacon", "bacon"),
    _p("all-meat", "All Meat", 269, CL, "Pepperoni, sausage, ham and bacon", "pep saus ham bacon"),
    _p("supreme", "Supreme", 279, SP, "Pepperoni, sausage, mushroom, onion, pepper, olives", "pep saus mush onion pepper olive"),
    _p("overload", "Overload Pizza", 299, SP, "Meats and veggies piled high, extra cheese", "pep saus ham bacon mush pepper olive", cheese="extra"),
    _p("meat-lovers", "Meat Lovers", 289, SP, "Pepperoni, sausage, bacon and ground beef", "pep saus bacon beef", cheese="extra"),
    _p("garden", "Garden Veggie", 229, SP, "Mushroom, onion, pepper, olives, tomato, basil", "mush onion pepper olive tomato basil"),
    _p("seafood", "Seafood Delight", 299, SP, "Shrimp, tuna, onion and tomato", "shrimp tuna onion tomato"),
    _p("deluxe", "Deluxe Special", 319, SP, "The works, with extra cheese", "pep saus ham mush pepper olive onion", cheese="extra"),
    _p("four-cheese", "Four Cheese", 279, CH, "Mozzarella, cheddar, parmesan and cream cheese", "cheddar parm cream", cheese="extra"),
    _p("mozz-overload", "Mozzarella Overload", 269, CH, "Mozzarella piled on, finished with basil", "basil", cheese="extra"),
    _p("creamy", "Creamy Cheese", 249, CH, "Garlic cream sauce and cream cheese", "cream", sauce="white"),
    _p("garlic-cheese", "Garlic Cheese", 229, CH, "Garlic cream sauce, roasted garlic, extra cheese", "garlic", sauce="white", cheese="extra"),
    _p("cheesy-bacon", "Cheesy Bacon", 269, CH, "Bacon and cheddar over extra mozzarella", "bacon cheddar", cheese="extra"),
]
