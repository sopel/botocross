# Copyright (c) 2012 Steffen Opel http://opelbrothers.net/
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

from datetime import datetime
from operator import attrgetter
import botocross as bc
import isodate
import logging
import time
ec2_log = logging.getLogger('botocross.ec2')

AWAIT_TRANSITION_DELAY = 4
AWAIT_TRANSITION_TIMEOUT = "P1D"
CREATED_BY_BOTO_EBS_SNAPSHOT_SCRIPT_SIGNATURE = "Created by Botocross EBS Snapshot Script from "
CREATED_BY_BOTO_EC2_IMAGE_SCRIPT_SIGNATURE = "Created by Botocross EC2 Image Script from "
IMAGE_STATES_PROGRESSING = { 'pending' }
IMAGE_STATES_SUCCEEDED = { 'available' }
IMAGE_STATES_FAILED = { 'failed', 'deregistered' }
SNAPSHOT_STATES_PROGRESSING = { 'pending' }
SNAPSHOT_STATES_SUCCEEDED = { 'completed' }
SNAPSHOT_STATES_FAILED = { 'error' }
TAG_NAME = "Name"
TAG_BACKUP_POLICY = "Backup Policy"

def derive_name(ec2, resource_id, iso_datetime=None, id_only=False):
    if not iso_datetime:
        iso_datetime = datetime.utcnow()

    name = resource_id
    if not id_only:
        filters = { "resource-id": resource_id}
        tags = ec2.get_all_tags(filters=filters)
        for tag in tags:
            if tag.name == TAG_NAME and tag.value:
                name = tag.value

    name += "." + iso_datetime.strftime("%Y%m%dT%H%M%SZ")
    return name

def format_states(states):
    return ', '.join(["{0}: {1}".format(k, len(v)) for (k, v) in states.iteritems()])

def await_resources(ec2, resource_function, resource_type, state_field, timeout, delay):
    log = ec2_log
    duration = None
    end = None
    states = {}

    if timeout:
        duration = isodate.parse_duration(timeout)
        end = datetime.now() + duration

    while True:
        states = {}
        resources = resource_function()
        for resource in resources:
            states.setdefault(getattr(resource, state_field), []).append(resource)

        # TODO: this should allow arbitrary resources via respective target state(s).
        if not "pending" in states:
            log.info("... {0} transitioned ({1})".format(resource_type, format_states(states)))
            break

        if end and datetime.now() > end:
            message = "FAILED to transition all {0} after {2} ({1})!".format(resource_type, format_states(states),
                                                                             isodate.duration_isoformat(duration))
            log.info("... " + message)
            raise bc.BotocrossAwaitTimeoutError(message)

        log.info("... {0} still transitioning ({1}) ...".format(resource_type, format_states(states)))
        time.sleep(delay)

    return states

def await_snapshots(ec2, snapshots, timeout=AWAIT_TRANSITION_TIMEOUT, delay=AWAIT_TRANSITION_DELAY):
    def list_snapshots():
        return ec2.get_all_snapshots(snapshot_ids=sorted(snapshots))

    return await_resources(ec2, list_snapshots, "snapshots", "status", timeout=timeout, delay=delay)

def create_snapshots(ec2, volumes, backup_set, description):
    log = ec2_log
    snapshots = []
    for volume in volumes:
        signature = description if description else CREATED_BY_BOTO_EBS_SNAPSHOT_SCRIPT_SIGNATURE + volume.id
        log.debug("Description: " + signature)
        snapshot = ec2.create_snapshot(volume.id, description=signature)
        # NOTE: create_image() currently (boto 2.6.0) returns just the id rather than the resource as create_snapshots() does!
        snapshots.append(snapshot.id)

        name = derive_name(ec2, volume.id)
        log.debug(TAG_NAME + ": " + name)
        tags = {TAG_NAME: name, TAG_BACKUP_POLICY: backup_set}
        ec2.create_tags([snapshot.id], tags)

    return snapshots

def expire_snapshots(ec2, volume_ids, backup_set, backup_retention, no_origin_safeguard=False):
    log = ec2_log
    for volume_id in volume_ids:
        snapshot_filters = {"volume-id": volume_id, "tag:" + TAG_BACKUP_POLICY: backup_set, "status": "completed"}
        if not no_origin_safeguard:
            snapshot_filters['description'] = CREATED_BY_BOTO_EBS_SNAPSHOT_SCRIPT_SIGNATURE + volume_id
        log.debug(snapshot_filters)
        snapshots = ec2.get_all_snapshots(owner='self', filters=snapshot_filters)
        log.info("Deleting snapshots of " + volume_id + " (set '" + backup_set + "', " + str(len(snapshots)) + " available, retaining " + str(backup_retention) + "):")
        # While snapshots are apparently returned in oldest to youngest order, this isn't documented;
        # therefore an explicit sort is performed to ensure this regardless.
        num_snapshots = len(snapshots);
        for snapshot in sorted(snapshots, key=attrgetter('start_time')):
            log.debug(snapshot.start_time)
            if num_snapshots <= backup_retention:
                log.info("... retaining last " + str(backup_retention) + " snapshots.")
                break
            num_snapshots -= 1
            log.info("... deleting snapshot '" + snapshot.id + "' ...")
            ec2.delete_snapshot(snapshot.id)

def await_images(ec2, images, timeout=AWAIT_TRANSITION_TIMEOUT, delay=AWAIT_TRANSITION_DELAY):
    def list_images():
        return ec2.get_all_images(image_ids=sorted(images), owners=['self'])

    return await_resources(ec2, list_images, "images", "state", timeout=timeout, delay=delay)

def create_images(ec2, instances, backup_set, description, no_reboot=False):
    log = ec2_log
    images = []
    for instance in instances:
        signature = description if description else CREATED_BY_BOTO_EC2_IMAGE_SCRIPT_SIGNATURE + instance.id
        log.debug("Description: " + signature)
        iso_datetime = datetime.utcnow()
        ami_name = derive_name(ec2, instance.id, iso_datetime, True)
        log.debug("AMI name: " + ami_name)
        image = ec2.create_image(instance.id, name=ami_name, description=signature, no_reboot=no_reboot)
        # NOTE: create_image() currently (boto 2.6.0) returns just the id rather than the resource as create_snapshots() does!
        images.append(image)

        name = derive_name(ec2, instance.id, iso_datetime)
        log.debug(TAG_NAME + ": " + name)
        tags = {TAG_NAME: name, TAG_BACKUP_POLICY: backup_set}
        ec2.create_tags([image], tags)

    return images

def expire_images(ec2, instance_ids, backup_set, backup_retention, no_origin_safeguard=False):
    log = ec2_log
    for instance_id in instance_ids:
        image_filters = {"name": instance_id + "*", "tag:" + TAG_BACKUP_POLICY: backup_set, "state": "available"}
        if not no_origin_safeguard:
            image_filters['description'] = CREATED_BY_BOTO_EC2_IMAGE_SCRIPT_SIGNATURE + instance_id
        log.debug(image_filters)
        images = ec2.get_all_images(owners=['self'], filters=image_filters)
        log.info("Deregistering images of " + instance_id + " (set '" + backup_set + "', " + str(len(images)) + " available, retaining " + str(backup_retention) + "):")
        # While images are apparently returned in oldest to youngest order, this isn't documented;
        # therefore an explicit sort is performed to ensure this regardless.
        num_images = len(images)
        for image in sorted(images, key=attrgetter('name')):
            log.debug(image.name)
            if num_images <= backup_retention:
                log.info("... retaining last " + str(backup_retention) + " images.")
                break
            num_images -= 1
            log.info("... deregistering image '" + image.id + "' ...")
            ec2.deregister_image(image.id, delete_snapshot=True)
