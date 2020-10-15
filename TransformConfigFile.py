#!/usr/bin/env python

import argparse
import yaml 
import json
import requests
import gnupg
import zipfile
import getpass
import subprocess
import hashlib
import os



origin_url = "https://releases.hashicorp.com/terraform"

def main():
  try:
    #args = parseArguments()
    #data = parseFile(args.configFile.name)
    terraform_version = "0.13.2"
    try:
      output = subprocess.check_output("terraform --version", shell = True ).decode("utf-8")
    except Exception as e:
      output = str(e.output)
    terraform_exists = output.find(terraform_version)
    print(str(terraform_exists))
    if terraform_exists == -1:
      # download terraform
      print("test2")
      error = installTerraform(terraform_version)
      if error > 0 :
        print("Therte were issues with installing terraform")
        raise Exception("Therte were issues with installing terraform")
    # if exists do other suff

	#&& curl -Os https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_SHA256SUMS.sig \
    print("done")
  except Exception as e:
    print(e)

def installTerraform(terraform_version):
  key = requests.get("https://keybase.io/hashicorp/pgp_keys.asc").content
  gpg = gnupg.GPG()
  import_result = gpg.import_keys(key)
  downloadAndSaveFile(origin_url + f"/{terraform_version}/terraform_{terraform_version}_linux_amd64.zip")
  downloadAndSaveFile(origin_url + f"/{terraform_version}/terraform_{terraform_version}_SHA256SUMS")
  downloadAndSaveFile(origin_url + f"/{terraform_version}/terraform_{terraform_version}_SHA256SUMS.sig")
  with open(f"terraform_{terraform_version}_SHA256SUMS.sig", "rb") as sig_file:
    verify = gpg.verify_file(sig_file, f"terraform_{terraform_version}_SHA256SUMS")
    print("Gpg veryfing status")
    print(verify.status)
    #if verify.status false than raise exception 

  #verify the shasum => first get the line 
  terraform_shasum = ""
  with open(f"terraform_{terraform_version}_SHA256SUMS", "r") as shasum_file:
    print("Reading shasm file")
    for line in shasum_file:
      if line.find(f"terraform_{terraform_version}_linux_amd64.zip") != -1:
        terraform_shasum = line.split()[0]
        print("terraform_shasum")
        print(terraform_shasum)
        break
  # get the shasum from the terraform zipfile and checki if it equals terraform_shasum
  file_hash = hashlib.sha256() 
  read_size = 65536
  with open(f"terraform_{terraform_version}_linux_amd64.zip", 'rb') as f: 
    fb = f.read(read_size) 
    while len(fb) > 0: 
        file_hash.update(fb) 
        fb = f.read(read_size)
  print("hexdigest")
  print(file_hash.hexdigest())
  if file_hash.hexdigest() != terraform_shasum:
    return
  # if shasum equals terroform shasum unpack terraform
  with zipfile.ZipFile(f"terraform_{terraform_version}_linux_amd64.zip", 'r') as zip_ref:
    zip_ref.extractall(f"/home/{getpass.getuser()}/bin")
  os.chmod(f'/home/{getpass.getuser()}/bin/terraform', 0o755)


def downloadAndSaveFile(url):
  terraform_resp = requests.get(url)
  terraform_file = open(url.rsplit('/', 1)[-1], 'wb')
  terraform_file.write(terraform_resp.content)
  terraform_resp.close()

def parseArguments():
  parser = argparse.ArgumentParser()
  parser.add_argument('configFile', type=argparse.FileType('r'),  help='Path to the config file')
  return parser.parse_args()

def parseFile(path):
  with open(path, 'r') as f:
    if path.endswith('.yml') or path.endswith('.yaml'):
      try:
        return yaml.safe_load(f)
      except yaml.YAMLError as exc:
          print(exc)
    elif path.endswith('.json'):
      return json.load(f)
    else:
      raise Exception("File is not in valid format")

main()