# HELPER SCRIPTS
>>> Built for data professionals by data professionals.

Note: Despite the tagline, this package can be used by anyone.

## PACKAGE DESCRIPTION
### DatabaseHandler
This code defines a class called `DatabaseHandler` that provides methods for interacting with a PostgreSQL database.

1. It imports necessary modules: `ConfigParser` from `configparser`, `psycopg2`, `DictCursor` from `psycopg2.extras`, and `sys`.

2. The `DatabaseHandler` class is defined.

3. The `__init__` method initializes the `DatabaseHandler` object with the `config_file` and `config_file_section` parameters. It also initializes `self.conn` as `None`.

4. The `read_db_config` method reads the configuration file specified in `self.config_file` using `ConfigParser`. It retrieves the parameters for the PostgreSQL section specified in `self.config_file_section` and returns them as a dictionary.

5. The `connect` method establishes a connection to the database using the parameters obtained from `read_db_config`.

6. The `get_cursor` method creates a cursor for executing database queries. It checks if a connection exists or is closed and connects if necessary. It returns a cursor with `DictCursor` as the cursor factory, which returns query results as dictionaries.

7. The `close` method closes the database connection if it is open.

8. The `commit` method commits the currently open transaction.

9. The `rollback` method rolls back the currently open transaction.

10. The `execute` method creates a cursor, executes a query with optional arguments, and returns the cursor. If an exception occurs during query execution, it rolls back the transaction, closes the cursor, and raises the exception.

11. The `fetchone` method executes a SELECT query that is expected to return a single row. It calls the `execute` method internally, fetches the first row from the cursor, closes the cursor, and returns the row as a `psycopg2 DictRow`.

12. The `fetchall` method executes a SELECT query that is expected to return multiple rows. It calls the `execute` method internally, fetches all rows from the cursor, closes the cursor, and returns the rows as a list of `psycopg2 DictRow` objects.

13. The `copy_to` method executes a COPY command to copy data from a table to a file. It opens the file specified in `path` and uses `copy_to` method of the cursor to perform the copying. If an exception occurs, it closes the cursor and raises the exception.

14. The `sql_copy_to` method executes an SQL COPY command to copy data from a table to a file. It opens the file specified in `path` and uses `copy_expert` method of the cursor to perform the copying. If an exception occurs, it closes the cursor and raises the exception.

15. The `sql_copy_from` method executes an SQL COPY command to copy data from a file to a table. It opens the file specified in `path` and uses `copy_expert` method of the cursor to perform the copying. If an exception occurs, it closes the cursor and raises the exception.

16. The `copy_from` method executes a COPY command to copy data from a file to a table. It opens the file specified in `path` and uses `copy_from` method of the cursor to perform the copying. If an exception occurs, it closes the cursor and raises the exception.

Overall, this code provides a set of methods to interact with a PostgreSQL database, including connecting to the database, executing queries, fetching results, and performing data copying operations using the `psycopg2` library.

### SendMail
This code defines a class called `SendMail` that is responsible for sending emails using the `smtplib` library. Here's a breakdown of what the code is doing:

1. It imports necessary modules: `MIMEBase`, `smtplib`, `ssl`, `MIMEText`, `MIMEMultipart`, `encoders` from `email.mime` and `email`, `Helpers` from `database_handler`, `config` from `database_handler`, and `path` from `os`.

2. It reads the email server configuration parameters from a configuration file using the `CONFIG` class from `database_handler` and assigns them to the `params` variable.

3. The `SendMail` class is defined.

4. The `send_email` method is defined within the `SendMail` class. It takes several parameters: `email_message` (the body of the email), `subject` (the subject of the email), `email_recepients` (a list of recipient email addresses), and `file_attachments` (a list of file paths for attachments, optional).

5. Inside the method, it retrieves the necessary email server configuration parameters from `params`.

6. It creates an instance of `MIMEMultipart` to construct the email message.

7. It sets the email subject, sender, recipient(s), and Cc fields of the message.

8. It constructs the HTML content of the email using the `email_message` parameter.

9. It attaches the HTML content to the email message using `MIMEText` and the 'html' subtype.

10. If there are file attachments, it iterates over the `file_attachments` list, opens each file, creates a `MIMEBase` object, reads the file content, encodes it using Base64, and adds it as an attachment to the email message.

11. It creates a SSL context using `ssl.create_default_context()`.

12. It establishes a connection to the SMTP server specified in the email server configuration using `smtplib.SMTP()`.

13. It starts a TLS connection with the server using `server.starttls()`.

14. It authenticates with the server using the login email and password specified in the email server configuration.

15. It sends the email message using `server.sendmail()`.

16. If an exception occurs during the process, it is raised.

Overall, this code provides a class that encapsulates the functionality to send emails with attachments using an email server specified in a configuration file.

### GoogleDrive
This code defines a class `worker` that provides various functionalities to interact with Google Drive using the Google Drive API. Below is a description of the key components and functionalities of this code:

#### Class `worker`

##### Class Attributes

- **scope_readonly**: Scope for read-only access to Google Drive.
- **scope_write**: Scope for read and write access to Google Drive.
- **initial_download_path**: Default path for downloading files, set to the current working directory.

##### Constructor

- `__init__(self, api_name='drive', api_version='v3', key_file_location='')`: Initializes the class with API name, version, and the location of the key file.

##### Methods

1. **construct_service(self, scope: str = None)**:
   - Constructs and returns a Google Drive service instance with the specified scope.

2. **read_drive_files(self, scope=scope_readonly, file_id: str = None, filename: str = None, ignore_trashed=True)**:
   - Reads files from Google Drive based on file ID or filename, with an option to ignore trashed files.

3. **download_drive_file(self, file_id=None, download_path=initial_download_path, filename=None, scope=scope_write)**:
   - Downloads a file from Google Drive based on file ID or filename to a specified download path.

4. **upload_file_to_drive(self, scope=scope_write, filename=None, file_path=None, parent_folder_id=None, mimetype=None, coerce=True)**:
   - Uploads a file to Google Drive with the specified parameters.

5. **get_file_permissions(self, file_id=None)**:
   - Retrieves and returns the permissions of a specified file on Google Drive.

6. **delete_drive_files(self, file_ids: list = [], reset=False)**:
   - Deletes specified files from Google Drive. If `reset` is True, it deletes all files.

### Error Handling

- The code handles errors using `try-except` blocks and returns appropriate error messages and codes.

#### Usage

- The class `worker` can be instantiated and used to interact with Google Drive, performing operations like reading, downloading, uploading, checking permissions, and deleting files.

This code provides a structured way to interact with Google Drive using the Google Drive API, encapsulating the logic within a class for ease of use and reusability.