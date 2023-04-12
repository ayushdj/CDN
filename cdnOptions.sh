#!/usr/bin/env bash

# Define usage message
usage="Usage: $0 -p <port> -o <origin> -n <name> -u <username> -i <keyfile>"

# Parse command-line options
while [[ $# -gt 0 ]]; do
  case "$1" in
    -p)
      port="$2"
      shift 2
      ;;
    -o)
      origin="$2"
      shift 2
      ;;
    -n)
      name="$2"
      shift 2
      ;;
    -u)
      username="$2"
      shift 2
      ;;
    -i)
      keyfile="$2"
      shift 2
      ;;
    --help)
      # Print usage message and option descriptions
      echo $usage
      echo "-p value: Port number for DNS and HTTP replica servers"
      echo "-o value: Origin server"
      echo "-n value: CDN-specific name that translates to an IP"
      echo "-u value: ssh username"
      echo "-i value: ssh private key"
      exit 0
      ;;
    *)
      echo "Invalid option: $1"
      exit 1
      ;;
  esac
done

# Check if all options are provided
if [[ -z "$port" || -z "$origin" || -z "$name" || -z "$username" || -z "$keyfile" ]]; then
  echo "Error: All options are mandatory."
  echo $usage
  exit 1
fi

# Define an array of replica servers
replicas=(
"cdn-http1.5700.network"
"cdn-http2.5700.network"
"cdn-http3.5700.network"
"cdn-http4.5700.network"
"cdn-http5.5700.network"
"cdn-http6.5700.network"
"cdn-http7.5700.network"
)

ssh_options='-oBatchMode=yes -oUserKnownHostsFile=/dev/null -oStrictHostKeyChecking=no -oLogLevel=ERROR'