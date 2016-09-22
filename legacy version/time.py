# -*- coding: utf-8 -*-

from datetime import datetime

Time_Page = '''
    <html>
        <head>
            <title>Time Page</title>
        </head>
        <body>
            <p>Generated {0}</p>
        </body>
    </html>
'''

print(Time_Page.format(datetime.now()))