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


origin_url = "https://releases.hashicorp.com/terraform"

def main():
  try:
    #args = parseArguments()
    #data = parseFile(args.configFile.name)
    terraform_version = "0.13.2"
    terraform_exists = terraform_version in terraform_version in subprocess.check_output("terraform --version", shell = True ).decode("utf-8") 
    if not terraform_exists:
      # download terraform
      error = installTerraform()
      if error > 0 :
        print("Therte wer issues with installing terraform")
        raise Exception("Therte wer issues with installing terraform")
    # if exists do other suff

	#&& curl -Os https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_SHA256SUMS.sig \
    test = ""
  except Exception as e:
    print(e)

def installTerraform(terraform_version):
  key = requests.get("https://keybase.io/hashicorp/pgp_keys.asc").content
  gpg = gnupg.GPG()
  import_result = gpg.import_keys(key)

  downloadAndSaveFile(originUrl + f"/{terraform_version}/terraform_{terraform_version}_linux_amd64.zip")
  downloadAndSaveFile(originUrl + f"/{terraform_version}/terraform_{terraform_version}_SHA256SUMS")
  downloadAndSaveFile(originUrl + f"/{terraform_version}/terraform_{terraform_version}_SHA256SUMS.sig")
  #terraform_0.13.3_linux_amd64.zip
 
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

  #	&& gpg --verify terraform_${TERRAFORM_VERSION}_SHA256SUMS.sig terraform_${TERRAFORM_VERSION}_SHA256SUMS \
  #   && grep 'linux_amd64\.zip$' terraform_${TERRAFORM_VERSION}_SHA256SUMS >  terraform_${TERRAFORM_VERSION}_linux_amd64_SHA256SUMS \
	#&& shasum -a 256 -c terraform_${TERRAFORM_VERSION}_linux_amd64_SHA256SUMS \

def downloadAndSaveFile(url):
  terraform_resp = requests.get(url)
  terraform_file = open(url.rsplit('/', 1)[-1], 'wb')
  terraform_file.write(terraform_resp)
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