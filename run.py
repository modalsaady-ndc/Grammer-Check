from Main import create_app
from Config.config import Config, DevConfig, SQLConfig, PostgreConfig
import sys


app = create_app(PostgreConfig)

if __name__ == '__main__':
    
    # Check the SQL Server connection
    # connection_status = PostgreConfig.test_connection()
    # if connection_status == "Failed to connect to PostgreSQL.":
    #     sys.exit("Failed to connect to PostgreSQL. Ending the project.")
    # else:
    #     print(connection_status)
    app.run(debug=True, port=9019)
    # serve(app, port=9009, threads=1)