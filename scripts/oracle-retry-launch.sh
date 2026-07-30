#!/bin/bash
# Retries launching an Oracle Cloud Always Free Ampere A1 instance until
# it succeeds, backing off correctly on both "out of capacity" and
# "too many requests" responses. Run from Oracle Cloud Shell (OCI CLI
# comes pre-authenticated there — no local setup needed).
#
# Fill in the four values below before running. Get them with:
#   echo $OCI_CLI_TENANCY_ID                      # compartment/tenancy OCID
#   oci iam availability-domain list               # availability domain name
#   oci network subnet list --compartment-id ...   # your public subnet OCID
#   oci compute image list --compartment-id ...    # an Ubuntu aarch64 image OCID
#     --operating-system "Canonical Ubuntu" --operating-system-version "24.04" \
#     --shape "VM.Standard.A1.Flex"

COMPARTMENT_ID="<your-compartment-ocid>"
AD="<your-availability-domain-name>"
SUBNET_ID="<your-public-subnet-ocid>"
IMAGE_ID="<your-ubuntu-aarch64-image-ocid>"
SHAPE="VM.Standard.A1.Flex"
OCPUS=1          # start small — a 1-OCPU request succeeds far more often
                 # than a larger one when capacity is tight; resize up later
MEMORY_GB=6
DISPLAY_NAME="health-fact-n8n"

[ -f ~/.ssh/id_rsa.pub ] || ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa

while true; do
  echo "$(date): attempting launch..."
  oci compute instance launch \
    --compartment-id "$COMPARTMENT_ID" \
    --availability-domain "$AD" \
    --shape "$SHAPE" \
    --shape-config "{\"ocpus\": $OCPUS, \"memoryInGBs\": $MEMORY_GB}" \
    --subnet-id "$SUBNET_ID" \
    --image-id "$IMAGE_ID" \
    --display-name "$DISPLAY_NAME" \
    --assign-public-ip true \
    --ssh-authorized-keys-file ~/.ssh/id_rsa.pub \
    --wait-for-state RUNNING 2> launch_error.log

  if [ $? -eq 0 ]; then
    echo "$(date): SUCCESS — instance is running!"
    break
  elif grep -qi "OutOfCapacity\|OutOfHostCapacity\|out of host capacity" launch_error.log; then
    echo "$(date): out of capacity, retrying in 5 min..."
    sleep 300
  elif grep -qi "TooManyRequests" launch_error.log; then
    echo "$(date): rate-limited by Oracle, backing off 5 min..."
    sleep 300
  else
    echo "$(date): different error — stopping to show you:"
    cat launch_error.log
    break
  fi
done
