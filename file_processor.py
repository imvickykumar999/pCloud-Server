import os
import csv
import random
import string
import pandas as pd
from datetime import datetime, timedelta
import requests
import pyzipper

class FileProcessor:
    def __init__(self, database_name):
        self.database_name = database_name
        self.current_dir = os.getcwd()
        
        self.csv_folder_path = os.path.join(self.current_dir, "csv_folder")
        os.makedirs(self.csv_folder_path, exist_ok=True)

        self.csv_output_path = os.path.join(self.current_dir, "Output_CSV")
        os.makedirs(self.csv_output_path, exist_ok=True)

        self.all_database_path = os.path.join(self.current_dir, "AllDatabase")
        os.makedirs(self.all_database_path, exist_ok=True)

    @staticmethod
    def generate_random_password(length=7):
        characters = string.ascii_uppercase + string.digits
        return ''.join(random.choice(characters) for _ in range(length))

    def zip_files_with_random_password(self, folder_path):
        try:
            output_folder_path = os.path.join(self.all_database_path, self.database_name)
            os.makedirs(output_folder_path, exist_ok=True)
            csv_file_path = os.path.join(self.csv_folder_path, "zip_passwords.csv")

            with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(["ZIP File Name", "ZipFilePassword"])

                for file_name in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, file_name)
                    password = self.generate_random_password()
                    zip_file_name = f"{os.path.splitext(file_name)[0]}.zip"
                    zip_file_path = os.path.join(output_folder_path, zip_file_name)

                    with pyzipper.AESZipFile(zip_file_path, 'w', compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES) as zipf:
                        zipf.setpassword(password.encode('utf-8'))
                        zipf.write(file_path, arcname=file_name)

                    print(f"Created ZIP file: {zip_file_path} with a random password.")
                    csv_writer.writerow([zip_file_name, password])

            print(f"All ZIP files saved in: {output_folder_path}")
            print(f"Passwords saved to CSV file: {csv_file_path}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def list_folder_contents(self, folder_id, access_token):
        output_csv = os.path.join(self.csv_folder_path, f"pcloud_password.csv")
        url = "https://api.pcloud.com/listfolder"
        params = {"folderid": folder_id, "access_token": access_token}

        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data.get("result") == 0:
                    contents = data["metadata"].get("contents", [])
                    with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
                        writer = csv.writer(file)
                        writer.writerow(["ZIP File Name", "Filelink", "DatabaseName", "LinkPassword"])
                        for index, item in enumerate(contents):
                            if not item.get("isfolder", False):
                                file_id = item["fileid"]
                                file_name = item["name"]
                                link_password = self.generate_random_password()
                                response_data = self.fetch_file(file_id, link_password, access_token)
                                if response_data and response_data.get("result") == 0:
                                    link = response_data.get("link")
                                    writer.writerow([file_name, link, self.database_name, link_password])
                    print(f"Folder contents saved to {output_csv}")
                else:
                    print(f"Error in API response: {data.get('error', 'Unknown error')}")
            else:
                print(f"Failed to fetch folder contents. Status Code: {response.status_code}")
        except Exception as e:
            print("An error occurred:", str(e))

    @staticmethod
    def fetch_file(file_id, link_password, access_token):
        url = "https://api.pcloud.com/getfilepublink"
        params = {"fileid": file_id, "linkpassword": link_password, "access_token": access_token}
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to fetch file. Status Code: {response.status_code}")
                return None
        except Exception as e:
            print("An error occurred while fetching the file:", str(e))
            return None

    def merge_csv_files(self):
        try:
            zipped_files_path = os.path.join(self.csv_folder_path, f"pcloud_password.csv")
            zip_passwords_path = os.path.join(self.csv_folder_path, "zip_passwords.csv")
            merged_file_path = os.path.join(self.csv_output_path, f"{self.database_name}.csv")

            zipped_files = pd.read_csv(zipped_files_path)
            zip_passwords = pd.read_csv(zip_passwords_path)
            merged_data = pd.merge(zipped_files, zip_passwords, on='ZIP File Name', how='outer')

            #merged_data.drop(columns=['ZIP File Name'], inplace=True)
            merged_data.to_csv(merged_file_path, index=False)
            print(f"Merged data saved to: {merged_file_path}")
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="File Processor Command Line Interface")
    parser.add_argument("database_name", type=str, help="Name of the database")
    parser.add_argument("command", type=str, help="Command to execute: zip, list, merge")
    parser.add_argument("--folder_path", type=str, help="Path to the folder for zipping")
    parser.add_argument("--folder_id", type=str, help="Folder ID for listing contents")
    parser.add_argument("--access_token", type=str, help="Access token for API calls")

    args = parser.parse_args()

    processor = FileProcessor(args.database_name)

    if args.command == "zip" and args.folder_path:
        processor.zip_files_with_random_password(args.folder_path)
    elif args.command == "list" and args.folder_id and args.access_token:
        processor.list_folder_contents(args.folder_id, args.access_token)
    elif args.command == "merge":
        processor.merge_csv_files()
    else:
        print("Invalid command or missing arguments.")

