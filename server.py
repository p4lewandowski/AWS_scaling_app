from flask import Flask, request, render_template
import boto3

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/uploaded')
def uploaded():
    return render_template('uploaded.html')


@app.route('/modify')
def modify():
    client = boto3.client('s3')
    response = client.list_objects_v2(
        Bucket='plewando-bucket',
        Prefix='images/'
    )
    image_list = []
    for image in response["Contents"]:
        key = image["Key"]
        if '.' in key and 'modified' not in key:
            image_list.append(key.split('/')[1])

    url_list = []
    for image in image_list:
        url_list.append(client.generate_presigned_url('get_object',
                                                Params={
                                                    'Bucket': 'plewando-bucket',
                                                    'Key': 'images/{}'.format(image),
                                                },
                                                ExpiresIn=600))

    return render_template('modify.html', size=len(url_list), url_list=url_list, image_list=image_list)

@app.route('/modified')
def modified():
    client = boto3.client('s3')
    response = client.list_objects_v2(
        Bucket='plewando-bucket',
        Prefix='images/'
    )
    image_list = []
    for image in response["Contents"]:
        key = image["Key"]
        if '.' in key and 'modified' in key:
            image_list.append(image["Key"].split('/')[1])

    url_list = []
    for image in image_list:
        url_list.append(client.generate_presigned_url('get_object',
                                                Params={
                                                    'Bucket': 'plewando-bucket',
                                                    'Key': 'images/{}'.format(image),
                                                },
                                                ExpiresIn=600))

    return render_template('modified.html', size=len(url_list), url_list=url_list, image_list=image_list)

@app.route('/queue', methods=["POST"])
def queue():
    # Get image list and queue
    image_list = request.form.getlist("images")
    sqs = boto3.resource("sqs")
    queue = sqs.get_queue_by_name(QueueName="plewando-queue")
    # Send message to queue for each image in list
    for image_name in image_list:
        queue.send_message(MessageBody="{0}".format(image_name))

    return render_template("sent.html")

if __name__ == '__main__':
    app.run()
