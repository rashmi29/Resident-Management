#importing all the required modules
import io

from flask import Flask, render_template, request
from pymysql import connections
import sys
import boto3
import os
from config import *
from PIL import Image
import json



app = Flask(__name__)

bucket = awsbucket
region = awsregion

db_conn = connections.Connection(
    host=apphost,
    port=3306,
    user=appuser,
    password=apppass,
    db=appdb
)


output = {}
table = 'resident'

#done
@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('admin.html')

#done
@app.route("/gotoadd", methods=['GET', 'POST'])
def gotoadd():
    return render_template('AddResident.html')

#done
@app.route("/about", methods=['GET', 'POST'])
def about():
    return render_template('about.html')

#done
@app.route("/addresident", methods=['POST'])
def AddResident():
    resident_id = request.form['resident_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    apt_num = request.form['apt_num']
    st_name = request.form['st_name']
    resident_image_file = request.files['resident_image_file']

    insert_sql = "INSERT INTO resident VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:

        cursor.execute(insert_sql, (resident_id, first_name,
                       last_name, apt_num, st_name))
        db_conn.commit()
        resident_name = "" + first_name + " " + last_name
        # Upload image file to S3 bucket #
        resident_image_file_name_in_s3 = "resident-id-" + str(resident_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(awsbucket).put_object(
                Key=resident_image_file_name_in_s3, Body=resident_image_file)
            bucket_location = boto3.client(
                's3').get_bucket_location(Bucket=awsbucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                awsbucket,
                resident_image_file_name_in_s3)

        except Exception as e:
            print(e)
            return render_template('Error1.html')

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('ResidentAdd_Success.html', name=resident_name)

#done
@app.route("/admin", methods=['GET', 'POST'])
def admin():
    return render_template("admin.html")

#done
@app.route("/getresident", methods=['GET', 'POST'])
def GetResident():
    return render_template("GetResidentInfo.html")

#done
@app.route("/fetchdata", methods=['POST'])
def FetchResident():
    resident_id = request.form['resident_id']

    output = {}
    select_sql = "SELECT resident_id, first_name, last_name, apt_num, st_name from resident where resident_id=%s"
    cursor = db_conn.cursor()
    resident_image_file_name_in_s3 = "resident-id-" + str(resident_id) + "_image_file"
    s3 = boto3.resource('s3')

    bucket_location = boto3.client(
        's3').get_bucket_location(Bucket=awsbucket)
    s3_location = (bucket_location['LocationConstraint'])

    if s3_location is None:
        s3_location = ''
    else:
        s3_location = '-' + s3_location

    image_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
        s3_location,
        awsbucket,
        resident_image_file_name_in_s3)
    print(image_url)

    try:
        cursor.execute(select_sql, (resident_id))
        result = cursor.fetchone()

        output["resident_id"] = result[0]
        print('EVERYTHING IS FINE TILL HERE')
        output["first_name"] = result[1]
        output["last_name"] = result[2]
        output["apt_num"] = result[3]
        output["st_name"] = result[4]
        print(output["resident_id"])

        return render_template("ResidentInfo_Output.html", id=output["resident_id"], fname=output["first_name"],
                               lname=output["last_name"], apt_num=output["apt_num"], st_name=output["st_name"], image_url=image_url)

    except Exception as e:
        print(e)
        return render_template('Error2.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
