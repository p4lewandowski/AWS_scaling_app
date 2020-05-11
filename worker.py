import boto3
import skimage.io
import skimage.transform
import os

sqs = boto3.resource("sqs")
queue = sqs.get_queue_by_name(QueueName="plewando-queue")
s3 = boto3.resource('s3')

while True:
    message_list = queue.receive_messages(MaxNumberOfMessages=3, VisibilityTimeout=30, WaitTimeSeconds=5)
    for message in message_list:
        image_name = message.body
        image = s3.meta.client.download_file("plewando-bucket", "images/{0}".format(image_name),
                                             "temp_{0}".format(image_name))
        image_to_transform = skimage.io.imread("temp_{0}".format(image_name))
        swirled_image = skimage.transform.swirl(image_to_transform, rotation=0, strength=10, radius=120)
        skimage.io.imsave("modified_{0}".format(image_name), swirled_image)
        s3.meta.client.upload_file("modified_{0}".format(image_name), "plewando-bucket",
                                   "images/modified_{}".format(image_name))

        message.delete()
        os.remove("temp_{0}".format(image_name))
        os.remove("modified_{0}".format(image_name))
