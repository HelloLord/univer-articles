from datetime import timedelta, date

password = 'testpass123'
today = date.today()
register_users = [
            {
                'username': 'validuser1',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'user1@example.com',
                'password': password,
                'phone': '+1234567890',
                'birth_date': str(today - timedelta(days=365 * 15))
            },
            {
                'username': 'usr',
                'first_name': 'Test',
                'last_name': 'User',
                'email': 'user2@example.com',
                'password': password,
                'phone': '+1234567891',
                'birth_date': str(today - timedelta(days=365 * 20))
            },
            {
                'username': '1invalid',
                'first_name': 'Test',
                'last_name': 'User',
                'email': 'user3@example.com',
                'password': password,
                'phone': '+1234567892',
                'birth_date': str(today - timedelta(days=365 * 20))
            },
            {
                'username': 'validuser4',
                'first_name': 'Jo',
                'last_name': 'Doe',
                'email': 'user4@example.com',
                'password': password,
                'phone': '+1234567893',
                'birth_date': str(today - timedelta(days=365 * 20))
            },
            {
                'username': 'validuser5',
                'first_name': 'Jane',
                'last_name': 'Doe1',
                'email': 'user5@example.com',
                'password': password,
                'phone': '+1234567894',
                'birth_date': str(today - timedelta(days=365 * 20))
            },
            {
                'username': 'validuser6',
                'first_name': 'Alice',
                'last_name': 'Smith',
                'email': '',
                'password': password,
                'phone': '+1234567895',
                'birth_date': str(today - timedelta(days=365 * 20))
            },
            {
                'username': 'validuser7',
                'first_name': 'Bob',
                'last_name': 'Johnson',
                'email': 'user1@example.com',  # дубликат
                'password': password,
                'phone': '+1234567896',
                'birth_date': str(today - timedelta(days=365 * 20))
            },
            {
                'username': 'validuser8',
                'first_name': 'Emma',
                'last_name': 'Davis',
                'email': 'user8@example.com',
                'password': password,
                'phone': '1234567897',
                'birth_date': str(today - timedelta(days=365 * 20))
            },
            {
                'username': 'validuser9',
                'first_name': 'Michael',
                'last_name': 'Brown',
                'email': 'user9@example.com',
                'password': password,
                'phone': '+12345',
                'birth_date': str(today - timedelta(days=365 * 20))
            },
            {
                'username': 'validuser10',
                'first_name': 'Sophia',
                'last_name': 'Wilson',
                'email': 'user10@example.com',
                'password': password,
                'phone': '+1234567898',
                'birth_date': str(today - timedelta(days=365 * 9))
            },
            {
                'username': 'validuser11',
                'first_name': 'William',
                'last_name': 'Taylor',
                'email': 'user11@example.com',
                'password': password,
                'phone': '+1234567899',
                'birth_date': str(today + timedelta(days=365))
            },
            {
                'username': 'gooduser123',
                'first_name': 'Valid',
                'last_name': 'User',
                'email': 'valid1@example.com',
                'password': password,
                'phone': '+12345678901',
                'birth_date': str(today - timedelta(days=365*20))
            },
            {
                'username': '1baduser',
                'first_name': 'Invalid',
                'last_name': 'User',
                'email': 'invalid1@example.com',
                'password': password,
                'phone': '+12345678902',
                'birth_date': str(today - timedelta(days=365*20))
            },
            {
                'username': 'usr',
                'first_name': 'Short',
                'last_name': 'Username',
                'email': 'invalid2@example.com',
                'password': password,
                'phone': '+12345678903',
                'birth_date': str(today - timedelta(days=365*20))
            },
            {
                'username': 'fnamevalid',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'valid2@example.com',
                'password': password,
                'phone': '+12345678904',
                'birth_date': str(today - timedelta(days=365*20))
            },
            {
                'username': 'fnameshort',
                'first_name': 'Jo',
                'last_name': 'Doe',
                'email': 'invalid3@example.com',
                'password': password,
                'phone': '+12345678905',
                'birth_date': str(today - timedelta(days=365*20))
            },
            {
                'username': 'fnamenumber',
                'first_name': 'John1',
                'last_name': 'Doe',
                'email': 'invalid4@example.com',
                'password': password,
                'phone': '+12345678906',
                'birth_date': str(today - timedelta(days=365*20))
            },
            {
                'username': 'lnamevalid',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'email': 'valid3@example.com',
                'password': password,
                'phone': '+12345678907',
                'birth_date': str(today - timedelta(days=365*20))
            },
            {
                'username': 'lnamelong',
                'first_name': 'Jane',
                'last_name': 'Smithsonian',
                'email': 'invalid5@example.com',
                'password': password,
                'phone': '+12345678908',
                'birth_date': str(today - timedelta(days=365*20))
            },
            {
                'username': 'lnamespecial',
                'first_name': 'Jane',
                'last_name': 'Sm!th',
                'email': 'invalid6@example.com',
                'password': password,
                'phone': '+12345678909',
                'birth_date': str(today - timedelta(days=365*20))
            },
            {
                'username': 'emailvalid',
                'first_name': 'Email',
                'last_name': 'Valid',
                'email': 'valid4@example.com',
                'password': password,
                'phone': '+12345678910',
                'birth_date': str(today - timedelta(days=365*20))
            },
            {
                'username': 'emailinvalid',
                'first_name': 'Email',
                'last_name': 'Invalid',
                'email': 'bademail',
                'password': password,
                'phone': '+12345678911',
                'birth_date': str(today - timedelta(days=365*20))
            },
            {
                'username': 'emailempty',
                'first_name': 'Email',
                'last_name': 'Empty',
                'email': '',
                'password': password,
                'phone': '+12345678912',
                'birth_date': str(today - timedelta(days=365*20))
            },
            {
                'username': 'phonevalid1',
                'first_name': 'Phone',
                'last_name': 'Valid',
                'email': 'valid5@example.com',
                'password': password,
                'phone': '+12345678913',
                'birth_date': str(today - timedelta(days=365*20))
            },
            {
                'username': 'phonevalid2',
                'first_name': 'Phone',
                'last_name': 'Valid',
                'email': 'valid6@example.com',
                'password': password,
                'phone': '12345678914',
                'birth_date': str(today - timedelta(days=365*20))
            },
            {
                'username': 'phoneshort',
                'first_name': 'Phone',
                'last_name': 'Short',
                'email': 'invalid7@example.com',
                'password': password,
                'phone': '+123',
                'birth_date': str(today - timedelta(days=365*20))
            },
            {
                'username': 'phoneletters',
                'first_name': 'Phone',
                'last_name': 'Letters',
                'email': 'invalid8@example.com',
                'password': password,
                'phone': '+123abc456',
                'birth_date': str(today - timedelta(days=365*20))
            },

            {
                'username': 'bdatevalid',
                'first_name': 'Birth',
                'last_name': 'Valid',
                'email': 'valid7@example.com',
                'password': password,
                'phone': '+12345678915',
                'birth_date': str(today - timedelta(days=365*20))
            },
            {
                'username': 'bdateyoung',
                'first_name': 'Birth',
                'last_name': 'Young',
                'email': 'invalid9@example.com',
                'password': password,
                'phone': '+12345678916',
                'birth_date': str(today - timedelta(days=365*9))
            },
            {
                'username': 'bdatefuture',
                'first_name': 'Birth',
                'last_name': 'Future',
                'email': 'invalid10@example.com',
                'password': password,
                'phone': '+12345678917',
                'birth_date': str(today + timedelta(days=365))
            }

]