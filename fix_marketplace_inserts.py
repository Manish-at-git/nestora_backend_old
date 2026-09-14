import re

with open('server.py', 'r') as f:
    content = f.read()

# Fix create_marketplace_item
content = content.replace('''        INSERT INTO marketplace_items (
            id, association_id, user_id, category_id, title, description, price, condition_state, 
            brand, item_age, location, contact_number, is_negotiable, status, listing_type
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', '''        INSERT INTO marketplace_items (
            association_id, user_id, category_id, title, description, price, condition_state, 
            brand, item_age, location, contact_number, is_negotiable, status, listing_type
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''')

content = content.replace('''    item_id = str(uuid.uuid4())
    await db_execute(\'\'\'
        INSERT INTO marketplace_items (
            association_id, user_id, category_id, title, description, price, condition_state, 
            brand, item_age, location, contact_number, is_negotiable, status, listing_type
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    \'\'\', (
        item_id, assoc_id, account["account_id"], payload.category_id, payload.title, payload.description,
        payload.price, payload.condition_state, payload.brand, payload.item_age, payload.location,
        payload.contact_number, payload.is_negotiable, payload.status, payload.listing_type
    ))''', '''    item_id = await db_execute(\'\'\'
        INSERT INTO marketplace_items (
            association_id, user_id, category_id, title, description, price, condition_state, 
            brand, item_age, location, contact_number, is_negotiable, status, listing_type
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    \'\'\', (
        assoc_id, account["account_id"], payload.category_id, payload.title, payload.description,
        payload.price, payload.condition_state, payload.brand, payload.item_age, payload.location,
        payload.contact_number, payload.is_negotiable, payload.status, payload.listing_type
    ))''')

# Fix images
content = content.replace('await db_execute("INSERT INTO marketplace_images (id, item_id, image_url) VALUES (%s, %s, %s)", (str(uuid.uuid4()), item_id, img_url))',
                          'await db_execute("INSERT INTO marketplace_images (item_id, image_url) VALUES (%s, %s)", (item_id, img_url))')

# Fix favorites
content = content.replace('await db_execute("INSERT INTO marketplace_favorites (id, user_id, item_id) VALUES (%s, %s, %s)", (str(uuid.uuid4()), account["account_id"], item_id))',
                          'await db_execute("INSERT INTO marketplace_favorites (user_id, item_id) VALUES (%s, %s)", (account["account_id"], item_id))')

# Fix reports
content = content.replace('await db_execute("INSERT INTO marketplace_reports (id, item_id, reporter_id, reason) VALUES (%s, %s, %s, %s)", (str(uuid.uuid4()), item_id, account["account_id"], payload.reason))',
                          'await db_execute("INSERT INTO marketplace_reports (item_id, reporter_id, reason) VALUES (%s, %s, %s)", (item_id, account["account_id"], payload.reason))')

# Fix chat
content = content.replace('await db_execute("INSERT INTO marketplace_chat (id, item_id, sender_id, receiver_id, message) VALUES (%s, %s, %s, %s, %s)", (str(uuid.uuid4()), item_id, account["account_id"], receiver_id, payload.message))',
                          'await db_execute("INSERT INTO marketplace_chat (item_id, sender_id, receiver_id, message) VALUES (%s, %s, %s, %s)", (item_id, account["account_id"], receiver_id, payload.message))')

# Fix views
content = content.replace('await db_execute("INSERT INTO marketplace_views (id, item_id, user_id) VALUES (%s, %s, %s)", (str(uuid.uuid4()), item_id, account["account_id"]))',
                          'await db_execute("INSERT INTO marketplace_views (item_id, user_id) VALUES (%s, %s)", (item_id, account["account_id"]))')

with open('server.py', 'w') as f:
    f.write(content)
